"""Base agent implementation for the Autogen project."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from jinja2 import Template
import openai
import pandas as pd
import PyPDF2
from docx import Document
import io
import os

from core import config, agent_logger


class FileProcessor:
    """Utility class for processing various file formats."""
    
    @staticmethod
    def read_pdf(file_path: str) -> str:
        """Read text content from a PDF file.
        
        Args:
            file_path: Path to the PDF file.
            
        Returns:
            Extracted text content.
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise ValueError(f"Error reading PDF file {file_path}: {str(e)}")
    
    @staticmethod
    def read_csv(file_path: str, **kwargs) -> pd.DataFrame:
        """Read data from a CSV file.
        
        Args:
            file_path: Path to the CSV file.
            **kwargs: Additional parameters for pandas.read_csv().
            
        Returns:
            DataFrame containing the CSV data.
        """
        try:
            return pd.read_csv(file_path, **kwargs)
        except Exception as e:
            raise ValueError(f"Error reading CSV file {file_path}: {str(e)}")
    
    @staticmethod
    def read_excel(file_path: str, sheet_name: Optional[str] = 0, **kwargs) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """Read data from an Excel file.
        
        Args:
            file_path: Path to the Excel file.
            sheet_name: Specific sheet name or index, or None for all sheets (default: 0 for first sheet).
            **kwargs: Additional parameters for pandas.read_excel().
            
        Returns:
            DataFrame or dictionary of DataFrames.
        """
        try:
            return pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
        except Exception as e:
            raise ValueError(f"Error reading Excel file {file_path}: {str(e)}")
    
    @staticmethod
    def read_docx(file_path: str) -> str:
        """Read text content from a Word document.
        
        Args:
            file_path: Path to the Word document.
            
        Returns:
            Extracted text content.
        """
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error reading Word document {file_path}: {str(e)}")
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """Get information about a file.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Dictionary containing file information.
        """
        try:
            path = Path(file_path)
            stat = path.stat()
            return {
                "name": path.name,
                "size": stat.st_size,
                "extension": path.suffix.lower(),
                "modified": stat.st_mtime,
                "exists": path.exists()
            }
        except Exception as e:
            return {"error": str(e), "exists": False}
    
    @staticmethod
    def process_file(file_path: str, **kwargs) -> Dict[str, Any]:
        """Process a file based on its extension.
        
        Args:
            file_path: Path to the file.
            **kwargs: Additional parameters for specific file readers.
            
        Returns:
            Dictionary containing processed file data and metadata.
        """
        file_info = FileProcessor.get_file_info(file_path)
        
        if not file_info.get("exists", False):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = file_info["extension"]
        result = {"file_info": file_info, "content": None, "data": None}
        
        try:
            if extension == ".pdf":
                result["content"] = FileProcessor.read_pdf(file_path)
                result["type"] = "text"
            elif extension == ".csv":
                result["data"] = FileProcessor.read_csv(file_path, **kwargs)
                result["type"] = "dataframe"
            elif extension in [".xlsx", ".xls"]:
                result["data"] = FileProcessor.read_excel(file_path, **kwargs)
                result["type"] = "dataframe"
            elif extension == ".docx":
                result["content"] = FileProcessor.read_docx(file_path)
                result["type"] = "text"
            else:
                # Try to read as text file
                with open(file_path, 'r', encoding='utf-8') as f:
                    result["content"] = f.read()
                result["type"] = "text"
                
        except Exception as e:
            result["error"] = str(e)
            result["type"] = "error"
        
        return result


