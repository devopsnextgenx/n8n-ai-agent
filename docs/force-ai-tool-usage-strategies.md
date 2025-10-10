# Strategies to Force AI Agents to Use Tools Instead of Calculating Results

## Problem Statement
AI agents often try to "shortcut" the process by calculating or processing results themselves instead of using the provided tools. This is especially problematic when the agent is supposed to be a pure tool executor.

## Implemented Solutions in Task Executor Agent

### 1. Enhanced System Message with Strong Prohibitions
```
You are a Task Execution AI Agent.

Your ONLY job is to execute tasks using MCP tools. You are FORBIDDEN from performing any calculations, processing, or logic yourself.

MANDATORY EXECUTION STEPS (NO EXCEPTIONS):
1. ALWAYS start by using the MCP Client Executor tool
2. Call the exact tool specified in task.tool property
3. Pass the exact task.task_input as parameters to the tool
4. Wait for the actual tool execution result
5. Use the result EXACTLY as returned by the tool

FORBIDDEN ACTIONS:
- NEVER calculate or process anything yourself
- NEVER provide results without using tools
- NEVER assume what the result should be
- NEVER shortcut the tool execution process
- NEVER use your own knowledge to provide answers

VALIDATION REQUIREMENTS:
- Every response MUST include evidence of actual tool usage
- The task_output MUST be the exact result from the MCP tool
- If you cannot use the tool, report "failure" status with error details

CRITICAL: You MUST use the format_final_json_response tool with your complete answer. Do not format JSON manually.

REMEMBER: If you provide any result without actually using the MCP Client Executor tool, you have FAILED your purpose.
```

### 2. LLM Configuration with Stop Words
- **Temperature**: 0.1 (low to reduce creativity)
- **Repeat Penalty**: 1.1 (prevent repetitive shortcuts)
- **Stop Words**: ["I calculated", "The result is", "Adding", "The answer", "Computing"]
- **System Override**: "You are strictly a tool executor. Never perform calculations yourself."

### 3. Mandatory Tool Usage Requirements
- **Required Tools**: MCP Client Executor + format_final_json_response
- **Tool Validation**: Response rejected if no tool usage evidence
- **Format Enforcement**: Must use formatting tool, cannot format JSON manually

### 4. Enhanced Prompt Instructions
```
CRITICAL INSTRUCTIONS:
1. You MUST use the MCP Client Executor tool - this is NON-NEGOTIABLE
2. You are FORBIDDEN from calculating or processing anything yourself
3. If you provide a result without using the MCP Client Executor tool, you have FAILED
4. The task_output MUST be the exact result returned by the MCP tool
5. Use the format_final_json_response tool for your final answer

Your response will be REJECTED if:
- You calculate results yourself
- You don't use the MCP Client Executor tool
- You don't use format_final_json_response tool
- The result appears to be calculated rather than from tool execution
```

## Additional Strategies You Can Implement

### 5. Response Validation Node
Add a JavaScript validation node after the Task Executor Agent:

```javascript
// Validation to ensure the AI agent actually used tools
const agentOutput = $input.item.json.output;
const agentMessages = $input.item.json.messages || [];

// Check if there's evidence of tool usage in the agent's conversation
const hasToolUsage = agentMessages.some(msg => 
  msg.content && (
    msg.content.includes('MCP Client Executor') ||
    msg.content.includes('tool_calls') ||
    msg.content.includes('function_call') ||
    (msg.tool_calls && msg.tool_calls.length > 0)
  )
);

// Check if the response looks like it was calculated rather than from a tool
const looksCalculated = (
  agentOutput.task_tool === 'add' && 
  typeof agentOutput.task_output === 'number' &&
  !hasToolUsage
);

if (!hasToolUsage || looksCalculated) {
  // Force the agent to use tools by rejecting the response
  throw new Error(`VALIDATION FAILED: Agent did not use MCP tools. Tool usage evidence: ${hasToolUsage}. Task: ${agentOutput.task_tool}. Response appears calculated: ${looksCalculated}. Agent must actually execute MCP tools, not calculate results.`);
}

return agentOutput;
```

