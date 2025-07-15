"""
Complete example showing file processing capabilities with sample API requests.
Run this to see the file data analyst in action.
"""

from agents import FileDataAnalyst
import json


def main():
    print("🚀 File Data Analysis System Demo")
    print("=" * 50)
    
    # Initialize the agent
    agent = FileDataAnalyst()
    
    # Show available files
    print("\n📁 Available Data Files:")
    files = agent.list_data_files()
    for file_info in files:
        print(f"   📄 {file_info['name']} ({file_info['size']} bytes)")
    
    # Example 1: Sales Data Analysis
    print("\n📊 Example 1: Sales Data Analysis")
    print("-" * 40)
    
    sales_task = {
        "analysis_request": "Analyze sales data to identify top products, revenue trends, and seasonal patterns",
        "files": ["sales_data.csv"]
    }
    
    sales_prompt = agent.prepare_task(sales_task)
    print("Generated Analysis Prompt:")
    print(sales_prompt[:300] + "...\n")
    
    # Example 2: Employee Data Analysis  
    print("👥 Example 2: Employee Data Analysis")
    print("-" * 40)
    
    employee_task = {
        "analysis_request": "Examine employee performance, salary distribution, and department insights",
        "files": ["employee_data.xlsx"]
    }
    
    employee_prompt = agent.prepare_task(employee_task)
    print("Generated Analysis Prompt:")
    print(employee_prompt[:300] + "...\n")
    
    # Example 3: Comprehensive Multi-File Analysis
    print("🔍 Example 3: Multi-File Analysis")
    print("-" * 40)
    
    multi_task = {
        "analysis_request": "Perform comprehensive business intelligence analysis across all data sources",
        "include_all_files": True
    }
    
    multi_prompt = agent.prepare_task(multi_task)
    print("Generated Analysis Prompt:")
    print(multi_prompt[:300] + "...\n")
    
    # Show sample API requests
    print("🌐 Sample API Requests:")
    print("-" * 40)
    
    api_examples = [
        {
            "name": "Sales Analysis API Call",
            "request": {
                "agent_name": "file_data_analyst",
                "task_data": sales_task,
                "provider": "deepseek",
                "model_name": "deepseek-chat",
                "llm_config": {
                    "temperature": 0.3,
                    "max_tokens": 1500
                }
            }
        },
        {
            "name": "Employee Analysis API Call", 
            "request": {
                "agent_name": "file_data_analyst",
                "task_data": employee_task,
                "provider": "openai",
                "model_name": "gpt-4",
                "llm_config": {
                    "temperature": 0.2,
                    "max_tokens": 1200
                }
            }
        }
    ]
    
    for example in api_examples:
        print(f"\n{example['name']}:")
        print("curl -X POST 'http://localhost:8000/run-agent' \\")
        print("  -H 'Content-Type: application/json' \\")
        print(f"  -d '{json.dumps(example['request'], indent=2)}'")
        print()
    
    # File processing capabilities summary
    print("✨ File Processing Capabilities:")
    print("-" * 40)
    
    capabilities = [
        "📄 PDF documents (text extraction)",
        "📊 CSV files (data analysis & statistics)",
        "📈 Excel files (multi-sheet support)",
        "📝 Word documents (content analysis)",
        "📃 Text files (content summarization)",
        "🔍 Automatic file type detection",
        "📋 Data quality assessment",
        "📊 Statistical summaries",
        "🎯 Business insights generation"
    ]
    
    for capability in capabilities:
        print(f"   {capability}")
    
    print("\n🎉 File Data Analysis System Ready!")
    print("To use with real API calls, set your API keys:")
    print("   export DEEPSEEK_API_KEY='your_key'")
    print("   export OPENAI_API_KEY='your_key'")


if __name__ == "__main__":
    main()
