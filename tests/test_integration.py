"""Integration tests for Meshtastic MQTT CLI."""

import os
import sys
import tempfile
import unittest
import yaml
from unittest.mock import patch, MagicMock
from io import StringIO

from src.meshtastic_mqtt_cli.cli import main, parse_arguments, validate_inputs
from src.meshtastic_mqtt_cli.config import Config


class TestEndToEndFlow(unittest.TestCase):
    """Test complete end-to-end flow scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'config.yaml')
        
        # Create a valid test configuration
        self.test_config = {
            'mqtt': {
                'server': 'test.mqtt.org',
                'port': 1883,
                'username': 'testuser',
                'password': 'testpass'
            },
            'meshtastic': {
                'from_id': '!12345678',
                'to_id': '^all',
                'channel': 'LongFast',
                'region': 'US'
            }
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(self.test_config, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('src.meshtastic_mqtt_cli.cli.MeshtasticMQTTClient')
    @patch('sys.argv', ['meshtastic-send', '--message', 'Test message', '--config'])
    def test_config_file_only(self, mock_client_class):
        """Test sending message using config file only."""
        # Append config path to sys.argv
        sys.argv.append(self.config_path)
        
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Run main
        with self.assertRaises(SystemExit) as cm:
            main()
        
        # Should exit with code 0 (success)
        self.assertEqual(cm.exception.code, 0)
        
        # Verify client was created with config values
        mock_client_class.assert_called_once_with(
            server='test.mqtt.org',
            port=1883,
            username='testuser',
            password='testpass'
        )
        
        # Verify connect, publish, and disconnect were called
        mock_client.connect.assert_called_once()
        mock_client.publish.assert_called_once()
        mock_client.disconnect.assert_called_once()

    @patch('src.meshtastic_mqtt_cli.cli.MeshtasticMQTTClient')
    @patch('sys.argv', ['meshtastic-send', '--message', 'Override test', 
                        '--server', 'override.mqtt.org', '--port', '8883',
                        '--username', 'override_user', '--from-id', '!99999999',
                        '--config'])
    def test_cli_overrides(self, mock_client_class):
        """Test CLI arguments overriding config file values."""
        # Append config path to sys.argv
        sys.argv.append(self.config_path)
        
        # Mock MQTT client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Run main
        with self.assertRaises(SystemExit) as cm:
            main()
        
        # Should exit with code 0 (success)
        self.assertEqual(cm.exception.code, 0)
        
        # Verify client was created with overridden values
        mock_client_class.assert_called_once_with(
            server='override.mqtt.org',
            port=8883,
            username='override_user',
            password='testpass'  # From config file
        )
        
        # Verify the message was published with overridden from_id
        call_args = mock_client.publish.call_args
        topic = call_args[0][0]
        self.assertIn('!99999999', topic)
    
    @patch('sys.argv', ['meshtastic-send', '--message', 'Test', '--config'])
    def test_missing_configuration(self, ):
        """Test error handling when required configuration is missing."""
        # Create config with missing required fields
        incomplete_config = {
            'mqtt': {
                'server': '',  # Missing
                'port': 1883,
                'username': '',  # Missing
                'password': ''  # Missing
            },
            'meshtastic': {
                'from_id': '',  # Missing
                'to_id': '^all',
                'channel': 'LongFast',
                'region': 'US'
            }
        }
        
        incomplete_path = os.path.join(self.temp_dir, 'incomplete.yaml')
        with open(incomplete_path, 'w') as f:
            yaml.dump(incomplete_config, f)
        
        sys.argv.append(incomplete_path)
        
        # Should exit with error code 3 (validation error)
        with self.assertRaises(SystemExit) as cm:
            main()
        
        self.assertEqual(cm.exception.code, 3)
    
    @patch('sys.argv', ['meshtastic-send', '--message', '', '--config'])
    def test_empty_message_error(self, ):
        """Test error handling for empty message."""
        sys.argv.append(self.config_path)
        
        # Should exit with error code 3 (validation error)
        with self.assertRaises(SystemExit) as cm:
            main()
        
        self.assertEqual(cm.exception.code, 3)
    
    @patch('src.meshtastic_mqtt_cli.cli.MeshtasticMQTTClient')
    @patch('sys.argv', ['meshtastic-send', '--message', 'Test', '--config'])
    def test_connection_error_scenario(self, mock_client_class):
        """Test error handling when MQTT connection fails."""
        sys.argv.append(self.config_path)
        
        # Mock MQTT client to raise connection error
        mock_client = MagicMock()
        mock_client.connect.side_effect = ConnectionError("Connection refused")
        mock_client_class.return_value = mock_client
        
        # Should exit with error code 2 (connection error)
        with self.assertRaises(SystemExit) as cm:
            main()
        
        self.assertEqual(cm.exception.code, 2)
    
    @patch('src.meshtastic_mqtt_cli.cli.MeshtasticMQTTClient')
    @patch('sys.argv', ['meshtastic-send', '--message', 'Test', '--config'])
    def test_publish_error_scenario(self, mock_client_class):
        """Test error handling when message publish fails."""
        sys.argv.append(self.config_path)
        
        # Mock MQTT client to raise publish error
        mock_client = MagicMock()
        mock_client.publish.side_effect = Exception("Publish failed")
        mock_client_class.return_value = mock_client
        
        # Should exit with error code 2 (publish error)
        with self.assertRaises(SystemExit) as cm:
            main()
        
        self.assertEqual(cm.exception.code, 2)
        
        # Verify disconnect was still called
        mock_client.disconnect.assert_called_once()
    
    @patch('sys.argv', ['meshtastic-send', '--message', 'Test', '--config'])
    def test_config_file_not_found_creates_default(self, ):
        """Test that missing config file triggers default config creation."""
        nonexistent_path = os.path.join(self.temp_dir, 'new_config.yaml')
        sys.argv.append(nonexistent_path)
        
        # Should exit with code 0 after creating default config
        with self.assertRaises(SystemExit) as cm:
            main()
        
        self.assertEqual(cm.exception.code, 0)
        
        # Verify default config was created
        self.assertTrue(os.path.exists(nonexistent_path))
        
        with open(nonexistent_path, 'r') as f:
            created_config = yaml.safe_load(f)
        
        self.assertIn('mqtt', created_config)
        self.assertIn('meshtastic', created_config)
    
    @patch('sys.argv', ['meshtastic-send', '--message', 'Test', '--config'])
    def test_invalid_yaml_syntax(self, ):
        """Test error handling for invalid YAML syntax."""
        invalid_path = os.path.join(self.temp_dir, 'invalid.yaml')
        with open(invalid_path, 'w') as f:
            f.write("invalid: yaml: syntax:\n  - broken [")
        
        sys.argv.append(invalid_path)
        
        # Should exit with error code 1 (config load error)
        with self.assertRaises(SystemExit) as cm:
            main()
        
        self.assertEqual(cm.exception.code, 1)


class TestValidateInputs(unittest.TestCase):
    """Test input validation logic."""
    
    def test_validate_complete_inputs(self):
        """Test validation with all required inputs present."""
        config = Config()
        config.config.mqtt.server = 'test.mqtt.org'
        config.config.mqtt.username = 'testuser'
        config.config.mqtt.password = 'testpass'
        config.config.meshtastic.from_id = '!12345678'
        
        is_valid, errors = validate_inputs(config, "Test message")
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_empty_message(self):
        """Test validation fails with empty message."""
        config = Config()
        config.config.mqtt.server = 'test.mqtt.org'
        config.config.mqtt.username = 'testuser'
        config.config.mqtt.password = 'testpass'
        config.config.meshtastic.from_id = '!12345678'
        
        is_valid, errors = validate_inputs(config, "")
        
        self.assertFalse(is_valid)
        self.assertTrue(any("empty" in err.lower() for err in errors))
    
    def test_validate_missing_mqtt_config(self):
        """Test validation fails with missing MQTT configuration."""
        config = Config()
        config.config.meshtastic.from_id = '!12345678'
        
        is_valid, errors = validate_inputs(config, "Test message")
        
        self.assertFalse(is_valid)
        self.assertTrue(any("mqtt" in err.lower() for err in errors))
    
    def test_validate_missing_from_id(self):
        """Test validation fails with missing from_id."""
        config = Config()
        config.config.mqtt.server = 'test.mqtt.org'
        config.config.mqtt.username = 'testuser'
        config.config.mqtt.password = 'testpass'
        
        is_valid, errors = validate_inputs(config, "Test message")
        
        self.assertFalse(is_valid)
        self.assertTrue(any("from_id" in err.lower() for err in errors))


if __name__ == '__main__':
    unittest.main()
