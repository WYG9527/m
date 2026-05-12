from typing import Dict, List, Any, Optional
from models.student import Student
from models.learning import Topic, Question
from utils.database import DatabaseManager
from utils.llm_client import LLMClient

class QAAgent:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.llm_client = LLMClient()
        self.conversation_history = {}
    
    def answer_question(self, student_id: str, question: str, subject: str = None) -> Dict[str, Any]:
        if student_id not in self.conversation_history:
            self.conversation_history[student_id] = []
        
        self.conversation_history[student_id].append({"role": "user", "content": question})
        
        relevant_topics = self._find_relevant_topics(question, subject)
        
        if relevant_topics:
            topic = relevant_topics[0]
            related_questions = self.db_manager.get_questions_by_topic(topic.id)
            
            if related_questions:
                similar_question = self._find_similar_question(question, related_questions)
                if similar_question:
                    answer = self._generate_answer_from_question(similar_question, topic)
                else:
                    answer = self._generate_answer_from_llm(question, topic)
            else:
                answer = self._generate_answer_from_llm(question, topic)
        else:
            answer = self._generate_answer_from_llm(question, None)
        
        self.conversation_history[student_id].append({"role": "assistant", "content": answer["answer"]})
        
        return answer
    
    def _find_relevant_topics(self, question: str, subject: Optional[str]) -> List[Topic]:
        if subject:
            topics = self.db_manager.get_topics_by_subject(subject)
        else:
            subjects = self.db_manager.get_all_subjects()
            topics = []
            for subj in subjects:
                topics.extend(self.db_manager.get_topics_by_subject(subj.id))
        
        relevant_topics = []
        for topic in topics:
            if self._topic_matches_question(topic, question):
                relevant_topics.append(topic)
        
        relevant_topics.sort(key=lambda t: self._match_score(t, question), reverse=True)
        return relevant_topics[:3]
    
    def _topic_matches_question(self, topic: Topic, question: str) -> bool:
        keywords = topic.name.lower().split() + (topic.description.lower().split() if topic.description else [])
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in keywords)
    
    def _match_score(self, topic: Topic, question: str) -> int:
        score = 0
        question_lower = question.lower()
        
        if topic.name.lower() in question_lower:
            score += 5
        if topic.description and topic.description.lower() in question_lower:
            score += 3
        
        return score
    
    def _find_similar_question(self, question: str, questions: List[Question]) -> Optional[Question]:
        max_similarity = 0
        best_match = None
        
        for q in questions:
            similarity = self._calculate_similarity(question, q.question_text)
            if similarity > max_similarity and similarity > 0.5:
                max_similarity = similarity
                best_match = q
        
        return best_match
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _generate_answer_from_question(self, question: Question, topic: Topic) -> Dict[str, Any]:
        options = question.options
        correct_answer = options[question.correct_answer]
        
        explanation = question.explanation if question.explanation else self.llm_client.generate_explanation(
            question.question_text, correct_answer, topic.name
        )
        
        return {
            "answer": explanation,
            "source": "database",
            "topic": topic.name,
            "confidence": 0.9
        }
    
    def _generate_answer_from_llm(self, question: str, topic: Optional[Topic]) -> Dict[str, Any]:
        topic_context = f"主题：{topic.name}\n{topic.description}" if topic else ""
        
        system_prompt = """
        你是一个耐心的教育助手，擅长用通俗易懂的语言解释复杂概念。
        请根据学生的问题，提供清晰、详细的解答。
        如果涉及具体的学科知识，请确保准确性。
        """
        
        prompt = f"""
        请回答以下问题：
        
        {question}
        
        {topic_context}
        
        请用简洁明了的语言回答，适合中学生理解。
        """
        
        answer = self.llm_client.generate_response(prompt, system_prompt)
        
        return {
            "answer": answer,
            "source": "llm",
            "topic": topic.name if topic else "综合",
            "confidence": 0.7
        }
    
    def analyze_conversation(self, student_id: str) -> Dict[str, Any]:
        if student_id not in self.conversation_history:
            return {"error": "没有对话历史"}
        
        history = self.conversation_history[student_id]
        analysis = self.llm_client.analyze_student_dialogue(history)
        
        return {
            "student_id": student_id,
            "total_questions": len([h for h in history if h["role"] == "user"]),
            "analysis": analysis
        }
    
    def clear_history(self, student_id: str):
        if student_id in self.conversation_history:
            del self.conversation_history[student_id]