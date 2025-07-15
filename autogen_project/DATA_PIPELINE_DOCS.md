# Data Pipeline Workflow Documentation

## Overview

The `run_data_pipeline_workflow` function provides enhanced multi-agent orchestration with sophisticated data passing capabilities between agents. This extends the basic `run_multi_agent_workflow` to support complex data transformations, mappings, and error handling.

## Key Features

### 🔄 Data Flow Management
- **Input Mapping**: Map outputs from previous steps to inputs of current steps
- **Shared Data**: Persistent data storage accessible across all workflow steps
- **Output Keys**: Named storage for step outputs that can be referenced by subsequent steps

### 🛠️ Data Transformations
- Built-in transformations: `uppercase`, `lowercase`, `strip`, `json_parse`, `to_list`, `to_string`, `extract_numbers`
- Custom transformation support via the `_apply_transformation` method
- Per-step transformation configuration

### 🚨 Error Handling
- **Stop on Error** (default): Workflow stops when a step fails
- **Continue on Error**: Workflow continues despite step failures
- Comprehensive error logging and reporting

### 📊 Enhanced Reporting
- Data flow summary showing step-by-step data movement
- Step output tracking with named keys
- Final shared data state
- Transformation audit trail

## Function Signature

```python
def run_data_pipeline_workflow(
    self,
    workflow: list[Dict[str, Any]],
    initial_data: Optional[Dict[str, Any]] = None,
    provider: Optional[str] = None,
    data_mapping: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
```

## Parameters

### workflow
List of workflow steps, each containing:

```python
{
    "agent": "agent_name",                    # Required: Agent to execute
    "task_data": {...},                       # Optional: Base task data
    "input_mapping": {                        # Optional: Map previous outputs to inputs
        "target_key": "source_output_key"
    },
    "output_key": "step_output_name",         # Optional: Name for this step's output
    "transform": "transformation_name",       # Optional: Data transformation to apply
    "on_error": "stop|continue"               # Optional: Error handling strategy
}
```

### initial_data
Dictionary of data available to all workflow steps from the beginning.

### provider
LLM provider to use for all agents (e.g., "deepseek", "openai").

### data_mapping
Global mapping to automatically transfer specific keys between steps.

## Usage Examples

### Basic Data Pipeline

```python
orchestrator = TaskOrchestrator()

workflow = [
    {
        "agent": "data_analyst",
        "task_data": {"task": "Analyze sales data"},
        "output_key": "analysis"
    },
    {
        "agent": "content_writer",
        "task_data": {"task": "Create report"},
        "input_mapping": {"analysis_data": "analysis"},
        "output_key": "report"
    }
]

result = orchestrator.run_data_pipeline_workflow(
    workflow=workflow,
    initial_data={"company": "Acme Corp"},
    provider="deepseek"
)
```

### Data Transformations

```python
workflow = [
    {
        "agent": "data_analyst",
        "task_data": {"task": "Generate numbers list"},
        "output_key": "raw_data",
        "transform": "extract_numbers"  # Extract only numbers
    },
    {
        "agent": "content_writer",
        "task_data": {"task": "Format output"},
        "input_mapping": {"numbers": "raw_data"},
        "output_key": "formatted",
        "transform": "uppercase"  # Convert to uppercase
    }
]
```

### Error Handling

```python
workflow = [
    {
        "agent": "data_analyst",
        "task_data": {"task": "Reliable step"},
        "output_key": "good_data"
    },
    {
        "agent": "unreliable_agent",
        "task_data": {"task": "Might fail"},
        "output_key": "risky_data",
        "on_error": "continue"  # Continue despite failure
    },
    {
        "agent": "content_writer",
        "task_data": {"task": "Use available data"},
        "input_mapping": {"data": "good_data"},  # Use data from step 1
        "output_key": "final_report"
    }
]
```

## Return Value Structure

