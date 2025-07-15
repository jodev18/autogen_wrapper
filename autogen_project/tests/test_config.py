"""Test configuration module."""

import pytest
import os
from pathlib import Path
from core.config import Config


class TestConfig:
    """Test configuration loading and validation."""
    
    def test_config_initialization(self, tmp_path):
        """Test configuration initialization with custom env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("""
OPENAI_API_KEY=test_openai_key
DEEPSEEK_API_KEY=test_deepseek_key
DEFAULT_PROVIDER=openai
LOG_LEVEL=DEBUG
""")
        
        config = Config(str(env_file))
        assert config.openai_api_key == "test_openai_key"
        assert config.deepseek_api_key == "test_deepseek_key"
        assert config.default_provider == "openai"
        assert config.log_level == "DEBUG"
    
    def test_missing_required_keys(self, tmp_path):
        """Test validation with missing required keys."""
        # Clear environment variables to ensure clean state
        old_openai_key = os.environ.pop("OPENAI_API_KEY", None)
        old_deepseek_key = os.environ.pop("DEEPSEEK_API_KEY", None)
        
        try:
            env_file = tmp_path / ".env"
            env_file.write_text("SOME_OTHER_KEY=value")
            
            with pytest.raises(ValueError, match="Missing required environment variables"):
                Config(str(env_file))
        finally:
            # Restore environment variables
            if old_openai_key:
                os.environ["OPENAI_API_KEY"] = old_openai_key
            if old_deepseek_key:
                os.environ["DEEPSEEK_API_KEY"] = old_deepseek_key
    
    def test_llm_config_openai(self, tmp_path):
        """Test OpenAI LLM configuration."""
        env_file = tmp_path / ".env"
        env_file.write_text("""
OPENAI_API_KEY=test_openai_key
DEEPSEEK_API_KEY=test_deepseek_key
OPENAI_MODEL=gpt-3.5-turbo
""")
        
        config = Config(str(env_file))
        llm_config = config.get_llm_config("openai")
        
        assert "config_list" in llm_config
        assert llm_config["config_list"][0]["model"] == "gpt-3.5-turbo"
        assert llm_config["config_list"][0]["api_key"] == "test_openai_key"
    
    def test_llm_config_deepseek(self, tmp_path):
        """Test DeepSeek LLM configuration."""
        env_file = tmp_path / ".env"
        env_file.write_text("""
OPENAI_API_KEY=test_openai_key
DEEPSEEK_API_KEY=test_deepseek_key
DEEPSEEK_MODEL=deepseek-coder
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
""")
        
        config = Config(str(env_file))
        llm_config = config.get_llm_config("deepseek")
        
        assert "config_list" in llm_config
        assert llm_config["config_list"][0]["model"] == "deepseek-coder"
        assert llm_config["config_list"][0]["api_key"] == "test_deepseek_key"
        assert llm_config["config_list"][0]["base_url"] == "https://api.deepseek.com/v1"
    
    def test_invalid_provider(self, tmp_path):
        """Test invalid provider raises error."""
        env_file = tmp_path / ".env"
        env_file.write_text("""
OPENAI_API_KEY=test_openai_key
DEEPSEEK_API_KEY=test_deepseek_key
""")
        
        config = Config(str(env_file))
        
        with pytest.raises(ValueError, match="Unsupported provider"):
            config.get_llm_config("invalid_provider")
