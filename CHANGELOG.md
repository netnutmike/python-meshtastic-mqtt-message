# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-01-XX

### Added
- Initial release of Meshtastic MQTT CLI
- Send messages to Meshtastic devices via MQTT
- Configuration file support (YAML)
- CLI argument overrides for all configuration options
- Support for broadcast and direct messages
- Separate channel name (for MQTT topic) and channel number (for message payload)
- Message format compliance with Meshtastic protocol
- Comprehensive test suite with unit, integration, and validation tests
- GPL v3 license
- Renovate configuration for automated dependency updates

### Features
- MQTT connection to mqtt.meshtastic.org or custom brokers
- Configurable node IDs, channels, and regions
- Message validation and error handling
- Verbose logging support
- Default configuration file creation
- Cross-platform support (Linux, macOS, Windows)

[Unreleased]: https://github.com/yourusername/meshtastic-mqtt-cli/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/meshtastic-mqtt-cli/releases/tag/v0.1.0
