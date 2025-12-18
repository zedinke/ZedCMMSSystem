"""
Localization Manager
Handles language selection and persistence
"""

from pathlib import Path
import json
from typing import Optional, Callable
from config.app_config import DEFAULT_LANGUAGE


class Translator:
    """Singleton translator for managing multilingual content"""
    
    _instance = None
    _translations = {}
    _current_language = DEFAULT_LANGUAGE
    _observers = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, translations_dir: Path):
        """Initialize translations from JSON files"""
        self._translations = {}
        
        # Load English
        en_file = translations_dir / "en.json"
        if en_file.exists():
            with open(en_file, 'r', encoding='utf-8') as f:
                self._translations['en'] = json.load(f)
        
        # Load Hungarian
        hu_file = translations_dir / "hu.json"
        if hu_file.exists():
            with open(hu_file, 'r', encoding='utf-8') as f:
                self._translations['hu'] = json.load(f)
    
    def get_text(self, key: str, lang_code: Optional[str] = None, **params) -> str:
        """
        Get translated text by key with optional parameters
        
        Args:
            key: Dot-notation key (e.g., "common.buttons.save")
            lang_code: Language code (en/hu), uses current if None
            **params: Format parameters for string interpolation
        
        Returns:
            Translated string or key if not found
        """
        if lang_code is None:
            lang_code = self._current_language
        
        # Navigate through nested dictionary
        translation_dict = self._translations.get(lang_code, {})
        keys = key.split('.')
        
        value = translation_dict
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, None)
            else:
                value = None
                break
        
        if value is None:
            # Fallback to English if not found
            if lang_code != 'en':
                return self.get_text(key, 'en', **params)
            return key
        
        # Format with parameters if provided
        if params and isinstance(value, str):
            try:
                return value.format(**params)
            except KeyError:
                return value
        
        return str(value) if value is not None else key
    
    def set_current_language(self, lang_code: str):
        """Set current language and notify observers"""
        if lang_code in self._translations:
            self._current_language = lang_code
            self._notify_observers()
    
    def get_current_language(self) -> str:
        """Get current language code"""
        return self._current_language
    
    def get_available_languages(self) -> list:
        """Get list of available language codes"""
        return list(self._translations.keys())
    
    def subscribe(self, observer: Callable):
        """Subscribe to language change events"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def unsubscribe(self, observer: Callable):
        """Unsubscribe from language change events"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_observers(self):
        """Notify all observers of language change"""
        for observer in self._observers:
            try:
                observer(self._current_language)
            except Exception as e:
                print(f"Error notifying observer: {e}")
    
    def validate_translations(self) -> dict:
        """
        Validate translation completeness
        Returns dict with validation results
        """
        results = {
            'valid': True,
            'missing_keys': {},
            'language_count': len(self._translations)
        }
        
        if not self._translations:
            results['valid'] = False
            results['error'] = "No translations loaded"
            return results
        
        # Get reference language keys
        reference_lang = 'en'
        if reference_lang not in self._translations:
            results['valid'] = False
            results['error'] = f"Reference language '{reference_lang}' not found"
            return results
        
        reference_keys = self._get_all_keys(self._translations[reference_lang])
        
        # Check other languages
        for lang in self._translations:
            if lang == reference_lang:
                continue
            
            lang_keys = self._get_all_keys(self._translations[lang])
            missing = set(reference_keys) - set(lang_keys)
            
            if missing:
                results['valid'] = False
                results['missing_keys'][lang] = list(missing)
        
        return results
    
    @staticmethod
    def _get_all_keys(d: dict, prefix: str = '') -> set:
        """Recursively get all dot-notation keys from nested dict"""
        keys = set()
        for k, v in d.items():
            full_key = f"{prefix}.{k}" if prefix else k
            keys.add(full_key)
            if isinstance(v, dict):
                keys.update(Translator._get_all_keys(v, full_key))
        return keys


# Create singleton instance
translator = Translator()
