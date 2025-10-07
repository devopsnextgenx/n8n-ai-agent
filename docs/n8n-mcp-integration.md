# N8N MCP Server Integration Guide

This guide shows how to integrate the N8N MCP Server with n8n workflows using HTTP endpoints.

## 🚀 Quick Start

### 1. Start the MCP Server

```bash
cd mcp-server
export PATH="$PATH:/c/Users/trzxs9/.local/bin"  # Windows with bash
uv run mcp-dev  # Development mode with HTTP endpoints
```

The server will start on `http://localhost:9000` (dev mode uses port+1000)

### 2. Available Endpoints for n8n

#### **Base URL**: `http://localhost:9000`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Server info and available endpoints |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API documentation |
| `/mcp/tools` | GET | List all available MCP tools |
| `/mcp/execute` | POST | Execute any MCP tool by name |
| `/mcp/base64/encode` | POST | Encode data to Base64 |
| `/mcp/base64/decode` | POST | Decode Base64 data |
| `/mcp/base64/validate` | POST | Validate Base64 format |

## 📋 N8N Workflow Examples

### Example 1: Base64 Encoding Workflow

**Use Case**: Encode user input to Base64 format

1. **Add HTTP Request Node**:
   - Method: `POST`
   - URL: `http://localhost:9000/mcp/base64/encode`
   - Headers: `Content-Type: application/json`
   - Body:
     ```json
     {
       "data": "{{ $json.input_text }}"
     }
     ```

2. **Expected Response**:
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

### Example 2: Base64 Decoding Workflow

**Use Case**: Decode Base64 data back to original text

1. **Add HTTP Request Node**:
   - Method: `POST`
   - URL: `http://localhost:9000/mcp/base64/decode`
   - Headers: `Content-Type: application/json`
   - Body:
     ```json
     {
       "encoded": "{{ $json.base64_data }}"
     }
     ```

2. **Expected Response**:
   ```json
   {
     "success": true,
     "data": {
       "encoded": "SGVsbG8gV29ybGQ=",
       "decoded": "Hello World"
     },
     "tool": "base64_decode"
   }
   ```

### Example 3: Generic Tool Execution

**Use Case**: Execute any MCP tool dynamically

1. **Add HTTP Request Node**:
   - Method: `POST`
   - URL: `http://localhost:9000/mcp/execute`
   - Headers: `Content-Type: application/json`
   - Body:
     ```json
     {
       "tool_name": "encrypt",
       "parameters": {
         "data": "{{ $json.text_to_encode }}"
       }
     }
     ```

### Example 4: Complete Base64 Processing Workflow

```json
{
  "name": "Base64 Processing Pipeline",
  "nodes": [
    {
      "parameters": {
        "method": "POST",
        "url": "http://localhost:9000/mcp/base64/encode",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "data",
              "value": "={{ $json.original_text }}"
            }
          ]
        }
      },
      "name": "Encode to Base64",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [500, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://localhost:9000/mcp/base64/validate",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "data",
              "value": "={{ $json.data.encoded }}"
            }
          ]
        }
      },
      "name": "Validate Base64",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [700, 300]
    }
  ],
  "connections": {
    "Encode to Base64": {
      "main": [
        [
          {
            "node": "Validate Base64",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

## 🔧 Advanced Integration

### Error Handling in N8N

Add error handling to your HTTP Request nodes:

1. **Enable "Continue on Fail"** in HTTP Request node settings
2. **Add IF node** to check response success:
   ```javascript
   // Expression in IF node
   {{ $json.success === true }}
   ```

3. **Handle errors appropriately**:
   ```javascript
   // Access error message
   {{ $json.error }}
   ```

### Dynamic Tool Discovery

**Use Case**: Dynamically list and execute available tools

1. **List Available Tools**:
   - URL: `http://localhost:9000/mcp/tools`
   - Method: `GET`

2. **Response Structure**:
   ```json
   [
     {
       "name": "encrypt",
       "description": "Encode data to Base64 format",
       "parameters": {
         "data": {
           "type": "str",
           "required": true,
           "default": null
         }
       }
     }
   ]
   ```

### Authentication (Optional)

If you add authentication to your MCP server:

1. **Add API Key Header**:
   ```json
   {
     "Authorization": "Bearer {{ $json.api_key }}",
     "Content-Type": "application/json"
   }
   ```

## 🔍 Testing Your Integration

### 1. Test Server Availability

**HTTP Request Node**:
- URL: `http://localhost:9000/health`
- Method: `GET`

**Expected Response**:
```json
{
  "status": "healthy",
  "tools_available": 3,
  "service": "n8n-mcp-server"
}
```

### 2. Test Tool Listing

**HTTP Request Node**:
- URL: `http://localhost:9000/mcp/tools`
- Method: `GET`

### 3. Test Tool Execution

**HTTP Request Node**:
- URL: `http://localhost:9000/mcp/base64/encode`
- Method: `POST`
- Body: `{"data": "test"}`

## 🚨 Troubleshooting

### Common Issues

1. **Connection Refused**:
   - Ensure MCP server is running: `uv run mcp-dev`
   - Check correct port (9000 for dev mode)

2. **Tool Not Found**:
   - Verify tool name with `/mcp/tools` endpoint
   - Check tool registration in server logs

3. **Invalid Parameters**:
   - Check tool parameter requirements at `/mcp/tools`
   - Validate JSON body format

### Server Logs

Monitor server logs for debugging:
```bash
# In terminal where server is running
# Logs will show incoming requests and tool executions
```

## 📝 API Documentation

Access interactive API documentation at:
- **Swagger UI**: `http://localhost:9000/docs`
- **ReDoc**: `http://localhost:9000/redoc`

## 🔗 Integration Patterns

### Pattern 1: Data Transformation Pipeline
```
Input → MCP Tool → Transform → Output
```

### Pattern 2: Validation Chain
```
Input → Validate → Process → Verify → Output
```

### Pattern 3: Multi-Tool Workflow
```
Input → Tool A → Tool B → Tool C → Output
```

## ⚡ Performance Tips

1. **Reuse Connections**: Use n8n's connection pooling
2. **Batch Operations**: Group multiple operations when possible
3. **Error Handling**: Always handle MCP server errors gracefully
4. **Monitoring**: Monitor server health regularly

## 🔧 Custom Tool Integration

To add your own tools:

1. **Create Tool File**: Add to `n8n_mcp_server/tools/`
2. **Register Tool**: Update `tools/__init__.py`
3. **Restart Server**: Tools auto-register on startup
4. **Test**: Use `/mcp/tools` to verify registration

Your custom tools will automatically be available via HTTP endpoints!