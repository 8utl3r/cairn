# Agent Operations Guide - Cairn MCP Packet Server

**This guide is your go-to reference for maintaining and operating the Cairn project.** Bookmark this file and refer to it whenever you need to understand how to work with the system.

## 🚨 **QUICK START FOR AGENTS**

### **1. First Time Setup (5 minutes)**
```bash
cd mcp_packet_server
pip install -r requirements.txt
cp env.example .env
# Edit .env with your API keys
python test_live_services.py  # Verify everything works
```

### **2. Daily Operations**
```bash
# Start the server
python mcp_server.py

# Run tests
python test_live_services.py

# Check code quality
ruff check .
mypy . --ignore-missing-imports --explicit-package-bases
```

---

## 🏗️ **SYSTEM ARCHITECTURE (Memorize This)**

### **Core Flow**
```
Client Request → mcp_server.py → EnhancedMCPServer → Service Handler → External API
                ↓
            JSON-RPC over stdin/stdout
```

### **Key Files & Their Purpose**
| File | Purpose | **Don't Touch** | **Safe to Modify** |
|------|---------|------------------|-------------------|
| `mcp_server.py` | MCP protocol entry point | ✅ Protocol logic | ❌ Service logic |
| `enhanced_server.py` | Main server with validation | ✅ Core validation | ❌ Service handlers |
| `services/*_handler.py` | Individual service logic | ❌ Base interface | ✅ Business logic |
| `validation_tripwires.py` | Packet validation system | ✅ Validation rules | ❌ Core logic |
| `bootstrap.py` | Environment loading | ✅ Auto-load logic | ❌ Loading mechanism |

### **Service Handler Pattern (Memorize)**
```python
class YourServiceHandler(BaseServiceHandler):
    def __init__(self):
        super().__init__("your_service")
        self.supported_actions = ["create", "read", "update", "delete", "list", "search"]
        self.supported_item_types = ["item1", "item2"]
    
    async def execute(self, action: str, payload: dict, item_type: str = None):
        # Your logic here
        pass
```

---

## 🔧 **MAINTENANCE OPERATIONS**

### **Adding a New Service (15 minutes)**
1. **Create handler file:**
   ```bash
   cp services/todoist_handler.py services/your_service_handler.py
   # Edit the new file
   ```

2. **Update services/__init__.py:**
   ```python
   from .your_service_handler import YourServiceHandler
   
   __all__ = [
       # ... existing ...
       'YourServiceHandler'
   ]
   ```

3. **Add to enhanced_server.py:**
   ```python
   from services import YourServiceHandler
   
   self.service_handlers = {
       # ... existing ...
       'your_service': YourServiceHandler()
   }
   ```

4. **Tools are automatically registered!** No other changes needed.

### **Updating Service Logic**
- **Safe to modify:** Business logic inside `execute()` method
- **Don't touch:** Method signature, error handling patterns, response format
- **Always test:** Run `python test_live_services.py` after changes

### **Adding New Actions or Item Types**
1. Update `supported_actions` or `supported_item_types` in handler
2. Add corresponding `_create_*`, `_read_*`, etc. methods
3. Tools are automatically generated
4. Run tests to verify

---

## 🚨 **TROUBLESHOOTING GUIDE**

### **Problem: "Service not available" error**
**Cause:** Service handler not properly registered
**Fix:**
```bash
# Check if handler is imported
grep -r "YourServiceHandler" services/__init__.py

# Check if handler is registered
grep -r "'your_service'" enhanced_server.py

# Restart server after changes
```

### **Problem: "Invalid tool_type" error**
**Cause:** Validation tripwires not updated
**Fix:**
```bash
# Check validation_tripwires.py line ~119
# Should have fallback: ['todoist', 'gcal', 'gmail', 'deep_pcb', 'your_service']
```

### **Problem: Tools not showing up**
**Cause:** Dynamic registry not working
**Fix:**
```bash
# Check handler has supported_actions and supported_item_types
# Run: python -c "from services.your_handler import YourHandler; h=YourHandler(); print(h.supported_actions)"
```

### **Problem: Environment variables not loading**
**Cause:** Bootstrap not working
**Fix:**
```bash
# Check bootstrap.py exists
# Check __init__.py imports bootstrap
# Verify .env file exists and has correct format
```

### **Problem: Import errors**
**Cause:** Python path issues
**Fix:**
```bash
# Always run from mcp_packet_server directory
cd mcp_packet_server
python your_script.py

# Or use absolute imports
from mcp_packet_server.services import YourHandler
```

---

## 🧪 **TESTING PROCEDURES**

### **Before Committing (Always Run)**
```bash
# 1. Lint check
ruff check . --fix

# 2. Type check
mypy . --ignore-missing-imports --explicit-package-bases

# 3. Live integration test
python test_live_services.py

# 4. Basic functionality test
python -c "
from enhanced_server import EnhancedMCPServer
server = EnhancedMCPServer()
print(f'✅ {len(server.service_handlers)} services loaded')
print(f'✅ {len(server.tool_manager.list_registered_tools())} tools registered')
"
```

### **Testing New Services**
```bash
# Create test file
cp test_todoist_integration.py test_your_service_integration.py
# Edit test file to test your service
python test_your_service_integration.py
```

### **Testing Validation System**
```bash
python test_enhanced_validation.py
```

---

## 📊 **MONITORING & DEBUGGING**

### **Server Health Check**
```bash
# Check service status
python -c "
from enhanced_server import EnhancedMCPServer
server = EnhancedMCPServer()
print('🔧 Services:', list(server.service_handlers.keys()))
print('📊 Tools:', len(server.tool_manager.list_registered_tools()))
print('🚨 Validation:', 'ACTIVE' if server.packet_tripwires else 'INACTIVE')
"
```

