"""
utils/translation_utils.py

Lightweight regional-language translation for the Farmer Assistant (Bonus E).
Uses `deep-translator` (free, wraps Google Translate's public endpoint — no
API key needed) with an in-memory cache so the same sentence is never
translated twice in a session.

If the translation backend is unreachable (offline judging environment,
firewall, etc.) we fail SOFT: return the original English text rather than
crashing the request. This keeps the core/bonus modules demo-safe.

Rate-limit handling: Google's free endpoint allows ~5 requests/second.
We serialize requests via a threading lock and retry with exponential
backoff when rate-limited (up to 3 retries), which eliminates the
"too many requests" errors that were causing language switching to fail.
"""

from functools import lru_cache
import logging
import threading
import time

logger = logging.getLogger(__name__)

# BCP-ish codes -> (display name, deep_translator/Google code)
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "gu": "Gujarati",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "bn": "Bengali",
    "pa": "Punjabi",
}

try:
    from deep_translator import GoogleTranslator
    _BACKEND_AVAILABLE = True
except ImportError:  # pragma: no cover
    _BACKEND_AVAILABLE = False
    logger.warning("deep-translator not installed — regional-language output will fall back to English.")

# Serialize translation API calls to avoid flooding Google's rate limit.
_translate_lock = threading.Lock()
_MAX_RETRIES = 3
_BASE_DELAY = 1.0  # seconds — doubles on each retry


@lru_cache(maxsize=1024)
def _cached_translate(text: str, target_lang: str) -> str:
    if not _BACKEND_AVAILABLE:
        return text

    for attempt in range(_MAX_RETRIES):
        try:
            with _translate_lock:
                result = GoogleTranslator(source="en", target=target_lang).translate(text)
            if result:
                return result
            return text
        except Exception as exc:
            is_rate_limit = "too many requests" in str(exc).lower() or "Server Error" in str(exc)
            if is_rate_limit and attempt < _MAX_RETRIES - 1:
                delay = _BASE_DELAY * (2 ** attempt)
                logger.info("Translation rate-limited, retrying in %.1fs (attempt %d/%d)...",
                            delay, attempt + 1, _MAX_RETRIES)
                time.sleep(delay)
                continue
            logger.warning("Translation failed (%s) — returning original text.", exc)
            return text

    return text


def translate_text(text: str, target_lang: str = "en") -> str:
    """
    Translate `text` (assumed English, since it is generated from our
    grounded English knowledge base) into `target_lang`.
    Returns the original text unchanged if target_lang is English/unsupported
    or the backend is unavailable.
    """
    if not text:
        return text
    if target_lang not in SUPPORTED_LANGUAGES or target_lang == "en":
        return text
    return _cached_translate(text, target_lang)


def translate_paragraph(text: str, target_lang: str = "en") -> str:
    """Translate an entire multi-line text block as one API call.

    This is more efficient than translating line-by-line because it uses
    a single Google Translate request for the whole paragraph, reducing
    the chance of hitting rate limits.
    """
    if not text or target_lang == "en" or target_lang not in SUPPORTED_LANGUAGES:
        return text
    return _cached_translate(text, target_lang)


def translate_bullets(bullets, target_lang: str = "en"):
    """Translate a list of short strings (e.g. precaution bullets).

    Joins all bullets into a single string separated by newlines,
    translates in one API call, then splits back — much fewer requests
    than translating each bullet individually.
    """
    if not bullets or target_lang == "en" or target_lang not in SUPPORTED_LANGUAGES:
        return bullets
    combined = "\n".join(bullets)
    translated = _cached_translate(combined, target_lang)
    result = translated.split("\n")
    # Ensure we return the same number of items; pad or trim if needed
    if len(result) < len(bullets):
        result.extend(bullets[len(result):])
    return result[:len(bullets)]
