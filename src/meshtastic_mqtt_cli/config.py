"""Configuration management module for Meshtastic MQTT CLI."""

import os
import yaml
from dataclasses import dataclass, field
from typing import Optional, Any


@dataclass
class MQTTConfig:
    """MQTT connection configuration."""
    server: str = ""
    port: int = 1883
    username: str = ""
    password: str = ""


@dataclass
class MeshtasticConfig:
    """Meshtastic-specific configuration."""
    from_id: str = ""
    to_id: str = "^all"
    channel: str = "LongFast"
    channel_number: int = 0
    region: str = "US"


@dataclass
class AppConfig:
    """Application configuration container."""
    mqtt: MQTTConfig = field(default_factory=MQTTConfig)
    meshtastic: MeshtasticConfig = field(default_factory=MeshtasticConfig)


class Config:
    """Configuration manager for the Meshtastic MQTT CLI tool."""
    
    def __init__(self):
        """Initialize an empty configuration."""
        self.config = AppConfig()

    
    def load_from_file(self, path: str) -> None:
        """
        Load configuration from a YAML file.
        
        Args:
            path: Path to the YAML configuration file
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            yaml.YAMLError: If the YAML file has syntax errors
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                
            if data is None:
                data = {}
                
            # Load MQTT configuration
            mqtt_data = data.get('mqtt', {})
            self.config.mqtt = MQTTConfig(
                server=mqtt_data.get('server', ''),
                port=mqtt_data.get('port', 1883),
                username=mqtt_data.get('username', ''),
                password=mqtt_data.get('password', '')
            )
            
            # Load Meshtastic configuration
            meshtastic_data = data.get('meshtastic', {})
            self.config.meshtastic = MeshtasticConfig(
                from_id=meshtastic_data.get('from_id', ''),
                to_id=meshtastic_data.get('to_id', '^all'),
                channel=meshtastic_data.get('channel', 'LongFast'),
                channel_number=meshtastic_data.get('channel_number', 0),
                region=meshtastic_data.get('region', 'US')
            )
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML syntax error in configuration file: {e}")

    
    @staticmethod
    def create_default_config(path: str) -> None:
        """
        Create a default configuration file with placeholder values.
        
        Args:
            path: Path where the configuration file should be created
        """
        # Create directory if it doesn't exist
        config_dir = os.path.dirname(path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir, mode=0o700)
        
        # Default configuration template
        default_config = {
            'mqtt': {
                'server': 'mqtt.meshtastic.org',
                'port': 1883,
                'username': 'meshdev',
                'password': 'large4cats'
            },
            'meshtastic': {
                'from_id': '!12345678',
                'to_id': '^all',
                'channel': 'LongFast',
                'channel_number': 0,
                'region': 'US'
            }
        }
        
        # Write configuration file
        with open(path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
        
        # Set file permissions to 0600 (owner read/write only) on Unix-like systems
        if os.name != 'nt':  # Not Windows
            os.chmod(path, 0o600)

    
    def merge_with_cli_args(self, args: Any) -> None:
        """
        Merge CLI arguments with configuration, giving CLI arguments priority.
        
        Args:
            args: Parsed command-line arguments (argparse.Namespace or dict-like object)
        """
        # Handle both argparse.Namespace and dict-like objects
        def get_arg(name: str, default=None):
            if hasattr(args, name):
                return getattr(args, name)
            elif isinstance(args, dict):
                return args.get(name, default)
            return default
        
        # Override MQTT configuration with CLI arguments
        if get_arg('server') is not None:
            self.config.mqtt.server = get_arg('server')
        if get_arg('port') is not None:
            self.config.mqtt.port = get_arg('port')
        if get_arg('username') is not None:
            self.config.mqtt.username = get_arg('username')
        if get_arg('password') is not None:
            self.config.mqtt.password = get_arg('password')
        
        # Override Meshtastic configuration with CLI arguments
        if get_arg('from_id') is not None:
            self.config.meshtastic.from_id = get_arg('from_id')
        if get_arg('to_id') is not None:
            self.config.meshtastic.to_id = get_arg('to_id')
        if get_arg('channel') is not None:
            self.config.meshtastic.channel = get_arg('channel')
        if get_arg('channel_number') is not None:
            self.config.meshtastic.channel_number = get_arg('channel_number')
        if get_arg('region') is not None:
            self.config.meshtastic.region = get_arg('region')
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate that required configuration fields are present.
        
        Returns:
            Tuple of (is_valid, list_of_missing_fields)
        """
        missing_fields = []
        
        # Check required MQTT fields
        if not self.config.mqtt.server:
            missing_fields.append('mqtt.server')
        if not self.config.mqtt.username:
            missing_fields.append('mqtt.username')
        if not self.config.mqtt.password:
            missing_fields.append('mqtt.password')
        
        return (len(missing_fields) == 0, missing_fields)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation (e.g., 'mqtt.server')
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        parts = key.split('.')
        value = self.config
        
        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            else:
                return default
        
        return value if value != '' else default
