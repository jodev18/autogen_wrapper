"""
Python equivalent of the curl command for file data analysis API call.
"""

import requests
import json


def call_file_data_analyst_api():
    """
    Python equivalent of:
    curl -X POST 'http://localhost:8000/run-agent' \
      -H 'Content-Type: application/json' \
      -d '{...}'
    """
    
    # API endpoint
    url = "http://localhost:8000/run-agent"
    
    # Headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Request payload
    payload = {
        "agent_name": "file_data_analyst",
        "task_data": {
            "analysis_request": "Examine employee performance, salary distribution, and department insights",
            "files": [
                "employee_data.xlsx"
            ]
        },
        "provider": "openai",
        "model_name": "gpt-4",
        "llm_config": {
            "temperature": 0.2,
            "max_tokens": 1200
        }
    }
    
    try:
        # Make the POST request
        response = requests.post(url, headers=headers, json=payload)
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse and return the JSON response
        result = response.json()
        
        print("✅ API Call Successful!")
        print(f"Status Code: {response.status_code}")
        print("\n📊 Response:")
        print(json.dumps(result, indent=2))
        
        return result
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the FastAPI server is running on localhost:8000")
        print("💡 Start the server with: uv run python main.py")
        return None
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response: {response.text}")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return None
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON response")
        print(f"Response: {response.text}")
        return None


def call_sales_data_analyst_api():
    """Alternative example with sales data analysis."""
    
    url = "http://localhost:8000/run-agent"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "agent_name": "file_data_analyst",
        "task_data": {
            "analysis_request": "Analyze sales data to identify top products, revenue trends, and seasonal patterns",
            "files": ["sales_data.csv"]
        },
        "provider": "deepseek",
        "model_name": "deepseek-chat",
        "llm_config": {
            "temperature": 0.3,
            "max_tokens": 1500
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Sales Analysis API Call Successful!")
        print(json.dumps(result, indent=2))
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def call_multi_file_analysis_api():
    """Example with multiple file analysis."""
    
    url = "http://localhost:8000/run-agent"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "agent_name": "file_data_analyst",
        "task_data": {
            "analysis_request": "Perform comprehensive business intelligence analysis across all data sources",
            "include_all_files": True
        },
        "provider": "deepseek",
        "model_name": "deepseek-chat",
        "llm_config": {
            "temperature": 0.4,
            "max_tokens": 2000
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Multi-File Analysis API Call Successful!")
        print(json.dumps(result, indent=2))
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def check_api_status():
    """Check if the API server is running."""
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ API Server is running!")
            return True
        else:
            print(f"⚠️ API Server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API Server is not running")
        print("💡 Start it with: uv run python main.py")
        return False


def list_available_agents():
    """List all available agents."""
    try:
        response = requests.get("http://localhost:8000/agents")
        response.raise_for_status()
        
        result = response.json()
        print("📋 Available Agents:")
        for agent in result.get("agents", []):
            print(f"  - {agent}")
        return result
        
    except Exception as e:
        print(f"❌ Error listing agents: {e}")
        return None


if __name__ == "__main__":
    print("🚀 File Data Analyst API Client")
    print("=" * 40)
    
    # Check if API is running
    if not check_api_status():
        exit(1)
    
    # List available agents
    print("\n📋 Checking available agents...")
    list_available_agents()
    
    print("\n" + "=" * 40)
    print("🧪 Running API Tests")
    print("=" * 40)
    
    # Example 1: Employee data analysis (original curl equivalent)
    print("\n1️⃣ Employee Data Analysis (Original curl equivalent):")
    result1 = call_file_data_analyst_api()
    
    # Example 2: Sales data analysis
    print("\n2️⃣ Sales Data Analysis:")
    result2 = call_sales_data_analyst_api()
    
    # Example 3: Multi-file analysis
    print("\n3️⃣ Multi-File Analysis:")
    result3 = call_multi_file_analysis_api()
    
    print("\n🎉 API Testing Complete!")
