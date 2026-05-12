import json
import os
from typing import Dict, List, Optional
from models.student import Student, StudentProfile, LearningProgress
from models.learning import Subject, Topic, Question, Resource

class DatabaseManager:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.students_file = os.path.join(data_dir, "students.json")
        self.subjects_file = os.path.join(data_dir, "subjects.json")
        self.topics_file = os.path.join(data_dir, "topics.json")
        self.questions_file = os.path.join(data_dir, "questions.json")
        self.resources_file = os.path.join(data_dir, "resources.json")
        
        self._init_files()
    
    def _init_files(self):
        for file_path in [self.students_file, self.subjects_file, 
                         self.topics_file, self.questions_file, self.resources_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False)
    
    def save_student(self, student: Student):
        students = self._load_json(self.students_file)
        students[student.profile.student_id] = student.model_dump(mode='json')
        self._save_json(self.students_file, students)
    
    def get_student(self, student_id: str) -> Optional[Student]:
        students = self._load_json(self.students_file)
        if student_id in students:
            return Student(**students[student_id])
        return None
    
    def get_all_students(self) -> List[Student]:
        students = self._load_json(self.students_file)
        return [Student(**data) for data in students.values()]
    
    def save_subject(self, subject: Subject):
        subjects = self._load_json(self.subjects_file)
        subjects[subject.id] = subject.model_dump()
        self._save_json(self.subjects_file, subjects)
    
    def get_subject(self, subject_id: str) -> Optional[Subject]:
        subjects = self._load_json(self.subjects_file)
        if subject_id in subjects:
            return Subject(**subjects[subject_id])
        return None
    
    def get_all_subjects(self) -> List[Subject]:
        subjects = self._load_json(self.subjects_file)
        return [Subject(**data) for data in subjects.values()]
    
    def save_topic(self, topic: Topic):
        topics = self._load_json(self.topics_file)
        topics[topic.id] = topic.model_dump()
        self._save_json(self.topics_file, topics)
    
    def get_topic(self, topic_id: str) -> Optional[Topic]:
        topics = self._load_json(self.topics_file)
        if topic_id in topics:
            return Topic(**topics[topic_id])
        return None
    
    def get_topics_by_subject(self, subject_id: str) -> List[Topic]:
        topics = self._load_json(self.topics_file)
        return [Topic(**data) for data in topics.values() if data.get("subject_id") == subject_id]
    
    def save_question(self, question: Question):
        questions = self._load_json(self.questions_file)
        questions[question.id] = question.model_dump()
        self._save_json(self.questions_file, questions)
    
    def get_question(self, question_id: str) -> Optional[Question]:
        questions = self._load_json(self.questions_file)
        if question_id in questions:
            return Question(**questions[question_id])
        return None
    
    def get_questions_by_topic(self, topic_id: str) -> List[Question]:
        questions = self._load_json(self.questions_file)
        return [Question(**data) for data in questions.values() if data.get("topic_id") == topic_id]
    
    def save_resource(self, resource: Resource):
        resources = self._load_json(self.resources_file)
        resources[resource.id] = resource.model_dump()
        self._save_json(self.resources_file, resources)
    
    def get_resource(self, resource_id: str) -> Optional[Resource]:
        resources = self._load_json(self.resources_file)
        if resource_id in resources:
            return Resource(**resources[resource_id])
        return None
    
    def get_resources_by_topic(self, topic_id: str) -> List[Resource]:
        resources = self._load_json(self.resources_file)
        return [Resource(**data) for data in resources.values() if data.get("topic_id") == topic_id]
    
    def _load_json(self, file_path: str) -> Dict:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, file_path: str, data: Dict):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)