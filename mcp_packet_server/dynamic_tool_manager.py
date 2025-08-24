"""
Dynamic Tool Manager for MCP Packet Server
Implements intelligent tool loading, unloading, and eviction policies
"""

import importlib
import sys
import time
from collections import OrderedDict, defaultdict
from typing import Any, Dict, Optional, Callable
from threading import Lock


class ToolCache:
    """Base tool cache with configurable capacity"""
    
    def __init__(self, capacity: int = 80):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = Lock()
    
    def get_tool(self, tool_name: str) -> Optional[Any]:
        """Get a tool from cache"""
        with self.lock:
            if tool_name in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(tool_name)
                return self.cache[tool_name]
            return None
    
    def add_tool(self, tool_name: str, tool_module: Any) -> None:
        """Add a tool to cache, evicting if necessary"""
        with self.lock:
            if len(self.cache) >= self.capacity:
                # Evict least recently used tool
                evicted_tool = self.cache.popitem(last=False)
                self._unload_tool(evicted_tool[0], evicted_tool[1])
            
            self.cache[tool_name] = tool_module
            self.cache.move_to_end(tool_name)
    
    def remove_tool(self, tool_name: str) -> bool:
        """Remove a specific tool from cache"""
        with self.lock:
            if tool_name in self.cache:
                tool_module = self.cache.pop(tool_name)
                self._unload_tool(tool_name, tool_module)
                return True
            return False
    
    def _unload_tool(self, tool_name: str, tool_module: Any) -> None:
        """Unload a tool module from memory"""
        try:
            # Remove from sys.modules if it exists
            if tool_name in sys.modules:
                del sys.modules[tool_name]
            
            # Call cleanup method if it exists
            if hasattr(tool_module, 'cleanup'):
                tool_module.cleanup()
                
            print(f"🔄 Unloaded tool: {tool_name}")
        except Exception as e:
            print(f"⚠️  Warning: Error unloading tool {tool_name}: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                "capacity": self.capacity,
                "current_size": len(self.cache),
                "available_slots": self.capacity - len(self.cache),
                "cached_tools": list(self.cache.keys())
            }


