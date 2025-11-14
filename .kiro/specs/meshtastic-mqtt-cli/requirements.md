# Requirements Document

## Introduction

This document specifies the requirements for a Python command-line tool that enables users to send JSON messages to a Meshtastic MQTT server. The tool provides configuration management through YAML files and command-line argument overrides, following the Meshtastic MQTT integration protocol as documented at https://meshtastic.org/docs/software/integrations/mqtt/.

## Glossary

- **CLI Tool**: The command-line interface application being developed
- **MQTT Server**: A message broker that implements the MQTT protocol for publish/subscribe messaging
- **Meshtastic**: A mesh networking platform that supports MQTT integration
- **YAML Config File**: A YAML-formatted configuration file containing default connection and message parameters
- **JSON Message**: A structured message payload formatted as JSON to be published to the MQTT server (constructed internally by the CLI Tool)
- **Command-Line Override**: A parameter provided via command-line arguments that supersedes the corresponding YAML config value

## Requirements

### Requirement 1

**User Story:** As a user, I want to send a message to a Meshtastic MQTT server using simple command-line options, so that I can integrate Meshtastic messaging into my scripts without needing to understand JSON formatting or the Meshtastic protocol.

#### Acceptance Criteria

1. WHEN the user executes the CLI Tool with message content via command-line argument, THE CLI Tool SHALL construct a properly formatted JSON message according to the Meshtastic protocol
2. THE CLI Tool SHALL accept message text as a simple string parameter without requiring the user to format JSON
3. WHEN the message is successfully published, THE CLI Tool SHALL display a confirmation message and terminate with exit code zero
4. IF the MQTT connection fails, THEN THE CLI Tool SHALL display an error message with connection details and terminate with a non-zero exit code
5. THE CLI Tool SHALL handle all JSON message construction internally without exposing JSON formatting to the user

### Requirement 2

**User Story:** As a user, I want to store my MQTT connection settings in a YAML configuration file, so that I don't have to specify them every time I run the tool.

#### Acceptance Criteria

1. THE CLI Tool SHALL read configuration parameters from a YAML Config File located in a standard configuration directory
2. THE YAML Config File SHALL contain fields for MQTT Server address, username, password, from identifier, to identifier, and channel identifier
3. WHEN the YAML Config File does not exist, THE CLI Tool SHALL create a default configuration file with placeholder values
4. WHEN the YAML Config File contains invalid YAML syntax, THE CLI Tool SHALL display an error message indicating the syntax error location and terminate with a non-zero exit code
5. THE CLI Tool SHALL validate that required configuration fields (MQTT Server address, username, password) are present in the YAML Config File

### Requirement 3

**User Story:** As a user, I want to override configuration file settings with command-line arguments, so that I can use different settings for specific invocations without modifying the config file.

#### Acceptance Criteria

1. WHEN the user provides an MQTT Server address via command-line argument, THE CLI Tool SHALL use that address instead of the YAML Config File value
2. WHEN the user provides username or password via command-line argument, THE CLI Tool SHALL use those credentials instead of the YAML Config File values
3. WHEN the user provides from, to, or channel identifiers via command-line argument, THE CLI Tool SHALL use those values instead of the YAML Config File values
4. THE CLI Tool SHALL apply command-line overrides after loading the YAML Config File values
5. WHEN both YAML Config File and command-line arguments are absent for a required parameter, THE CLI Tool SHALL display an error message listing the missing parameters and terminate with a non-zero exit code

### Requirement 4

**User Story:** As a user, I want clear help documentation for the command-line tool, so that I can understand how to use it without referring to external documentation.

#### Acceptance Criteria

1. WHEN the user executes the CLI Tool with a help flag, THE CLI Tool SHALL display usage information including all available command-line arguments
2. THE CLI Tool SHALL display descriptions for each command-line argument in the help output
3. THE CLI Tool SHALL display the location of the YAML Config File in the help output
4. THE CLI Tool SHALL display example usage commands in the help output
5. WHEN the user executes the CLI Tool without required arguments, THE CLI Tool SHALL display a brief usage message and terminate with a non-zero exit code

### Requirement 5

**User Story:** As a user, I want the tool to follow the Meshtastic MQTT message format, so that my messages are correctly processed by Meshtastic devices.

#### Acceptance Criteria

1. THE CLI Tool SHALL format messages according to the Meshtastic MQTT protocol specification
2. THE CLI Tool SHALL publish messages to the correct MQTT topic structure as defined by Meshtastic
3. THE CLI Tool SHALL include required Meshtastic message fields in the JSON payload
4. WHEN optional Meshtastic fields are not provided, THE CLI Tool SHALL use appropriate default values as specified in the Meshtastic documentation
5. THE CLI Tool SHALL encode message payloads in the format expected by Meshtastic MQTT subscribers

### Requirement 6

**User Story:** As a developer, I want the project to have proper repository setup with version control and dependency management, so that the tool can be easily maintained and distributed.

#### Acceptance Criteria

1. THE project SHALL include a .gitignore file that excludes Python cache files, virtual environments, and sensitive configuration files
2. THE project SHALL include a requirements.txt file listing all Python package dependencies with version specifications
3. THE project SHALL include a README.md file with installation instructions, usage examples, and configuration documentation
4. THE project SHALL use a standard Python project structure with appropriate directories for source code and configuration
5. THE project SHALL include a setup.py or pyproject.toml file for package installation and distribution
