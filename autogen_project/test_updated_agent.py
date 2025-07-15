"""
Test the updated FileDataAnalyst that directly analyzes data content.
"""

from agents import FileDataAnalyst
import pandas as pd


def test_direct_data_analysis():
    """Test the updated agent with direct data analysis."""
    print("🧪 Testing Updated FileDataAnalyst")
    print("=" * 50)
    
    agent = FileDataAnalyst()
    
    # Test 1: File-based analysis (should now include full data)
    print("\n1️⃣ Testing file-based analysis with full data inclusion:")
    task_data = {
        "analysis_request": "Analyze the employee performance and salary data",
        "files": ["employee_data.xlsx"]
    }
    
    prompt = agent.prepare_task(task_data)
    print(f"Prompt length: {len(prompt)} characters")
    
    # Check if actual data is included
    data_indicators = [
        "Alice Johnson",
        "Marketing",
        "75000",
        "Complete Dataset:",
        "Statistical Summary:"
    ]
    
    print("\n📊 Data Content Checks:")
    for indicator in data_indicators:
        if indicator in prompt:
            print(f"✅ {indicator}: Found in prompt")
        else:
            print(f"❌ {indicator}: NOT found in prompt")
    
    # Test 2: Direct data analysis
    print("\n2️⃣ Testing direct data analysis:")
    sample_data = pd.DataFrame({
        'Product': ['A', 'B', 'C'],
        'Sales': [100, 200, 150],
        'Region': ['North', 'South', 'East']
    })
    
    result = agent.analyze_data_directly(
        data=sample_data,
        analysis_request="Analyze sales performance by product and region"
    )
    
    print("Direct data analysis prepared successfully!")
    
    # Test 3: Show a portion of the file-based prompt
    print("\n3️⃣ Sample of file-based prompt content:")
    print("-" * 40)
    print(prompt[:800] + "..." if len(prompt) > 800 else prompt)
    

if __name__ == "__main__":
    test_direct_data_analysis()
