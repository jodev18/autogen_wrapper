"""Quick demonstration script for the Autogen project."""

import json
from api.orchestrator import TaskOrchestrator


def demo_without_api_keys():
    """Demonstrate the project structure without actually calling LLMs."""
    print("🧠 Autogen Agent Orchestration Project Demo")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = TaskOrchestrator()
    
    # List available agents
    print("\n📋 Available Agents:")
    agents = orchestrator.list_agents()
    for name, class_name in agents.items():
        print(f"  • {name} ({class_name})")
    
    # Show sample task data for each agent
    print("\n🔧 Sample Task Data:")
    
    print("\n1. DataAnalyst Agent:")
    data_task = {
        "data": "Sales Q1: $100k, Q2: $120k, Q3: $110k, Q4: $140k",
        "context": "Annual sales performance analysis"
    }
    print(f"   {json.dumps(data_task, indent=4)}")
    
    print("\n2. ContentWriter Agent:")
    content_task = {
        "topic": "AI in Business",
        "audience": "business executives",
        "content_type": "article",
        "tone": "professional and engaging"
    }
    print(f"   {json.dumps(content_task, indent=4)}")
    
    print("\n3. CodeReviewer Agent:")
    code_task = {
        "code": """
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total
""",
        "context": "Review for performance and best practices"
    }
    print(f"   {json.dumps(code_task, indent=4)}")
    
    print("\n✅ Project Structure Successfully Created!")
    print("\n📝 Next Steps:")
    print("1. Add your API keys to the .env file")
    print("2. Test with: uv run python cli.py --agent data_analyst --data 'Sample data'")
    print("3. Start the API: uv run python main.py")
    print("4. Access API docs: http://localhost:8000/docs")
    
    print("\n🚀 Features Available:")
    print("  • Modular agent system with template-based prompts")
    print("  • Support for OpenAI and DeepSeek providers")  
    print("  • FastAPI-based HTTP orchestration")
    print("  • Thread-aware logging system")
    print("  • Multi-agent workflows")
    print("  • CLI interface for testing")
    print("  • Comprehensive test suite")
    print("  • Uses uv for fast dependency management")


if __name__ == "__main__":
    demo_without_api_keys()
