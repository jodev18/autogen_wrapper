"""
Test to see the exact prompt being sent to the LLM.
"""

from agents import FileDataAnalyst


def test_prompt_content():
    """Test what's actually in the prompt."""
    print("🔍 Testing actual prompt content...")
    
    agent = FileDataAnalyst()
    
    task_data = {
        "analysis_request": "Examine employee performance, salary distribution, and department insights",
        "files": ["employee_data.xlsx"]
    }
    
    prompt = agent.prepare_task(task_data)
    
    print("=" * 60)
    print("FULL PROMPT CONTENT:")
    print("=" * 60)
    print(prompt)
    print("=" * 60)
    print(f"Prompt length: {len(prompt)} characters")
    
    # Check for key elements
    checks = [
        ("employee_data.xlsx", "File name"),
        ("Data shape:", "Data shape info"),
        ("Columns:", "Column information"),
        ("Alice Johnson", "Sample data"),
        ("Salary", "Salary column"),
        ("Performance_Score", "Performance column")
    ]
    
    print("\n📋 Content Checks:")
    for check_text, description in checks:
        if check_text in prompt:
            print(f"✅ {description}: Found")
        else:
            print(f"❌ {description}: NOT found")


if __name__ == "__main__":
    test_prompt_content()
