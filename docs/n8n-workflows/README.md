# N8N Workflow Examples for MCP Server Integration

This directory contains ready-to-use n8n workflow examples that demonstrate how to integrate with the N8N MCP Server.

## 📁 Available Workflows

### 1. `base64-encoder.json`
**Simple Base64 Encoding Workflow**

- **Purpose**: Encode text input to Base64 format
- **Trigger**: Webhook (`POST /encode-webhook`)
- **Input**: `{"text": "Hello World"}`
- **Output**: 
  ```json
  {
    "success": true,
    "data": {
      "original": "Hello World",
      "encoded": "SGVsbG8gV29ybGQ="
    },
    "tool": "base64_encode"
  }
  ```

### 2. `base64-decoder.json`
**Base64 Decoding with Error Handling**

- **Purpose**: Decode Base64 data with proper error handling
- **Trigger**: Webhook (`POST /decode-webhook`)
- **Input**: `{"encoded_data": "SGVsbG8gV29ybGQ="}`
- **Features**: 
  - Success/error branching
  - Proper HTTP status codes
  - Error message handling

### 3. `base64-pipeline.json`
**Complete Base64 Processing Pipeline**

- **Purpose**: Full encode → validate → decode round-trip test
- **Trigger**: Webhook (`POST /base64-pipeline`)
- **Input**: `{"text": "Hello World"}`
- **Process Flow**:
  1. Encode input text to Base64
  2. Validate the encoded result
  3. Decode back to original text
  4. Verify round-trip success
- **Output**: Complete processing report

## 🚀 How to Import Workflows

### Method 1: Copy-Paste Import
1. Open n8n interface
2. Click **"+ Add workflow"**
3. Click **"Import from JSON"**
4. Copy the content from any `.json` file
5. Paste and click **"Import"**

### Method 2: File Upload
1. Download the `.json` file to your computer
2. In n8n, click **"Import from file"**
3. Select the downloaded workflow file

## ⚙️ Configuration Required

Before using these workflows:

### 1. Start MCP Server
```bash
cd mcp-server
export PATH="$PATH:/c/Users/trzxs9/.local/bin"
uv run mcp-dev
```

### 2. Verify Server URL
Ensure the HTTP Request nodes point to the correct URL:
- **Development**: `http://localhost:9000`
- **Production**: `http://localhost:8000`

### 3. Test Server Connectivity
```bash
curl http://localhost:9000/health
```

## 🧪 Testing the Workflows

### Test Base64 Encoder
```bash
curl -X POST http://your-n8n-instance/webhook/encode-webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World"}'
```

### Test Base64 Decoder
```bash
curl -X POST http://your-n8n-instance/webhook/decode-webhook \
  -H "Content-Type: application/json" \
  -d '{"encoded_data": "SGVsbG8gV29ybGQ="}'
```

### Test Complete Pipeline
```bash
curl -X POST http://your-n8n-instance/webhook/base64-pipeline \
  -H "Content-Type: application/json" \
  -d '{"text": "Testing the complete pipeline"}'
```

## 🔧 Customization Tips

### Modify MCP Server URL
Update the HTTP Request node URLs if your MCP server runs on a different port:
```json
{
  "url": "http://localhost:YOUR_PORT/mcp/base64/encode"
}
```

### Add Authentication
If you secure your MCP server, add headers to HTTP Request nodes:
```json
{
  "headerParameters": {
    "parameters": [
      {
        "name": "Authorization",
        "value": "Bearer YOUR_API_KEY"
      }
    ]
  }
}
```

### Error Handling Enhancement
Add more sophisticated error handling:
```javascript
// In IF node condition
{{ $json.success === true && $json.data !== null }}
```

## 📊 Workflow Monitoring

### Enable Execution Logging
1. Go to **Settings** → **Log Level**
2. Set to **"debug"** for detailed logs
3. Monitor executions in **"Executions"** tab

### Common Issues
1. **Connection Refused**: MCP server not running
2. **404 Errors**: Check endpoint URLs
3. **JSON Parse Errors**: Verify request body format

## 🔄 Advanced Workflows

### Multi-Tool Workflow Template
```json
{
  "nodes": [
    {
      "name": "List Available Tools",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:9000/mcp/tools",
        "method": "GET"
      }
    },
    {
      "name": "Execute Dynamic Tool",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:9000/mcp/execute",
        "method": "POST",
        "body": {
          "tool_name": "{{ $json.selected_tool }}",
          "parameters": "{{ $json.tool_params }}"
        }
      }
    }
  ]
}
```

## 📈 Performance Optimization

### Connection Reuse
Enable connection pooling in HTTP Request nodes:
```json
{
  "options": {
    "timeout": 30000,
    "followRedirect": true,
    "followAllRedirects": true
  }
}
```

### Batch Processing
For multiple items, use the **"Execute Once for All Items"** option in HTTP Request nodes.

## 🏷️ Workflow Tags

All workflows include these tags for easy organization:
- **MCP**: Model Context Protocol related
- **Base64**: Base64 encoding/decoding
- **Pipeline**: Multi-step processing

## 📝 Creating Your Own Workflows

### Template Structure
```json
{
  "name": "Your MCP Workflow",
  "nodes": [
    {
      "name": "Trigger",
      "type": "n8n-nodes-base.webhook"
    },
    {
      "name": "MCP Tool Call",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:9000/mcp/YOUR_ENDPOINT",
        "method": "POST"
      }
    },
    {
      "name": "Response",
      "type": "n8n-nodes-base.respondToWebhook"
    }
  ]
}
```

## 🆘 Support

For issues with these workflows:
1. Check MCP server logs
2. Verify n8n execution logs
3. Test MCP endpoints directly with curl
4. Review the integration documentation in `../n8n-mcp-integration.md`