### **Packet Validation Debugging**
```bash
# Enable detailed logging in validation_tripwires.py
# Add print statements in _check_* methods
# Run with test packet to see validation flow
```

### **Tool Registry Debugging**
```bash
# Check what tools are registered
python -c "
from enhanced_server import EnhancedMCPServer
server = EnhancedMCPServer()
for name, service in server.tool_manager.tool_registry.items():
    print(f'{name} -> {service}')
"
```

---

## 🔐 **SECURITY & CREDENTIALS**

### **Adding New API Keys**
1. **Never commit credentials** - they're in `.gitignore`
2. **Add to `.env`:**
   ```bash
   YOUR_SERVICE_API_KEY=your_key_here
   YOUR_SERVICE_API_URL=https://api.yourservice.com
   ```
3. **Update handler to read from environment:**
   ```python
   self.api_key = os.getenv("YOUR_SERVICE_API_KEY")
   if not self.api_key:
       print("⚠️  Warning: YOUR_SERVICE_API_KEY not set - running in mock mode")
   ```

### **Credential Rotation**
```bash
# Update .env file
# Restart server (no code changes needed)
# Test with: python test_live_services.py
```

---

## 🚀 **DEPLOYMENT & CI/CD**

### **Local Development**
```bash
# Standard workflow
git pull
pip install -r requirements.txt
# Make changes
ruff check . --fix
mypy . --ignore-missing-imports
python test_live_services.py
git add .
git commit -m "Description of changes"
git push
```

### **CI Pipeline (Automatic)**
- **Linting** runs on every push
- **Type checking** runs on every push  
- **Integration tests** run if credentials available
- **Basic tests** always run

### **Production Deployment**
```bash
# 1. Ensure .env has production credentials
# 2. Run health check
python -c "from enhanced_server import EnhancedMCPServer; server = EnhancedMCPServer(); print('✅ Ready')"
# 3. Start server
python mcp_server.py
```

---

## 📚 **REFERENCE MATERIALS**

### **Quick Commands**
```bash
# List all services
python -c "from enhanced_server import EnhancedMCPServer; s=EnhancedMCPServer(); print(list(s.service_handlers.keys()))"

# List all tools
python -c "from enhanced_server import EnhancedMCPServer; s=EnhancedMCPServer(); print(len(s.tool_manager.list_registered_tools()))"

# Test specific service
python -c "from services.todoist_handler import TodoistServiceHandler; h=TodoistServiceHandler(); print(h.supported_actions)"
```

### **File Locations**
- **Service handlers:** `mcp_packet_server/services/`
- **Core server:** `mcp_packet_server/enhanced_server.py`
- **Validation:** `mcp_packet_server/validation_tripwires.py`
- **Tests:** `mcp_packet_server/test_*.py`
- **Configuration:** `mcp_packet_server/pyproject.toml`

### **Common Patterns**
- **Error handling:** Always use `_create_response()` method
- **Mock mode:** Fall back gracefully when credentials missing
- **Validation:** Use tripwire system for packet validation
- **Tool registration:** Automatic from service handler capabilities

---

## 🆘 **EMERGENCY PROCEDURES**

### **System Won't Start**
```bash
# 1. Check Python version (need 3.9+)
python --version

# 2. Check dependencies
pip list | grep -E "(ruff|mypy|python-dotenv)"

# 3. Check imports
python -c "from enhanced_server import EnhancedMCPServer; print('✅ Imports OK')"

# 4. Check environment
ls -la .env
cat .env | head -5
```

### **Services Not Responding**
```bash
# 1. Check service handlers loaded
python -c "from enhanced_server import EnhancedMCPServer; s=EnhancedMCPServer(); print(s.service_handlers.keys())"

# 2. Check tool registry
python -c "from enhanced_server import EnhancedMCPServer; s=EnhancedMCPServer(); print(len(s.tool_manager.tool_registry))"

# 3. Check validation system
python -c "from enhanced_server import EnhancedMCPServer; s=EnhancedMCPServer(); print('Validation:', s.packet_tripwires is not None)"
```

### **Validation Errors**
```bash
# 1. Check packet format
python -c "
from packet import MCPPacket
p = MCPPacket(tool_type='todoist', action='create', item_type='task', payload={})
print('✅ Packet created:', p.validate())
"

# 2. Check validation tripwires
python -c "
from validation_tripwires import PacketValidationTripwires
t = PacketValidationTripwires()
print('✅ Tripwires loaded')
"
```

---

## 📝 **CHANGE LOG TEMPLATE**

When making changes, use this format:

```markdown
## [Date] - [Change Type]

### What Changed
- Description of changes

### Why Changed  
- Reason for changes

### Testing Done
- [ ] Linting passes
- [ ] Type checking passes  
- [ ] Live integration tests pass
- [ ] Basic functionality tests pass

### Files Modified
- `path/to/file.py` - what changed
- `path/to/another.py` - what changed

### Breaking Changes
- None (or describe if any)

### Rollback Plan
- How to undo if needed
```

---

## 🎯 **SUCCESS METRICS**

Your work is successful when:
- ✅ **All tests pass** (`python test_live_services.py`)
- ✅ **No linting errors** (`ruff check .`)
- ✅ **No type errors** (`mypy .`)
- ✅ **Services respond** to `execute_packet` calls
- ✅ **Tools auto-register** when adding new services
- ✅ **Validation catches** malformed packets
- ✅ **CI pipeline** shows green on GitHub

---

**Remember: When in doubt, run the tests!** The test suite is your safety net and will catch most issues before they become problems.

**Last Updated:** July 2025  
**Maintained By:** AI Agents & Human Developers  
**Next Review:** When architecture changes or new patterns emerge

