from typing import Dict, List, Any, Optional
from models.student import Student, LearningProgress
from models.learning import Topic, Resource, Question, DifficultyLevel
from utils.database import DatabaseManager
import numpy as np

class ContentRecommendationAgent:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def recommend_resources(self, student_id: str, subject: str, limit: int = 5) -> List[Dict]:
        student = self.db_manager.get_student(student_id)
        if not student:
            return []
        
        progress_dict = {(p.subject, p.topic): p for p in student.progress}
        
        topics = self.db_manager.get_topics_by_subject(subject)
        recommendations = []
        
        for topic in topics:
            topic_key = (subject, topic.name)
            progress = progress_dict.get(topic_key)
            
            resources = self.db_manager.get_resources_by_topic(topic.id)
            
            for resource in resources:
                score = self._calculate_resource_score(resource, progress, topic)
                recommendations.append({
                    "resource": resource.model_dump(),
                    "topic": topic.name,
                    "score": score,
                    "reason": self._generate_reason(resource, progress)
                })
        
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations[:limit]
    
    def _calculate_resource_score(self, resource: Resource, progress: Optional[LearningProgress], topic: Topic) -> float:
        score = 50.0
        
        if progress:
            if progress.score < 60:
                if resource.difficulty == DifficultyLevel.EASY:
                    score += 30
                elif resource.difficulty == DifficultyLevel.MEDIUM:
                    score += 15
            elif progress.score >= 80:
                if resource.difficulty == DifficultyLevel.HARD:
                    score += 20
                elif resource.difficulty == DifficultyLevel.MEDIUM:
                    score += 10
        
        if resource.type == "video":
            score += 10
        elif resource.type == "interactive":
            score += 15
        
        if resource.duration and resource.duration < 15:
            score += 5
        
        return score
    
    def _generate_reason(self, resource: Resource, progress: Optional[LearningProgress]) -> str:
        reasons = []
        
        if progress:
            if progress.score < 60:
                reasons.append("根据您的学习进度，推荐基础资源帮助巩固")
            elif progress.score >= 80:
                reasons.append("您已掌握基础知识，推荐进阶资源")
        
        if resource.type == "video":
            reasons.append("视频资源更直观易懂")
        elif resource.type == "interactive":
            reasons.append("互动资源有助于加深理解")
        
        if resource.duration and resource.duration < 15:
            reasons.append("短时长资源，适合碎片化学习")
        
        return "; ".join(reasons) if reasons else "推荐学习此资源"
    
    def recommend_questions(self, student_id: str, subject: str, limit: int = 10) -> List[Dict]:
        student = self.db_manager.get_student(student_id)
        if not student:
            return []
        
        progress_dict = {(p.subject, p.topic): p for p in student.progress}
        
        topics = self.db_manager.get_topics_by_subject(subject)
        recommendations = []
        
        for topic in topics:
            topic_key = (subject, topic.name)
            progress = progress_dict.get(topic_key)
            
            questions = self.db_manager.get_questions_by_topic(topic.id)
            
            for question in questions:
                score = self._calculate_question_score(question, progress)
                recommendations.append({
                    "question": question.model_dump(),
                    "topic": topic.name,
                    "score": score
                })
        
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations[:limit]
    
    def _calculate_question_score(self, question: Question, progress: Optional[LearningProgress]) -> float:
        score = 50.0
        
        if progress:
            if progress.score < 60:
                if question.difficulty == DifficultyLevel.EASY:
                    score += 30
                elif question.difficulty == DifficultyLevel.MEDIUM:
                    score += 10
            elif 60 <= progress.score < 80:
                if question.difficulty == DifficultyLevel.MEDIUM:
                    score += 20
                elif question.difficulty == DifficultyLevel.EASY:
                    score += 10
            else:
                if question.difficulty == DifficultyLevel.HARD:
                    score += 30
                elif question.difficulty == DifficultyLevel.MEDIUM:
                    score += 15
        
        return score
    
    def recommend_next_topic(self, student_id: str, subject: str) -> Optional[Dict]:
        student = self.db_manager.get_student(student_id)
        if not student:
            return None
        
        topics = self.db_manager.get_topics_by_subject(subject)
        progress_dict = {(p.subject, p.topic): p for p in student.progress}
        
        topic_scores = []
        
        for topic in topics:
            topic_key = (subject, topic.name)
            progress = progress_dict.get(topic_key)
            
            prereqs_met = all(
                (subject, prereq) in progress_dict and 
                progress_dict[(subject, prereq)].score >= 70
                for prereq in topic.prerequisites
            )
            
            if prereqs_met:
                current_score = progress.score if progress else 0
                priority = self._calculate_topic_priority(topic, current_score)
                topic_scores.append({
                    "topic": topic.model_dump(),
                    "current_score": current_score,
                    "priority": priority
                })
        
        if topic_scores:
            topic_scores.sort(key=lambda x: x["priority"], reverse=True)
            return topic_scores[0]
        
        return None
    
    def _calculate_topic_priority(self, topic: Topic, current_score: float) -> float:
        base_priority = 50.0
        
        if current_score < 60:
            base_priority += 30
        elif current_score >= 80:
            base_priority -= 10
        
        if topic.difficulty == DifficultyLevel.HARD:
            base_priority += 15
        elif topic.difficulty == DifficultyLevel.EASY:
            base_priority += 5
        
        if topic.prerequisites:
            base_priority += 10
        
        return base_priority