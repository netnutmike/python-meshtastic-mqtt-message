"""Unit tests for message module."""

import json
import unittest

from src.meshtastic_mqtt_cli.message import (
    MeshtasticMessage,
    build_message_payload,
    build_topic,
    encode_message_text,
    _parse_node_id
)


class TestMeshtasticMessage(unittest.TestCase):
    """Test MeshtasticMessage dataclass."""
    
    def test_to_json_broadcast(self):
        """Test JSON serialization with broadcast (no 'to' field)."""
        message = MeshtasticMessage(
            from_node=305419896,
            to_node=4294967295,
            channel=0,
            message_type="sendtext",
            text="Hello Meshtastic"
        )
        
        json_str = message.to_json()
        data = json.loads(json_str)
        
        self.assertEqual(data["from"], 305419896)
        self.assertNotIn("to", data)  # Should not include "to" for broadcast
        self.assertEqual(data["channel"], 0)
        self.assertEqual(data["type"], "sendtext")
        self.assertEqual(data["payload"], "Hello Meshtastic")  # Payload is just the text
    
    def test_to_json_direct_message(self):
        """Test JSON serialization with direct message (includes 'to' field)."""
        message = MeshtasticMessage(
            from_node=305419896,
            to_node=2271560481,  # !87654321
            channel=0,
            message_type="sendtext",
            text="Direct message"
        )
        
        json_str = message.to_json()
        data = json.loads(json_str)
        
        self.assertEqual(data["from"], 305419896)
        self.assertEqual(data["to"], 2271560481)  # Should include "to" for direct message
        self.assertEqual(data["channel"], 0)
        self.assertEqual(data["type"], "sendtext")
        self.assertEqual(data["payload"], "Direct message")  # Payload is just the text


class TestBuildMessagePayload(unittest.TestCase):
    """Test build_message_payload function."""
    
    def test_build_payload_with_hex_ids(self):
        """Test building payload with hex node IDs."""
        payload = build_message_payload("Test message", "!12345678", "!87654321")
        data = json.loads(payload)
        
        self.assertEqual(data["from"], 0x12345678)
        self.assertEqual(data["to"], 0x87654321)
        self.assertEqual(data["type"], "sendtext")
        self.assertEqual(data["payload"], "Test message")  # Payload is just the text
    
    def test_build_payload_with_broadcast(self):
        """Test building payload with broadcast address (no 'to' field)."""
        payload = build_message_payload("Broadcast message", "!12345678", "^all")
        data = json.loads(payload)
        
        self.assertEqual(data["from"], 0x12345678)
        self.assertNotIn("to", data)  # Should not include "to" for broadcast
        self.assertEqual(data["payload"], "Broadcast message")  # Payload is just the text
    
    def test_build_payload_with_numeric_ids(self):
        """Test building payload with numeric node IDs."""
        payload = build_message_payload("Numeric test", "123456", "789012")
        data = json.loads(payload)
        
        self.assertEqual(data["from"], 123456)
        self.assertEqual(data["to"], 789012)


class TestParseNodeId(unittest.TestCase):
    """Test _parse_node_id function."""
    
    def test_parse_broadcast(self):
        """Test parsing broadcast address."""
        node_id = _parse_node_id("^all")
        self.assertEqual(node_id, 4294967295)
    
    def test_parse_hex_id(self):
        """Test parsing hex node ID."""
        node_id = _parse_node_id("!12345678")
        self.assertEqual(node_id, 0x12345678)
    
    def test_parse_numeric_id(self):
        """Test parsing numeric node ID."""
        node_id = _parse_node_id("305419896")
        self.assertEqual(node_id, 305419896)


class TestBuildTopic(unittest.TestCase):
    """Test build_topic function."""
    
    def test_build_topic_standard(self):
        """Test building standard MQTT topic."""
        topic = build_topic("US", "LongFast", "!12345678")
        self.assertEqual(topic, "msh/US/2/json/LongFast/!12345678")
    
    def test_build_topic_different_region(self):
        """Test building topic with different region."""
        topic = build_topic("EU", "ShortSlow", "!abcdef12")
        self.assertEqual(topic, "msh/EU/2/json/ShortSlow/!abcdef12")
    
    def test_build_topic_with_broadcast(self):
        """Test building topic with broadcast address."""
        topic = build_topic("US", "LongFast", "^all")
        self.assertEqual(topic, "msh/US/2/json/LongFast/^all")


class TestEncodeMessageText(unittest.TestCase):
    """Test encode_message_text function."""
    
    def test_encode_simple_text(self):
        """Test encoding simple text."""
        encoded = encode_message_text("Hello World")
        self.assertEqual(encoded, "Hello World")
    
    def test_encode_text_with_whitespace(self):
        """Test encoding text with leading/trailing whitespace."""
        encoded = encode_message_text("  Hello World  ")
        self.assertEqual(encoded, "Hello World")
    
    def test_encode_text_with_special_chars(self):
        """Test encoding text with special characters."""
        encoded = encode_message_text("Hello! @#$% World")
        self.assertEqual(encoded, "Hello! @#$% World")
    
    def test_encode_bytes_input(self):
        """Test encoding bytes input."""
        encoded = encode_message_text(b"Hello World")
        self.assertEqual(encoded, "Hello World")


if __name__ == "__main__":
    unittest.main()
