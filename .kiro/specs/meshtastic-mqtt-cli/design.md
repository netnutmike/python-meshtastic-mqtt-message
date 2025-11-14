# Design Document

## Overview

The Meshtastic MQTT CLI tool is a Python command-line application that simplifies sending messages to Meshtastic devices via MQTT. The tool abstracts the complexity of the Meshtastic MQTT protocol, allowing users to send messages using simple command-line arguments while the tool handles JSON message construction, MQTT connection management, and protocol compliance.

Based on the Meshtastic MQTT documentation (https://meshtastic.org/docs/software/integrations/mqtt/), messages are published to topics following the pattern `msh/[region]/2/json/[channel]/[node_id]` and require specific JSON payload structures.

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
meshtastic-mqtt-cli/
├── src/
│   └── meshtastic_mqtt_cli/
│       ├── __init__.py
│       ├── cli.py           # Command-line interface and argument parsing
│       ├── config.py        # Configuration management (YAML loading/saving)
│       ├── mqtt_client.py   # MQTT connection and publishing logic
│       └── message.py       # Meshtastic message formatting
├── config/
│   └── default_config.yaml  # Default configuration template
├── .gitignore
├── requirements.txt
├── setup.py
└── README.md
```

### Component Responsibilities

1. **CLI Module**: Handles argument parsing, validates user input, orchestrates the flow
2. **Config Module**: Manages YAML configuration file reading, writing, and merging with CLI overrides
3. **MQTT Client Module**: Establishes MQTT connections and publishes messages
4. **Message Module**: Constructs Meshtastic-compliant JSON message payloads

## Components and Interfaces

### CLI Module (`cli.py`)

**Purpose**: Entry point for the application, handles command-line argument parsing and orchestration.

**Key Functions**:
- `main()`: Entry point that coordinates all operations
- `parse_arguments()`: Uses argparse to define and parse command-line arguments
- `validate_inputs()`: Validates that required parameters are present after merging config and CLI args

**Command-Line Arguments**:
- `--message` or `-m`: Message text to send (required)
- `--server`: MQTT server address (optional, overrides config)
- `--port`: MQTT server port (optional, overrides config, default: 1883)
- `--username` or `-u`: MQTT username (optional, overrides config)
- `--password` or `-p`: MQTT password (optional, overrides config)
- `--from-id`: Sender node ID (optional, overrides config)
- `--to-id`: Recipient node ID (optional, overrides config)
- `--channel`: Meshtastic channel (optional, overrides config)
- `--config`: Path to config file (optional, default: ~/.meshtastic-mqtt-cli/config.yaml)
- `--help` or `-h`: Display help information

### Config Module (`config.py`)

**Purpose**: Manages configuration file operations and merging with command-line overrides.

**Key Classes/Functions**:
- `Config` class: Represents configuration state
  - `load_from_file(path)`: Loads YAML configuration
  - `merge_with_cli_args(args)`: Merges CLI arguments, giving them priority
  - `validate()`: Ensures required fields are present
  - `create_default_config(path)`: Creates a default config file if none exists
  - `get(key, default=None)`: Retrieves configuration value

**YAML Configuration Structure**:
```yaml
mqtt:
  server: "mqtt.meshtastic.org"
  port: 1883
  username: "meshdev"
  password: "large4cats"
  
meshtastic:
  from_id: "!12345678"
  to_id: "^all"
  channel: "LongFast"
  region: "US"
```

### MQTT Client Module (`mqtt_client.py`)

**Purpose**: Handles MQTT connection establishment and message publishing.

**Key Classes/Functions**:
- `MeshtasticMQTTClient` class:
  - `__init__(server, port, username, password)`: Initialize client with connection parameters
  - `connect()`: Establish connection to MQTT broker
  - `publish(topic, payload)`: Publish message to specified topic
  - `disconnect()`: Clean disconnect from broker
  - `_on_connect(client, userdata, flags, rc)`: Connection callback
  - `_on_publish(client, userdata, mid)`: Publish callback

**Dependencies**: Uses `paho-mqtt` library for MQTT protocol implementation.

### Message Module (`message.py`)

**Purpose**: Constructs Meshtastic-compliant JSON message payloads and topic strings.

**Key Functions**:
- `build_message_payload(text, from_id, to_id)`: Creates JSON payload following Meshtastic format
- `build_topic(region, channel, from_id)`: Constructs MQTT topic string
- `encode_message_text(text)`: Encodes message text appropriately for Meshtastic

**Meshtastic Message Format**:
Based on Meshtastic documentation, the JSON payload structure includes:
```json
{
  "from": 123456789,
  "to": 4294967295,
  "channel": 0,
  "type": "sendtext",
  "payload": {
    "text": "message content"
  }
}
```

Topic format: `msh/[region]/2/json/[channel]/[node_id]`

## Data Models

### Configuration Data Model

```python
@dataclass
class MQTTConfig:
    server: str
    port: int = 1883
    username: str = ""
    password: str = ""

@dataclass
class MeshtasticConfig:
    from_id: str = ""
    to_id: str = "^all"
    channel: str = "LongFast"
    region: str = "US"

@dataclass
class AppConfig:
    mqtt: MQTTConfig
    meshtastic: MeshtasticConfig
```

### Message Data Model

```python
@dataclass
class MeshtasticMessage:
    from_node: int
    to_node: int
    channel: int
    message_type: str
    text: str
    
    def to_json(self) -> str:
        """Convert to Meshtastic JSON format"""
```

## Error Handling

### Error Categories and Handling Strategy

1. **Configuration Errors**:
   - Missing required configuration: Display clear error message listing missing fields, exit code 1
   - Invalid YAML syntax: Display parse error with line number, exit code 1
   - Invalid file permissions: Display permission error, exit code 1

2. **MQTT Connection Errors**:
   - Connection refused: Display server/port details and suggest checking connectivity, exit code 2
   - Authentication failure: Display authentication error, suggest checking credentials, exit code 2
   - Timeout: Display timeout error with server details, exit code 2

3. **Message Errors**:
   - Empty message: Display error requiring message content, exit code 3
   - Invalid node ID format: Display format requirements, exit code 3

4. **General Errors**:
   - Unexpected exceptions: Log full traceback, display user-friendly error, exit code 99

### Logging Strategy

- Use Python's `logging` module with configurable verbosity
- Default: INFO level (connection status, publish confirmation)
- Verbose mode (`--verbose` flag): DEBUG level (full MQTT protocol details)
- All errors logged to stderr
- Success messages logged to stdout

## Testing Strategy

### Unit Tests

1. **Config Module Tests**:
   - Test YAML parsing with valid configuration
   - Test handling of missing configuration file
   - Test CLI argument override logic
   - Test validation of required fields
   - Test default config file creation

2. **Message Module Tests**:
   - Test JSON payload construction with various inputs
   - Test topic string generation
   - Test node ID format handling
   - Test message text encoding

3. **MQTT Client Module Tests**:
   - Test connection establishment (using mock broker)
   - Test publish operation
   - Test error handling for connection failures
   - Test clean disconnect

### Integration Tests

1. **End-to-End Flow**:
   - Test complete flow from CLI args to message publish (using test MQTT broker)
   - Test config file + CLI override combination
   - Test error scenarios (missing config, bad credentials)

### Manual Testing

1. Test against actual Meshtastic MQTT broker (mqtt.meshtastic.org)
2. Verify message format compliance with Meshtastic devices
3. Test various command-line argument combinations
4. Verify help documentation clarity

## Dependencies

### Required Python Packages

- `paho-mqtt>=1.6.1`: MQTT client library
- `PyYAML>=6.0`: YAML configuration file parsing
- `argparse`: Command-line argument parsing (standard library)
- `dataclasses`: Data models (standard library, Python 3.7+)
- `logging`: Logging functionality (standard library)

### Python Version

- Minimum: Python 3.7 (for dataclasses support)
- Recommended: Python 3.9+

## Installation and Distribution

### Installation Methods

1. **From source**:
   ```bash
   git clone <repository>
   cd meshtastic-mqtt-cli
   pip install -e .
   ```

2. **Using pip** (future):
   ```bash
   pip install meshtastic-mqtt-cli
   ```

### Entry Point

The tool will be installed as a command-line executable `meshtastic-send` using setuptools entry_points.

## Configuration File Location

Default configuration file location follows platform conventions:
- Linux/macOS: `~/.config/meshtastic-mqtt-cli/config.yaml`
- Windows: `%APPDATA%\meshtastic-mqtt-cli\config.yaml`

The tool creates the directory and default config file on first run if they don't exist.

## Security Considerations

1. **Credential Storage**: YAML config file should have restricted permissions (0600 on Unix-like systems)
2. **Password Handling**: Passwords in CLI arguments visible in process list - config file preferred
3. **Config File Exclusion**: .gitignore must exclude config files to prevent credential commits
4. **Input Validation**: Sanitize all user inputs before constructing MQTT messages
5. **Connection Security**: Support for TLS/SSL connections to MQTT broker (future enhancement)

## Future Enhancements

1. Support for TLS/SSL encrypted MQTT connections
2. Interactive mode for sending multiple messages
3. Support for receiving/subscribing to Meshtastic messages
4. Message templates for common message types
5. Batch message sending from file input
6. Support for additional Meshtastic message types beyond text
