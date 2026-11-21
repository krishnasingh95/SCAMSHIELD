"""
ScamShield — Input Validators
"""
import re
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """
    Return True if the string looks like a valid URL or web domain.
    Supports schemes (http, https, ftp) as well as raw domain/path formats.
    """
    if not url or not isinstance(url, str):
        return False
    
    cleaned = url.strip()
    if not cleaned or " " in cleaned or "\n" in cleaned:
        return False

    candidate = cleaned
    if candidate.startswith("//"):
        candidate = "http:" + candidate
    elif not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", candidate):
        candidate = "http://" + candidate

    try:
        result = urlparse(candidate)
        netloc = (result.netloc or "").strip()
        if not netloc:
            return False
        # Valid domain hostname or IP
        return ("." in netloc or ":" in netloc or netloc.count(".") >= 1)
    except Exception:
        return False


def normalize_url(url: str) -> str:
    """Ensure URL string has a standard scheme prefix for consistent handling."""
    cleaned = (url or "").strip()
    if not cleaned:
        return ""
    if cleaned.startswith("//"):
        return "http:" + cleaned
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", cleaned):
        return "https://" + cleaned
    return cleaned


def sanitize_text(text: str, max_length: int = 5000) -> str:
    """Strip leading/trailing whitespace and enforce max length."""
    return text.strip()[:max_length]


def is_empty(text: str) -> bool:
    return not text or not text.strip()

