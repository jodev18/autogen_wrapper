"""
Debug the exact prompt being sent to check if data is included.
"""

from agents import FileDataAnalyst


def show_full_prompt():
    """Show the complete prompt with data."""
    agent = FileDataAnalyst()
    
    task_data = {
        "analysis_request": "Examine employee performance, salary distribution, and department insights",
        "files": ["employee_data.xlsx"]
    }
    
    prompt = agent.prepare_task(task_data)
    
    print("=" * 80)
    print("COMPLETE PROMPT BEING SENT TO LLM:")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    print(f"Total length: {len(prompt)} characters")
    
    # Check for complete dataset
    if "Complete Dataset:" in prompt:
        print("✅ Complete dataset is included!")
        # Find where the complete dataset starts
        start_idx = prompt.find("Complete Dataset:")
        end_idx = prompt.find("Statistical Summary:")
        if start_idx != -1 and end_idx != -1:
            dataset_section = prompt[start_idx:end_idx]
            print(f"\nDataset section length: {len(dataset_section)} characters")
            print("First 300 chars of dataset:")
            print(dataset_section[:300])
    else:
        print("❌ Complete dataset NOT found in prompt")


if __name__ == "__main__":
    show_full_prompt()
