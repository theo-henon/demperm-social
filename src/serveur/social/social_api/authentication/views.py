"""
Authentication views using JWT.
Based on Specifications.md section 3.1.
"""
import jwt
import datetime
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from core.models import User, RefreshToken, AuditLog


def generate_access_token(user):
    """Generate JWT access token (15 minutes validity)."""
    import uuid
    payload = {
        'user_id': user.id,
        'username': user.username,
        'roles': user.roles or ['user'],
        'jti': str(uuid.uuid4()),  # Unique token identifier
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
        'iat': datetime.datetime.utcnow(),
        'type': 'access'
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def generate_refresh_token(user):
    """Generate and store refresh token (7 days validity)."""
    import uuid
    expires_at = timezone.now() + datetime.timedelta(days=7)
    
    payload = {
        'user_id': user.id,
        'jti': str(uuid.uuid4()),  # Unique token identifier
        'exp': expires_at,
        'iat': timezone.now(),
        'type': 'refresh'
    }
    token_string = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    # Store in database
    refresh_token = RefreshToken.objects.create(
        user=user,
        token=token_string,
        expires_at=expires_at
    )
    
    return token_string


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class LoginView(APIView):
    """POST /api/v1/auth/login"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Username and password required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            AuditLog.objects.create(
                event_type='auth.login.failed',
                actor=None,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                payload={'username': username}
            )
            
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)
        
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        AuditLog.objects.create(
            event_type='auth.login.success',
            actor=user,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 900
        }, status=status.HTTP_200_OK)


class RefreshTokenView(APIView):
    """POST /api/v1/auth/refresh"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token_string = request.data.get('refresh_token')
        
        if not refresh_token_string:
            return Response(
                {'error': 'Refresh token required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            payload = jwt.decode(
                refresh_token_string,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            if payload.get('type') != 'refresh':
                return Response(
                    {'error': 'Invalid token type'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            refresh_token = RefreshToken.objects.filter(
                token=refresh_token_string,
                revoked=False
            ).first()
            
            if not refresh_token or not refresh_token.is_valid():
                return Response(
                    {'error': 'Invalid or expired refresh token'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            user = refresh_token.user
            
            # Revoke old token (token rotation)
            refresh_token.revoked = True
            refresh_token.save(update_fields=['revoked'])
            
            # Generate new tokens
            new_access_token = generate_access_token(user)
            new_refresh_token = generate_refresh_token(user)
            
            return Response({
                'access_token': new_access_token,
                'refresh_token': new_refresh_token,
                'expires_in': 900
            }, status=status.HTTP_200_OK)
        
        except jwt.ExpiredSignatureError:
            return Response(
                {'error': 'Refresh token expired'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except jwt.InvalidTokenError:
            return Response(
                {'error': 'Invalid refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    """POST /api/v1/auth/logout"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        refresh_token_string = request.data.get('refresh_token')
        
        if not refresh_token_string:
            return Response(
                {'error': 'Refresh token required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        RefreshToken.objects.filter(
            token=refresh_token_string,
            user=request.user
        ).update(revoked=True)
        
        AuditLog.objects.create(
            event_type='auth.logout',
            actor=request.user,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(APIView):
    """POST /api/v1/auth/register"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        from core.serializers import UserRegistrationSerializer
        
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            AuditLog.objects.create(
                event_type='auth.register',
                actor=user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)
            
            return Response({
                'user': {
                    'id': str(user.public_uuid),
                    'username': user.username,
                    'email': user.email
                },
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': 900
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
