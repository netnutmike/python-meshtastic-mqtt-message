# Meshtastic MQTT CLI

A Python command-line tool for sending messages to Meshtastic devices via MQTT. This tool simplifies the process of sending messages through the Meshtastic MQTT network by handling JSON message construction and protocol compliance automatically.

## Features

- 📝 Simple command-line interface for sending Meshtastic messages
- ⚙️ YAML-based configuration file for storing connection settings
- 🔄 Command-line argument overrides for flexible usage
- 🔒 Secure credential storage in configuration files
- ✅ Automatic message formatting according to Meshtastic protocol
- 📊 Verbose logging mode for debugging
- 🎯 Support for broadcast and direct messages

## Installation

### From Source

1. Clone the repository:
```bash
git clone <repository-url>
cd meshtastic-mqtt-cli
```

2. Install the package:
```bash
pip install -e .
```

This will install the `meshtastic-send` command globally.

### Using pip (Future)

```bash
pip install meshtastic-mqtt-cli
```

## Configuration

### Configuration File Location

The tool uses a YAML configuration file stored at:
- **Linux/macOS**: `~/.config/meshtastic-mqtt-cli/config.yaml`
- **Windows**: `%APPDATA%\meshtastic-mqtt-cli\config.yaml`

### Creating the Configuration File

On first run, if no configuration file exists, the tool will create a default template:

```bash
meshtastic-send --message "test"
```

This will create the configuration file and exit. Edit the file with your MQTT credentials before sending messages.

### Configuration File Format

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

**Configuration Options:**

- `mqtt.server`: MQTT broker address (required)
- `mqtt.port`: MQTT broker port (default: 1883)
- `mqtt.username`: MQTT username for authentication (required)
- `mqtt.password`: MQTT password for authentication (required)
- `meshtastic.from_id`: Your Meshtastic node ID, e.g., `!12345678` (required)
- `meshtastic.to_id`: Recipient node ID or `^all` for broadcast (default: `^all`)
- `meshtastic.channel`: Meshtastic channel name (default: `LongFast`)
- `meshtastic.region`: Meshtastic region code, e.g., `US`, `EU` (default: `US`)

## Usage

### Basic Usage

Send a message using configuration file settings:

```bash
meshtastic-send --message "Hello, Meshtastic!"
```

### Command-Line Arguments

All command-line arguments override values from the configuration file.

**Required Arguments:**
- `--message`, `-m`: Message text to send (required)

**MQTT Connection Arguments:**
- `--server`: MQTT server address
- `--port`: MQTT server port (default: 1883)
- `--username`, `-u`: MQTT username
- `--password`, `-p`: MQTT password

**Meshtastic Arguments:**
- `--from-id`: Sender node ID (e.g., `!12345678`)
- `--to-id`: Recipient node ID (e.g., `^all` for broadcast)
- `--channel`: Meshtastic channel name
- `--region`: Meshtastic region code

**Other Arguments:**
- `--config`: Path to custom configuration file
- `--verbose`, `-v`: Enable verbose (DEBUG level) logging
- `--help`, `-h`: Display help information

### Usage Examples

**Send a message with config file:**
```bash
meshtastic-send --message "Hello, Meshtastic!"
```

**Override MQTT server:**
```bash
meshtastic-send -m "Test message" --server mqtt.example.com
```

**Send a direct message to a specific node:**
```bash
meshtastic-send -m "Direct message" --to-id "!87654321"
```

**Specify all parameters via command line:**
```bash
meshtastic-send -m "Complete example" \
  --server mqtt.meshtastic.org \
  --username meshdev \
  --password large4cats \
  --from-id "!12345678" \
  --to-id "^all" \
  --channel "LongFast" \
  --region "US"
```

**Use a custom configuration file:**
```bash
meshtastic-send -m "Hello" --config /path/to/config.yaml
```

**Enable verbose logging for debugging:**
```bash
meshtastic-send -m "Debug message" --verbose
```

## Troubleshooting

### Configuration File Not Found

**Problem:** `Configuration file not found at ~/.config/meshtastic-mqtt-cli/config.yaml`

**Solution:** Run the tool once to create the default configuration file, then edit it with your credentials:
```bash
meshtastic-send --message "test"
# Edit the created config file
nano ~/.config/meshtastic-mqtt-cli/config.yaml
```

### Connection Failed

**Problem:** `Connection failed: [Errno 111] Connection refused`

**Solution:** 
- Verify the MQTT server address is correct
- Check that the MQTT broker is running and accessible
- Ensure your firewall allows outbound connections on port 1883
- Try using verbose mode to see detailed connection logs: `--verbose`

### Authentication Failed

**Problem:** `Connection failed: Authentication error`

**Solution:**
- Verify your MQTT username and password are correct
- Check that your credentials have permission to publish to Meshtastic topics
- For public Meshtastic MQTT server, use: username=`meshdev`, password=`large4cats`

### Missing Required Parameters

**Problem:** `Missing required configuration parameters: server, username, password`

**Solution:** Either:
1. Add the missing parameters to your configuration file, or
2. Provide them via command-line arguments:
```bash
meshtastic-send -m "test" --server mqtt.meshtastic.org --username meshdev --password large4cats
```

### Invalid Node ID Format

**Problem:** Messages not appearing on Meshtastic devices

**Solution:**
- Ensure your `from_id` starts with `!` followed by 8 hexadecimal characters (e.g., `!12345678`)
- For broadcast messages, use `^all` as the `to_id`
- For direct messages, use the recipient's node ID (e.g., `!87654321`)

### Permission Denied on Config File

**Problem:** `Permission denied` when creating or reading config file

**Solution:**
- Ensure you have write permissions to the configuration directory
- On Linux/macOS, the config file should have permissions `0600` for security
- Try creating the directory manually: `mkdir -p ~/.config/meshtastic-mqtt-cli`

## Meshtastic MQTT Protocol

This tool follows the Meshtastic MQTT integration protocol. For more information about the protocol, message formats, and MQTT topics, see the official documentation:

**[Meshtastic MQTT Documentation](https://meshtastic.org/docs/software/integrations/mqtt/)**

### Message Format

Messages are published to topics following the pattern:
```
msh/[region]/2/json/[channel]/[node_id]
```

The JSON payload structure follows the Meshtastic protocol specification.

## Requirements

- Python 3.7 or higher
- `paho-mqtt>=1.6.1`
- `PyYAML>=6.0`

## Security Considerations

- Configuration files containing credentials should have restricted permissions (0600 on Unix-like systems)
- Avoid passing passwords via command-line arguments in shared environments (they appear in process lists)
- Use the configuration file for storing credentials instead
- The `.gitignore` file excludes configuration files to prevent accidental credential commits

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

## Support

For issues, questions, or contributions, please [open an issue](link-to-issues) on the project repository.
