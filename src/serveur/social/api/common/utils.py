"""
Common utility functions.
"""
from django.core.paginator import Paginator
from rest_framework.response import Response


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def paginate_queryset(queryset, request, page_size=20):
    """
    Paginate a queryset.
    
    Args:
        queryset: Django queryset to paginate
        request: HTTP request object
        page_size: Number of items per page
    
    Returns:
        tuple: (paginated_data, has_next, has_previous)
    """
    page_number = request.GET.get('page', 1)
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page_number)
    
    return (
        page_obj.object_list,
        page_obj.has_next(),
        page_obj.has_previous()
    )


def success_response(data=None, message=None, status=200):
    """
    Standard success response format.
    """
    response_data = {}
    if data is not None:
        response_data['data'] = data
    if message:
        response_data['message'] = message
    return Response(response_data, status=status)


def error_response(message, errors=None, status=400):
    """
    Standard error response format.
    """
    response_data = {'error': message}
    if errors:
        response_data['details'] = errors
    return Response(response_data, status=status)
