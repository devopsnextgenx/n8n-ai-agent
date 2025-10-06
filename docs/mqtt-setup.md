# MQTT Setup Documentation

## Overview
This setup includes Eclipse Mosquitto MQTT broker configured to work with your n8n instance.

## Configuration

### Ports
- **1883**: Standard MQTT port
- **9001**: WebSocket MQTT port (for web-based MQTT clients)

### Connection Details
- **Host**: `mqtt` (from within Docker network) or `localhost` (from host machine)
- **Port**: `1883` (MQTT) or `9001` (WebSocket)
- **Authentication**: Currently disabled for development (anonymous access allowed)

### Volumes
- `./config/mqtt/mosquitto.conf`: Configuration file
- `./data/mqtt-data`: Persistent data storage
- `./data/mqtt-logs`: Log files

## Usage with n8n

In your n8n workflows, you can connect to the MQTT broker using:
- **Host**: `mqtt` (internal Docker network name)
- **Port**: `1883`
- **Username/Password**: Not required (anonymous access enabled)

## Security Considerations

For production use, consider:

1. **Enable Authentication**:
   ```bash
   # Create password file
   docker exec -it mqtt-broker mosquitto_passwd -c /mosquitto/config/passwd username
   ```
   
   Then update `mosquitto.conf`:
   ```
   allow_anonymous false
   password_file /mosquitto/config/passwd
   ```

2. **Enable SSL/TLS**:
   Add SSL certificates and update configuration:
   ```
   listener 8883 0.0.0.0
   protocol mqtt
   cafile /mosquitto/config/ca.crt
   certfile /mosquitto/config/server.crt
   keyfile /mosquitto/config/server.key
   ```

3. **Access Control Lists (ACL)**:
   Create `/config/mqtt/acl` file to control topic access per user.

## Testing the MQTT Broker

1. **Start the services**:
   ```bash
   docker-compose up -d
   ```

2. **Test with mosquitto clients**:
   ```bash
   # Subscribe to a test topic
   docker exec -it mqtt-broker mosquitto_sub -h localhost -t test/topic
   
   # Publish a message (in another terminal)
   docker exec -it mqtt-broker mosquitto_pub -h localhost -t test/topic -m "Hello MQTT!"
   ```

3. **Check logs**:
   ```bash
   docker logs mqtt-broker
   ```

## Troubleshooting

- Check container logs: `docker logs mqtt-broker`
- Verify network connectivity: `docker network ls` and `docker network inspect n8n-ai-agent_n8n-network`
- Test connectivity from n8n container: `docker exec -it n8n ping mqtt`