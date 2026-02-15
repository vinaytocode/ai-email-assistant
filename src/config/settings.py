"""Application settings and configuration with MCP support."""

import os
import yaml
from typing import Optional, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with MCP configuration support."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    default_model: str = Field("gpt-4o-mini", env="DEFAULT_MODEL")
    default_temperature: float = Field(0.3, env="DEFAULT_TEMPERATURE")
    max_tokens: int = Field(1000, env="MAX_TOKENS")
    
    # Application Configuration
    app_title: str = Field("AI Email Assistant", env="APP_TITLE")
    app_port: int = Field(8501, env="APP_PORT")
    debug: bool = Field(False, env="DEBUG")
    
    # Context Management
    max_context_entries: int = Field(3, env="MAX_CONTEXT_ENTRIES")
    enable_context_memory: bool = Field(True, env="ENABLE_CONTEXT_MEMORY")
    
    # MCP Configuration
    mcp_config_path: str = Field("src/config/mcp.yaml", env="MCP_CONFIG_PATH")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mcp_config = self._load_mcp_config()
    
    def _load_mcp_config(self) -> Dict[str, Any]:
        """Load MCP configuration from YAML file."""
        try:
            config_path = Path(__file__).parent / 'mcp.yaml'
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        except Exception:
            pass
        return {}
    
    @property
    def mcp_config(self) -> Dict[str, Any]:
        """Get MCP configuration."""
        return self._mcp_config
    
    def get_agent_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for specific agent."""
        return self._mcp_config.get("agents", {}).get(agent_name)


# Global settings instance - lazy loaded
_settings = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# For backward compatibility
settings = property(lambda self: get_settings())
