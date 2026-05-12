from typing import Dict, List, Optional, Any
from models.student import Student, LearningProgress
from models.learning import Topic, Question, DifficultyLevel
from utils.database import DatabaseManager
import numpy as np

class LearningDiagnosisAgent:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def diagnose_student(self, student_id: str) -> Dict[str, Any]:
        student = self.db_manager.get_student(student_id)
        if not student:
            return {"error": "学生不存在"}
        
        diagnosis_result = {
            "student_id": student_id,
            "name": student.profile.name,
            "overall_score": 0.0,
            "subject_scores": {},
            "weak_topics": [],
            "strong_topics": [],
            "suggestions": []
        }
        
        subject_scores = {}
        topic_scores = {}
        
        for progress in student.progress:
            subject = progress.subject
            topic = progress.topic
            
            if subject not in subject_scores:
                subject_scores[subject] = []
            subject_scores[subject].append(progress.score)
            
            topic_scores[(subject, topic)] = progress.score
        
        for subject, scores in subject_scores.items():
            avg_score = np.mean(scores) if scores else 0
            diagnosis_result["subject_scores"][subject] = avg_score
            
            topics = self.db_manager.get_topics_by_subject(subject)
            for topic in topics:
                topic_key = (subject, topic.name)
                score = topic_scores.get(topic_key, 0)
                
                if score < 60:
                    diagnosis_result["weak_topics"].append({
                        "subject": subject,
                        "topic": topic.name,
                        "score": score,
                        "difficulty": topic.difficulty.value
                    })
                elif score >= 80:
                    diagnosis_result["strong_topics"].append({
                        "subject": subject,
                        "topic": topic.name,
                        "score": score
                    })
        
        if diagnosis_result["subject_scores"]:
            diagnosis_result["overall_score"] = np.mean(list(diagnosis_result["subject_scores"].values()))
        
        diagnosis_result["suggestions"] = self._generate_suggestions(diagnosis_result)
        
        return diagnosis_result
    
    def _generate_suggestions(self, diagnosis: Dict) -> List[str]:
        suggestions = []
        
        if diagnosis["overall_score"] < 60:
            suggestions.append("建议加强基础知识学习，可以从简单的概念开始复习")
        
        for weak in diagnosis["weak_topics"]:
            suggestions.append(f"在{weak['subject']}的{weak['topic']}方面需要加强练习")
        
        if len(diagnosis["strong_topics"]) > 0:
            suggestions.append("继续保持在以下强项的学习：" + ", ".join([t["topic"] for t in diagnosis["strong_topics"]]))
        
        return suggestions
    
    def generate_diagnostic_test(self, student_id: str, subject: str, num_questions: int = 5) -> List[Dict]:
        topics = self.db_manager.get_topics_by_subject(subject)
        questions = []
        
        for topic in topics:
            topic_questions = self.db_manager.get_questions_by_topic(topic.id)
            if topic_questions:
                sampled = np.random.choice(topic_questions, min(2, len(topic_questions)), replace=False)
                questions.extend([q.model_dump() for q in sampled])
        
        if len(questions) > num_questions:
            questions = list(np.random.choice(questions, num_questions, replace=False))
        
        return questions
    
    def evaluate_test(self, student_id: str, answers: Dict[str, int]) -> Dict[str, Any]:
        results = {
            "student_id": student_id,
            "total_score": 0,
            "correct_count": 0,
            "total_questions": len(answers),
            "topic_scores": {},
            "weak_points": []
        }
        
        for question_id, user_answer in answers.items():
            question = self.db_manager.get_question(question_id)
            if question:
                topic = self.db_manager.get_topic(question.topic_id)
                topic_name = topic.name if topic else "未知"
                
                if topic_name not in results["topic_scores"]:
                    results["topic_scores"][topic_name] = {"correct": 0, "total": 0}
                
                results["topic_scores"][topic_name]["total"] += 1
                
                if user_answer == question.correct_answer:
                    results["correct_count"] += 1
                    results["topic_scores"][topic_name]["correct"] += 1
        
        if results["total_questions"] > 0:
            results["total_score"] = (results["correct_count"] / results["total_questions"]) * 100
        
        for topic_name, score_info in results["topic_scores"].items():
            if score_info["total"] > 0:
                topic_score = (score_info["correct"] / score_info["total"]) * 100
                if topic_score < 60:
                    results["weak_points"].append(topic_name)
        
        return results