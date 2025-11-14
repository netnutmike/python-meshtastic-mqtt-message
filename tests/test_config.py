"""Unit tests for the configuration module."""

import os
import tempfile
import unittest
import yaml
from pathlib import Path

from src.meshtastic_mqtt_cli.config import Config, MQTTConfig, MeshtasticConfig, AppConfig


class TestConfigDataModels(unittest.TestCase):
    """Test configuration data models."""
    
    def test_mqtt_config_defaults(self):
        """Test MQTTConfig default values."""
        mqtt = MQTTConfig()
        self.assertEqual(mqtt.server, "")
        self.assertEqual(mqtt.port, 1883)
        self.assertEqual(mqtt.username, "")
        self.assertEqual(mqtt.password, "")
    
    def test_meshtastic_config_defaults(self):
        """Test MeshtasticConfig default values."""
        mesh = MeshtasticConfig()
        self.assertEqual(mesh.from_id, "")
        self.assertEqual(mesh.to_id, "^all")
        self.assertEqual(mesh.channel, "LongFast")
        self.assertEqual(mesh.region, "US")
    
    def test_app_config_initialization(self):
        """Test AppConfig initialization."""
        app = AppConfig()
        self.assertIsInstance(app.mqtt, MQTTConfig)
        self.assertIsInstance(app.meshtastic, MeshtasticConfig)


class TestConfigClass(unittest.TestCase):
    """Test Config class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_config_initialization(self):
        """Test Config class initialization."""
        config = Config()
        self.assertIsInstance(config.config, AppConfig)
    
    def test_load_valid_yaml(self):
        """Test loading a valid YAML configuration file."""
        config_path = os.path.join(self.temp_dir, 'config.yaml')
        config_data = {
            'mqtt': {
                'server': 'test.mqtt.org',
                'port': 8883,
                'username': 'testuser',
                'password': 'testpass'
            },
            'meshtastic': {
                'from_id': '!87654321',
                'to_id': '!12345678',
                'channel': 'TestChannel',
                'region': 'EU'
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        self.config.load_from_file(config_path)
        
        self.assertEqual(self.config.config.mqtt.server, 'test.mqtt.org')
        self.assertEqual(self.config.config.mqtt.port, 8883)
        self.assertEqual(self.config.config.mqtt.username, 'testuser')
        self.assertEqual(self.config.config.mqtt.password, 'testpass')
        self.assertEqual(self.config.config.meshtastic.from_id, '!87654321')
        self.assertEqual(self.config.config.meshtastic.to_id, '!12345678')
        self.assertEqual(self.config.config.meshtastic.channel, 'TestChannel')
        self.assertEqual(self.config.config.meshtastic.region, 'EU')
    
    def test_load_missing_file(self):
        """Test handling of missing configuration file."""
        config_path = os.path.join(self.temp_dir, 'nonexistent.yaml')
        
        with self.assertRaises(FileNotFoundError) as context:
            self.config.load_from_file(config_path)
        
        self.assertIn('Configuration file not found', str(context.exception))
    
    def test_load_invalid_yaml(self):
        """Test handling of YAML syntax errors."""
        config_path = os.path.join(self.temp_dir, 'invalid.yaml')
        
        with open(config_path, 'w') as f:
            f.write("invalid: yaml: syntax: error:\n  - broken")
        
        with self.assertRaises(yaml.YAMLError):
            self.config.load_from_file(config_path)
    
    def test_create_default_config(self):
        """Test creation of default configuration file."""
        config_path = os.path.join(self.temp_dir, 'subdir', 'config.yaml')
        
        Config.create_default_config(config_path)
        
        self.assertTrue(os.path.exists(config_path))
        
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        self.assertIn('mqtt', data)
        self.assertIn('meshtastic', data)
        self.assertEqual(data['mqtt']['server'], 'mqtt.meshtastic.org')
        self.assertEqual(data['mqtt']['port'], 1883)
        
        # Check file permissions on Unix-like systems
        if os.name != 'nt':
            stat_info = os.stat(config_path)
            permissions = oct(stat_info.st_mode)[-3:]
            self.assertEqual(permissions, '600')
    
    def test_merge_with_cli_args_namespace(self):
        """Test merging CLI arguments with configuration."""
        # Load initial config
        config_path = os.path.join(self.temp_dir, 'config.yaml')
        config_data = {
            'mqtt': {
                'server': 'original.mqtt.org',
                'port': 1883,
                'username': 'original_user',
                'password': 'original_pass'
            },
            'meshtastic': {
                'from_id': '!11111111',
                'to_id': '^all',
                'channel': 'OriginalChannel',
                'region': 'US'
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        self.config.load_from_file(config_path)
        
        # Create mock CLI args
        class Args:
            server = 'override.mqtt.org'
            port = 8883
            username = None
            password = 'new_pass'
            from_id = '!99999999'
            to_id = None
            channel = 'NewChannel'
            region = None
        
        self.config.merge_with_cli_args(Args())
        
        # Check overridden values
        self.assertEqual(self.config.config.mqtt.server, 'override.mqtt.org')
        self.assertEqual(self.config.config.mqtt.port, 8883)
        self.assertEqual(self.config.config.mqtt.password, 'new_pass')
        self.assertEqual(self.config.config.meshtastic.from_id, '!99999999')
        self.assertEqual(self.config.config.meshtastic.channel, 'NewChannel')
        
        # Check non-overridden values remain
        self.assertEqual(self.config.config.mqtt.username, 'original_user')
        self.assertEqual(self.config.config.meshtastic.to_id, '^all')
        self.assertEqual(self.config.config.meshtastic.region, 'US')
    
    def test_validate_complete_config(self):
        """Test validation of complete configuration."""
        self.config.config.mqtt.server = 'test.mqtt.org'
        self.config.config.mqtt.username = 'testuser'
        self.config.config.mqtt.password = 'testpass'
        
        is_valid, missing = self.config.validate()
        
        self.assertTrue(is_valid)
        self.assertEqual(len(missing), 0)
    
    def test_validate_missing_fields(self):
        """Test validation with missing required fields."""
        # Leave all fields empty
        is_valid, missing = self.config.validate()
        
        self.assertFalse(is_valid)
        self.assertIn('mqtt.server', missing)
        self.assertIn('mqtt.username', missing)
        self.assertIn('mqtt.password', missing)
    
    def test_get_method(self):
        """Test retrieving configuration values."""
        self.config.config.mqtt.server = 'test.mqtt.org'
        self.config.config.mqtt.port = 8883
        self.config.config.meshtastic.channel = 'TestChannel'
        
        self.assertEqual(self.config.get('mqtt.server'), 'test.mqtt.org')
        self.assertEqual(self.config.get('mqtt.port'), 8883)
        self.assertEqual(self.config.get('meshtastic.channel'), 'TestChannel')
        self.assertEqual(self.config.get('nonexistent.key', 'default'), 'default')


if __name__ == '__main__':
    unittest.main()
