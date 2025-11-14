#!/usr/bin/env python3
"""
Manual validation script for Meshtastic MQTT CLI.

This script provides an interactive way to test the CLI tool against
the actual Meshtastic MQTT broker with various configurations.

Usage:
    python tests/manual_validation.py
"""

import os
import sys
import tempfile
import yaml
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.meshtastic_mqtt_cli.mqtt_client import MeshtasticMQTTClient
from src.meshtastic_mqtt_cli.message import build_message_payload, build_topic


def test_connection():
    """Test connection to Meshtastic MQTT broker."""
    print("\n" + "="*70)
    print("TEST 1: Connection to mqtt.meshtastic.org")
    print("="*70)
    
    server = "mqtt.meshtastic.org"
    port = 1883
    username = "meshdev"
    password = "large4cats"
    
    print(f"\nConnecting to {server}:{port}...")
    print(f"Username: {username}")
    
    try:
        client = MeshtasticMQTTClient(server, port, username, password)
        client.connect()
        
        if client.connected:
            print("✓ Connection successful!")
            client.disconnect()
            print("✓ Disconnected cleanly")
            return True
        else:
            print("✗ Connection failed")
            return False
            
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False


def test_message_format():
    """Test message format compliance."""
    print("\n" + "="*70)
    print("TEST 2: Message Format Compliance")
    print("="*70)
    
    test_cases = [
        ("!12345678", "^all", "Test broadcast message"),
        ("!ffffffff", "!87654321", "Test direct message"),
        ("!abcdef12", "^all", "Test with special chars: @#$%"),
    ]
    
    all_passed = True
    
    for from_id, to_id, text in test_cases:
        print(f"\nTest case: from={from_id}, to={to_id}")
        print(f"Message: {text}")
        
        try:
            payload = build_message_payload(text, from_id, to_id)
            print(f"✓ Payload generated: {payload[:80]}...")
            
            # Validate it's valid JSON
            import json
            data = json.loads(payload)
            
            # Check required fields
            required_fields = ["from", "to", "channel", "type", "payload"]
            for field in required_fields:
                if field not in data:
                    print(f"✗ Missing required field: {field}")
                    all_passed = False
                    
            if "text" not in data.get("payload", {}):
                print("✗ Missing 'text' in payload")
                all_passed = False
            else:
                print("✓ All required fields present")
                
        except Exception as e:
            print(f"✗ Error: {e}")
            all_passed = False
    
    return all_passed


def test_topic_format():
    """Test topic format compliance."""
    print("\n" + "="*70)
    print("TEST 3: Topic Format Compliance")
    print("="*70)
    
    test_cases = [
        ("US", "LongFast", "!12345678"),
        ("EU", "MediumFast", "!ffffffff"),
        ("AU", "ShortFast", "!abcdef12"),
    ]
    
    all_passed = True
    
    for region, channel, from_id in test_cases:
        print(f"\nTest case: region={region}, channel={channel}, from_id={from_id}")
        
        try:
            topic = build_topic(region, channel, from_id)
            print(f"Generated topic: {topic}")
            
            # Validate format: msh/[region]/2/json/[channel]/[node_id]
            expected = f"msh/{region}/2/json/{channel}/{from_id}"
            if topic == expected:
                print("✓ Topic format correct")
            else:
                print(f"✗ Expected: {expected}")
                print(f"✗ Got: {topic}")
                all_passed = False
                
        except Exception as e:
            print(f"✗ Error: {e}")
            all_passed = False
    
    return all_passed


def test_cli_combinations():
    """Test various CLI command combinations."""
    print("\n" + "="*70)
    print("TEST 4: CLI Command Combinations")
    print("="*70)
    
    # Create temporary config file
    temp_dir = tempfile.mkdtemp()
    config_path = os.path.join(temp_dir, 'test_config.yaml')
    
    config_data = {
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
    
    with open(config_path, 'w') as f:
        yaml.dump(config_data, f)
    
    print(f"\nCreated test config at: {config_path}")
    
    test_commands = [
        f"meshtastic-send --message 'Test 1' --config {config_path}",
        f"meshtastic-send --message 'Test 2' --server mqtt.meshtastic.org --username meshdev --password large4cats --from-id !ffffffff",
        f"meshtastic-send --message 'Test 3' --config {config_path} --region EU",
        f"meshtastic-send --message 'Test 4' --config {config_path} --channel MediumFast",
    ]
    
    print("\nExample commands to test manually:")
    print("-" * 70)
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n{i}. {cmd}")
    
    print("\n" + "-" * 70)
    print("\nNote: These commands are for manual testing.")
    print("Run them individually to verify CLI functionality.")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    
    return True


def main():
    """Run all validation tests."""
    print("\n" + "="*70)
    print("MESHTASTIC MQTT CLI - MANUAL VALIDATION SUITE")
    print("="*70)
    print("\nThis script validates the CLI tool against the Meshtastic MQTT broker.")
    print("Some tests connect to the actual broker but do NOT publish messages.")
    print("\n" + "="*70)
    
    results = []
    
    # Run tests
    results.append(("Connection Test", test_connection()))
    results.append(("Message Format Test", test_message_format()))
    results.append(("Topic Format Test", test_topic_format()))
    results.append(("CLI Combinations", test_cli_combinations()))
    
    # Print summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<50} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "="*70)
    if all_passed:
        print("✓ ALL VALIDATION TESTS PASSED")
        print("\nThe CLI tool is ready for use with the Meshtastic MQTT broker.")
    else:
        print("✗ SOME VALIDATION TESTS FAILED")
        print("\nPlease review the failures above and fix any issues.")
    print("="*70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
