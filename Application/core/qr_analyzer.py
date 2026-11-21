"""
ScamShield — QR Code Analyzer
Decodes QR using OpenCV + pyzbar, then routes to URL/SMS analyzer.
Supports URLs both with and without explicit scheme.
"""
import re
import ipaddress
from urllib.parse import urlsplit
import cv2
import numpy as np
from utils.validators import is_valid_url
from utils.logger import get_logger

logger = get_logger("qr_analyzer")

try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False
    logger.warning("pyzbar not installed; QR decoding unavailable.")


def is_url_content(text: str) -> bool:
    """
    Determine whether decoded text is a URL, with or without an explicit scheme.
    Rejects multi-line or whitespace-containing text messages.
    """
    text = str(text).strip()
    if not text or " " in text or "\n" in text or "\r" in text:
        return False

    if is_valid_url(text):
        return True

    if text.lower().startswith(("www.", "//")):
        return True

    candidate = text if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", text) else "http://" + text
    try:
        parsed = urlsplit(candidate)
        hostname = (parsed.hostname or "").lower().rstrip(".")
        if not hostname:
            return False

        try:
            ipaddress.ip_address(hostname)
            return True
        except ValueError:
            pass

        parts = hostname.split(".")
        if len(parts) >= 2 and all(len(p) > 0 for p in parts) and len(parts[-1]) >= 2:
            return True
    except Exception:
        pass

    return False


class QRAnalyzer:
    def __init__(self, url_analyzer=None, sms_analyzer=None):
        self.url_analyzer = url_analyzer
        self.sms_analyzer = sms_analyzer

    def is_url(self, text: str) -> bool:
        """Helper to test if a decoded text payload is a URL."""
        return is_url_content(text)

    def decode_image(self, image_bytes: bytes) -> dict:
        """
        Accepts raw image bytes, returns decoded QR content.
        Returns {"status": "ok", "data": str, "data_type": str, "barcode_type": str}
        or      {"status": "error"|"no_qr_found", "message": str}
        """
        try:
            # Convert bytes → numpy array → OpenCV image
            nparr  = np.frombuffer(image_bytes, np.uint8)
            img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img_cv is None:
                return {"status": "error", "message": "Could not decode image file."}

            data = ""
            barcode_type = "QR"

            if PYZBAR_AVAILABLE:
                # Pre-process: grayscale + adaptive threshold for better detection
                gray   = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                thresh = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY, 11, 2
                )

                codes = pyzbar.decode(thresh) or pyzbar.decode(gray)
                if codes:
                    code = codes[0]
                    data = code.data.decode("utf-8", errors="replace")
                    barcode_type = code.type

            # Fallback to OpenCV QRCodeDetector if pyzbar not installed or found no code
            if not data:
                detector = cv2.QRCodeDetector()
                decoded_info, points, _ = detector.detectAndDecode(img_cv)
                if decoded_info:
                    data = decoded_info
                    barcode_type = "QRCODE"

            if not data:
                return {"status": "no_qr_found", "message": "No QR code detected in image."}

            data_type = "url" if is_url_content(data) else "text"

            return {
                "status":       "ok",
                "data":         data,
                "data_type":    data_type,
                "barcode_type": barcode_type,
            }
        except Exception as e:
            logger.error(f"QR decode error: {e}")
            return {"status": "error", "message": str(e)}

    def route_and_analyze(self, data: str, data_type: str = None, url_analyzer=None, sms_analyzer=None) -> dict:
        """
        Routes extracted payload to URLAnalyzer (if URL) or SMSAnalyzer (if text).
        """
        u_analyzer = url_analyzer or self.url_analyzer
        s_analyzer = sms_analyzer or self.sms_analyzer
        target_type = data_type or ("url" if is_url_content(data) else "text")

        if target_type == "url" and u_analyzer:
            result = u_analyzer.predict(data)
            result["qr_source"] = True
            result["routed_to"] = "URLAnalyzer"
            return result
        elif target_type != "url" and s_analyzer:
            result = s_analyzer.predict(data)
            result["qr_source"] = True
            result["routed_to"] = "SMSAnalyzer"
            return result
        else:
            return {
                "status": "error",
                "message": f"Analyzer for {target_type} is not available.",
                "data_type": target_type
            }
