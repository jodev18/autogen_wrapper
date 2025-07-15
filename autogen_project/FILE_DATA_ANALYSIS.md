# File Data Analysis API Examples

These examples demonstrate how to use the enhanced Autogen Agent system with file processing capabilities.

## Prerequisites

1. Install dependencies:
```bash
uv add pypdf2 pandas openpyxl python-docx
```

2. Set up data files in the `data/` directory:
- `sales_data.csv` - Sample sales data
- `employee_data.xlsx` - Employee information
- `market_report.txt` - Market research report

## Sample API Requests

### 1. Analyze Sales Data

```bash
curl -X POST "http://localhost:8000/run-agent" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "file_data_analyst",
    "task_data": {
      "analysis_request": "Analyze the sales data to identify revenue trends, top-performing products, and seasonal patterns. Provide recommendations for improving sales performance.",
      "files": ["sales_data.csv"]
    },
    "provider": "deepseek",
    "model_name": "deepseek-chat",
    "llm_config": {
      "temperature": 0.3,
      "max_tokens": 1500
    }
  }'
```

### 2. Analyze Employee Data

```bash
curl -X POST "http://localhost:8000/run-agent" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "file_data_analyst",
    "task_data": {
      "analysis_request": "Examine the employee data to identify salary patterns, performance correlations, and department-wise insights. Suggest improvements for HR policies.",
      "files": ["employee_data.xlsx"]
    },
    "provider": "openai",
    "model_name": "gpt-4",
    "llm_config": {
      "temperature": 0.2,
      "max_tokens": 1200
    }
  }'
```

### 3. Multi-File Comprehensive Analysis

```bash
curl -X POST "http://localhost:8000/run-agent" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "file_data_analyst",
    "task_data": {
      "analysis_request": "Perform a comprehensive analysis across all available data files. Identify cross-dataset correlations and provide strategic business recommendations.",
      "include_all_files": true
    },
    "provider": "deepseek",
    "model_name": "deepseek-chat",
    "llm_config": {
      "temperature": 0.4,
      "max_tokens": 2000
    }
  }'
```

### 4. Specific File Pattern Analysis

```bash
curl -X POST "http://localhost:8000/run-agent" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "file_data_analyst",
    "task_data": {
      "analysis_request": "Analyze all CSV files to identify data quality issues and suggest data cleaning strategies.",
      "file_pattern": "*.csv"
    },
    "provider": "deepseek",
    "llm_config": {
      "temperature": 0.1,
      "max_tokens": 1000
    }
  }'
```

### 5. Enhanced Workflow with File Analysis

```bash
curl -X POST "http://localhost:8000/run-enhanced-workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": [
      {
        "agent": "file_data_analyst",
        "task_data": {
          "analysis_request": "Analyze sales and employee data to extract key business metrics and trends.",
          "files": ["sales_data.csv", "employee_data.xlsx"]
        },
        "provider": "deepseek",
        "model_name": "deepseek-chat",
        "llm_config": {
          "temperature": 0.3,
          "max_tokens": 1500
        }
      },
      {
        "agent": "content_writer",
        "task_data": {
          "topic": "Business Intelligence Report",
          "audience": "executives",
          "format": "executive_summary",
          "tone": "professional"
        },
        "provider": "openai",
        "model_name": "gpt-4",
        "llm_config": {
          "temperature": 0.7,
          "max_tokens": 1200
        }
      }
    ],
    "default_provider": "deepseek"
  }'
```

## File Processing Features

### Supported File Types

1. **CSV Files** (`.csv`)
   - Automatic data type detection
   - Statistical summaries
   - Column analysis

2. **Excel Files** (`.xlsx`, `.xls`)
   - Multi-sheet support
   - Data validation
   - Numeric analysis

3. **PDF Files** (`.pdf`)
   - Text extraction
   - Content analysis
   - Document structure recognition

4. **Word Documents** (`.docx`)
   - Text extraction
   - Document analysis
   - Content summarization

5. **Text Files** (`.txt`, `.md`)
   - Content analysis
   - Text summarization
   - Pattern recognition

### Available Agent Methods

The `FileDataAnalyst` agent provides convenience methods:

- `analyze_sales_data(filename)` - Quick sales analysis
- `analyze_employee_data(filename)` - HR data insights
- `compare_multiple_datasets(filenames)` - Cross-dataset analysis
- `get_available_files_info()` - File inventory

## Python Usage Examples

```python
from agents import FileDataAnalyst, AgentFactory

# Create agent directly
agent = FileDataAnalyst(provider="deepseek")

# Or use factory
agent = AgentFactory.create_agent(
    "file_data_analyst",
    provider="deepseek",
    model_name="deepseek-chat"
)

# Quick sales analysis
result = agent.analyze_sales_data("sales_data.csv")

# Multi-file analysis
result = agent.compare_multiple_datasets([
    "sales_data.csv", 
    "employee_data.xlsx"
])

# Custom analysis
result = agent.execute({
    "analysis_request": "Find correlations between sales and employee performance",
    "files": ["sales_data.csv", "employee_data.xlsx"]
})
```

## File Structure

```
autogen_project/
├── data/
│   ├── sales_data.csv
│   ├── employee_data.xlsx
│   ├── market_report.txt
│   └── [your data files]
├── agents/
│   ├── file_data_analyst.py
│   └── base_agent.py (enhanced with FileProcessor)
└── templates/
    └── data_analyst_with_files.txt
```

## Configuration

The agent automatically:
- Creates a `data/` directory if it doesn't exist
- Processes files based on their extensions
- Provides detailed error handling for unsupported formats
- Generates comprehensive data summaries for LLM analysis

## Best Practices

1. **File Organization**: Keep data files in the designated `data/` directory
2. **File Naming**: Use descriptive filenames that indicate content type
3. **Data Quality**: Ensure CSV/Excel files have proper headers
4. **File Size**: Large files may need chunking for optimal LLM processing
5. **Error Handling**: The system gracefully handles missing or corrupted files

This enhanced system provides powerful file processing capabilities while maintaining the flexibility and customization of the original agent framework.
