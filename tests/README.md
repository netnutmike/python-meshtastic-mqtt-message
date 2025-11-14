# Meshtastic MQTT CLI - Test Suite

This directory contains comprehensive tests for the Meshtastic MQTT CLI tool.

## Test Files

### Unit Tests

- **test_config.py** - Tests for configuration management module
  - YAML file loading and parsing
  - CLI argument merging
  - Configuration validation
  - Default config creation

- **test_message.py** - Tests for message formatting module
  - JSON payload construction
  - MQTT topic generation
  - Node ID parsing
  - Message text encoding

- **test_mqtt_client.py** - Tests for MQTT client module
  - Connection handling
  - Message publishing
  - Error handling
  - Clean disconnection

### Integration Tests

- **test_integration.py** - End-to-end flow tests
  - Config file only scenarios
  - CLI override scenarios
  - Missing configuration handling
  - Error scenarios (connection, publish, validation)
  - Empty message validation

### Validation Tests

- **test_meshtastic_validation.py** - Meshtastic broker validation
  - Connection to mqtt.meshtastic.org
  - Message format compliance
  - Topic format compliance
  - Live publish tests (disabled by default)

- **manual_validation.py** - Interactive validation script
  - Manual testing helper
  - Connection verification
  - Format compliance checks
  - Example CLI commands

## Running Tests

### Run All Tests
```bash
python -m unittest discover tests -v
```

### Run Specific Test File
```bash
python -m unittest tests.test_integration -v
```

### Run Manual Validation
```bash
python tests/manual_validation.py
```

### Run Live Tests (publishes to actual broker)
```bash
SKIP_LIVE_TESTS=false python -m unittest tests.test_meshtastic_validation -v
```

## Test Coverage

The test suite covers:

- ✓ Configuration loading and validation (Requirements 2.1-2.5)
- ✓ CLI argument parsing and merging (Requirements 3.1-3.5)
- ✓ MQTT connection handling (Requirements 1.4, 1.5)
- ✓ Message publishing (Requirements 1.1, 1.3)
- ✓ Meshtastic protocol compliance (Requirements 5.1-5.5)
- ✓ Error handling and validation (Requirements 3.5, 4.5)
- ✓ End-to-end workflows (Requirements 1.1, 1.3, 1.4, 1.5, 3.4, 3.5)

## Test Results

**Total Tests:** 60  
**Passed:** 55  
**Skipped:** 5 (live publish tests)  
**Failed:** 0  

All core functionality is tested and validated against the Meshtastic MQTT protocol specification.

## Notes

- Live publish tests are disabled by default to avoid spamming the Meshtastic network
- The test suite uses mocking for most MQTT operations to avoid network dependencies
- Validation tests connect to the actual broker but only publish when explicitly enabled
- All tests follow the requirements specified in the design document
