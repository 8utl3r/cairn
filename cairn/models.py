"""
Data models for Cairn MCP Server
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class StepType(str, Enum):
    """Types of workflow steps"""
    PROMPT = "prompt"
    TOOL_CALL = "tool_call"
    CONTEXT_INJECTION = "context_injection"
    CONDITIONAL = "conditional"
    LOOP = "loop"


class StepStatus(str, Enum):
    """Status of workflow steps"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    TESTING = "testing"


class Step(BaseModel):
    """Individual workflow step"""
    id: str = Field(..., description="Unique identifier for the step")
    name: str = Field(..., description="Human-readable name for the step")
    description: str = Field(..., description="Description of what the step does")
    step_type: StepType = Field(..., description="Type of step")
    content: str = Field(..., description="The actual step content (prompt, tool call, etc.)")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context for the step")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")
    status: StepStatus = Field(default=StepStatus.DRAFT, description="Current status of the step")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1, description="Step version number")
    parent_step_id: Optional[str] = Field(None, description="Parent step if this is a modification")


class PathStatus(str, Enum):
    """Status of workflow paths"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class Path(BaseModel):
    """Complete workflow path"""
    id: str = Field(..., description="Unique identifier for the path")
    name: str = Field(..., description="Human-readable name for the path")
    description: str = Field(..., description="Description of what the path accomplishes")
    steps: List[Step] = Field(..., description="Ordered list of steps in the path")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    status: PathStatus = Field(default=PathStatus.DRAFT, description="Current status of the path")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1, description="Path version number")
    branch: str = Field(default="main", description="Git-like branch name")
    parent_path_id: Optional[str] = Field(None, description="Parent path if this is a modification")
    success_rate: Optional[float] = Field(None, description="Historical success rate")
    avg_execution_time: Optional[float] = Field(None, description="Average execution time in seconds")
    usage_count: int = Field(default=0, description="Number of times this path has been used")


class PathExecution(BaseModel):
    """Record of path execution for metadata tracking"""
    id: str = Field(..., description="Unique identifier for the execution")
    path_id: str = Field(..., description="ID of the executed path")
    user_id: Optional[str] = Field(None, description="User who executed the path")
    start_time: datetime = Field(..., description="When execution started")
    end_time: Optional[datetime] = Field(None, description="When execution completed")
    success: bool = Field(..., description="Whether execution was successful")
    execution_time: Optional[float] = Field(None, description="Total execution time in seconds")
    feedback: Optional[str] = Field(None, description="User feedback on the path")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional execution metadata")


class SearchQuery(BaseModel):
    """Query for searching paths and steps"""
    query: str = Field(..., description="Search query string")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    step_types: Optional[List[StepType]] = Field(None, description="Filter by step types")
    status: Optional[PathStatus] = Field(None, description="Filter by path status")
    min_success_rate: Optional[float] = Field(None, description="Minimum success rate")
    max_execution_time: Optional[float] = Field(None, description="Maximum execution time")
    limit: int = Field(default=50, description="Maximum number of results")
