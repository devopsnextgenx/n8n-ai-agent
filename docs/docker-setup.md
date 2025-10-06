### connect docker container to localhost
```bash
 ip route | grep docker0 

 # Get IP and use it in container app for connection

```

## Data Persistence

### n8n Data Storage
n8n configuration and data are stored in a mounted folder:
- **Host path**: `./n8n-data`
- **Container path**: `/home/node/.n8n`

This includes:
- Workflows
- Credentials (encrypted)
- Settings
- User data
- Custom nodes

### Backup and Migration
To backup your n8n data, simply copy the `./n8n-data` directory.
To migrate to a new instance, copy the entire `./n8n-data` folder to the new location.