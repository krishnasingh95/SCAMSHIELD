"""
ScamShield — Feature Extractors (structural, text, URL)
These extract raw features; ML prediction happens in core/ analyzers.
Aligned exactly with training pipeline feature definitions and metadata.
"""
import re
import ipaddress
from urllib.parse import urlsplit


# ─── SMS / Text Features ─────────────────────────────────────────────────────

# Exact 26 suspicious keywords from training metadata
SCAM_KEYWORDS = [
    "urgent", "winner", "won", "free", "claim",
    "prize", "cash", "guaranteed", "offer",
    "credit", "loan", "verify", "login",
    "click", "award", "congratulations",
    "selected", "limited", "immediately",
    "suspended", "blocked", "password",
    "otp", "bank", "kyc", "payment"
]

# Exact URL detection pattern from training notebook
URL_PATTERN = re.compile(
    r"(?i)(?<![@\w])(?:https?://|www\.)?"
    r"[a-z0-9-]+(?:\.[a-z0-9-]+)+"
    r"(?:/[^\s<>\"']*)?"
)


def extract_sms_features(text: str) -> dict:
    """Extract structural and lexical features from SMS text matching training."""
    message = str(text)
    lower_message = message.lower()
    total_chars = len(message)

    # Character and word features
    char_count = total_chars
    word_count = len(message.split())

    # URL features
    urls = URL_PATTERN.findall(message)
    url_count = len(urls)
    has_url = int(url_count > 0)

    # Uppercase ratio
    uppercase_ratio = (
        sum(char.isupper() for char in message) / total_chars
        if total_chars > 0 else 0.0
    )

    # Digit ratio
    digit_ratio = (
        sum(char.isdigit() for char in message) / total_chars
        if total_chars > 0 else 0.0
    )

    # Special characters
    special_char_count = len(
        re.findall(r"[!?$#@*]", message)
    )

    # Suspicious keyword hits (cumulative occurrences with word boundaries)
    keyword_hits = sum(
        len(re.findall(
            r"(?<!\w)" + re.escape(word) + r"(?!\w)",
            lower_message
        ))
        for word in SCAM_KEYWORDS
    )

    # Punctuation features
    exclamation_count = message.count("!")
    question_count = message.count("?")

    features = {
        "char_count":           char_count,
        "word_count":           word_count,
        "url_count":            url_count,
        "has_url":              has_url,
        "uppercase_ratio":      uppercase_ratio,
        "digit_ratio":          digit_ratio,
        "special_char_count":   special_char_count,
        "keyword_hits":         keyword_hits,
        "exclamation_count":    exclamation_count,
        "question_count":       question_count,
    }

    # UI presentation metadata
    features["_matched_keywords"] = [
        kw for kw in SCAM_KEYWORDS
        if re.search(r"(?<!\w)" + re.escape(kw) + r"(?!\w)", lower_message)
    ]
    features["_extracted_urls"]   = urls
    return features


# ─── URL Features ─────────────────────────────────────────────────────────────

# Exact 9 suspicious TLDs from training metadata
SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq",
    "xyz", "top", "click", "pw"
}

# Exact 16 brand keywords from training metadata
BRAND_KEYWORDS = [
    "paypal", "google", "amazon", "apple",
    "microsoft", "facebook", "instagram",
    "whatsapp", "netflix", "sbi",
    "hdfc", "icici", "axisbank",
    "paytm", "phonepe", "visa"
]


def extract_url_features(url: str) -> dict:
    """Extract structural features from a URL string matching training."""
    url = str(url).strip()
    lower_url = url.lower()

    # Handle URLs without schemes (matching training cell 15)
    candidate = url
    if candidate.startswith("//"):
        candidate = "http:" + candidate
    elif not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", candidate):
        candidate = "http://" + candidate

    try:
        parsed = urlsplit(candidate)
    except Exception:
        return {}

    # Extract hostname
    domain = (parsed.hostname or "").lower().rstrip(".")

    # Detect IP address
    try:
        ipaddress.ip_address(domain)
        has_ip = 1
    except ValueError:
        has_ip = 0

    # TLD extraction
    if has_ip or "." not in domain:
        tld = ""
    else:
        tld = domain.rsplit(".", 1)[-1]

    has_suspicious_tld = int(tld in SUSPICIOUS_TLDS)

    # Domain components
    domain_parts = domain.split(".") if domain else []
    num_subdomains = max(domain.count("."), 0)

    # Brand detection
    has_brand_keyword = int(
        any(brand in domain for brand in BRAND_KEYWORDS)
    )

    # Brand in leftmost subdomain
    brand_in_subdomain = int(
        len(domain_parts) > 2
        and any(
            brand in domain_parts[0]
            for brand in BRAND_KEYWORDS
        )
    )

    # Redirect indicators
    has_redirect = int(
        "redirect" in lower_url
        or "url=" in lower_url
    )

    features = {
        "url_length":           len(url),
        "domain_length":        len(domain),
        "path_length":          len(parsed.path),
        "query_length":         len(parsed.query),
        "num_subdomains":       num_subdomains,
        "has_ip_address":       has_ip,
        "has_https":            int(parsed.scheme.lower() == "https"),
        "has_suspicious_tld":   has_suspicious_tld,
        "num_special_chars":    sum(char in "-_@!%" for char in url),
        "num_digits_in_domain": sum(char.isdigit() for char in domain),
        "has_brand_keyword":    has_brand_keyword,
        "brand_in_subdomain":   brand_in_subdomain,
        "has_redirect":         has_redirect,
        "path_depth":           parsed.path.count("/"),
    }

    # UI presentation metadata
    features["_parsed_domain"] = domain
    features["_tld"]           = f".{tld}" if tld else ""
    features["_scheme"]        = parsed.scheme
    return features
