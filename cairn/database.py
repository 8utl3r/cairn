"""
SQLite database layer for Cairn MCP Server
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import uuid

from .models import Step, Path as PathModel, PathExecution, SearchQuery


class CairnDatabase:
    """SQLite database manager for Cairn"""
    
    def __init__(self, db_path: str = "cairn.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS steps (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    step_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    context TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    parent_step_id TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS paths (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    steps TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    status TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    branch TEXT NOT NULL,
                    parent_path_id TEXT,
                    success_rate REAL,
                    avg_execution_time REAL,
                    usage_count INTEGER NOT NULL DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS path_executions (
                    id TEXT PRIMARY KEY,
                    path_id TEXT NOT NULL,
                    user_id TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    success INTEGER NOT NULL,
                    execution_time REAL,
                    feedback TEXT,
                    metadata TEXT NOT NULL,
                    FOREIGN KEY (path_id) REFERENCES paths (id)
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_paths_tags ON paths(tags)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_paths_status ON paths(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_paths_branch ON paths(branch)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_steps_type ON steps(step_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_steps_status ON steps(status)")
            
            conn.commit()
    
    def _serialize_dict(self, data: Dict[str, Any]) -> str:
        """Serialize dictionary to JSON string"""
        return json.dumps(data, default=str)
    
    def _deserialize_dict(self, data: str) -> Dict[str, Any]:
        """Deserialize JSON string to dictionary"""
        return json.loads(data) if data else {}
    
    def _serialize_list(self, data: List[str]) -> str:
        """Serialize list to JSON string"""
        return json.dumps(data)
    
    def _deserialize_list(self, data: str) -> List[str]:
        """Deserialize JSON string to list"""
        return json.loads(data) if data else []
    
    def _serialize_steps(self, steps: List[Step]) -> str:
        """Serialize list of steps to JSON string"""
        return json.dumps([step.dict() for step in steps], default=str)
    
    def _deserialize_steps(self, data: str) -> List[Step]:
        """Deserialize JSON string to list of steps"""
        steps_data = json.loads(data) if data else []
        return [Step(**step_data) for step_data in steps_data]
    
    # Step operations
    def create_step(self, step: Step) -> Step:
        """Create a new step"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO steps VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                step.id,
                step.name,
                step.description,
                step.step_type.value,
                step.content,
                self._serialize_dict(step.context),
                self._serialize_dict(step.metadata),
                step.status.value,
                step.created_at.isoformat(),
                step.updated_at.isoformat(),
                step.version,
                step.parent_step_id
            ))
            conn.commit()
        return step
    
    def get_step(self, step_id: str) -> Optional[Step]:
        """Get a step by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM steps WHERE id = ?", (step_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return Step(
                id=row[0],
                name=row[1],
                description=row[2],
                step_type=row[3],
                content=row[4],
                context=self._deserialize_dict(row[5]),
                metadata=self._deserialize_dict(row[6]),
                status=row[7],
                created_at=datetime.fromisoformat(row[8]),
                updated_at=datetime.fromisoformat(row[9]),
                version=row[10],
                parent_step_id=row[11]
            )
    
    def update_step(self, step: Step) -> Step:
        """Update an existing step"""
        step.updated_at = datetime.utcnow()
        step.version += 1
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE steps SET 
                    name = ?, description = ?, step_type = ?, content = ?, 
                    context = ?, metadata = ?, status = ?, updated_at = ?, version = ?
                WHERE id = ?
            """, (
                step.name,
                step.description,
                step.step_type.value,
                step.content,
                self._serialize_dict(step.context),
                self._serialize_dict(step.metadata),
                step.status.value,
                step.updated_at.isoformat(),
                step.version,
                step.id
            ))
            conn.commit()
        return step
    
    def delete_step(self, step_id: str) -> bool:
        """Delete a step"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM steps WHERE id = ?", (step_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # Path operations
    def create_path(self, path: PathModel) -> PathModel:
        """Create a new path"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO paths VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                path.id,
                path.name,
                path.description,
                self._serialize_steps(path.steps),
                self._serialize_list(path.tags),
                path.status.value,
                self._serialize_dict(path.metadata),
                path.created_at.isoformat(),
                path.updated_at.isoformat(),
                path.version,
                path.branch,
                path.parent_path_id,
                path.success_rate,
                path.avg_execution_time,
                path.usage_count
            ))
            conn.commit()
        return path
    
    def get_path(self, path_id: str, branch: str = "main") -> Optional[PathModel]:
        """Get a path by ID and branch"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM paths WHERE id = ? AND branch = ?
            """, (path_id, branch))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return PathModel(
                id=row[0],
                name=row[1],
                description=row[2],
                steps=self._deserialize_steps(row[3]),
                tags=self._deserialize_list(row[4]),
                status=row[5],
                metadata=self._deserialize_dict(row[6]),
                created_at=datetime.fromisoformat(row[7]),
                updated_at=datetime.fromisoformat(row[8]),
                version=row[9],
                branch=row[10],
                parent_path_id=row[11],
                success_rate=row[12],
                avg_execution_time=row[13],
                usage_count=row[14]
            )
    
    def update_path(self, path: PathModel) -> PathModel:
        """Update an existing path"""
        path.updated_at = datetime.utcnow()
        path.version += 1
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE paths SET 
                    name = ?, description = ?, steps = ?, tags = ?, status = ?,
                    metadata = ?, updated_at = ?, version = ?, success_rate = ?,
                    avg_execution_time = ?, usage_count = ?
                WHERE id = ? AND branch = ?
            """, (
                path.name,
                path.description,
                self._serialize_steps(path.steps),
                self._serialize_list(path.tags),
                path.status.value,
                self._serialize_dict(path.metadata),
                path.updated_at.isoformat(),
                path.version,
                path.success_rate,
                path.avg_execution_time,
                path.usage_count,
                path.id,
                path.branch
            ))
            conn.commit()
        return path
    
    def delete_path(self, path_id: str, branch: str = "main") -> bool:
        """Delete a path"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM paths WHERE id = ? AND branch = ?
            """, (path_id, branch))
            conn.commit()
            return cursor.rowcount > 0
    
    def search_paths(self, query: SearchQuery) -> List[PathModel]:
        """Search for paths based on criteria"""
        with sqlite3.connect(self.db_path) as conn:
            # Build dynamic query
            sql = "SELECT * FROM paths WHERE 1=1"
            params = []
            
            if query.query:
                sql += " AND (name LIKE ? OR description LIKE ?)"
                params.extend([f"%{query.query}%", f"%{query.query}%"])
            
            if query.tags:
                # Search for paths containing any of the specified tags
                placeholders = ",".join(["?" for _ in query.tags])
                sql += f" AND tags LIKE '%{query.tags[0]}%'"
                for tag in query.tags[1:]:
                    sql += f" AND tags LIKE '%{tag}%'"
            
            if query.status:
                sql += " AND status = ?"
                params.append(query.status.value)
            
            if query.min_success_rate is not None:
                sql += " AND success_rate >= ?"
                params.append(query.min_success_rate)
            
            if query.max_execution_time is not None:
                sql += " AND avg_execution_time <= ?"
                params.append(query.max_execution_time)
            
            sql += " ORDER BY usage_count DESC, success_rate DESC LIMIT ?"
            params.append(query.limit)
            
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            
            paths = []
            for row in rows:
                path = PathModel(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    steps=self._deserialize_steps(row[3]),
                    tags=self._deserialize_list(row[4]),
                    status=row[5],
                    metadata=self._deserialize_dict(row[6]),
                    created_at=datetime.fromisoformat(row[7]),
                    updated_at=datetime.fromisoformat(row[8]),
                    version=row[9],
                    branch=row[10],
                    parent_path_id=row[11],
                    success_rate=row[12],
                    avg_execution_time=row[13],
                    usage_count=row[14]
                )
                paths.append(path)
            
            return paths
    
    def create_branch(self, path_id: str, base_branch: str, new_branch: str) -> Optional[PathModel]:
        """Create a new branch from an existing path"""
        base_path = self.get_path(path_id, base_branch)
        if not base_path:
            return None
        
        # Create new path with new branch
        new_path = PathModel(
            id=str(uuid.uuid4()),
            name=f"{base_path.name} ({new_branch})",
            description=base_path.description,
            steps=base_path.steps,
            tags=base_path.tags,
            status=base_path.status,
            metadata=base_path.metadata,
            branch=new_branch,
            parent_path_id=base_path.id,
            version=1
        )
        
        return self.create_path(new_path)
    
    def record_execution(self, execution: PathExecution) -> PathExecution:
        """Record a path execution for metadata tracking"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO path_executions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution.id,
                execution.path_id,
                execution.user_id,
                execution.start_time.isoformat(),
                execution.end_time.isoformat() if execution.end_time else None,
                1 if execution.success else 0,
                execution.execution_time,
                execution.feedback,
                self._serialize_dict(execution.metadata)
            ))
            
            # Update path usage count and success rate
            if execution.end_time and execution.execution_time:
                conn.execute("""
                    UPDATE paths SET usage_count = usage_count + 1
                    WHERE id = ?
                """, (execution.path_id,))
                
                # Calculate new success rate and avg execution time
                cursor = conn.execute("""
                    SELECT success, execution_time FROM path_executions 
                    WHERE path_id = ? AND end_time IS NOT NULL
                """, (execution.path_id,))
                executions = cursor.fetchall()
                
                if executions:
                    success_count = sum(1 for ex in executions if ex[0])
                    total_count = len(executions)
                    success_rate = success_count / total_count
                    
                    avg_time = sum(ex[1] for ex in executions if ex[1]) / total_count
                    
                    conn.execute("""
                        UPDATE paths SET 
                            success_rate = ?, avg_execution_time = ?
                        WHERE id = ?
                    """, (success_rate, avg_time, execution.path_id))
            
            conn.commit()
        
        return execution