class LFUCache(ToolCache):
    """Least Frequently Used cache implementation"""
    
    def __init__(self, capacity: int = 80):
        super().__init__(capacity)
        self.usage_count = defaultdict(int)
        self.access_time = {}
    
    def get_tool(self, tool_name: str) -> Optional[Any]:
        """Get a tool and update usage statistics"""
        with self.lock:
            if tool_name in self.cache:
                # Update usage count and access time
                self.usage_count[tool_name] += 1
                self.access_time[tool_name] = time.time()
                
                # Move to end (most recently used)
                self.cache.move_to_end(tool_name)
                return self.cache[tool_name]
            return None
    
    def add_tool(self, tool_name: str, tool_module: Any) -> None:
        """Add a tool, evicting least frequently used if necessary"""
        with self.lock:
            if len(self.cache) >= self.capacity:
                # Find least frequently used tool
                least_used_tool = min(self.usage_count, key=self.usage_count.get)
                
                # If there's a tie, use access time as tiebreaker
                if self.usage_count[least_used_tool] == 1:
                    least_used_tool = min(self.access_time, key=self.access_time.get)
                
                # Evict the least frequently used tool
                evicted_tool = self.cache.pop(least_used_tool)
                self.usage_count.pop(least_used_tool)
                self.access_time.pop(least_used_tool)
                self._unload_tool(least_used_tool, evicted_tool)
                
                print(f"🗑️  Evicted least frequently used tool: {least_used_tool}")
            
            # Add new tool
            self.cache[tool_name] = tool_module
            self.usage_count[tool_name] = 1
            self.access_time[tool_name] = time.time()
            self.cache.move_to_end(tool_name)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get detailed cache statistics including usage patterns"""
        with self.lock:
            stats = super().get_cache_stats()
            stats.update({
                "usage_patterns": dict(self.usage_count),
                "access_times": dict(self.access_time),
                "least_used_tool": min(self.usage_count, key=self.usage_count.get) if self.usage_count else None,
                "most_used_tool": max(self.usage_count, key=self.usage_count.get) if self.usage_count else None
            })
            return stats


class DynamicToolManager:
    """Manages dynamic loading and unloading of MCP tools"""
    
    def __init__(self, cache_policy: str = "lfu", max_tools: int = 80):
        """
        Initialize the dynamic tool manager
        
        Args:
            cache_policy: "lru" (Least Recently Used) or "lfu" (Least Frequently Used)
            max_tools: Maximum number of tools to keep in memory
        """
        self.max_tools = max_tools
        self.cache_policy = cache_policy
        
        if cache_policy == "lfu":
            self.cache = LFUCache(max_tools)
        else:
            self.cache = ToolCache(max_tools)
        
        # Tool registry - maps tool names to their loading functions
        self.tool_registry: Dict[str, Callable] = {}
        
        # Service-based tool grouping
        self.service_tools: Dict[str, list] = {
            "todoist": [],
            "gcal": [],
            "gmail": []
        }
        
        # Initialize with core tools (always loaded)
        self.core_tools = {
            "execute_packet",
            "list_services", 
            "get_service_schema",
            "batch_execute",
            "get_packet_status"
        }
        
        print(f"🚀 Dynamic Tool Manager initialized with {cache_policy.upper()} policy")
        print(f"📊 Maximum tools: {max_tools}")
    
    def register_tool(self, tool_name: str, loader_function: Callable, service: str = None) -> None:
        """Register a tool with its loading function"""
        self.tool_registry[tool_name] = loader_function
        
        if service and service in self.service_tools:
            self.service_tools[service].append(tool_name)
        
        print(f"📝 Registered tool: {tool_name} (service: {service or 'core'})")
    
    def load_tool(self, tool_name: str) -> Optional[Any]:
        """Dynamically load a tool when needed"""
        # Check if tool is already loaded
        cached_tool = self.cache.get_tool(tool_name)
        if cached_tool:
            return cached_tool
        
        # Check if tool is registered
        if tool_name not in self.tool_registry:
            print(f"❌ Tool not registered: {tool_name}")
            return None
        
        try:
            # Load the tool using its loader function
            print(f"🔄 Loading tool: {tool_name}")
            tool_module = self.tool_registry[tool_name]()
            
            # Add to cache (will evict if necessary)
            self.cache.add_tool(tool_name, tool_module)
            
            print(f"✅ Successfully loaded tool: {tool_name}")
            return tool_module
            
        except Exception as e:
            print(f"❌ Failed to load tool {tool_name}: {e}")
            return None
    
    def load_service_tools(self, service_name: str) -> Dict[str, Any]:
        """Load all tools for a specific service"""
        if service_name not in self.service_tools:
            print(f"❌ Unknown service: {service_name}")
            return {}
        
        loaded_tools = {}
        for tool_name in self.service_tools[service_name]:
            tool = self.load_tool(tool_name)
            if tool:
                loaded_tools[tool_name] = tool
        
        print(f"🔧 Loaded {len(loaded_tools)} tools for service: {service_name}")
        return loaded_tools
    
    def unload_tool(self, tool_name: str) -> bool:
        """Manually unload a specific tool"""
        if tool_name in self.core_tools:
            print(f"⚠️  Cannot unload core tool: {tool_name}")
            return False
        
        return self.cache.remove_tool(tool_name)
    
    def unload_service_tools(self, service_name: str) -> int:
        """Unload all tools for a specific service"""
        if service_name not in self.service_tools:
            return 0
        
        unloaded_count = 0
        for tool_name in self.service_tools[service_name]:
            if self.unload_tool(tool_name):
                unloaded_count += 1
        
        print(f"🗑️  Unloaded {unloaded_count} tools for service: {service_name}")
        return unloaded_count
    
    def get_tool_status(self, tool_name: str) -> Dict[str, Any]:
        """Get status of a specific tool"""
        is_loaded = tool_name in self.cache.cache
        is_core = tool_name in self.core_tools
        
        status = {
            "name": tool_name,
            "loaded": is_loaded,
            "core_tool": is_core,
            "service": self._get_tool_service(tool_name)
        }
        
        if is_loaded and hasattr(self.cache, 'usage_count'):
            status["usage_count"] = self.cache.usage_count.get(tool_name, 0)
            status["last_access"] = self.cache.access_time.get(tool_name, None)
        
        return status
    
    def _get_tool_service(self, tool_name: str) -> Optional[str]:
        """Get the service that a tool belongs to"""
        for service, tools in self.service_tools.items():
            if tool_name in tools:
                return service
        return None
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size in MB
            "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size in MB
            "percent": process.memory_percent(),
            "available_mb": psutil.virtual_memory().available / 1024 / 1024
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        stats = self.cache.get_cache_stats()
        
        # Calculate hit rate (if we had access to request counts)
        # For now, return basic cache statistics
        return {
            "cache_stats": stats,
            "memory_usage": self.get_memory_usage(),
            "policy": self.cache_policy,
            "max_tools": self.max_tools
        }
    
    def optimize_cache(self) -> Dict[str, Any]:
        """Optimize the cache based on current usage patterns"""
        if not hasattr(self.cache, 'usage_count'):
            return {"message": "Optimization only available for LFU cache"}
        
        with self.cache.lock:
            # Find tools with very low usage that could be evicted
            low_usage_threshold = 1
            candidates = [
                tool for tool, count in self.cache.usage_count.items()
                if count <= low_usage_threshold and tool not in self.core_tools
            ]
            
            if not candidates:
                return {"message": "No optimization needed"}
            
            # Evict low-usage tools
            evicted_count = 0
            for tool in candidates:
                if self.cache.remove_tool(tool):
                    evicted_count += 1
            
            return {
                "message": f"Optimization completed",
                "evicted_tools": evicted_count,
                "freed_memory": "See memory_usage for details"
            }
    
    def set_cache_policy(self, policy: str) -> None:
        """Change the cache policy at runtime"""
        if policy not in ["lru", "lfu"]:
            raise ValueError("Policy must be 'lru' or 'lfu'")
        
        if policy == self.cache_policy:
            return
        
        print(f"🔄 Changing cache policy from {self.cache_policy.upper()} to {policy.upper()}")
        
        # Create new cache with current tools
        current_tools = dict(self.cache.cache)
        
        if policy == "lfu":
            self.cache = LFUCache(self.max_tools)
        else:
            self.cache = ToolCache(self.max_tools)
        
        # Restore tools to new cache
        for tool_name, tool_module in current_tools.items():
            self.cache.add_tool(tool_name, tool_module)
        
        self.cache_policy = policy
        print(f"✅ Cache policy changed to {policy.upper()}")
    
    def set_max_tools(self, new_max: int) -> None:
        """Change the maximum number of tools at runtime"""
        if new_max < len(self.cache.cache):
            print(f"⚠️  Warning: New max ({new_max}) is less than current loaded tools ({len(self.cache.cache)})")
            print("   Some tools will be evicted")
        
        self.max_tools = new_max
        self.cache.capacity = new_max
        
        # If we're over the new limit, evict excess tools
        while len(self.cache.cache) > new_max:
            if hasattr(self.cache, 'usage_count'):
                # For LFU, evict least frequently used
                least_used = min(self.cache.usage_count, key=self.cache.usage_count.get)
                self.cache.remove_tool(least_used)
            else:
                # For LRU, evict least recently used
                evicted = self.cache.cache.popitem(last=False)
                self.cache._unload_tool(evicted[0], evicted[1])
        
        print(f"✅ Maximum tools changed to {new_max}")


# Example usage and testing
def create_example_tool_manager():
    """Create an example tool manager for demonstration"""
    
    def load_todoist_tool():
        """Mock loader for Todoist tool"""
        return {"type": "todoist", "loaded": True, "timestamp": time.time()}
    
    def load_gcal_tool():
        """Mock loader for Google Calendar tool"""
        return {"type": "gcal", "loaded": True, "timestamp": time.time()}
    
    def load_gmail_tool():
        """Mock loader for Gmail tool"""
        return {"type": "gmail", "loaded": True, "timestamp": time.time()}
    
    # Create manager with LFU policy and 10 tool limit
    manager = DynamicToolManager(cache_policy="lfu", max_tools=10)
    
    # Register tools
    manager.register_tool("todoist_task_creator", load_todoist_tool, "todoist")
    manager.register_tool("todoist_project_manager", load_todoist_tool, "todoist")
    manager.register_tool("gcal_event_creator", load_gcal_tool, "gcal")
    manager.register_tool("gcal_calendar_manager", load_gcal_tool, "gcal")
    manager.register_tool("gmail_sender", load_gmail_tool, "gmail")
    manager.register_tool("gmail_searcher", load_gmail_tool, "gmail")
    
    return manager


if __name__ == "__main__":
    # Test the dynamic tool manager
    print("🧪 Testing Dynamic Tool Manager")
    print("=" * 40)
    
    manager = create_example_tool_manager()
    
    # Test loading tools
    print("\n1️⃣ Loading tools...")
    manager.load_tool("todoist_task_creator")
    manager.load_tool("gcal_event_creator")
    manager.load_tool("gmail_sender")
    
    # Check cache stats
    print("\n2️⃣ Cache statistics:")
    stats = manager.get_performance_metrics()
    print(f"   Cache size: {stats['cache_stats']['current_size']}/{stats['cache_stats']['capacity']}")
    print(f"   Available slots: {stats['cache_stats']['available_slots']}")
    
    # Test eviction by loading more tools
    print("\n3️⃣ Testing eviction...")
    for i in range(8):  # This will trigger eviction
        manager.load_tool(f"test_tool_{i}")
    
    print("\n4️⃣ Final cache statistics:")
    stats = manager.get_performance_metrics()
    print(f"   Cache size: {stats['cache_stats']['current_size']}/{stats['cache_stats']['capacity']}")
    print(f"   Cached tools: {stats['cache_stats']['cached_tools']}")
    
    print("\n✅ Dynamic Tool Manager test completed!")
