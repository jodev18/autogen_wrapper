"""
Debug script to test FileDataAnalyst data loading.
"""

from agents import FileDataAnalyst
import json


def test_file_loading():
    """Test the file loading functionality."""
    print("🔍 Testing FileDataAnalyst file loading...")
    
    # Create agent
    agent = FileDataAnalyst()
    
    # Test 1: List available files
    print("\n📁 Available files:")
    files = agent.list_data_files()
    for file_info in files:
        print(f"  - {file_info['name']} ({file_info['size']} bytes)")
    
    # Test 2: Load a specific file
    print("\n📊 Loading employee_data.xlsx:")
    try:
        file_data = agent.load_data_file("employee_data.xlsx")
        print(f"  Type: {file_data.get('type')}")
        print(f"  Has data: {'data' in file_data}")
        if file_data.get('data') is not None:
            df = file_data['data']
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test 3: Get data summary
    print("\n📋 Data summary for employee_data.xlsx:")
    try:
        summary = agent.get_data_summary("employee_data.xlsx")
        print(summary[:300] + "..." if len(summary) > 300 else summary)
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test 4: Prepare task with file
    print("\n🎯 Preparing task with file:")
    task_data = {
        "analysis_request": "Analyze employee data for insights",
        "files": ["employee_data.xlsx"]
    }
    
    try:
        prompt = agent.prepare_task(task_data)
        print("Prompt generated successfully!")
        print(f"Prompt length: {len(prompt)} characters")
        
        # Check if file data is included
        if "employee_data.xlsx" in prompt:
            print("✅ File name found in prompt")
        if "shape:" in prompt.lower() or "columns:" in prompt.lower():
            print("✅ File data summary found in prompt")
        else:
            print("❌ File data summary NOT found in prompt")
            
        # Show first part of prompt
        print("\nPrompt preview:")
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        
    except Exception as e:
        print(f"  Error preparing task: {e}")


if __name__ == "__main__":
    test_file_loading()
