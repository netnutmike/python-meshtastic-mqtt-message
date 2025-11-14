"""Unit tests for the MQTT client module."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import paho.mqtt.client as mqtt

from src.meshtastic_mqtt_cli.mqtt_client import MeshtasticMQTTClient


class TestMeshtasticMQTTClient(unittest.TestCase):
    """Test MeshtasticMQTTClient class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.server = "test.mqtt.org"
        self.port = 1883
        self.username = "testuser"
        self.password = "testpass"
        self.client = MeshtasticMQTTClient(
            self.server, self.port, self.username, self.password
        )
    
    def test_initialization(self):
        """Test client initialization."""
        self.assertEqual(self.client.server, self.server)
        self.assertEqual(self.client.port, self.port)
        self.assertEqual(self.client.username, self.username)
        self.assertEqual(self.client.password, self.password)
        self.assertIsNone(self.client.client)
        self.assertFalse(self.client.connected)
        self.assertIsNone(self.client.connection_error)
    
    @patch('paho.mqtt.client.Client')
    def test_successful_connection(self, mock_mqtt_client):
        """Test successful connection to MQTT broker."""
        mock_client_instance = MagicMock()
        mock_mqtt_client.return_value = mock_client_instance
        
        # Simulate successful connection
        def simulate_connect(*args, **kwargs):
            # Trigger the on_connect callback with success code
            self.client._on_connect(mock_client_instance, None, None, 0)
        
        mock_client_instance.connect.side_effect = simulate_connect
        
        self.client.connect()
        
        mock_client_instance.username_pw_set.assert_called_once_with(
            self.username, self.password
        )
        mock_client_instance.connect.assert_called_once_with(
            self.server, self.port, keepalive=60
        )
        mock_client_instance.loop_start.assert_called_once()
        self.assertTrue(self.client.connected)
    
    @patch('paho.mqtt.client.Client')
    def test_connection_with_bad_credentials(self, mock_mqtt_client):
        """Test connection failure with bad credentials."""
        mock_client_instance = MagicMock()
        mock_mqtt_client.return_value = mock_client_instance
        
        # Simulate connection failure with bad credentials (rc=4)
        def simulate_connect(*args, **kwargs):
            self.client._on_connect(mock_client_instance, None, None, 4)
        
        mock_client_instance.connect.side_effect = simulate_connect
        
        with self.assertRaises(ConnectionError) as context:
            self.client.connect()
        
        self.assertIn("bad username or password", str(context.exception))
        self.assertFalse(self.client.connected)
    
    @patch('paho.mqtt.client.Client')
    def test_connection_timeout(self, mock_mqtt_client):
        """Test connection timeout."""
        mock_client_instance = MagicMock()
        mock_mqtt_client.return_value = mock_client_instance
        
        # Don't trigger on_connect callback to simulate timeout
        with self.assertRaises(ConnectionError) as context:
            self.client.connect()
        
        self.assertIn("timeout", str(context.exception).lower())
    
    @patch('paho.mqtt.client.Client')
    def test_connection_exception(self, mock_mqtt_client):
        """Test handling of connection exceptions."""
        mock_client_instance = MagicMock()
        mock_mqtt_client.return_value = mock_client_instance
        mock_client_instance.connect.side_effect = Exception("Network error")
        
        with self.assertRaises(ConnectionError) as context:
            self.client.connect()
        
        self.assertIn("Network error", str(context.exception))
    
    def test_on_connect_callback_success(self):
        """Test _on_connect callback with success code."""
        mock_client = Mock()
        self.client._on_connect(mock_client, None, None, 0)
        
        self.assertTrue(self.client.connected)
        self.assertIsNone(self.client.connection_error)
    
    def test_on_connect_callback_failure(self):
        """Test _on_connect callback with various failure codes."""
        mock_client = Mock()
        
        # Test different error codes
        error_codes = [1, 2, 3, 4, 5]
        for rc in error_codes:
            self.client.connected = False
            self.client.connection_error = None
            self.client._on_connect(mock_client, None, None, rc)
            
            self.assertFalse(self.client.connected)
            self.assertIsNotNone(self.client.connection_error)
    
    @patch('paho.mqtt.client.Client')
    def test_publish_success(self, mock_mqtt_client):
        """Test successful message publishing."""
        mock_client_instance = MagicMock()
        mock_mqtt_client.return_value = mock_client_instance
        
        # Set up connected state
        self.client.client = mock_client_instance
        self.client.connected = True
        
        # Mock publish result
        mock_result = Mock()
        mock_result.rc = mqtt.MQTT_ERR_SUCCESS
        mock_client_instance.publish.return_value = mock_result
        
        topic = "msh/US/2/json/LongFast/!12345678"
        payload = '{"test": "message"}'
        
        self.client.publish(topic, payload)
        
        mock_client_instance.publish.assert_called_once_with(topic, payload, qos=1)
        mock_result.wait_for_publish.assert_called_once()
    
    def test_publish_not_connected(self):
        """Test publish when not connected."""
        topic = "test/topic"
        payload = "test message"
        
        with self.assertRaises(RuntimeError) as context:
            self.client.publish(topic, payload)
        
        self.assertIn("Not connected", str(context.exception))
    
    @patch('paho.mqtt.client.Client')
    def test_publish_failure(self, mock_mqtt_client):
        """Test publish failure."""
        mock_client_instance = MagicMock()
        mock_mqtt_client.return_value = mock_client_instance
        
        # Set up connected state
        self.client.client = mock_client_instance
        self.client.connected = True
        
        # Mock publish result with error
        mock_result = Mock()
        mock_result.rc = mqtt.MQTT_ERR_NO_CONN
        mock_client_instance.publish.return_value = mock_result
        
        topic = "test/topic"
        payload = "test message"
        
        with self.assertRaises(Exception) as context:
            self.client.publish(topic, payload)
        
        self.assertIn("Publish failed", str(context.exception))
    
    def test_on_publish_callback(self):
        """Test _on_publish callback."""
        mock_client = Mock()
        # Should not raise any exceptions
        self.client._on_publish(mock_client, None, 123)
    
    def test_disconnect(self):
        """Test disconnection from broker."""
        mock_client = MagicMock()
        self.client.client = mock_client
        self.client.connected = True
        
        self.client.disconnect()
        
        mock_client.loop_stop.assert_called_once()
        mock_client.disconnect.assert_called_once()
        self.assertFalse(self.client.connected)
        self.assertIsNone(self.client.client)
    
    def test_disconnect_with_no_client(self):
        """Test disconnect when client is None."""
        self.client.client = None
        # Should not raise any exceptions
        self.client.disconnect()
        self.assertIsNone(self.client.client)
    
    def test_disconnect_with_exception(self):
        """Test disconnect handles exceptions gracefully."""
        mock_client = MagicMock()
        mock_client.disconnect.side_effect = Exception("Disconnect error")
        self.client.client = mock_client
        self.client.connected = True
        
        # Should not raise exception, but should clean up
        self.client.disconnect()
        
        self.assertIsNone(self.client.client)


if __name__ == '__main__':
    unittest.main()
