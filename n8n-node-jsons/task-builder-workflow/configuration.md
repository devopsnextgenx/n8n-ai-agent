# Task Builder Workflow Configuration

## Environment Setup

### Required Services
- **n8n**: Version 1.0+ with LangChain node support
- **Ollama**: Running Qwen2.5 model
- **MCP Server**: Your custom MCP server with tools
- **Redis/Database**: For session management (optional)

### MCP Server Configuration
```yaml
# config.yml for MCP Server
server:
  host: "host.docker.internal"
  port: 6789
  endpoint: "/resources/tools"
  
tools:
  - calculator
  - encrypt_decrypt
  - crypto_price
  - text_generator
  - data_processor
  
logging:
  level: "INFO"
  file: "logs/mcp-server.log"
```

### Ollama Model Setup
```bash
# Pull Qwen2.5 model
ollama pull qwen2.5:latest

# Verify model is available
ollama list
```

### n8n Environment Variables
```env
# Ollama Configuration
OLLAMA_HOST=host.docker.internal
OLLAMA_PORT=11434

# MCP Server Configuration
MCP_SERVER_HOST=host.docker.internal
MCP_SERVER_PORT=6789
MCP_TOOLS_ENDPOINT=/resources/tools

# Workflow Configuration
TASK_BUILDER_MAX_TASKS=20
TASK_BUILDER_MAX_DEPTH=5
TASK_BUILDER_TIMEOUT=120000

# Debug Configuration
DEBUG_MODE=false
LOG_LEVEL=info
```

## Workflow Import Instructions

### Step 1: Import Main Workflow
1. Copy `task-builder-workflow.json` content
2. In n8n, go to **Workflows** > **Import from JSON**
3. Paste the JSON content
4. Click **Import**

### Step 2: Configure Credentials
1. **Ollama API Credential**:
   - Name: `host.docker.internal`
   - Base URL: `http://host.docker.internal:11434`
   - Authentication: None

2. **MCP Server Endpoints**:
   - Task Executor: `http://localhost:5678/mcp-test/task-executor-mcp-endpoint`
   - List Tools: Update reference to existing list-tool-service-trigger

### Step 3: Verify Dependencies
Ensure these workflows exist and are active:
- `list-tool-service-trigger` (ID: aVdyMV0AxIk92VwD)
- Your MCP tool trigger workflows (calculator, encrypt-decrypt, etc.)

### Step 4: Test Configuration
1. Activate the workflow
2. Send test message: "Calculate 5 + 3"
3. Verify response and check execution logs

## Agent Configuration

### Agent 1: Task Planner
```json
{
  "systemMessage": "You are a Task Planning AI Agent...",
  "model": "qwen2.5:latest",
  "temperature": 0.3,
  "maxTokens": 2000,
  "tools": ["listTools"]
}
```

### Agent 2: Task Executor  
```json
{
  "systemMessage": "You are a Task Execution AI Agent...",
  "model": "qwen2.5:latest", 
  "temperature": 0.1,
  "maxTokens": 1500,
  "tools": "all_mcp_tools"
}
```

### Agent 3: Response Synthesis
```json
{
  "systemMessage": "You are a Response Synthesis AI Agent...",
  "model": "qwen2.5:latest",
  "temperature": 0.5,
  "maxTokens": 1000,
  "tools": []
}
```

## MCP Tool Registration

### Required MCP Tools
1. **calculator** - Basic math operations
2. **encrypt_decrypt** - Text encryption/decryption
3. **crypto_price** - Cryptocurrency price lookup
4. **text_generator** - Report and text generation
5. **data_processor** - Data transformation utilities

### Tool Interface Requirements
Each tool must implement:
```json
{
  "name": "tool_name",
  "description": "Tool description",
  "parameters": {
    "type": "object",
    "properties": {
      "param1": {"type": "string", "description": "Parameter description"}
    },
    "required": ["param1"]
  }
}
```

## Monitoring and Logging

### Key Metrics to Track
- **Task Execution Time**: Per task and total workflow
- **Success Rate**: Percentage of successful task completions
- **Dependency Resolution**: Time to resolve dependencies
- **Agent Response Quality**: JSON validation success rate

### Log Configuration
```yaml
logging:
  enabled: true
  level: INFO
  destinations:
    - console
    - file: logs/task-builder.log
  
  categories:
    task_planning: DEBUG
    task_execution: INFO
    dependency_resolution: DEBUG
    response_synthesis: INFO
```

### Monitoring Endpoints
- Health Check: `GET /health`
- Metrics: `GET /metrics`
- Task Status: `GET /tasks/{workflow_id}/status`

## Performance Optimization

### Ollama Model Settings
```json
{
  "temperature": 0.1,
  "top_p": 0.9,
  "repeat_penalty": 1.1,
  "num_ctx": 4096,
  "num_predict": 1000
}
```

### n8n Workflow Settings
```json
{
  "executionOrder": "v1",
  "timezone": "UTC",
  "saveDataErrorExecution": "all",
  "saveDataSuccessExecution": "all",
  "saveManualExecutions": true
}
```

### Memory Management
- **Task Registry**: Limit to 1000 entries
- **Result Cache**: 24-hour TTL
- **Session Cleanup**: Automatic after 1 hour

## Security Configuration

### API Security
```yaml
security:
  authentication:
    enabled: true
    type: "bearer_token"
  
  rate_limiting:
    enabled: true
    requests_per_minute: 100
  
  cors:
    enabled: true
    allowed_origins: ["http://localhost:5678"]
```

### Data Privacy
- **PII Detection**: Automatic redaction
- **Encryption**: At-rest and in-transit
- **Audit Logging**: All task executions logged
- **Data Retention**: 30-day automatic cleanup

## Troubleshooting

### Common Configuration Issues

#### Ollama Connection Failed
```bash
# Check Ollama status
curl http://host.docker.internal:11434/api/tags

# Restart if needed
docker restart ollama
```

#### MCP Server Not Responding
```bash
# Check MCP server logs
tail -f logs/mcp-server.log

# Test endpoint
curl http://host.docker.internal:6789/resources/tools
```

#### Invalid JSON Responses
- Check system message formatting
- Verify model temperature settings
- Review output parser schema

### Debug Mode Activation
1. Set `DEBUG_MODE=true` in environment
2. Enable verbose logging in all agents
3. Monitor task registry state changes
4. Capture all intermediate responses

## Backup and Recovery

### Workflow Backup
```bash
# Export workflow JSON
n8n export:workflow --id=task-builder-workflow --output=backup/

# Export credentials
n8n export:credentials --output=backup/credentials.json
```

### Data Recovery
```bash
# Import workflow
n8n import:workflow --input=backup/task-builder-workflow.json

# Import credentials  
n8n import:credentials --input=backup/credentials.json
```

### Disaster Recovery Plan
1. **Service Failure**: Automatic restart policies
2. **Data Loss**: Daily automated backups
3. **Corruption**: Version-controlled configurations
4. **Scaling**: Horizontal scaling ready