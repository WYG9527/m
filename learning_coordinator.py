from typing import Dict, List, Any, Optional
from models.student import Student, StudentProfile
from models.learning import LearningPath
from agents import (
    LearningDiagnosisAgent,
    LearningPlanAgent,
    ContentRecommendationAgent,
    QAAgent,
    ProgressTrackingAgent
)
from utils.database import DatabaseManager
import os

class LearningCoordinator:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "data")
        
        self.db_manager = DatabaseManager(data_dir)
        
        self.diagnosis_agent = LearningDiagnosisAgent(self.db_manager)
        self.plan_agent = LearningPlanAgent(self.db_manager)
        self.recommendation_agent = ContentRecommendationAgent(self.db_manager)
        self.qa_agent = QAAgent(self.db_manager)
        self.progress_agent = ProgressTrackingAgent(self.db_manager)
    
    def register_student(self, student_id: str, name: str, age: int, grade: str, subjects: List[str]) -> Dict:
        existing_student = self.db_manager.get_student(student_id)
        if existing_student:
            return {"error": "学生已存在"}
        
        profile = StudentProfile(
            student_id=student_id,
            name=name,
            age=age,
            grade=grade,
            subjects=subjects
        )
        
        student = Student(profile=profile)
        self.db_manager.save_student(student)
        
        return {"success": True, "message": "学生注册成功"}
    
    def diagnose_student(self, student_id: str) -> Dict:
        return self.diagnosis_agent.diagnose_student(student_id)
    
    def create_learning_plan(self, student_id: str, subject: str) -> Dict:
        student = self.db_manager.get_student(student_id)
        if not student:
            return {"error": "学生不存在"}
        
        diagnosis = self.diagnosis_agent.diagnose_student(student_id)
        if "error" in diagnosis:
            return diagnosis
        
        learning_path = self.plan_agent.create_learning_path(student_id, subject, diagnosis)
        
        return {
            "success": True,
            "learning_path": learning_path.model_dump()
        }
    
    def get_daily_plan(self, student_id: str, subject: str, day: int) -> Dict:
        diagnosis = self.diagnosis_agent.diagnose_student(student_id)
        if "error" in diagnosis:
            return diagnosis
        
        learning_path = self.plan_agent.create_learning_path(student_id, subject, diagnosis)
        daily_plan = self.plan_agent.generate_daily_plan(student_id, learning_path, day)
        
        return {"success": True, "daily_plan": daily_plan}
    
    def recommend_resources(self, student_id: str, subject: str, limit: int = 5) -> Dict:
        resources = self.recommendation_agent.recommend_resources(student_id, subject, limit)
        return {"success": True, "resources": resources}
    
    def recommend_questions(self, student_id: str, subject: str, limit: int = 10) -> Dict:
        questions = self.recommendation_agent.recommend_questions(student_id, subject, limit)
        return {"success": True, "questions": questions}
    
    def recommend_next_topic(self, student_id: str, subject: str) -> Dict:
        topic = self.recommendation_agent.recommend_next_topic(student_id, subject)
        if topic:
            return {"success": True, "topic": topic}
        return {"success": False, "message": "没有推荐的下一个学习主题"}
    
    def ask_question(self, student_id: str, question: str, subject: str = None) -> Dict:
        answer = self.qa_agent.answer_question(student_id, question, subject)
        return {"success": True, "answer": answer}
    
    def update_progress(self, student_id: str, subject: str, topic: str, score: float, completed: bool = False) -> Dict:
        return self.progress_agent.update_progress(student_id, subject, topic, score, completed)
    
    def get_progress(self, student_id: str) -> Dict:
        return self.progress_agent.get_student_progress(student_id)
    
    def generate_report(self, student_id: str, period: str = "week") -> Dict:
        return self.progress_agent.generate_progress_report(student_id, period)
    
    def compare_with_peers(self, student_id: str, subject: str) -> Dict:
        return self.progress_agent.compare_with_peers(student_id, subject)
    
    def run_diagnostic_test(self, student_id: str, subject: str, answers: Dict[str, int]) -> Dict:
        questions = self.diagnosis_agent.generate_diagnostic_test(student_id, subject)
        question_ids = [q["id"] for q in questions]
        
        valid_answers = {q_id: ans for q_id, ans in answers.items() if q_id in question_ids}
        result = self.diagnosis_agent.evaluate_test(student_id, valid_answers)
        
        for topic_name in result["topic_scores"]:
            topic_score = (result["topic_scores"][topic_name]["correct"] / result["topic_scores"][topic_name]["total"]) * 100
            self.progress_agent.update_progress(student_id, subject, topic_name, topic_score)
        
        return {"success": True, "test_result": result}