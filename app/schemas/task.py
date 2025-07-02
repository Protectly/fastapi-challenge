from datetime import datetime
from typing import Optional
from pydantic import BaseModel, validator
from enum import Enum


# Bug: Priority enum not used in Task models
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"  # Bug: Should use Priority enum
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    # Bug: Missing title length validation
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None

    # Bug: No validation for priority values here either


class TaskInDB(TaskBase):
    id: int
    is_completed: bool
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None  # Bug: This should not be Optional

    class Config:
        from_attributes = True


class Task(TaskInDB):
    pass


class TaskListResponse(BaseModel):
    tasks: list[Task]
    total: int
    # Bug: Missing pagination fields like page, size, etc.
