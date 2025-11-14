"""Meshtastic message formatting module."""

import json
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class MeshtasticMessage:
    """Data model for a Meshtastic message."""
    from_node: int
    to_node: int
    channel: int
    message_type: str
    text: str
    
    def to_json(self) -> str:
        """Convert to Meshtastic JSON format."""
        payload = {
            "from": self.from_node,
            "channel": self.channel,
            "type": self.message_type,
            "payload": self.text  # Payload is just the text string
        }
        
        # Only include "to" field if not broadcasting to all
        # Broadcast address is 0xFFFFFFFF (4294967295)
        if self.to_node != 4294967295:
            payload["to"] = self.to_node
        
        return json.dumps(payload)


def build_message_payload(text: str, from_id: str, to_id: str, channel_number: int = 0) -> str:
    """
    Construct JSON payload following Meshtastic protocol specification.
    
    Args:
        text: Message text to send
        from_id: Sender node ID (e.g., "!12345678")
        to_id: Recipient node ID (e.g., "^all" for broadcast)
        channel_number: Channel number/index (0-7, default: 0)
    
    Returns:
        JSON string formatted according to Meshtastic protocol
    """
    # Convert node IDs to integers
    # Meshtastic node IDs starting with ! are hex values
    # ^all is broadcast (0xFFFFFFFF = 4294967295)
    from_node = _parse_node_id(from_id)
    to_node = _parse_node_id(to_id)
    
    # Create message with specified channel number
    message = MeshtasticMessage(
        from_node=from_node,
        to_node=to_node,
        channel=channel_number,
        message_type="sendtext",
        text=text
    )
    
    return message.to_json()


def _parse_node_id(node_id: str) -> int:
    """
    Parse a Meshtastic node ID string to integer.
    
    Args:
        node_id: Node ID string (e.g., "!12345678", "^all")
    
    Returns:
        Integer representation of the node ID
    """
    if node_id == "^all":
        # Broadcast address
        return 4294967295  # 0xFFFFFFFF
    elif node_id.startswith("!"):
        # Hex node ID
        return int(node_id[1:], 16)
    else:
        # Assume it's already a numeric string
        return int(node_id)



def build_topic(region: str, channel: str, from_id: str) -> str:
    """
    Construct MQTT topic string following Meshtastic pattern.
    
    Topic pattern: msh/[region]/2/json/[channel]/[node_id]
    
    Args:
        region: Meshtastic region (e.g., "US", "EU")
        channel: Channel name (e.g., "LongFast")
        from_id: Sender node ID (e.g., "!12345678")
    
    Returns:
        MQTT topic string
    """
    return f"msh/{region}/2/json/{channel}/{from_id}"



def encode_message_text(text: str) -> str:
    """
    Encode message text for proper handling of special characters.
    
    Args:
        text: Raw message text
    
    Returns:
        Encoded message text suitable for Meshtastic transmission
    """
    # Ensure text is properly encoded as UTF-8
    # Handle any special characters that might cause issues
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='replace')
    
    # Normalize the text to ensure consistent encoding
    return text.strip()
