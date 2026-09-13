"""
utils/translation_utils.py

Lightweight regional-language translation for the Farmer Assistant (Bonus E).
Uses `deep-translator` (free, wraps Google Translate's public endpoint — no
API key needed) with an in-memory cache so the same sentence is never
translated twice in a session.

If the translation backend is unreachable (offline judging environment,
firewall, etc.) we fail SOFT: return the original English text rather than
crashing the request. This keeps the core/bonus modules demo-safe.
"""

from functools import lru_cache
import logging

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


@lru_cache(maxsize=1024)
def _cached_translate(text: str, target_lang: str) -> str:
    if not _BACKEND_AVAILABLE:
        return text
    try:
        return GoogleTranslator(source="en", target=target_lang).translate(text)
    except Exception as exc:  # network issues, rate limit, unsupported pair, etc.
        logger.warning("Translation failed (%s) — returning original text.", exc)
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


def translate_bullets(bullets, target_lang: str = "en"):
    """Translate a list of short strings (e.g. precaution bullets)."""
    return [translate_text(b, target_lang) for b in bullets]
