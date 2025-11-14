# Implementation Plan

- [x] 1. Set up project structure and repository configuration
- [x] 1.1 Create Python package directory structure
  - Create `src/meshtastic_mqtt_cli/` directory with `__init__.py`
  - Create placeholder files: `cli.py`, `config.py`, `mqtt_client.py`, `message.py`
  - _Requirements: 6.4_

- [x] 1.2 Create .gitignore file for Python project
  - Add Python cache files (`__pycache__/`, `*.pyc`, `*.pyo`)
  - Add virtual environment directories (`venv/`, `.venv/`, `env/`)
  - Add IDE files (`.vscode/`, `.idea/`)
  - Add config files with credentials (`config.yaml`, `*.yaml` in user directories)
  - Add distribution files (`dist/`, `build/`, `*.egg-info/`)
  - _Requirements: 6.1_

- [x] 1.3 Create requirements.txt with dependencies
  - Add `paho-mqtt>=1.6.1` for MQTT client functionality
  - Add `PyYAML>=6.0` for YAML configuration parsing
  - _Requirements: 6.2_

- [x] 1.4 Create setup.py for package installation
  - Define package metadata (name, version, description, author)
  - Configure entry point for `meshtastic-send` command
  - Specify Python version requirement (>=3.7)
  - Include package dependencies from requirements.txt
  - _Requirements: 6.5_

- [x] 2. Implement configuration management module
- [x] 2.1 Create Config class with data models
  - Define `MQTTConfig`, `MeshtasticConfig`, and `AppConfig` dataclasses
  - Implement `Config` class with initialization method
  - _Requirements: 2.1, 2.2_

- [x] 2.2 Implement YAML configuration file loading
  - Write `load_from_file()` method to read and parse YAML
  - Handle file not found scenario
  - Handle YAML syntax errors with descriptive messages
  - _Requirements: 2.1, 2.4_

- [x] 2.3 Implement default configuration file creation
  - Write `create_default_config()` method
  - Create config directory if it doesn't exist
  - Write default YAML template with placeholder values
  - Set appropriate file permissions (0600 on Unix-like systems)
  - _Requirements: 2.3_

- [x] 2.4 Implement CLI argument merging and validation
  - Write `merge_with_cli_args()` method to override config with CLI arguments
  - Write `validate()` method to check required fields are present
  - Implement `get()` method for retrieving configuration values
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 2.5 Write unit tests for config module
  - Test YAML parsing with valid configuration
  - Test handling of missing configuration file
  - Test CLI argument override logic
  - Test validation of required fields
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 3. Implement Meshtastic message formatting module
- [x] 3.1 Create message data model and JSON builder
  - Define `MeshtasticMessage` dataclass
  - Implement `build_message_payload()` function to construct JSON payload
  - Ensure JSON structure matches Meshtastic protocol specification
  - _Requirements: 5.1, 5.3, 5.4, 5.5_

- [x] 3.2 Implement MQTT topic string builder
  - Write `build_topic()` function to construct topic from region, channel, and node ID
  - Follow Meshtastic topic pattern: `msh/[region]/2/json/[channel]/[node_id]`
  - _Requirements: 5.2_

- [x] 3.3 Implement message text encoding
  - Write `encode_message_text()` function for proper text encoding
  - Handle special characters and encoding requirements
  - _Requirements: 5.5_

- [x] 3.4 Write unit tests for message module
  - Test JSON payload construction with various inputs
  - Test topic string generation
  - Test message text encoding
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 4. Implement MQTT client module
- [x] 4.1 Create MeshtasticMQTTClient class with connection handling
  - Implement `__init__()` with server, port, username, password parameters
  - Implement `connect()` method using paho-mqtt library
  - Implement connection callbacks (`_on_connect()`)
  - Add connection error handling with descriptive messages
  - _Requirements: 1.5_

- [x] 4.2 Implement message publishing functionality
  - Write `publish()` method to send message to MQTT broker
  - Implement publish callback (`_on_publish()`)
  - Add error handling for publish failures
  - _Requirements: 1.1_

- [x] 4.3 Implement clean disconnect and resource cleanup
  - Write `disconnect()` method for graceful connection closure
  - Ensure proper cleanup of MQTT client resources
  - _Requirements: 1.4_

- [x] 4.4 Write unit tests for MQTT client module
  - Test connection establishment using mock broker
  - Test publish operation
  - Test error handling for connection failures
  - _Requirements: 1.1, 1.4, 1.5_

- [x] 5. Implement command-line interface module
- [x] 5.1 Create argument parser with all CLI options
  - Use argparse to define all command-line arguments
  - Define `--message`, `--server`, `--port`, `--username`, `--password` arguments
  - Define `--from-id`, `--to-id`, `--channel`, `--config` arguments
  - Add help text for each argument
  - _Requirements: 3.1, 3.2, 3.3, 4.2_

- [x] 5.2 Implement input validation logic
  - Write `validate_inputs()` function to check required parameters
  - Validate message text is not empty
  - Validate required MQTT connection parameters are present
  - Display clear error messages for missing parameters
  - _Requirements: 3.5, 4.5_

- [x] 5.3 Implement main orchestration flow
  - Write `main()` function to coordinate all operations
  - Load configuration from file
  - Parse command-line arguments
  - Merge config with CLI overrides
  - Validate inputs
  - Build message and topic
  - Connect to MQTT broker
  - Publish message
  - Display confirmation or error messages
  - Handle all error scenarios with appropriate exit codes
  - _Requirements: 1.1, 1.3, 1.4, 1.5, 3.4_

- [x] 5.4 Implement help documentation display
  - Ensure help flag displays comprehensive usage information
  - Include examples in help output
  - Display config file location in help
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 5.5 Add logging and verbose output support
  - Configure Python logging module
  - Add INFO level logging for connection status and publish confirmation
  - Add optional verbose mode for DEBUG level logging
  - _Requirements: 1.4_

- [x] 6. Create project documentation
- [x] 6.1 Write comprehensive README.md
  - Add project description and features overview
  - Include installation instructions (from source and pip)
  - Document configuration file format and location
  - Provide usage examples with various command-line options
  - Document all CLI arguments
  - Add troubleshooting section
  - Include link to Meshtastic MQTT documentation
  - _Requirements: 6.3_

- [x] 6.2 Create default configuration template file
  - Create `config/default_config.yaml` with example values
  - Include comments explaining each configuration option
  - Provide placeholder values for MQTT server, credentials, and Meshtastic settings
  - _Requirements: 2.2, 2.3_

- [x] 7. Integration testing and validation
- [x] 7.1 Test complete end-to-end flow
  - Test with config file only
  - Test with CLI overrides
  - Test with missing configuration
  - Test error scenarios
  - _Requirements: 1.1, 1.3, 1.4, 1.5, 3.4, 3.5_

- [x] 7.2 Validate against Meshtastic MQTT broker
  - Test connection to mqtt.meshtastic.org
  - Verify message format compliance
  - Test various command-line combinations
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
