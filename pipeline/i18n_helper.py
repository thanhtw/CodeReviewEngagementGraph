#!/usr/bin/env python3
"""
Internationalization (i18n) module for the Pipeline Server.
Uses python-i18n package to provide multi-language support.
"""

import i18n
import json
from pathlib import Path

# Configuration
TRANSLATIONS_DIR = Path(__file__).parent / "translations"

def setup_i18n(default_locale: str = 'en'):
    """Initialize i18n with translation files."""
    i18n.set('load_path', [str(TRANSLATIONS_DIR)])
    i18n.set('fallback', 'en')
    i18n.set('locale', default_locale)
    i18n.set('file_format', 'json')
    i18n.set('enable_memoization', True)


def get_translation(key: str, locale: str = None, **kwargs) -> str:
    """Get translated string for a key.
    
    Args:
        key: Translation key (e.g., 'app.title', 'nav.home')
        locale: Language code (e.g., 'en', 'zh-TW')
        **kwargs: Interpolation variables
        
    Returns:
        Translated string
    """
    if locale:
        return i18n.t(key, locale=locale, **kwargs)
    return i18n.t(key, **kwargs)


def get_all_translations(locale: str = 'en') -> dict:
    """Load all translations for a specific locale.
    
    Args:
        locale: Language code
        
    Returns:
        Dictionary with all translations
    """
    translation_file = TRANSLATIONS_DIR / f"{locale}.json"
    if translation_file.exists():
        with open(translation_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get(locale, {})
    return {}


def get_available_locales() -> list:
    """Get list of available language codes."""
    locales = []
    for file in TRANSLATIONS_DIR.glob('*.json'):
        locales.append(file.stem)
    return sorted(locales)


def set_locale(locale: str):
    """Set the current locale."""
    i18n.set('locale', locale)


def get_current_locale() -> str:
    """Get the current locale."""
    return i18n.get('locale')


# Initialize on import
setup_i18n()


# Convenience function for templates
def t(key: str, locale: str = None, **kwargs) -> str:
    """Shorthand for get_translation."""
    return get_translation(key, locale, **kwargs)
