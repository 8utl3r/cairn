#!/usr/bin/env python3
"""
Simple test script for Cairn MCP Server
"""

import asyncio
import sys
from pathlib import Path

# Add the cairn package to the path
sys.path.insert(0, str(Path(__file__).parent))

from cairn.database import CairnDatabase
from cairn.models import Step, Path, StepType, StepStatus, PathStatus


def test_database():
    """Test basic database operations"""
    print("Testing Cairn Database...")
    
    # Initialize database
    db = CairnDatabase("test_cairn.db")
    
    # Create a test step
    step = Step(
        id="test-step-1",
        name="Test Step",
        description="A test step for testing",
        step_type=StepType.PROMPT,
        content="This is a test prompt content",
        context={"test": True},
        metadata={"version": "1.0"}
    )
    
    # Create a test path
    path = Path(
        id="test-path-1",
        name="Test Path",
        description="A test workflow path",
        steps=[step],
        tags=["test", "example"],
        status=PathStatus.DRAFT
    )
    
    try:
        # Test step operations
        print("Creating step...")
        created_step = db.create_step(step)
        print(f"✓ Step created: {created_step.id}")
        
        # Test path operations
        print("Creating path...")
        created_path = db.create_path(path)
        print(f"✓ Path created: {created_path.id}")
        
        # Test retrieval
        print("Retrieving path...")
        retrieved_path = db.get_path(created_path.id)
        if retrieved_path:
            print(f"✓ Path retrieved: {retrieved_path.name} with {len(retrieved_path.steps)} steps")
        else:
            print("✗ Failed to retrieve path")
        
        # Test search
        print("Searching paths...")
        search_results = db.search_paths(
            SearchQuery(query="test", limit=10)
        )
        print(f"✓ Found {len(search_results)} paths")
        
        print("\n🎉 All database tests passed!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_database()