class ModelConfig:
    """Configuration for LLM models."""
    
    def __init__(
        self,
        model_name: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0
    ):
        """Initialize model configuration.
        
        Args:
            model_name: Name of the model to use.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0.0 to 2.0).
            top_p: Nucleus sampling parameter (0.0 to 1.0).
            frequency_penalty: Frequency penalty (-2.0 to 2.0).
            presence_penalty: Presence penalty (-2.0 to 2.0).
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        return {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty
        }


class ProviderConfig:
    """Configuration for LLM providers."""
    
    # Predefined model configurations for different providers
    PROVIDER_MODELS = {
        "openai": {
            "gpt-4": ModelConfig("gpt-4", max_tokens=2000, temperature=0.7),
            "gpt-4-turbo": ModelConfig("gpt-4-turbo", max_tokens=4000, temperature=0.7),
            "gpt-3.5-turbo": ModelConfig("gpt-3.5-turbo", max_tokens=1500, temperature=0.7),
            "gpt-4o": ModelConfig("gpt-4o", max_tokens=4000, temperature=0.7),
            "gpt-4o-mini": ModelConfig("gpt-4o-mini", max_tokens=2000, temperature=0.7)
        },
        "deepseek": {
            "deepseek-chat": ModelConfig("deepseek-chat", max_tokens=2000, temperature=0.7),
            "deepseek-coder": ModelConfig("deepseek-coder", max_tokens=2000, temperature=0.3),
            "deepseek-math": ModelConfig("deepseek-math", max_tokens=1500, temperature=0.5)
        },
        "anthropic": {
            "claude-3-opus": ModelConfig("claude-3-opus-20240229", max_tokens=2000, temperature=0.7),
            "claude-3-sonnet": ModelConfig("claude-3-sonnet-20240229", max_tokens=2000, temperature=0.7),
            "claude-3-haiku": ModelConfig("claude-3-haiku-20240307", max_tokens=1500, temperature=0.7)
        }
    }
    
    @classmethod
    def get_model_config(cls, provider: str, model_name: str) -> ModelConfig:
        """Get model configuration for a provider and model.
        
        Args:
            provider: Provider name (e.g., 'openai', 'deepseek', 'anthropic').
            model_name: Model name.
            
        Returns:
            ModelConfig instance.
            
        Raises:
            ValueError: If provider or model is not supported.
        """
        provider = provider.lower()
        if provider not in cls.PROVIDER_MODELS:
            raise ValueError(f"Unsupported provider: {provider}")
        
        if model_name not in cls.PROVIDER_MODELS[provider]:
            raise ValueError(f"Unsupported model '{model_name}' for provider '{provider}'")
        
        return cls.PROVIDER_MODELS[provider][model_name]
    
    @classmethod
    def list_models(cls, provider: Optional[str] = None) -> Dict[str, list]:
        """List available models for providers.
        
        Args:
            provider: Specific provider to list models for, or None for all.
            
        Returns:
            Dictionary mapping providers to their available models.
        """
        if provider:
            provider = provider.lower()
            if provider in cls.PROVIDER_MODELS:
                return {provider: list(cls.PROVIDER_MODELS[provider].keys())}
            else:
                return {}
        
        return {p: list(models.keys()) for p, models in cls.PROVIDER_MODELS.items()}


class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(
        self, 
        name: str, 
        template_name: str,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        model_config: Optional[ModelConfig] = None,
        system_message: Optional[str] = None,
        custom_client_params: Optional[Dict[str, Any]] = None,
        data_dir: Optional[str] = None
    ) -> None:
        """Initialize the base agent.
        
        Args:
            name: Agent name.
            template_name: Name of the prompt template file.
            provider: LLM provider ('openai', 'deepseek', 'anthropic').
            model_name: Specific model to use (overrides config defaults).
            model_config: Custom model configuration (overrides defaults).
            system_message: System message for the agent.
            custom_client_params: Additional parameters for the client.
            data_dir: Directory path for data files (defaults to 'data' in project root).
        """
        self.name = name
        self.template_name = template_name
        self.provider = provider or config.default_provider
        self.custom_client_params = custom_client_params or {}
        self.data_dir = Path(data_dir) if data_dir else Path("data")
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
        # Set up model configuration
        if model_config:
            self.model_config = model_config
        elif model_name:
            self.model_config = ProviderConfig.get_model_config(self.provider, model_name)
        else:
            # Use default model from config
            default_model = self._get_default_model_name()
            self.model_config = ProviderConfig.get_model_config(self.provider, default_model)
        
        self.system_message = system_message or f"You are {name}, a helpful AI assistant."
        
        # Load prompt template
        self.template = self._load_template()
        
        # Initialize client
        self.client = self._create_client()
        
        agent_logger.info(
            f"Initialized agent '{self.name}' with provider '{self.provider}' "
            f"and model '{self.model_config.model_name}'"
        )
    
    def _get_default_model_name(self) -> str:
        """Get the default model name for the current provider."""
        if self.provider.lower() == "openai":
            return config.openai_model
        elif self.provider.lower() == "deepseek":
            return config.deepseek_model
        else:
            # For other providers, use a sensible default
            provider_models = ProviderConfig.PROVIDER_MODELS.get(self.provider.lower(), {})
            if provider_models:
                return list(provider_models.keys())[0]
            else:
                raise ValueError(f"No default model available for provider: {self.provider}")
    
    def _load_template(self) -> Template:
        """Load prompt template from file."""
        template_path = Path(config.templates_dir) / self.template_name
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        return Template(template_content)
    
    def _create_client(self) -> Union[openai.OpenAI, Any]:
        """Create the appropriate client based on provider."""
        base_params = self.custom_client_params.copy()
        
        if self.provider.lower() == "openai":
            base_params.setdefault("api_key", config.openai_api_key)
            return openai.OpenAI(**base_params)
        elif self.provider.lower() == "deepseek":
            base_params.setdefault("api_key", config.deepseek_api_key)
            base_params.setdefault("base_url", config.deepseek_api_base)
            return openai.OpenAI(**base_params)
        elif self.provider.lower() == "anthropic":
            # Note: This would require anthropic client, but using OpenAI-compatible interface for now
            base_params.setdefault("api_key", config.get("anthropic_api_key", ""))
            base_params.setdefault("base_url", config.get("anthropic_api_base", ""))
            return openai.OpenAI(**base_params)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def update_model_config(self, **kwargs: Any) -> None:
        """Update model configuration parameters.
        
        Args:
            **kwargs: Model configuration parameters to update.
        """
        for key, value in kwargs.items():
            if hasattr(self.model_config, key):
                setattr(self.model_config, key, value)
            else:
                raise ValueError(f"Invalid model configuration parameter: {key}")
        
        agent_logger.info(f"Updated model config for agent '{self.name}': {kwargs}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get current model information.
        
        Returns:
            Dictionary containing model and provider information.
        """
        return {
            "agent_name": self.name,
            "provider": self.provider,
            "model_name": self.model_config.model_name,
            "model_config": self.model_config.to_dict(),
            "system_message": self.system_message
        }
    
    def render_prompt(self, **kwargs: Any) -> str:
        """Render the prompt template with provided variables.
        
        Args:
            **kwargs: Variables to substitute in the template.
            
        Returns:
            Rendered prompt string.
        """
        return self.template.render(**kwargs)
    
    def load_data_file(self, filename: str, **kwargs) -> Dict[str, Any]:
        """Load a data file from the data directory.
        
        Args:
            filename: Name of the file to load.
            **kwargs: Additional parameters for file processing.
            
        Returns:
            Dictionary containing file data and metadata.
        """
        file_path = self.data_dir / filename
        return FileProcessor.process_file(str(file_path), **kwargs)
    
    def list_data_files(self, pattern: str = "*") -> List[Dict[str, Any]]:
        """List available data files in the data directory.
        
        Args:
            pattern: File pattern to match (e.g., "*.csv", "*.pdf").
            
        Returns:
            List of file information dictionaries.
        """
        files = []
        for file_path in self.data_dir.glob(pattern):
            if file_path.is_file():
                files.append(FileProcessor.get_file_info(str(file_path)))
        return files
    
    def process_multiple_files(self, filenames: List[str], **kwargs) -> Dict[str, Any]:
        """Process multiple data files.
        
        Args:
            filenames: List of filenames to process.
            **kwargs: Additional parameters for file processing.
            
        Returns:
            Dictionary mapping filenames to their processed data.
        """
        results = {}
        for filename in filenames:
            try:
                results[filename] = self.load_data_file(filename, **kwargs)
            except Exception as e:
                results[filename] = {"error": str(e), "type": "error"}
        return results
    
    def get_data_summary(self, filename: str) -> str:
        """Get a text summary of a data file suitable for LLM processing.
        
        Args:
            filename: Name of the file to summarize.
            
        Returns:
            Text summary of the file contents.
        """
        try:
            file_data = self.load_data_file(filename)
            
            if file_data.get("type") == "error":
                return f"Error processing file {filename}: {file_data.get('error', 'Unknown error')}"
            
            summary = f"File: {filename}\n"
            summary += f"Size: {file_data['file_info']['size']} bytes\n"
            summary += f"Type: {file_data['file_info']['extension']}\n\n"
            
            if file_data.get("type") == "text":
                content = file_data.get("content", "")
                if len(content) > 2000:
                    summary += f"Content preview (first 2000 chars):\n{content[:2000]}...\n"
                else:
                    summary += f"Content:\n{content}\n"
            
            elif file_data.get("type") == "dataframe":
                df = file_data.get("data")
                
                # Handle case where Excel file returns dict of DataFrames (multiple sheets)
                if isinstance(df, dict):
                    summary += "Excel file with multiple sheets:\n"
                    for sheet_name, sheet_df in df.items():
                        summary += f"\nSheet '{sheet_name}':\n"
                        summary += f"  Shape: {sheet_df.shape[0]} rows × {sheet_df.shape[1]} columns\n"
                        summary += f"  Columns: {', '.join(sheet_df.columns.tolist())}\n"
                        summary += f"  First 3 rows:\n{sheet_df.head(3).to_string()}\n"
                elif hasattr(df, 'shape'):  # Single DataFrame
                    summary += f"Data shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
                    summary += f"Columns: {', '.join(df.columns.tolist())}\n"
                    summary += f"Data types:\n{df.dtypes.to_string()}\n\n"
                    summary += f"First 5 rows:\n{df.head().to_string()}\n"
                    if df.shape[0] > 5:
                        summary += f"\nStatistical summary:\n{df.describe().to_string()}\n"
                else:
                    summary += f"Data type: {type(df)}\n"
                    summary += f"Data preview: {str(df)[:500]}\n"
            
            return summary
            
        except Exception as e:
            return f"Error getting summary for {filename}: {str(e)}"
    
    @abstractmethod
    def prepare_task(self, task_data: Dict[str, Any]) -> str:
        """Prepare the task prompt from input data.
        
        Args:
            task_data: Input data for the task.
            
        Returns:
            Prepared prompt string.
        """
        pass
    
    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent task.
        
        Args:
            task_data: Input data for the task.
            
        Returns:
            Dictionary containing execution results.
        """
        agent_logger.log_agent_start(self.name, str(task_data))
        
        try:
            # Prepare the task prompt
            prompt = self.prepare_task(task_data)
            
            # Create messages
            messages = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt}
            ]
            
            # Prepare API call parameters
            api_params = self.model_config.to_dict()
            api_params["messages"] = messages
            
            # Call the LLM
            response = self.client.chat.completions.create(**api_params)
            
            result = {
                "success": True,
                "response": response.choices[0].message.content,
                "agent_name": self.name,
                "provider": self.provider,
                "model_name": self.model_config.model_name,
                "usage": getattr(response, 'usage', None)
            }
            
            agent_logger.log_agent_end(self.name, str(task_data), True)
            return result
            
        except Exception as e:
            agent_logger.error(f"Agent '{self.name}' execution failed", {"error": str(e)})
            agent_logger.log_agent_end(self.name, str(task_data), False)
            
            return {
                "success": False,
                "error": str(e),
                "agent_name": self.name,
                "provider": self.provider,
                "model_name": getattr(self.model_config, 'model_name', 'unknown')
            }
