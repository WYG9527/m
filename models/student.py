from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class StudentProfile(BaseModel):
    student_id: str
    name: str
    age: int
    grade: str
    subjects: List[str] = Field(default_factory=list)
    learning_style: Optional[str] = None
    goals: List[str] = Field(default_factory=list)

class LearningProgress(BaseModel):
    student_id: str
    subject: str
    topic: str
    score: float = 0.0
    completed: bool = False
    last_practice_date: Optional[datetime] = None
    practice_count: int = 0
    weak_points: List[str] = Field(default_factory=list)

class Student(BaseModel):
    profile: StudentProfile
    progress: List[LearningProgress] = Field(default_factory=list)
    question_history: List[Dict] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)