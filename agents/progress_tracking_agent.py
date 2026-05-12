from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from models.student import Student, LearningProgress
from models.learning import Subject, Topic
from utils.database import DatabaseManager
import numpy as np

class ProgressTrackingAgent:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def update_progress(self, student_id: str, subject: str, topic: str, score: float, completed: bool = False):
        student = self.db_manager.get_student(student_id)
        if not student:
            return {"error": "学生不存在"}
        
        existing_progress = next(
            (p for p in student.progress if p.subject == subject and p.topic == topic),
            None
        )
        
        if existing_progress:
            existing_progress.score = score
            existing_progress.completed = completed
            existing_progress.last_practice_date = datetime.now()
            existing_progress.practice_count += 1
            
            if score < 60 and topic not in existing_progress.weak_points:
                existing_progress.weak_points.append(topic)
            elif score >= 70 and topic in existing_progress.weak_points:
                existing_progress.weak_points.remove(topic)
        else:
            weak_points = [topic] if score < 60 else []
            new_progress = LearningProgress(
                student_id=student_id,
                subject=subject,
                topic=topic,
                score=score,
                completed=completed,
                last_practice_date=datetime.now(),
                practice_count=1,
                weak_points=weak_points
            )
            student.progress.append(new_progress)
        
        student.updated_at = datetime.now()
        self.db_manager.save_student(student)
        
        return {"success": True, "message": "进度已更新"}
    
    def get_student_progress(self, student_id: str) -> Dict[str, Any]:
        student = self.db_manager.get_student(student_id)
        if not student:
            return {"error": "学生不存在"}
        
        result = {
            "student_id": student_id,
            "name": student.profile.name,
            "total_topics": len(student.progress),
            "completed_topics": sum(1 for p in student.progress if p.completed),
            "average_score": np.mean([p.score for p in student.progress]) if student.progress else 0,
            "progress_by_subject": {},
            "weekly_activity": self._calculate_weekly_activity(student),
            "learning_streak": self._calculate_learning_streak(student),
            "weak_points": self._get_weak_points(student)
        }
        
        for progress in student.progress:
            if progress.subject not in result["progress_by_subject"]:
                result["progress_by_subject"][progress.subject] = {
                    "topics": 0,
                    "completed": 0,
                    "average_score": []
                }
            
            result["progress_by_subject"][progress.subject]["topics"] += 1
            result["progress_by_subject"][progress.subject]["completed"] += 1 if progress.completed else 0
            result["progress_by_subject"][progress.subject]["average_score"].append(progress.score)
        
        for subject in result["progress_by_subject"]:
            scores = result["progress_by_subject"][subject]["average_score"]
            result["progress_by_subject"][subject]["average_score"] = np.mean(scores) if scores else 0
        
        return result
    
    def _calculate_weekly_activity(self, student: Student) -> List[Dict]:
        activity = [{"day": d, "count": 0} for d in ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]]
        
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        
        for progress in student.progress:
            if progress.last_practice_date and progress.last_practice_date >= week_ago:
                day_index = progress.last_practice_date.weekday()
                activity[day_index]["count"] += 1
        
        return activity
    
    def _calculate_learning_streak(self, student: Student) -> int:
        if not student.progress:
            return 0
        
        dates = sorted([p.last_practice_date for p in student.progress if p.last_practice_date], reverse=True)
        
        if not dates:
            return 0
        
        streak = 1
        today = datetime.now().date()
        
        if dates[0].date() != today and dates[0].date() != today - timedelta(days=1):
            return 0
        
        for i in range(1, len(dates)):
            prev_date = dates[i-1].date()
            curr_date = dates[i].date()
            
            if prev_date - curr_date == timedelta(days=1):
                streak += 1
            else:
                break
        
        return streak
    
    def _get_weak_points(self, student: Student) -> List[Dict]:
        weak_points = []
        for progress in student.progress:
            if progress.score < 60:
                weak_points.append({
                    "subject": progress.subject,
                    "topic": progress.topic,
                    "score": progress.score,
                    "last_practice": progress.last_practice_date.isoformat() if progress.last_practice_date else None
                })
        
        weak_points.sort(key=lambda x: x["score"])
        return weak_points
    
    def generate_progress_report(self, student_id: str, period: str = "week") -> Dict[str, Any]:
        progress = self.get_student_progress(student_id)
        
        if "error" in progress:
            return progress
        
        report = {
            "student_id": student_id,
            "name": progress["name"],
            "report_period": period,
            "generated_at": datetime.now().isoformat(),
            "summary": {},
            "details": {},
            "recommendations": []
        }
        
        report["summary"] = {
            "overall_score": round(progress["average_score"], 2),
            "completion_rate": round((progress["completed_topics"] / progress["total_topics"]) * 100, 2) if progress["total_topics"] > 0 else 0,
            "learning_streak": progress["learning_streak"],
            "weekly_activity": progress["weekly_activity"]
        }
        
        report["details"] = {
            "progress_by_subject": progress["progress_by_subject"],
            "weak_points": progress["weak_points"]
        }
        
        report["recommendations"] = self._generate_report_recommendations(progress)
        
        return report
    
    def _generate_report_recommendations(self, progress: Dict) -> List[str]:
        recommendations = []
        
        if progress["average_score"] < 60:
            recommendations.append("整体学习需要加强，建议增加练习频率")
        
        if progress["learning_streak"] < 3:
            recommendations.append("建议保持连续学习，养成良好的学习习惯")
        
        if len(progress["weak_points"]) > 0:
            weak_topics = ", ".join([f"{wp['subject']}-{wp['topic']}" for wp in progress["weak_points"]])
            recommendations.append(f"需要重点关注以下薄弱环节：{weak_topics}")
        
        completion_rate = (progress["completed_topics"] / progress["total_topics"]) * 100 if progress["total_topics"] > 0 else 0
        if completion_rate < 50:
            recommendations.append("学习完成度较低，建议合理安排学习时间")
        
        return recommendations
    
    def compare_with_peers(self, student_id: str, subject: str) -> Dict[str, Any]:
        student = self.db_manager.get_student(student_id)
        if not student:
            return {"error": "学生不存在"}
        
        all_students = self.db_manager.get_all_students()
        subject_scores = []
        
        for s in all_students:
            subject_progress = next((p for p in s.progress if p.subject == subject), None)
            if subject_progress:
                subject_scores.append(subject_progress.score)
        
        if not subject_scores:
            return {"error": "没有足够的同伴数据"}
        
        student_score = next((p.score for p in student.progress if p.subject == subject), 0)
        
        return {
            "student_score": student_score,
            "average_score": round(np.mean(subject_scores), 2),
            "median_score": round(np.median(subject_scores), 2),
            "highest_score": max(subject_scores),
            "lowest_score": min(subject_scores),
            "student_rank": sum(1 for s in subject_scores if s > student_score) + 1,
            "total_students": len(subject_scores)
        }