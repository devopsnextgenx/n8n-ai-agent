# Troubleshooting Task Planner Agent Output Parser Issues

## Problem
The Task Planner Agent fails with error: "Model output doesn't fit required format" when using the structured output parser.

## Root Causes
1. **LLM Output Format**: The model may be producing extra text, explanations, or malformed JSON
2. **Schema Strictness**: The JSON schema may be too restrictive
3. **Model Configuration**: Temperature/parameters may cause inconsistent output
4. **Tool Integration**: MCP tool responses may interfere with JSON formatting

## Solutions Applied

### 1. Simplified System Message
Updated the Task Planner Agent system message to be more explicit:
- Removed complex instructions
- Added clear JSON format example
- Emphasized "JSON ONLY" output
- Simplified dependency handling

### 2. Relaxed JSON Schema
Modified the output parser schema:
- Removed `$schema` reference
- Made `dependencies` field optional with default `[]`
- Added `additionalProperties: true` for `task_input`
- Simplified required field validation

### 3. Model Configuration
Updated Qwen2.5 model settings:
- Set `temperature: 0.1` for more deterministic output
- Added `format: "json"` option to force JSON mode
- Reduced randomness in responses

### 4. Connection Fix
Fixed the tool connection:
- Connected "List Available Tools" to Task Planner Agent
- Ensured MCP Client is properly connected

## Testing Steps

### Step 1: Test Without Output Parser
1. Import `task-planner-test.json`
2. Test with simple message: "Calculate 5 + 3"
3. Check raw output format
4. Verify JSON structure manually

### Step 2: Validate JSON Schema
```javascript
// Test your agent output against this schema
{
  "tasks": [
    {
      "tool": "calculator",
      "task_description": "Add two numbers",
      "task_input": {
        "a": 5,
        "b": 3,
        "operation": "add"
      },
      "dependencies": [],
      "task_id": "task_1"
    }
  ]
}
```

### Step 3: Progressive Testing
1. Start with simple single-task requests
2. Test dependency-free tasks only
3. Gradually add complexity

## Alternative Solutions

### Option 1: Remove Output Parser Temporarily
```json
{
  "parameters": {
    "hasOutputParser": false,
    // Remove output parser entirely for testing
  }
}
```

### Option 2: Use Code Node for JSON Parsing
Replace structured output parser with custom JavaScript parsing:

```javascript
// Add after Task Planner Agent
const agentOutput = $input.item.json.output;

try {
  // Try to extract JSON from response
  let jsonStr = agentOutput;
  
  // Remove any markdown formatting
  jsonStr = jsonStr.replace(/```json\n?/g, '').replace(/```\n?/g, '');
  
  // Find JSON object in text
  const jsonMatch = jsonStr.match(/\{[\s\S]*\}/);
  if (jsonMatch) {
    const parsed = JSON.parse(jsonMatch[0]);
    return { output: parsed };
  } else {
    throw new Error('No JSON found in response');
  }
} catch (error) {
  return { 
    error: 'Failed to parse JSON', 
    rawOutput: agentOutput,
    details: error.message 
  };
}
```

### Option 3: Chain Prompting
Split the task into two steps:
1. First prompt: Get available tools and understand request
2. Second prompt: Generate the JSON task list

## Debugging Commands

### Check MCP Server Response
```bash
curl -X GET "http://host.docker.internal:6789/mcp" \
  -H "Content-Type: application/json"
```

### Test Ollama Model
```bash
curl -X POST "http://host.docker.internal:11434/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5:latest",
    "prompt": "Generate a JSON object with tasks array",
    "format": "json",
    "options": {
      "temperature": 0.1
    }
  }'
```

### Validate JSON Schema
Use an online JSON schema validator to test your output format.

## Common Issues and Fixes

### Issue 1: Extra Text in Output
**Symptoms**: Output contains explanations before/after JSON
**Fix**: Update system message to emphasize JSON-only response

### Issue 2: Missing Required Fields
**Symptoms**: Schema validation fails on missing properties
**Fix**: Make fields optional or provide defaults in schema

### Issue 3: Inconsistent Task IDs
**Symptoms**: Task IDs don't match expected format
**Fix**: Provide clear examples in system message

### Issue 4: Tool Names Don't Match
**Symptoms**: Agent uses tool names not available in MCP
**Fix**: Ensure MCP client is properly connected and functional

## Recommended Approach

1. **Start Simple**: Use the test workflow without output parser
2. **Verify Raw Output**: Check what the model actually produces
3. **Fix Gradually**: Add output parser once raw output is correct
4. **Monitor Logs**: Enable detailed logging to see intermediate steps

## Final Configuration

If the above solutions don't work, consider this minimal configuration:

```json
{
  "systemMessage": "Generate JSON with tasks array. Example: {\"tasks\":[{\"tool\":\"calculator\",\"task_description\":\"add numbers\",\"task_input\":{\"a\":5,\"b\":3,\"operation\":\"add\"},\"dependencies\":[],\"task_id\":\"task_1\"}]}",
  "hasOutputParser": false,
  "temperature": 0.1
}
```

Then use a Code node to parse and validate the JSON manually.