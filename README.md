# Cairn

A Model Context Protocol (MCP) server that serves as a repository for AI workflow paths and steps, designed to increase replicability and consistency of AI agents.

## What is Cairn?

Cairn acts as a "pathfinder" that stores and serves optimized workflows for AI agents, eliminating the need for them to rediscover solutions from scratch. It provides:

- **Workflow Management**: Create, read, update, delete AI workflow paths and steps
- **Version Control**: Git-like branching for workflow evolution
- **Metadata Tracking**: Success rates, execution time, user feedback, and usage patterns
- **Context Injection**: Provide AI agents with proven workflows and relevant context

## Architecture

- **Paths**: Complete workflows made up of sequential steps
- **Steps**: Individual actions with prompts and context
- **MCP Server**: Exposes workflows through standardized MCP tools and resources
- **SQLite Backend**: Lightweight, reliable data storage
- **HTTP API**: RESTful interface for easy integration

## Features

### Core Functionality
- ✅ **Workflow Creation**: Build complex workflows with multiple steps
- ✅ **Step Types**: Support for prompts, tool calls, context injection, conditionals, and loops
- ✅ **Versioning**: Track changes and maintain workflow history
- ✅ **Branching**: Create experimental branches from stable workflows
- ✅ **Search & Discovery**: Find workflows by tags, content, and metadata
- ✅ **Execution Tracking**: Monitor success rates and performance metrics

### MCP Tools
- `create_path` - Create new workflow paths
- `get_path` - Retrieve specific workflows
- `search_paths` - Find workflows by criteria
- `create_branch` - Create workflow variants
- `record_execution` - Track workflow performance

### MCP Resources
- `cairn://paths` - List all available workflows
- `cairn://paths/{id}` - Get specific workflow details

## Getting Started

### Prerequisites
- Python 3.9+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone git@github.com:8utl3r/cairn.git
   cd cairn
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**
   ```bash
   # Start the HTTP server
   python3 -m cairn.http_server
   
   # Or run the basic MCP server
   python3 main.py
   ```

The server will start on `http://localhost:8000` by default.

## Usage

### HTTP API

#### Server Status
```bash
curl http://localhost:8000/
```

#### List Available Tools
```bash
curl http://localhost:8000/tools
```

#### List Available Resources
```bash
curl http://localhost:8000/resources
```

#### Create a Workflow Path
```bash
curl -X POST http://localhost:8000/tool \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "create_path",
    "arguments": {
      "name": "Data Analysis Workflow",
      "description": "Standard workflow for data analysis tasks",
      "steps": [
        {
          "name": "Data Loading",
          "description": "Load and validate input data",
          "step_type": "prompt",
          "content": "Please provide the data file path and format."
        },
        {
          "name": "Data Processing",
          "description": "Clean and transform the data",
          "step_type": "tool_call",
          "content": "Process the data according to specifications."
        }
      ],
      "tags": ["data-analysis", "workflow"],
      "branch": "main"
    }
  }'
```

#### Search Workflows
```bash
curl -X POST http://localhost:8000/tool \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "search_paths",
    "arguments": {
      "query": "data analysis",
      "tags": ["workflow"],
      "limit": 10
    }
  }'
```

#### Get Workflow Resource
```bash
curl http://localhost:8000/resource/cairn://paths/{path_id}
```

### Python Client

```python
import requests

# Create a workflow
response = requests.post('http://localhost:8000/tool', json={
    'name': 'create_path',
    'arguments': {
        'name': 'My Workflow',
        'description': 'A custom workflow',
        'steps': [
            {
                'name': 'Step 1',
                'description': 'First step',
                'step_type': 'prompt',
                'content': 'What would you like to do?'
            }
        ]
    }
})

if response.status_code == 200:
    result = response.json()
    path_id = result['path_id']
    print(f"Created workflow: {path_id}")
```

## Testing

### Run the Test Client
```bash
# Start the server in one terminal
python3 -m cairn.http_server

# Run tests in another terminal
python3 test_client.py
```

### Run Database Tests
```bash
python3 test_cairn.py
```

## Project Structure

```
cairn/
├── __init__.py          # Package initialization
├── models.py            # Data models (Step, Path, etc.)
├── database.py          # SQLite database layer
├── server.py            # Core MCP server implementation
├── http_server.py       # HTTP server wrapper
├── main.py              # Entry point for basic server
├── test_cairn.py        # Database tests
├── test_client.py       # HTTP API tests
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Database Schema

### Tables
- **steps**: Individual workflow steps with metadata
- **paths**: Complete workflows with step collections
- **path_executions**: Execution history and performance metrics

### Key Features
- JSON serialization for flexible metadata
- Indexed queries for performance
- Foreign key relationships for data integrity

## Development

### Adding New Tools
1. Define the tool schema in `_register_tools()`
2. Implement the tool logic in a private method
3. Add the tool to `handle_tool_call()`

### Adding New Resources
1. Define the resource in `_register_resources()`
2. Implement resource retrieval in `get_resource()`

### Database Changes
1. Update the schema in `init_database()`
2. Add migration logic if needed
3. Update serialization methods

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[License information to be added]

## Roadmap

- [ ] **Authentication & Authorization**: User management and access control
- [ ] **Advanced Search**: Full-text search and semantic matching
- [ ] **Workflow Templates**: Pre-built workflow patterns
- [ ] **Collaboration**: Multi-user workflow editing and sharing
- [ ] **API Rate Limiting**: Protect against abuse
- [ ] **Monitoring & Analytics**: Advanced performance insights
- [ ] **Plugin System**: Extensible workflow step types
- [ ] **Import/Export**: Workflow portability across systems

## Support

For questions, issues, or contributions, please:
1. Check the existing issues
2. Create a new issue with detailed information
3. Join the discussion in the project repository

---

**Cairn** - Building the path to consistent AI workflows 🗿
