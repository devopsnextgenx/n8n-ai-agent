# Task Builder Workflow

This n8n workflow implements a sophisticated three-agent system for breaking down user requests into tasks, executing them with dependency management, and synthesizing final responses.

## Architecture Overview

### Three-Agent System

1. **Task Planner Agent (Agent 1)**
   - Uses `listTools` MCP tool to discover available tools
   - Breaks down user requests into specific, actionable tasks
   - Determines tool requirements and task dependencies
   - Returns structured JSON with task definitions

2. **Task Executor Agent (Agent 2)**
   - Has access to all MCP tools for task execution
   - Executes individual tasks based on planner specifications
   - Handles task inputs and produces structured outputs
   - Tracks task status (success/failure)

3. **Response Synthesis Agent (Agent 3)**
   - Collects all completed task results
   - Synthesizes outputs into coherent final response
   - Provides comprehensive summary and key findings

## Key Features

### Dependency Management
- Tasks can specify dependencies on other tasks
- System resolves dependencies and executes tasks in proper order
- Dependency outputs are automatically injected into dependent task inputs
- Sequential execution ensures data flow integrity

### Task Structure
Each task follows this JSON structure:
```json
{
  "tool": "tool_name",
  "task_description": "Clear description of task",
  "task_input": {
    "parameter1": "value1",
    "parameter2": "value2"
  },
  "dependencies": ["task_1", "task_2"],
  "task_id": "unique_identifier"
}
```

### Task Result Structure
Each completed task returns:
```json
{
  "task_description": "What was accomplished",
  "task_input": "Original input parameters",
  "task_tool": "Tool used",
  "task_output": "Actual result/output",
  "task_status": "success|failure",
  "task_id": "unique_identifier"
}
```

## Workflow Components

### Core Nodes
1. **Chat Trigger** - Receives user input
2. **Task Planner Agent** - Breaks down requests
3. **Task Dependency Resolver** - Manages task execution order
4. **Task Executor Agent** - Executes individual tasks
5. **Response Synthesis Agent** - Creates final response

### Supporting Nodes
- **Task List Parser** - Validates task planning output
- **Task Result Parser** - Validates task execution output
- **Final Response Parser** - Validates synthesis output
- **Update Task Registry** - Tracks task completion
- **Check Ready Tasks/Check More Tasks** - Controls execution flow

### MCP Integration
- **List Tools Workflow** - Provides available tools to planner
- **MCP Client Executor** - Connects to MCP server for task execution
- **MCP Server Executor** - Handles MCP tool invocations

## Execution Flow

1. **User Input** → Chat Trigger receives request
2. **Task Planning** → Agent 1 analyzes request and creates task list
3. **Dependency Resolution** → System identifies tasks ready for execution
4. **Task Execution Loop**:
   - Execute ready tasks (no dependencies)
   - Update task registry with results
   - Identify newly ready tasks (dependencies satisfied)
   - Repeat until all tasks completed
5. **Response Synthesis** → Agent 3 creates final coherent response
6. **User Response** → Formatted response sent to user

## Configuration Requirements

### Prerequisites
- n8n instance with LangChain nodes
- Ollama with Qwen2.5 model
- MCP server running with available tools
- List-tool-service-trigger workflow (for tool discovery)

### Credentials Needed
- Ollama API credentials pointing to Qwen2.5
- MCP server endpoint configuration

### Environment Variables
- MCP server URL (default: http://host.docker.internal:6789)
- Ollama endpoint (default: host.docker.internal)

## Usage Examples

### Simple Request
**User**: "Calculate 10 + 5 and encrypt the result"

**Generated Tasks**:
1. Task 1: Use calculator tool to compute 10 + 5
2. Task 2: Use encryption tool on result from Task 1 (depends on Task 1)

### Complex Multi-Step Request
**User**: "Get weather for New York, convert temperature to Celsius, and create a summary report"

**Generated Tasks**:
1. Task 1: Get weather data for New York
2. Task 2: Convert temperature from Task 1 to Celsius (depends on Task 1)
3. Task 3: Create summary report using data from Tasks 1 and 2 (depends on Task 1, Task 2)

## Error Handling

- Individual task failures are tracked and reported
- Failed tasks don't block independent tasks
- Dependent tasks are skipped if dependencies fail
- Final response includes summary of successes and failures

## Customization Options

### System Messages
Each agent has customizable system messages for:
- Task planning strategies
- Execution approaches
- Response synthesis styles

### Task Schema
The task JSON schema can be extended to include:
- Priority levels
- Execution timeouts
- Resource requirements
- Retry policies

### MCP Integration
- Support for multiple MCP servers
- Tool filtering and selection
- Custom tool mappings

## Monitoring and Debugging

### Task Registry
The workflow maintains a comprehensive task registry with:
- Task definitions and status
- Execution results and outputs
- Dependency relationships
- Completion timestamps

### Execution Tracking
- Batch processing with iteration counting
- Task completion percentage
- Performance metrics
- Error logging

## Future Enhancements

1. **Parallel Task Execution** - Execute independent tasks simultaneously
2. **Dynamic Tool Discovery** - Real-time tool availability checking
3. **Task Prioritization** - Execute high-priority tasks first
4. **Resource Management** - Monitor and limit resource usage
5. **Caching Layer** - Cache results for repeated operations
6. **Workflow Templates** - Pre-defined task patterns for common scenarios

## Troubleshooting

### Common Issues
1. **Task Dependencies Not Resolving** - Check task_id references
2. **MCP Tools Not Available** - Verify MCP server connection
3. **Agent Responses Invalid** - Review system message formatting
4. **Infinite Loops** - Check for circular dependencies

### Debug Mode
Enable detailed logging by adding debug nodes to track:
- Task registry state changes
- Agent response validation
- MCP tool invocation results
- Dependency resolution progress