```python
{
    "success": bool,                          # Overall workflow success
    "job_id": str,                           # Unique workflow identifier
    "execution_time": float,                 # Total execution time
    "workflow_steps": int,                   # Total steps in workflow
    "completed_steps": int,                  # Successfully completed steps
    "results": [                             # Individual step results
        {"success": bool, "response": str, ...}
    ],
    "final_data": Dict[str, Any],           # Final shared data state
    "step_outputs": Dict[str, Any],         # Named outputs from each step
    "data_flow": {                          # Data flow summary
        "steps": [                          # Step-by-step flow info
            {
                "step": int,
                "agent": str,
                "input_mapping": Dict,
                "output_key": str,
                "transform": str,
                "has_output": bool
            }
        ],
        "data_keys": List[str],             # All output keys generated
        "transformations": [                # Applied transformations
            {"step": int, "transform": str}
        ]
    },
    "orchestrator": "TaskOrchestrator"
}
```

## Built-in Transformations

| Transformation | Description | Example |
|----------------|-------------|---------|
| `uppercase` | Convert to uppercase | "hello" → "HELLO" |
| `lowercase` | Convert to lowercase | "HELLO" → "hello" |
| `strip` | Remove whitespace | " text " → "text" |
| `json_parse` | Parse JSON string | '{"key": "value"}' → dict |
| `to_list` | Convert to list | "item" → ["item"] |
| `to_string` | Convert to string | 123 → "123" |
| `extract_numbers` | Extract digits only | "abc123def456" → "123456" |

## Data Flow Concepts

### Input Mapping
Maps outputs from previous steps to inputs of the current step:
```python
"input_mapping": {
    "current_step_input_key": "previous_step_output_key"
}
```

### Shared Data
Persistent data available to all steps via `task_data["shared_data"]`:
- Initial data provided at workflow start
- Data from `step_result.get("data", {})` from each successful step
- Global data mapping results

### Step Outputs
Named storage for step results:
- Stored using the `output_key` parameter
- Accessible to subsequent steps via input mapping
- Available in final result under `step_outputs`

## Best Practices

1. **Use Descriptive Output Keys**: Name outputs clearly for easy reference
2. **Handle Errors Gracefully**: Use `on_error: "continue"` for non-critical steps
3. **Transform Data Early**: Apply transformations close to data generation
4. **Validate Mappings**: Ensure source keys exist before mapping
5. **Monitor Data Flow**: Use the data flow summary for debugging

## Comparison with Basic Workflow

| Feature | Basic Workflow | Data Pipeline |
|---------|----------------|---------------|
| Data Passing | Simple context | Named outputs + mapping |
| Error Handling | Stop on failure | Configurable per step |
| Transformations | None | Built-in + custom |
| Reporting | Basic results | Comprehensive flow tracking |
| Data Persistence | Context only | Shared data + outputs |
| Debugging | Limited | Full data flow audit |

## Performance Considerations

- **Memory Usage**: Large datasets in shared_data consume memory throughout workflow
- **Serialization**: Complex objects may need custom transformations
- **Error Recovery**: Continue-on-error can mask important failures
- **Logging**: Comprehensive logging may impact performance for large workflows

## Advanced Usage

### Custom Transformations
Extend `_apply_transformation` method to add domain-specific transformations:

```python
def _apply_transformation(self, data: Any, transform: str) -> Any:
    custom_transforms = {
        "extract_emails": lambda x: re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', str(x)),
        "calculate_sum": lambda x: sum(float(i) for i in re.findall(r'\d+\.?\d*', str(x)))
    }
    
    if transform in custom_transforms:
        return custom_transforms[transform](data)
    
    # Fall back to built-in transformations
    return super()._apply_transformation(data, transform)
```

### Dynamic Workflow Generation
Build workflows programmatically based on data or conditions:

```python
def create_analysis_workflow(data_types: List[str]) -> List[Dict]:
    workflow = []
    
    for i, data_type in enumerate(data_types):
        workflow.append({
            "agent": f"{data_type}_analyst",
            "task_data": {"task": f"Analyze {data_type} data"},
            "output_key": f"{data_type}_analysis"
        })
    
    # Add summary step
    workflow.append({
        "agent": "content_writer",
        "task_data": {"task": "Create comprehensive summary"},
        "input_mapping": {f"{dt}_data": f"{dt}_analysis" for dt in data_types},
        "output_key": "final_summary"
    })
    
    return workflow
```

This enhanced workflow system provides the flexibility and power needed for complex multi-agent data processing pipelines while maintaining simplicity for basic use cases.