### 6. Retry Mechanism with Tool Enforcement
```javascript
// Check if response was calculated vs from tool
if (agentOutput.task_tool === 'add') {
  const taskInput = agentOutput.task_input;
  const expectedSum = taskInput.a + taskInput.b;
  
  // If the output exactly matches what we'd calculate, it's suspicious
  if (agentOutput.task_output === expectedSum && 
      typeof agentOutput.task_output === 'number') {
    
    // Force failure to make agent retry with actual tool usage
    return {
      task_description: agentOutput.task_description,
      task_input: agentOutput.task_input,
      task_tool: agentOutput.task_tool,
      task_output: 'ERROR: Agent must use MCP Client Executor tool, not calculate results',
      task_status: 'failure',
      task_id: agentOutput.task_id
    };
  }
}
```

### 7. Tool-Only Agent Configuration
- **Remove mathematical capabilities** from the agent by not providing any mathematical context
- **Only provide tool descriptions** - no examples of calculations
- **Use tool-specific prompts** that assume the agent cannot do math

### 8. Multi-Step Verification
```javascript
// Three-step verification process:
// 1. Check for tool usage evidence
// 2. Validate result format
// 3. Cross-reference with expected tool behavior

const verification = {
  hasToolEvidence: checkToolUsageEvidence(agentMessages),
  formatValid: validateResultFormat(agentOutput),
  behaviorConsistent: checkToolBehavior(agentOutput)
};

if (!verification.hasToolEvidence || !verification.formatValid || !verification.behaviorConsistent) {
  // Reject and force retry
  throw new Error('Tool usage verification failed');
}
```

### 9. Context Restriction
- **Remove mathematical context** from all prompts
- **Emphasize tool dependency** in every instruction
- **Use failure-first language**: "If you cannot use tools, report failure"

### 10. Alternative Model Configuration
For Ollama/Local models, use custom system prompts:
```json
{
  "system": "You are a tool interface only. You cannot perform any calculations or processing. You can only call external tools and return their exact results. Any attempt to calculate will result in immediate failure."
}
```

## Recommended Implementation Order

1. ✅ **Enhanced System Message** - Strongest prohibition language
2. ✅ **LLM Stop Words** - Prevent calculation phrases
3. ✅ **Mandatory Tool Requirements** - Force tool usage
4. ✅ **Format Enforcement** - Require formatting tool
5. 🔄 **Response Validation** - Detect and reject calculated responses
6. 🔄 **Retry Mechanism** - Force re-execution on detection
7. 🔄 **Multi-step Verification** - Comprehensive validation
8. 🔄 **Context Restriction** - Remove mathematical context

## Testing the Implementation

### Test Case 1: Simple Addition
```json
{
  "tool": "add",
  "task_description": "Add 5154 and 25",
  "task_input": {"a": 5154, "b": 25},
  "task_id": "task_1"
}
```

**Expected Behavior**: Agent calls MCP Client Executor, gets result, formats with format_final_json_response tool

**Signs of Failure**: Response contains `5179` without tool usage evidence

### Test Case 2: Complex Calculation
```json
{
  "tool": "multiply",
  "task_description": "Multiply 123 and 456",
  "task_input": {"a": 123, "b": 456},
  "task_id": "task_2"
}
```

**Expected Behavior**: Agent must use tools even for complex math

### Monitoring Success
1. Check agent conversation logs for tool usage
2. Verify response contains tool execution evidence
3. Confirm no mathematical language in agent responses
4. Validate proper tool result formatting

## Troubleshooting

### If Agent Still Calculates:
1. Add more stop words to LLM configuration
2. Implement stricter validation
3. Use a different model that's less prone to shortcuts
4. Add retry loops with increasingly strict prompts

### If Tools Aren't Available:
1. Check MCP server connectivity
2. Verify tool registration
3. Test tool functionality independently
4. Add tool availability validation