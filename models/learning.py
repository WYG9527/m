from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Subject(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    topics: List[str] = Field(default_factory=list)

class Topic(BaseModel):
    id: str
    name: str
    subject_id: str
    description: Optional[str] = None
    prerequisites: List[str] = Field(default_factory=list)
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM

class Question(BaseModel):
    id: str
    topic_id: str
    question_text: str
    options: List[str] = Field(default_factory=list)
    correct_answer: int
    explanation: Optional[str] = None
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM

class Resource(BaseModel):
    id: str
    topic_id: str
    title: str
    type: str
    url: str
    duration: Optional[int] = None
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM

class LearningPath(BaseModel):
    student_id: str
    subject: str
    topics: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)
    questions: List[str] = Field(default_factory=list)
    estimated_duration_days: int = 7
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)