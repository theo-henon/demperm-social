"""
JWT Authentication backend for DRF.
"""
import jwt
import datetime
from django.conf import settings
from django.utils import timezone
from rest_framework import authentication, exceptions
from .models import User, RefreshToken


def create_access_token(user):
    """Generate JWT access token (15 minutes validity)."""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'roles': user.roles or ['user'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME),
        'iat': datetime.datetime.utcnow(),
        'type': 'access'
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')


def create_refresh_token(user):
    """Generate and store refresh token (7 days validity)."""
    expires_at = timezone.now() + datetime.timedelta(seconds=settings.JWT_REFRESH_TOKEN_LIFETIME)
    
    payload = {
        'user_id': user.id,
        'exp': expires_at,
        'iat': timezone.now(),
        'type': 'refresh'
    }
    token_string = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
    
    # Store in database
    RefreshToken.objects.create(
        user=user,
        token=token_string,
        expires_at=expires_at
    )
    
    return token_string


def decode_refresh_token(token):
    """Decode and validate refresh token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        if payload.get('type') != 'refresh':
            raise jwt.InvalidTokenError('Not a refresh token')
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.InvalidTokenError('Token expired')
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError('Invalid token')


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Custom JWT authentication for Django REST Framework.
    Expects: Authorization: Bearer <token>
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decode and verify token
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
            
            # Verify it's an access token
            if payload.get('type') != 'access':
                raise exceptions.AuthenticationFailed('Invalid token type')
            
            # Get user
            user_id = payload.get('user_id')
            if not user_id:
                raise exceptions.AuthenticationFailed('Invalid token payload')
            
            user = User.objects.filter(id=user_id).first()
            if not user:
                raise exceptions.AuthenticationFailed('User not found')
            
            return (user, token)
        
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
    
    def authenticate_header(self, request):
        return 'Bearer'
