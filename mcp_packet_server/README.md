# MCP Packet Server

A **Model Context Protocol (MCP) Packet Server** that provides a unified interface to multiple external services through standardized JSON-RPC packets.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation
```bash
cd mcp_packet_server
pip install -r requirements.txt
```

### Environment Setup
1. Copy `env.example` to `.env`
2. Add your service API keys:
   ```bash
   TODOIST_API_TOKEN=your_todoist_token
   DEEPPCB_API_KEY=your_deeppcb_key
   GOOGLE_CREDENTIALS_FILE=/path/to/google_credentials.json
   ```

### Run the Server
```bash
# Start MCP server (stdin/stdout mode)
python mcp_server.py

# Or run the enhanced server directly
python enhanced_server.py
```

## 🏗️ Architecture

### Core Components
- **`mcp_server.py`** - MCP protocol entry point (JSON-RPC over stdin/stdout)
- **`enhanced_server.py`** - Main server with dynamic tool registry and validation
- **`services/`** - Modular service handlers for each external API
- **`validation_tripwires.py`** - Comprehensive packet validation system

### Service Handlers
Each service handler implements the `BaseServiceHandler` interface:
- **`todoist_handler.py`** - Task & project management
- **`google_calendar_handler.py`** - Calendar & event management  
- **`gmail_handler.py`** - Email operations
- **`deep_pcb_handler.py`** - PCB design automation

### Dynamic Tool Registry
Tools are automatically discovered from service handlers:
- **114 tools** dynamically registered based on `supported_actions` × `supported_item_types`
- No hard-coded tool lists - adding a new service automatically exposes its capabilities
- Generic tools (e.g., `create_todoist`) and specific tools (e.g., `create_todoist_task`)

## 🔧 Development

### Code Quality
```bash
# Run linter
ruff check .

# Run type checker  
mypy . --ignore-missing-imports --explicit-package-bases

# Auto-fix linting issues
ruff check . --fix
```

### Testing
```bash
# Run live integration tests
python test_live_services.py

# Test individual services
python test_todoist_integration.py
python test_gmail_integration.py
python test_deeppcb.py
```

### Adding a New Service
1. Create `services/your_service_handler.py`
2. Inherit from `BaseServiceHandler`
3. Implement `supported_actions` and `supported_item_types`
4. Override `execute()` method
5. Add to `services/__init__.py`
6. Tools are automatically registered!

## 📡 MCP Protocol

### Core Tools
- **`execute_packet`** - Execute any operation via standardized packet
- **`list_services`** - List available services and capabilities
- **`get_service_schema`** - Get detailed schema for a service

### Packet Structure
```json
{
  "tool_type": "todoist",
  "action": "create", 
  "item_type": "task",
  "payload": {
    "content": "Buy groceries",
    "due_date": "tomorrow"
  },
  "priority": "normal"
}
```

### Validation Tripwires
- **Format validation** - Field presence, types, enum values
- **Service availability** - Target service exists and is registered
- **Action support** - Service supports requested action
- **Item type support** - Service supports requested item type

## 🔐 Security

- API keys stored in `.env` (git-ignored)
- Automatic environment loading via `bootstrap.py`
- Graceful fallback to mock mode when credentials missing
- No secrets ever committed to version control

## 🧪 CI/CD

GitHub Actions workflow runs on every push/PR:
- ✅ Linting (ruff)
- ✅ Type checking (mypy)  
- ✅ Live integration tests (with secrets)
- ✅ Basic functionality tests

## 📚 Documentation

- **`docs/ARCHITECTURE.md`** - High-level architecture overview
- **`MODULAR_ARCHITECTURE_REFACTOR.md`** - Refactoring details
- **`DEEPPCB_SERVICE_IMPLEMENTATION.md`** - DeepPCB integration guide

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is part of the Cairn platform.
