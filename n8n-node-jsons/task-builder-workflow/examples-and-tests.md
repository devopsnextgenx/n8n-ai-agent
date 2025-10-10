# Task Builder Workflow - Examples and Test Scenarios

## Example Task Scenarios

### Scenario 1: Simple Calculation with Encryption
**User Request**: "Calculate 15 * 7 and then encrypt the result using AES"

**Expected Task Breakdown**:
```json
{
  "tasks": [
    {
      "tool": "calculator",
      "task_description": "Calculate multiplication of 15 and 7",
      "task_input": {
        "a": 15,
        "b": 7,
        "operation": "multiply"
      },
      "dependencies": [],
      "task_id": "calc_1"
    },
    {
      "tool": "encrypt",
      "task_description": "Encrypt the calculation result using AES encryption",
      "task_input": {
        "text": "{{ dependency_calc_1 }}",
        "action": "encrypt"
      },
      "dependencies": ["calc_1"],
      "task_id": "encrypt_1"
    }
  ]
}
```

**Expected Flow**:
1. Execute calc_1: 15 * 7 = 105
2. Execute encrypt_1: Encrypt "105" using AES
3. Final response: "The result of 15 * 7 is 105, which has been encrypted as: [encrypted_value]"

### Scenario 2: Multi-Step Data Processing
**User Request**: "Get the current Bitcoin price, calculate 10% of that value, and create a summary report"

**Expected Task Breakdown**:
```json
{
  "tasks": [
    {
      "tool": "crypto_price",
      "task_description": "Get current Bitcoin price in USD",
      "task_input": {
        "symbol": "BTC",
        "currency": "USD"
      },
      "dependencies": [],
      "task_id": "btc_price"
    },
    {
      "tool": "calculator",
      "task_description": "Calculate 10% of the Bitcoin price",
      "task_input": {
        "a": "{{ dependency_btc_price }}",
        "b": 0.1,
        "operation": "multiply"
      },
      "dependencies": ["btc_price"],
      "task_id": "calc_10_percent"
    },
    {
      "tool": "text_generator",
      "task_description": "Create a summary report with Bitcoin price and 10% calculation",
      "task_input": {
        "template": "Bitcoin Analysis Report",
        "data": {
          "current_price": "{{ dependency_btc_price }}",
          "ten_percent_value": "{{ dependency_calc_10_percent }}"
        }
      },
      "dependencies": ["btc_price", "calc_10_percent"],
      "task_id": "summary_report"
    }
  ]
}
```

### Scenario 3: Complex Workflow with Multiple Dependencies
**User Request**: "Calculate the area of a circle with radius 5, encrypt that result, and also calculate the circumference of the same circle, then create a combined report"

**Expected Task Breakdown**:
```json
{
  "tasks": [
    {
      "tool": "calculator",
      "task_description": "Calculate area of circle with radius 5 (π * r²)",
      "task_input": {
        "a": 3.14159,
        "b": 25,
        "operation": "multiply"
      },
      "dependencies": [],
      "task_id": "circle_area"
    },
    {
      "tool": "calculator",
      "task_description": "Calculate circumference of circle with radius 5 (2 * π * r)",
      "task_input": {
        "a": 6.28318,
        "b": 5,
        "operation": "multiply"
      },
      "dependencies": [],
      "task_id": "circle_circumference"
    },
    {
      "tool": "encrypt",
      "task_description": "Encrypt the calculated area",
      "task_input": {
        "text": "{{ dependency_circle_area }}",
        "action": "encrypt"
      },
      "dependencies": ["circle_area"],
      "task_id": "encrypt_area"
    },
    {
      "tool": "text_generator",
      "task_description": "Create combined report with all circle calculations",
      "task_input": {
        "template": "Circle Analysis Report",
        "data": {
          "radius": 5,
          "area": "{{ dependency_circle_area }}",
          "encrypted_area": "{{ dependency_encrypt_area }}",
          "circumference": "{{ dependency_circle_circumference }}"
        }
      },
      "dependencies": ["circle_area", "circle_circumference", "encrypt_area"],
      "task_id": "combined_report"
    }
  ]
}
```

## Test Cases

### Test Case 1: Basic Functionality
```bash
# Input
"Calculate 8 + 12"

# Expected Output
{
  "final_response": "The calculation of 8 + 12 equals 20.",
  "task_summary": {
    "total_tasks": 1,
    "successful_tasks": 1,
    "failed_tasks": 0
  },
  "key_results": ["Mathematical operation completed: 8 + 12 = 20"]
}
```

