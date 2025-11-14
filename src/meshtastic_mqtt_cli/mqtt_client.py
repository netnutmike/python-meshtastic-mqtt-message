"""MQTT client module for Meshtastic MQTT CLI."""

import logging
import paho.mqtt.client as mqtt


logger = logging.getLogger(__name__)


class MeshtasticMQTTClient:
    """MQTT client for publishing messages to Meshtastic MQTT broker."""
    
    def __init__(self, server, port, username, password):
        """
        Initialize the MQTT client.
        
        Args:
            server: MQTT broker server address
            port: MQTT broker port
            username: MQTT username for authentication
            password: MQTT password for authentication
        """
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.client = None
        self.connected = False
        self.connection_error = None
        
    def _on_connect(self, client, userdata, flags, rc):
        """
        Callback for when the client receives a CONNECT response from the server.
        
        Args:
            client: The client instance
            userdata: User data of any type
            flags: Response flags sent by the broker
            rc: Connection result code
        """
        if rc == 0:
            self.connected = True
            logger.info(f"Successfully connected to MQTT broker at {self.server}:{self.port}")
        else:
            self.connected = False
            error_messages = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorized"
            }
            error_msg = error_messages.get(rc, f"Connection refused - unknown error code {rc}")
            self.connection_error = error_msg
            logger.error(f"Failed to connect to MQTT broker: {error_msg}")
    
    def connect(self):
        """
        Establish connection to the MQTT broker.
        
        Raises:
            ConnectionError: If connection to the broker fails
        """
        try:
            self.client = mqtt.Client()
            self.client.on_connect = self._on_connect
            
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            logger.debug(f"Attempting to connect to {self.server}:{self.port}")
            self.client.connect(self.server, self.port, keepalive=60)
            
            # Start the network loop to process callbacks
            self.client.loop_start()
            
            # Wait for connection to be established (with timeout)
            import time
            timeout = 10
            elapsed = 0
            while not self.connected and self.connection_error is None and elapsed < timeout:
                time.sleep(0.1)
                elapsed += 0.1
            
            if not self.connected:
                error_msg = self.connection_error or f"Connection timeout after {timeout} seconds"
                raise ConnectionError(f"Failed to connect to MQTT broker at {self.server}:{self.port} - {error_msg}")
                
        except Exception as e:
            if isinstance(e, ConnectionError):
                raise
            raise ConnectionError(f"Failed to connect to MQTT broker at {self.server}:{self.port} - {str(e)}")
    
    def _on_publish(self, client, userdata, mid):
        """
        Callback for when a message is successfully published.
        
        Args:
            client: The client instance
            userdata: User data of any type
            mid: Message ID of the published message
        """
        logger.debug(f"Message published successfully (mid: {mid})")
    
    def publish(self, topic, payload):
        """
        Publish a message to the MQTT broker.
        
        Args:
            topic: MQTT topic to publish to
            payload: Message payload (string or bytes)
            
        Raises:
            RuntimeError: If not connected to broker
            Exception: If publish operation fails
        """
        if not self.connected or self.client is None:
            raise RuntimeError("Not connected to MQTT broker. Call connect() first.")
        
        try:
            self.client.on_publish = self._on_publish
            
            logger.debug(f"Publishing message to topic: {topic}")
            result = self.client.publish(topic, payload, qos=1)
            
            # Wait for publish to complete
            result.wait_for_publish()
            
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                raise Exception(f"Publish failed with error code: {result.rc}")
            
            logger.info(f"Message published successfully to {topic}")
            
        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            raise Exception(f"Failed to publish message to {topic} - {str(e)}")
    
    def disconnect(self):
        """
        Disconnect from the MQTT broker and clean up resources.
        """
        if self.client is not None:
            try:
                logger.debug("Disconnecting from MQTT broker")
                self.client.loop_stop()
                self.client.disconnect()
                self.connected = False
                logger.info("Disconnected from MQTT broker")
            except Exception as e:
                logger.warning(f"Error during disconnect: {str(e)}")
            finally:
                self.client = None
