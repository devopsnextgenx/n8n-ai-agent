"""Configuration management for MCP Crypto Server.

This module handles loading and validating configuration from YAML files.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    """Server configuration model."""
    host: str = Field(default="0.0.0.0", description="Server host address")
    port: int = Field(default=6789, description="Server port number")
    mode: str = Field(default="auto", description="Server transport mode")


class LoggingConfig(BaseModel):
    """Logging configuration model."""
    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    file: str = Field(default="logs/mcp-server.log", description="Log file path")
    max_file_size: str = Field(default="10MB", description="Maximum log file size")
    backup_count: int = Field(default=5, description="Number of backup log files")


class Config(BaseModel):
    """Main configuration model."""
    server: ServerConfig = Field(default_factory=ServerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


class ConfigManager:
    """Configuration manager for loading and managing configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. Defaults to 'config.yml'
        """
        self.config_path = config_path or "config.yml"
        self._config: Optional[Config] = None
    
    def load_config(self) -> Config:
        """Load configuration from YAML file.
        
        Returns:
            Config: Loaded and validated configuration
            
        Raises:
            FileNotFoundError: If config file is not found
            yaml.YAMLError: If config file is invalid YAML
            ValueError: If config validation fails
        """
        if not os.path.exists(self.config_path):
            # Create default config if it doesn't exist
            default_config = Config()
            self._save_default_config(default_config)
            return default_config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if config_data is None:
                config_data = {}
            
            self._config = Config(**config_data)
            return self._config
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in config file {self.config_path}: {e}")
        except Exception as e:
            raise ValueError(f"Config validation failed: {e}")
    
    def _save_default_config(self, config: Config) -> None:
        """Save default configuration to file.
        
        Args:
            config: Configuration to save
        """
        # Ensure config directory exists
        config_dir = Path(self.config_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_dict = config.model_dump()
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    def get_config(self) -> Config:
        """Get current configuration.
        
        Returns:
            Config: Current configuration
        """
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def reload_config(self) -> Config:
        """Reload configuration from file.
        
        Returns:
            Config: Reloaded configuration
        """
        self._config = None
        return self.load_config()


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> Config:
    """Get global configuration instance.
    
    Returns:
        Config: Global configuration
    """
    return config_manager.get_config()


def reload_config() -> Config:
    """Reload global configuration.
    
    Returns:
        Config: Reloaded global configuration
    """
    return config_manager.reload_config()