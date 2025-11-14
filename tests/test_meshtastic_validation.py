"""
Validation tests against actual Meshtastic MQTT broker.

These tests connect to the real mqtt.meshtastic.org broker to validate
message format compliance and protocol implementation.

NOTE: These tests require network connectivity and will publish actual
messages to the Meshtastic MQTT network. Run with caution.

To run these tests:
    python -m unittest tests.test_meshtastic_validation -v

Or to skip these tests in normal test runs, they can be marked as integration tests.
"""

import json
import os
import sys
import tempfile
import time
import unittest
import yaml
from unittest.mock import patch

from src.meshtastic_mqtt_cli.cli import main
from src.meshtastic_mqtt_cli.message import build_message_payload, build_topic
from src.meshtastic_mqtt_cli.mqtt_client import MeshtasticMQTTClient


class TestMeshtasticBrokerConnection(unittest.TestCase):
    """Test connection to actual Meshtastic MQTT broker."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test configuration."""
        cls.server = "mqtt.meshtastic.org"
        cls.port = 1883
        cls.username = "meshdev"
        cls.password = "large4cats"
        cls.test_from_id = "!ffffffff"  # Test node ID
        cls.test_region = "US"
        cls.test_channel = "LongFast"
    
    def test_connection_to_broker(self):
        """Test successful connection to mqtt.meshtastic.org."""
        client = MeshtasticMQTTClient(
            server=self.server,
            port=self.port,
            username=self.username,
            password=self.password
        )
        
        try:
            # Attempt connection
            client.connect()
            self.assertTrue(client.connected, "Failed to connect to Meshtastic MQTT broker")
            
            # Clean disconnect
            client.disconnect()
            self.assertFalse(client.connected, "Client should be disconnected")
            
        except ConnectionError as e:
            self.fail(f"Connection to Meshtastic MQTT broker failed: {e}")
    
    def test_message_format_compliance(self):
        """Test that message payload follows Meshtastic protocol specification."""
        text = "Test message from CLI validation"
        from_id = self.test_from_id
        to_id = "^all"
        
        # Build message payload
        payload = build_message_payload(text, from_id, to_id)
        
        # Parse JSON to validate structure
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as e:
            self.fail(f"Message payload is not valid JSON: {e}")
        
        # Validate required fields according to Meshtastic protocol
        self.assertIn("from", data, "Message missing 'from' field")
        self.assertIn("to", data, "Message missing 'to' field")
        self.assertIn("channel", data, "Message missing 'channel' field")
        self.assertIn("type", data, "Message missing 'type' field")
        self.assertIn("payload", data, "Message missing 'payload' field")
        
        # Validate field types
        self.assertIsInstance(data["from"], int, "'from' field should be integer")
        self.assertIsInstance(data["to"], int, "'to' field should be integer")
        self.assertIsInstance(data["channel"], int, "'channel' field should be integer")
        self.assertEqual(data["type"], "sendtext", "'type' field should be 'sendtext'")
        
        # Validate payload structure
        self.assertIsInstance(data["payload"], dict, "'payload' should be a dictionary")
        self.assertIn("text", data["payload"], "Payload missing 'text' field")
        self.assertEqual(data["payload"]["text"], text, "Text content doesn't match")
    
    def test_topic_format_compliance(self):
        """Test that MQTT topic follows Meshtastic pattern."""
        topic = build_topic(self.test_region, self.test_channel, self.test_from_id)
        
        # Validate topic pattern: msh/[region]/2/json/[channel]/[node_id]
        parts = topic.split('/')
        
        self.assertEqual(len(parts), 6, f"Topic should have 6 parts, got {len(parts)}")
        self.assertEqual(parts[0], "msh", "Topic should start with 'msh'")
        self.assertEqual(parts[1], self.test_region, f"Region should be {self.test_region}")
        self.assertEqual(parts[2], "2", "Protocol version should be '2'")
        self.assertEqual(parts[3], "json", "Format should be 'json'")
        self.assertEqual(parts[4], self.test_channel, f"Channel should be {self.test_channel}")
        self.assertEqual(parts[5], self.test_from_id, f"Node ID should be {self.test_from_id}")
    
    @unittest.skipIf(
        os.environ.get('SKIP_LIVE_TESTS', 'true').lower() == 'true',
        "Skipping live publish test (set SKIP_LIVE_TESTS=false to enable)"
    )
    def test_publish_to_broker(self):
        """Test publishing a message to the actual Meshtastic MQTT broker."""
        client = MeshtasticMQTTClient(
            server=self.server,
            port=self.port,
            username=self.username,
            password=self.password
        )
        
        try:
            # Connect to broker
            client.connect()
            self.assertTrue(client.connected)
            
            # Build message and topic
            text = f"CLI validation test at {time.time()}"
            payload = build_message_payload(text, self.test_from_id, "^all")
            topic = build_topic(self.test_region, self.test_channel, self.test_from_id)
            
            # Publish message
            try:
                client.publish(topic, payload)
                # If we get here, publish succeeded
                self.assertTrue(True, "Message published successfully")
            except Exception as e:
                self.fail(f"Failed to publish message: {e}")
            
        finally:
            client.disconnect()


