"""
HTTP utilities for handling file downloads with Unicode filenames
"""
import re
import unicodedata
from urllib.parse import quote


def content_disposition_for_filename(filename: str) -> str:
    """
    Generate Content-Disposition header value with RFC 5987 encoding support
    
    This provides both ASCII and UTF-8 versions of the filename:
    - filename="ascii_version" - for older browsers
    - filename*=UTF-8''utf8_version - for modern browsers (supports Chinese, etc.)
    
    Args:
        filename: Original filename (may contain Unicode characters)
        
    Returns:
        Content-Disposition header value
        
    Example:
        >>> content_disposition_for_filename("resume_张三.pdf")
        'attachment; filename="resume___.pdf"; filename*=UTF-8\'\'resume_%E5%BC%A0%E4%B8%89.pdf'
    """
    def slugify_ascii(value: str) -> str:
        """Convert Unicode string to ASCII-safe version"""
        # Normalize Unicode characters (e.g., é -> e)
        v = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
        # Replace non-alphanumeric characters with underscore
        v = re.sub(r"[^A-Za-z0-9._-]+", "_", v).strip("_")
        return v or "download"
    
    # ASCII version for compatibility
    ascii_name = slugify_ascii(filename)
    
    # RFC 5987 format: filename*=UTF-8''<percent-encoded-filename>
    return f'attachment; filename="{ascii_name}"; filename*=UTF-8\'\'{quote(filename)}'