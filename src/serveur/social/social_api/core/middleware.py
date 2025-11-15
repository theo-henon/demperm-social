"""
Rate limiting middleware using Redis.
Based on Specifications.md section 7.
"""
import time
import hashlib
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status


class RateLimitMiddleware:
    """
    Rate limiting middleware using Redis with sliding window algorithm.
    """
    
    # Rate limits by endpoint pattern (requests / seconds)
    RATE_LIMITS = {
        # Authentication
        'POST:/api/v1/auth/login': (5, 900),  # 5 per 15 min
        'POST:/api/v1/auth/register': (3, 3600),  # 3 per hour
        'POST:/api/v1/auth/refresh': (10, 60),  # 10 per minute
        
        # Read operations
        'GET:/api/v1/users/search': (100, 3600),  # 100 per hour
        'GET:/api/v1/users/bulk': (50, 3600),  # 50 per hour
        'GET:/api/v1/posts/feed': (200, 3600),  # 200 per hour
        'GET:/api/v1/messages/': (1000, 3600),  # 1000 per hour
        
        # Write operations
        'POST:/api/v1/posts/create': (10, 3600),  # 10 per hour
        'PATCH:/api/v1/posts/': (20, 3600),  # 20 per hour
        'DELETE:/api/v1/posts/': (100, 86400),  # 100 per day
        
        'POST:/api/v1/messages/': (50, 3600),  # 50 per hour
        'DELETE:/api/v1/messages/': (20, 3600),  # 20 per hour
        
        'POST:/api/v1/followers/': (20, 3600),  # 20 per hour
        
        'POST:/api/v1/forums/create': (5, 3600),  # 5 per hour
        'POST:/api/v1/subscriptions/': (50, 3600),  # 50 per hour
        
        'PATCH:/api/v1/users/me': (10, 3600),  # 10 per hour
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check rate limit before processing request
        if not self._check_rate_limit(request):
            return self._rate_limit_exceeded_response(request)
        
        response = self.get_response(request)
        
        # Add rate limit headers to response
        self._add_rate_limit_headers(response, request)
        
        return response
    
    def _get_rate_limit_key(self, request):
        """
        Generate Redis key for rate limiting.
        Format: rate_limit:{endpoint}:{user_id|ip}:{window}
        """
        # Get endpoint pattern
        method = request.method
        path = request.path
        
        # Normalize path (remove UUIDs and IDs)
        import re
        normalized_path = re.sub(
            r'/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',
            '/:uuid',
            path
        )
        normalized_path = re.sub(r'/\d+', '/:id', normalized_path)
        
        endpoint = f"{method}:{normalized_path}"
        
        # Get identifier (user ID or IP)
        if request.user and request.user.is_authenticated:
            identifier = f"user:{request.user.id}"
        else:
            identifier = f"ip:{self._get_client_ip(request)}"
        
        # Get current time window
        window = int(time.time())
        
        return f"rate_limit:{endpoint}:{identifier}:{window}"
    
    def _get_client_ip(self, request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _check_rate_limit(self, request):
        """
        Check if request is within rate limit.
        Returns True if allowed, False if exceeded.
        """
        # Get rate limit for this endpoint
        method = request.method
        path = request.path
        
        # Normalize path
        import re
        normalized_path = re.sub(
            r'/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',
            '/:uuid',
            path
        )
        normalized_path = re.sub(r'/\d+', '/:id', normalized_path)
        
        endpoint = f"{method}:{normalized_path}"
        
        # Find matching rate limit
        limit_count, limit_window = None, None
        for pattern, (count, window) in self.RATE_LIMITS.items():
            if endpoint.startswith(pattern) or pattern in endpoint:
                limit_count, limit_window = count, window
                break
        
        # No rate limit configured for this endpoint
        if limit_count is None:
            return True
        
        # Get identifier
        if request.user and request.user.is_authenticated:
            identifier = f"user:{request.user.id}"
        else:
            identifier = f"ip:{self._get_client_ip(request)}"
        
        # Generate cache key
        current_window = int(time.time() / limit_window)
        cache_key = f"rate_limit:{endpoint}:{identifier}:{current_window}"
        
        # Get current count
        current_count = cache.get(cache_key, 0)
        
        # Check if exceeded
        if current_count >= limit_count:
            # Log rate limit violation
            self._log_rate_limit_violation(request, endpoint)
            return False
        
        # Increment counter
        cache.set(cache_key, current_count + 1, limit_window)
        
        # Store limit info for headers
        request._rate_limit_info = {
            'limit': limit_count,
            'remaining': limit_count - current_count - 1,
            'reset': (current_window + 1) * limit_window,
            'window': limit_window
        }
        
        return True
    
    def _log_rate_limit_violation(self, request, endpoint):
        """Log rate limit violation for analysis."""
        from .models import AuditLog
        
        try:
            AuditLog.objects.create(
                event_type='rate_limit.exceeded',
                actor=request.user if request.user.is_authenticated else None,
                target_type='endpoint',
                target_id=None,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                payload={'endpoint': endpoint}
            )
        except Exception:
            # Don't fail the request if logging fails
            pass
    
    def _rate_limit_exceeded_response(self, request):
        """Return 429 response when rate limit is exceeded."""
        retry_after = getattr(request, '_rate_limit_info', {}).get('window', 3600)
        
        response = JsonResponse({
            'error': 'Rate limit exceeded',
            'retry_after': retry_after
        }, status=429)
        
        response['Retry-After'] = retry_after
        
        return response
    
    def _add_rate_limit_headers(self, response, request):
        """Add rate limit headers to response."""
        info = getattr(request, '_rate_limit_info', None)
        if info:
            response['X-RateLimit-Limit'] = info['limit']
            response['X-RateLimit-Remaining'] = info['remaining']
            response['X-RateLimit-Reset'] = info['reset']
