"""Configuration management for the Autogen project."""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from pathlib import Path


class Config:
    """Configuration loader for environment variables and settings."""
    
    def __init__(self, env_file: Optional[str] = None) -> None:
        """Initialize configuration loader.
        
        Args:
            env_file: Path to .env file. If None, looks for .env in project root.
        """
        if env_file is None:
            # Look for .env in project root
            project_root = Path(__file__).parent.parent
            env_file = project_root / ".env"
        
        # For testing, we want to override existing environment variables
        load_dotenv(env_file, override=True)
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate required configuration values."""
        required_keys = ["OPENAI_API_KEY", "DEEPSEEK_API_KEY"]
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {missing_keys}")
    
    @property
    def openai_api_key(self) -> str:
        """OpenAI API key."""
        return os.getenv("OPENAI_API_KEY", "")
    
    @property
    def deepseek_api_key(self) -> str:
        """DeepSeek API key."""
        return os.getenv("DEEPSEEK_API_KEY", "")
    
    @property
    def default_provider(self) -> str:
        """Default LLM provider."""
        return os.getenv("DEFAULT_PROVIDER", "openai")
    
    @property
    def openai_model(self) -> str:
        """OpenAI model name."""
        return os.getenv("OPENAI_MODEL", "gpt-4")
    
    @property
    def deepseek_model(self) -> str:
        """DeepSeek model name."""
        return os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    @property
    def deepseek_api_base(self) -> str:
        """DeepSeek API base URL."""
        return os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    
    @property
    def log_dir(self) -> str:
        """Logging directory."""
        return os.getenv("LOG_DIR", "logs")
    
    @property
    def log_level(self) -> str:
        """Logging level."""
        return os.getenv("LOG_LEVEL", "INFO")
    
    @property
    def api_host(self) -> str:
        """API host."""
        return os.getenv("API_HOST", "localhost")
    
    @property
    def api_port(self) -> int:
        """API port."""
        return int(os.getenv("API_PORT", "8000"))
    
    @property
    def templates_dir(self) -> str:
        """Templates directory."""
        return os.getenv("TEMPLATES_DIR", "templates")
    
    @property
    def max_rounds(self) -> int:
        """Maximum conversation rounds."""
        return int(os.getenv("MAX_ROUNDS", "10"))
    
    def get_llm_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """Get LLM configuration for specified provider.
        
        Args:
            provider: LLM provider ('openai' or 'deepseek'). 
                     If None, uses default provider.
        
        Returns:
            Dictionary containing LLM configuration.
        """
        if provider is None:
            provider = self.default_provider
        
        if provider.lower() == "openai":
            return {
                "config_list": [
                    {
                        "model": self.openai_model,
                        "api_key": self.openai_api_key,
                    }
                ],
                "temperature": 0.7,
            }
        elif provider.lower() == "deepseek":
            return {
                "config_list": [
                    {
                        "model": self.deepseek_model,
                        "api_key": self.deepseek_api_key,
                        "base_url": self.deepseek_api_base,
                    }
                ],
                "temperature": 0.7,
            }
        else:
            raise ValueError(f"Unsupported provider: {provider}")


# Global configuration instance
config = Config()
