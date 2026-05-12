from typing import Dict, List, Any
from datetime import datetime, timedelta
from models.student import Student
from models.learning import Topic, Resource, LearningPath, DifficultyLevel
from utils.database import DatabaseManager

class LearningPlanAgent:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_learning_path(self, student_id: str, subject: str, diagnosis: Dict = None) -> LearningPath:
        if not diagnosis:
            from agents.learning_diagnosis_agent import LearningDiagnosisAgent
            diagnosis_agent = LearningDiagnosisAgent(self.db_manager)
            diagnosis = diagnosis_agent.diagnose_student(student_id)
        
        topics = self.db_manager.get_topics_by_subject(subject)
        weak_topics = [w["topic"] for w in diagnosis.get("weak_topics", [])]
        
        topic_order = self._determine_topic_order(topics, weak_topics)
        
        resources = []
        questions = []
        
        for topic in topic_order:
            topic_resources = self.db_manager.get_resources_by_topic(topic.id)
            resources.extend([r.id for r in topic_resources[:3]])
            
            topic_questions = self.db_manager.get_questions_by_topic(topic.id)
            questions.extend([q.id for q in topic_questions[:5]])
        
        estimated_days = self._calculate_duration(topic_order, weak_topics)
        
        learning_path = LearningPath(
            student_id=student_id,
            subject=subject,
            topics=[t.name for t in topic_order],
            resources=resources,
            questions=questions,
            estimated_duration_days=estimated_days
        )
        
        return learning_path
    
    def _determine_topic_order(self, topics: List[Topic], weak_topics: List[str]) -> List[Topic]:
        topic_dict = {t.name: t for t in topics}
        ordered_topics = []
        visited = set()
        
        def visit(topic: Topic):
            if topic.name in visited:
                return
            visited.add(topic.name)
            
            for prereq in topic.prerequisites:
                if prereq in topic_dict and prereq not in visited:
                    visit(topic_dict[prereq])
            
            ordered_topics.append(topic)
        
        for topic in topics:
            visit(topic)
        
        weak_first = [t for t in ordered_topics if t.name in weak_topics]
        strong_later = [t for t in ordered_topics if t.name not in weak_topics]
        
        return weak_first + strong_later
    
    def _calculate_duration(self, topics: List[Topic], weak_topics: List[str]) -> int:
        base_days = len(topics)
        
        for topic in topics:
            if topic.difficulty == DifficultyLevel.HARD:
                base_days += 2
            elif topic.difficulty == DifficultyLevel.MEDIUM:
                base_days += 1
            
            if topic.name in weak_topics:
                base_days += 2
        
        return base_days
    
    def generate_daily_plan(self, student_id: str, learning_path: LearningPath, day: int) -> Dict[str, Any]:
        total_topics = len(learning_path.topics)
        topics_per_day = max(1, total_topics // learning_path.estimated_duration_days)
        
        start_idx = (day - 1) * topics_per_day
        end_idx = min(start_idx + topics_per_day, total_topics)
        
        day_topics = learning_path.topics[start_idx:end_idx]
        
        plan = {
            "day": day,
            "student_id": student_id,
            "subject": learning_path.subject,
            "topics": day_topics,
            "resources": [],
            "exercises": [],
            "estimated_time_minutes": 0
        }
        
        for topic_name in day_topics:
            topic = next((t for t in self.db_manager.get_topics_by_subject(learning_path.subject) if t.name == topic_name), None)
            if topic:
                resources = self.db_manager.get_resources_by_topic(topic.id)
                plan["resources"].extend([r.model_dump() for r in resources[:2]])
                
                questions = self.db_manager.get_questions_by_topic(topic.id)
                plan["exercises"].extend([q.model_dump() for q in questions[:3]])
                
                plan["estimated_time_minutes"] += 45
        
        return plan
    
    def update_learning_path(self, student_id: str, learning_path: LearningPath, progress: Dict) -> LearningPath:
        completed_topics = progress.get("completed_topics", [])
        
        remaining_topics = [t for t in learning_path.topics if t not in completed_topics]
        learning_path.topics = remaining_topics
        
        completed_resources = []
        completed_questions = []
        
        for topic_name in completed_topics:
            topic = next((t for t in self.db_manager.get_topics_by_subject(learning_path.subject) if t.name == topic_name), None)
            if topic:
                topic_resources = self.db_manager.get_resources_by_topic(topic.id)
                completed_resources.extend([r.id for r in topic_resources])
                
                topic_questions = self.db_manager.get_questions_by_topic(topic.id)
                completed_questions.extend([q.id for q in topic_questions])
        
        learning_path.resources = [r for r in learning_path.resources if r not in completed_resources]
        learning_path.questions = [q for q in learning_path.questions if q not in completed_questions]
        
        learning_path.estimated_duration_days = max(1, len(remaining_topics))
        
        return learning_path