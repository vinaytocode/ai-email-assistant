"""Memory and profile management module."""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ProfileManager:
    """Manages user profiles from JSON configuration."""
    
    def __init__(self):
        self.profiles_path = Path(__file__).parent / "user_profiles.json"
        self.profiles = self._load_profiles()
    
    def _load_profiles(self) -> Dict[str, Any]:
        """Load user profiles from JSON file."""
        try:
            with open(self.profiles_path, 'r') as f:
                profiles = json.load(f)
            logger.info(f"Loaded {len(profiles)} user profiles")
            return profiles
        except Exception as e:
            logger.error(f"Error loading profiles: {str(e)}")
            return {}
    
    def get_profile(self, user_type: str) -> Optional[Dict[str, Any]]:
        """Get profile for specific user type."""
        return self.profiles.get(user_type)
    
    def list_profiles(self) -> list:
        """List all available profile types."""
        return list(self.profiles.keys())


__all__ = ["ProfileManager"]
