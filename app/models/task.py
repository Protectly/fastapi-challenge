from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)  # Bug: Should allow longer titles
    description = Column(Text)
    is_completed = Column(Boolean, default=False)
    priority = Column(
        String(10), default="medium"
    )  # Bug: No validation for priority values
    due_date = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Bug: Missing nullable=False constraint
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Bug: Wrong back_populates reference - should be "tasks" not "task"
    owner = relationship("User", back_populates="task")

    def __repr__(self):
        return f"<Task(title='{self.title}', completed={self.is_completed})>"
