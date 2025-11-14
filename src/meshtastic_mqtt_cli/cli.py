"""Command-line interface module for Meshtastic MQTT CLI."""

import argparse
import logging
import os
import sys
from pathlib import Path

from .config import Config
from .mqtt_client import MeshtasticMQTTClient
from .message import build_message_payload, build_topic, encode_message_text


# Configure logging
logger = logging.getLogger(__name__)


def get_default_config_path() -> str:
    """
    Get the default configuration file path based on the platform.
    
    Returns:
        Default configuration file path
    """
    if os.name == 'nt':  # Windows
        config_dir = os.path.join(os.environ.get('APPDATA', ''), 'meshtastic-mqtt-cli')
    else:  # Linux/macOS
        config_dir = os.path.join(os.path.expanduser('~'), '.config', 'meshtastic-mqtt-cli')
    
    return os.path.join(config_dir, 'config.yaml')


def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        prog='meshtastic-send',
        description='Send messages to Meshtastic devices via MQTT',
        epilog='''
Examples:
  # Send a message using config file settings
  meshtastic-send --message "Hello, Meshtastic!"
  
  # Override MQTT server from command line
  meshtastic-send -m "Test message" --server mqtt.example.com
  
  # Specify all parameters via command line
  meshtastic-send -m "Direct message" --server mqtt.meshtastic.org \\
    --username meshdev --password large4cats --from-id !12345678
  
  # Use custom config file
  meshtastic-send -m "Hello" --config /path/to/config.yaml

Configuration file location: {}
        '''.format(get_default_config_path()),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Required arguments
    parser.add_argument(
        '--message', '-m',
        type=str,
        required=True,
        help='Message text to send (required)'
    )
    
    # MQTT connection arguments
    parser.add_argument(
        '--server',
        type=str,
        help='MQTT server address (overrides config file)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        help='MQTT server port (default: 1883, overrides config file)'
    )
    
    parser.add_argument(
        '--username', '-u',
        type=str,
        help='MQTT username (overrides config file)'
    )
    
    parser.add_argument(
        '--password', '-p',
        type=str,
        help='MQTT password (overrides config file)'
    )
    
    # Meshtastic arguments
    parser.add_argument(
        '--from-id',
        type=str,
        dest='from_id',
        help='Sender node ID, e.g., !12345678 (overrides config file)'
    )
    
    parser.add_argument(
        '--to-id',
        type=str,
        dest='to_id',
        help='Recipient node ID, e.g., ^all for broadcast (overrides config file)'
    )
    
    parser.add_argument(
        '--channel',
        type=str,
        help='Meshtastic channel name (overrides config file)'
    )
    
    parser.add_argument(
        '--region',
        type=str,
        help='Meshtastic region, e.g., US, EU (overrides config file)'
    )
    
    # Configuration file
    parser.add_argument(
        '--config',
        type=str,
        default=get_default_config_path(),
        help=f'Path to configuration file (default: {get_default_config_path()})'
    )
    
    # Logging options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose (DEBUG level) logging'
    )
    
    return parser.parse_args()


def validate_inputs(config: Config, message: str) -> tuple[bool, list[str]]:
    """
    Validate that all required parameters are present.
    
    Args:
        config: Configuration object
        message: Message text
    
    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []
    
    # Validate message text is not empty
    if not message or not message.strip():
        errors.append("Message text cannot be empty")
    
    # Validate required MQTT connection parameters
    is_valid, missing_fields = config.validate()
    if not is_valid:
        errors.append(f"Missing required configuration parameters: {', '.join(missing_fields)}")
    
    # Validate from_id is present
    if not config.get('meshtastic.from_id'):
        errors.append("Missing required parameter: from_id (sender node ID)")
    
    return (len(errors) == 0, errors)


def setup_logging(verbose: bool = False):
    """
    Configure logging for the application.
    
    Args:
        verbose: If True, set logging level to DEBUG, otherwise INFO
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )
    
    # Set level for our package logger
    logger.setLevel(log_level)
    
    # Set level for paho-mqtt logger (reduce noise unless verbose)
    mqtt_logger = logging.getLogger('paho.mqtt')
    mqtt_logger.setLevel(logging.WARNING if not verbose else logging.DEBUG)


def main():
    """
    Main entry point for the CLI application.
    
    Orchestrates the complete flow:
    1. Parse command-line arguments
    2. Setup logging
    3. Load configuration
    4. Merge CLI overrides
    5. Validate inputs
    6. Build message and topic
    7. Connect to MQTT broker
    8. Publish message
    9. Display confirmation
    """
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Setup logging
        setup_logging(args.verbose)
        
        logger.debug("Starting Meshtastic MQTT CLI")
        
        # Initialize configuration
        config = Config()
        
        # Load configuration from file
        config_path = args.config
        if os.path.exists(config_path):
            logger.debug(f"Loading configuration from {config_path}")
            try:
                config.load_from_file(config_path)
            except Exception as e:
                logger.error(f"Failed to load configuration file: {e}")
                sys.exit(1)
        else:
            logger.info(f"Configuration file not found at {config_path}")
            logger.info("Creating default configuration file...")
            try:
                Config.create_default_config(config_path)
                logger.info(f"Default configuration created at {config_path}")
                logger.info("Please edit the configuration file with your MQTT credentials and try again")
                sys.exit(0)
            except Exception as e:
                logger.error(f"Failed to create default configuration: {e}")
                sys.exit(1)
        
        # Merge CLI arguments with configuration (CLI takes priority)
        logger.debug("Merging CLI arguments with configuration")
        config.merge_with_cli_args(args)
        
        # Validate inputs
        is_valid, errors = validate_inputs(config, args.message)
        if not is_valid:
            logger.error("Validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            sys.exit(3)
        
        # Encode message text
        message_text = encode_message_text(args.message)
        logger.debug(f"Message text: {message_text}")
        
        # Build message payload
        logger.debug("Building message payload")
        from_id = config.get('meshtastic.from_id')
        to_id = config.get('meshtastic.to_id')
        payload = build_message_payload(message_text, from_id, to_id)
        logger.debug(f"Message payload: {payload}")
        
        # Build MQTT topic
        region = config.get('meshtastic.region')
        channel = config.get('meshtastic.channel')
        topic = build_topic(region, channel, from_id)
        logger.debug(f"MQTT topic: {topic}")
        
        # Connect to MQTT broker
        logger.info(f"Connecting to MQTT broker at {config.get('mqtt.server')}:{config.get('mqtt.port')}")
        client = MeshtasticMQTTClient(
            server=config.get('mqtt.server'),
            port=config.get('mqtt.port'),
            username=config.get('mqtt.username'),
            password=config.get('mqtt.password')
        )
        
        try:
            client.connect()
        except ConnectionError as e:
            logger.error(f"Connection failed: {e}")
            logger.error("Please check your MQTT server address, credentials, and network connectivity")
            sys.exit(2)
        
        # Publish message
        logger.info(f"Publishing message to topic: {topic}")
        try:
            client.publish(topic, payload)
            logger.info("✓ Message sent successfully!")
            print(f"Message sent to {to_id} via {channel}")
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            sys.exit(2)
        finally:
            # Clean disconnect
            client.disconnect()
        
        # Success
        sys.exit(0)
        
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if logger.level == logging.DEBUG:
            import traceback
            traceback.print_exc()
        sys.exit(99)


if __name__ == '__main__':
    main()