class TestCLIWithMeshtasticBroker(unittest.TestCase):
    """Test CLI with various command-line combinations against Meshtastic broker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'config.yaml')
        
        # Create test configuration with Meshtastic broker
        self.test_config = {
            'mqtt': {
                'server': 'mqtt.meshtastic.org',
                'port': 1883,
                'username': 'meshdev',
                'password': 'large4cats'
            },
            'meshtastic': {
                'from_id': '!ffffffff',
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
    
    @unittest.skipIf(
        os.environ.get('SKIP_LIVE_TESTS', 'true').lower() == 'true',
        "Skipping live CLI test (set SKIP_LIVE_TESTS=false to enable)"
    )
    @patch('sys.argv', ['meshtastic-send', '--message', 'CLI test message', '--config'])
    def test_cli_with_config_file(self):
        """Test CLI with config file against Meshtastic broker."""
        sys.argv.append(self.config_path)
        
        # Run CLI
        with self.assertRaises(SystemExit) as cm:
            main()
        
        # Should exit successfully
        self.assertEqual(cm.exception.code, 0)
    
    @unittest.skipIf(
        os.environ.get('SKIP_LIVE_TESTS', 'true').lower() == 'true',
        "Skipping live CLI test (set SKIP_LIVE_TESTS=false to enable)"
    )
    @patch('sys.argv', [
        'meshtastic-send',
        '--message', 'CLI override test',
        '--server', 'mqtt.meshtastic.org',
        '--port', '1883',
        '--username', 'meshdev',
        '--password', 'large4cats',
        '--from-id', '!ffffffff',
        '--to-id', '^all',
        '--channel', 'LongFast',
        '--region', 'US'
    ])
    def test_cli_with_all_arguments(self):
        """Test CLI with all arguments specified on command line."""
        # Run CLI without config file
        with self.assertRaises(SystemExit) as cm:
            main()
        
        # Should exit successfully
        self.assertEqual(cm.exception.code, 0)
    
    @unittest.skipIf(
        os.environ.get('SKIP_LIVE_TESTS', 'true').lower() == 'true',
        "Skipping live CLI test (set SKIP_LIVE_TESTS=false to enable)"
    )
    @patch('sys.argv', [
        'meshtastic-send',
        '--message', 'Region override test',
        '--region', 'EU',
        '--config'
    ])
    def test_cli_with_region_override(self):
        """Test CLI with region override."""
        sys.argv.append(self.config_path)
        
        # Run CLI
        with self.assertRaises(SystemExit) as cm:
            main()
        
        # Should exit successfully
        self.assertEqual(cm.exception.code, 0)
    
    @unittest.skipIf(
        os.environ.get('SKIP_LIVE_TESTS', 'true').lower() == 'true',
        "Skipping live CLI test (set SKIP_LIVE_TESTS=false to enable)"
    )
    @patch('sys.argv', [
        'meshtastic-send',
        '--message', 'Channel override test',
        '--channel', 'MediumFast',
        '--config'
    ])
    def test_cli_with_channel_override(self):
        """Test CLI with channel override."""
        sys.argv.append(self.config_path)
        
        # Run CLI
        with self.assertRaises(SystemExit) as cm:
            main()
        
        # Should exit successfully
        self.assertEqual(cm.exception.code, 0)


if __name__ == '__main__':
    # Print information about test execution
    print("\n" + "="*70)
    print("Meshtastic MQTT Broker Validation Tests")
    print("="*70)
    print("\nNOTE: These tests connect to the actual Meshtastic MQTT broker.")
    print("Live publish tests are DISABLED by default to avoid spamming the network.")
    print("\nTo enable live publish tests, run:")
    print("  SKIP_LIVE_TESTS=false python -m unittest tests.test_meshtastic_validation -v")
    print("\n" + "="*70 + "\n")
    
    unittest.main()