### Test Case 2: Dependency Handling
```bash
# Input
"Calculate 5 * 6 and encrypt the result"

# Expected Output
{
  "final_response": "The calculation of 5 * 6 equals 30, which has been encrypted as: [encrypted_value]",
  "task_summary": {
    "total_tasks": 2,
    "successful_tasks": 2,
    "failed_tasks": 0
  },
  "key_results": [
    "Mathematical operation: 5 * 6 = 30",
    "Encryption completed successfully"
  ]
}
```

### Test Case 3: Error Handling
```bash
# Input
"Calculate 10 / 0 and encrypt the result"

# Expected Behavior
- First task fails (division by zero)
- Second task is skipped (dependency failed)
- Final response explains the error

# Expected Output
{
  "final_response": "Unable to complete the request due to a mathematical error: division by zero is undefined. The encryption task was skipped due to the calculation failure.",
  "task_summary": {
    "total_tasks": 2,
    "successful_tasks": 0,
    "failed_tasks": 1
  },
  "key_results": ["Mathematical error: Division by zero"]
}
```

## Testing Checklist

### Agent 1 (Task Planner) Tests
- [ ] Can access listTools and retrieve available tools
- [ ] Breaks down simple requests into single tasks
- [ ] Breaks down complex requests into multiple tasks
- [ ] Correctly identifies task dependencies
- [ ] Generates valid JSON output structure
- [ ] Handles edge cases (empty input, unclear requests)

### Agent 2 (Task Executor) Tests
- [ ] Can access all MCP tools
- [ ] Executes tasks with correct tool selection
- [ ] Handles task inputs properly
- [ ] Processes dependency data correctly
- [ ] Returns structured task results
- [ ] Handles tool execution errors gracefully

### Agent 3 (Response Synthesis) Tests
- [ ] Processes multiple task results
- [ ] Creates coherent final responses
- [ ] Summarizes task execution statistics
- [ ] Highlights key findings appropriately
- [ ] Handles mixed success/failure scenarios

### Dependency System Tests
- [ ] Executes independent tasks immediately
- [ ] Waits for dependencies before execution
- [ ] Injects dependency outputs correctly
- [ ] Handles circular dependency detection
- [ ] Manages complex dependency chains
- [ ] Skips dependent tasks when dependencies fail

### Integration Tests
- [ ] End-to-end workflow execution
- [ ] MCP server connectivity
- [ ] Ollama model integration
- [ ] Chat interface functionality
- [ ] Error propagation and handling
- [ ] Performance with large task sets

## Performance Benchmarks

### Expected Response Times
- Simple single task: < 5 seconds
- 2-3 dependent tasks: < 15 seconds
- Complex workflows (5+ tasks): < 30 seconds

### Resource Usage
- Memory: Monitor task registry size
- CPU: Track LLM inference load
- Network: MCP server communication

### Scalability Limits
- Maximum tasks per workflow: 20
- Maximum dependency depth: 5 levels
- Maximum execution time: 2 minutes

## Debugging Scenarios

### Common Issues and Solutions

#### Issue: Tasks not executing in correct order
**Symptoms**: Dependent tasks fail due to missing inputs
**Solution**: Check dependency task_id references match exactly

#### Issue: Invalid JSON from agents
**Symptoms**: Parser errors, workflow stops
**Solution**: Review and refine system messages, add examples

#### Issue: MCP tools not available
**Symptoms**: Tool execution failures
**Solution**: Verify MCP server status and endpoint configuration

#### Issue: Infinite execution loops
**Symptoms**: Workflow never completes
**Solution**: Add maximum iteration limits, check for circular dependencies

### Debug Mode Configuration
```json
{
  "debug": {
    "enabled": true,
    "log_level": "verbose",
    "track_task_registry": true,
    "monitor_dependencies": true,
    "capture_agent_responses": true
  }
}
```

## Advanced Usage Patterns

### Pattern 1: Conditional Task Execution
```json
{
  "tool": "conditional_executor",
  "task_description": "Execute task only if previous result meets criteria",
  "task_input": {
    "condition": "{{ dependency_prev_task }} > 100",
    "if_true": "encrypt_result",
    "if_false": "skip_task"
  }
}
```

### Pattern 2: Batch Processing
```json
{
  "tool": "batch_processor",
  "task_description": "Process multiple items with same operation",
  "task_input": {
    "items": ["item1", "item2", "item3"],
    "operation": "calculate_hash"
  }
}
```

### Pattern 3: Data Transformation Pipeline
```json
{
  "tasks": [
    {"task_id": "extract", "tool": "data_extractor"},
    {"task_id": "transform", "tool": "data_transformer", "dependencies": ["extract"]},
    {"task_id": "load", "tool": "data_loader", "dependencies": ["transform"]},
    {"task_id": "validate", "tool": "data_validator", "dependencies": ["load"]}
  ]
}
```