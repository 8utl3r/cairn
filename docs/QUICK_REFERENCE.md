# Quick Reference Card - Cairn MCP Server

**Keep this open while working!** This is your cheat sheet for common operations.

---

## 🚀 **DAILY COMMANDS**

```bash
# Start server
python mcp_server.py

# Run all tests
python test_live_services.py

# Check code quality
ruff check . --fix
mypy . --ignore-missing-imports --explicit-package-bases

# Health check
python -c "from enhanced_server import EnhancedMCPServer; s=EnhancedMCPServer(); print(f'✅ {len(s.service_handlers)} services, {len(s.tool_manager.list_registered_tools())} tools')"
```

---

## 🏗️ **ARCHITECTURE (Memorize)**

```
Client → mcp_server.py → EnhancedMCPServer → Service Handler → External API
```

**Files to know:**
- `enhanced_server.py` - Main server (don't touch core validation)
- `services/*_handler.py` - Service logic (safe to modify)
- `validation_tripwires.py` - Packet validation (don't touch rules)
- `bootstrap.py` - Environment loading (don't touch)

---

## ➕ **ADDING NEW SERVICE (15 min)**

1. **Copy existing handler:**
   ```bash
   cp services/todoist_handler.py services/your_service_handler.py
   ```

2. **Update services/__init__.py:**
   ```python
   from .your_service_handler import YourServiceHandler
   __all__ = [..., 'YourServiceHandler']
   ```

3. **Add to enhanced_server.py:**
   ```python
   'your_service': YourServiceHandler()
   ```

4. **Tools auto-register!** No other changes needed.

---

## 🔧 **SERVICE HANDLER PATTERN**

```python
class YourServiceHandler(BaseServiceHandler):
    def __init__(self):
        super().__init__("your_service")
        self.supported_actions = ["create", "read", "update", "delete", "list", "search"]
        self.supported_item_types = ["item1", "item2"]
    
    async def execute(self, action: str, payload: dict, item_type: str = None):
        # Your logic here - safe to modify
        pass
```

---

## 🚨 **TROUBLESHOOTING**

| Problem | Quick Fix |
|---------|-----------|
| "Service not available" | Check handler registered in enhanced_server.py |
| "Invalid tool_type" | Check validation_tripwires.py line ~119 |
| Tools not showing | Verify supported_actions/item_types in handler |
| Env vars not loading | Check bootstrap.py and .env file |
| Import errors | Run from mcp_packet_server directory |

---

## 🧪 **TESTING CHECKLIST**

Before committing, run:
- [ ] `ruff check . --fix` (linting)
- [ ] `mypy . --ignore-missing-imports` (types)
- [ ] `python test_live_services.py` (integration)
- [ ] Health check command above (basic)

---

## 📍 **KEY LOCATIONS**

- **Service handlers:** `mcp_packet_server/services/`
- **Main server:** `mcp_packet_server/enhanced_server.py`
- **Tests:** `mcp_packet_server/test_*.py`
- **Config:** `mcp_packet_server/pyproject.toml`
- **Environment:** `mcp_packet_server/.env`

---

## 🎯 **SUCCESS SIGNS**

✅ All tests pass  
✅ No linting errors  
✅ No type errors  
✅ Services respond to execute_packet  
✅ Tools auto-register  
✅ CI pipeline green  

---

**When in doubt: RUN THE TESTS!** They're your safety net.

**Full guide:** `docs/AGENT_OPERATIONS_GUIDE.md`

