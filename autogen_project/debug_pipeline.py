"""
Debug the data pipeline to see exactly what's being passed between agents.
"""

from api.orchestrator import TaskOrchestrator

def debug_data_pipeline():
    """Debug data passing between agents."""
    
    orchestrator = TaskOrchestrator()
    
    # Simple test workflow
    workflow = [
        {
            "agent": "data_analyst",
            "task_data": {
                "task": "Return exactly this text: 'Numbers: 100, 200, 300'"
            },
            "output_key": "step1_output"
        },
        {
            "agent": "data_analyst",
            "task_data": {
                "task": "Analyze the data you received"
            },
            "input_mapping": {
                "input_data": "step1_output"
            },
            "output_key": "step2_output"
        }
    ]
    
    print("🔍 Debugging Data Pipeline...")
    print("=" * 40)
    
    result = orchestrator.run_data_pipeline_workflow(
        workflow=workflow,
        provider="deepseek"
    )
    
    print(f"Success: {result['success']}")
    print(f"Steps: {result['completed_steps']}/{result['workflow_steps']}")
    
    # Debug step outputs
    print("\n📤 Raw Step Outputs:")
    for key, value in result.get('step_outputs', {}).items():
        print(f"{key}:")
        print(f"  Value: {repr(value)}")
        print(f"  Type: {type(value)}")
        print(f"  Length: {len(str(value))}")
        print()
    
    # Debug transformations
    print("\n🔄 Testing Transformations:")
    test_text = "Numbers: 100, 200, 300"
    print(f"Original: {test_text}")
    
    # Test the extract_numbers transformation manually
    numbers = ''.join(filter(str.isdigit, test_text))
    print(f"Extract numbers: {numbers}")
    
    return result

def test_transformation_only():
    """Test just the transformation function."""
    
    orchestrator = TaskOrchestrator()
    
    # Test data
    test_data = "The revenue numbers are: 1000, 2000, 3000, 4000"
    
    print(f"\n🧪 Testing transformation on: '{test_data}'")
    
    # Apply the transformation directly
    try:
        result = orchestrator._apply_transformation(test_data, "extract_numbers")
        print(f"Transform result: '{result}'")
        print(f"Expected: '1000200030004000'")
        print(f"Match: {result == '1000200030004000'}")
    except Exception as e:
        print(f"Transform error: {e}")

if __name__ == "__main__":
    debug_data_pipeline()
    test_transformation_only()
