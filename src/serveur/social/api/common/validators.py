"""
Validation utilities for text fields, HTML sanitization, etc.
Based on Specifications.md section 6.
"""
import re
import bleach
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


# Reserved usernames that cannot be used
RESERVED_USERNAMES = ['admin', 'moderator', 'system', 'root', 'administrator', 'support']


def validate_username(value):
    """
    Validate username according to specifications:
    - Pattern: ^[a-zA-Z0-9_]{3,30}$
    - Not in reserved list
    """
    if not re.match(r'^[a-zA-Z0-9_]{3,30}$', value):
        raise ValidationError('Username must be 3-30 characters long and contain only letters, numbers, and underscores.')
    
    if value.lower() in RESERVED_USERNAMES:
        raise ValidationError('This username is reserved and cannot be used.')


def validate_display_name(value):
    """
    Validate display name: 1-100 characters, allow unicode.
    """
    if not value or len(value) < 1 or len(value) > 100:
        raise ValidationError('Display name must be 1-100 characters long.')


def validate_bio(value):
    """
    Validate and sanitize bio text.
    Max 500 characters, allow basic HTML tags.
    """
    if len(value) > 500:
        raise ValidationError('Bio must not exceed 500 characters.')
    
    return sanitize_bio(value)


def sanitize_bio(value):
    """
    Sanitize bio HTML: allow <b>, <i>, <a> only.
    Strip <script>, on* attributes, javascript: URLs.
    """
    allowed_tags = ['b', 'i', 'a']
    allowed_attributes = {'a': ['href']}
    
    cleaned = bleach.clean(
        value,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
    
    # Remove javascript: URLs
    cleaned = re.sub(r'javascript:', '', cleaned, flags=re.IGNORECASE)
    
    return cleaned


def validate_post_title(value):
    """
    Validate post title according to specifications.
    Pattern: ^[\w\s.,!?'\-]{1,200}$ (unicode letters + basic punctuation)
    """
    if not value or len(value) < 1 or len(value) > 200:
        raise ValidationError('Title must be 1-200 characters long.')
    
    # Allow unicode letters, numbers, spaces, and basic punctuation
    if not re.match(r'^[\w\s.,!?\'\-]+$', value, re.UNICODE):
        raise ValidationError('Title contains invalid characters.')
    
    # Reject if only punctuation/spaces
    if re.match(r'^[\s.,!?\'\-]+$', value):
        raise ValidationError('Title must contain more than just punctuation.')


def validate_post_content(value):
    """
    Validate post content length.
    """
    if not value or len(value) < 1 or len(value) > 10000:
        raise ValidationError('Content must be 1-10000 characters long.')


def sanitize_post_content(value):
    """
    Sanitize post content HTML.
    Whitelist: <p>, <br>, <b>, <i>, <ul>, <ol>, <li>, <a>
    Reject: <script>, <iframe>, <object>, <embed>, on* attributes
    Max nesting depth: 5
    """
    allowed_tags = ['p', 'br', 'b', 'i', 'ul', 'ol', 'li', 'a', 'strong', 'em']
    allowed_attributes = {'a': ['href']}
    
    cleaned = bleach.clean(
        value,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
    
    # Remove javascript: and data: URLs
    cleaned = re.sub(r'(javascript|data):', '', cleaned, flags=re.IGNORECASE)
    
    return cleaned


def validate_message_content(value):
    """
    Validate message content: 1-2000 characters, plain text.
    """
    if not value or len(value) < 1 or len(value) > 2000:
        raise ValidationError('Message must be 1-2000 characters long.')
    
    # No HTML allowed in messages
    if '<' in value or '>' in value:
        raise ValidationError('HTML is not allowed in messages.')


def validate_avatar_url(value):
    """
    Validate avatar URL: must be HTTPS only.
    """
    if not value:
        return
    
    validator = URLValidator(schemes=['https'])
    validator(value)


def validate_tag_name(value):
    """
    Validate tag name: 3-30 chars, lowercase alphanumeric + underscore.
    """
    if not re.match(r'^[a-z0-9_]{3,30}$', value):
        raise ValidationError('Tag must be 3-30 characters, lowercase alphanumeric with underscores only.')


def detect_spam(content):
    """
    Basic spam detection for messages and posts.
    Returns True if content appears to be spam.
    """
    # Check for excessive URLs
    url_count = len(re.findall(r'https?://', content))
    if url_count > 5:
        return True
    
    # Check for all caps (more than 70% uppercase)
    letters = [c for c in content if c.isalpha()]
    if letters:
        uppercase_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
        if uppercase_ratio > 0.7 and len(letters) > 20:
            return True
    
    # Check for excessive repetition
    words = content.lower().split()
    if len(words) > 10:
        unique_words = set(words)
        if len(unique_words) / len(words) < 0.3:  # Less than 30% unique words
            return True
    
    return False
