from openai import OpenAI
from typing import Optional, Dict, Any
from config import config

class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model_name = config.MODEL_NAME
        self.temperature = config.TEMPERATURE
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            max_tokens=2000
        )
        
        return response.choices[0].message.content.strip()
    
    def analyze_student_dialogue(self, history: list) -> Dict[str, Any]:
        history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
        
        system_prompt = """
        你是一个教育领域的AI助手，擅长分析学生的对话历史来理解他们的学习需求。
        请分析以下对话历史，提取关键信息：
        1. 学生的问题主题
        2. 学生的理解水平
        3. 学生的困惑点
        4. 推荐的下一步学习建议
        """
        
        prompt = f"请分析以下学生对话历史：\n\n{history_str}\n\n请以JSON格式输出分析结果，包含以下字段：topic, understanding_level, confusion_points, suggestions"
        
        response = self.generate_response(prompt, system_prompt)
        try:
            import json
            return json.loads(response)
        except:
            return {"topic": "", "understanding_level": "unknown", "confusion_points": [], "suggestions": []}
    
    def generate_explanation(self, question: str, answer: str, topic: str) -> str:
        system_prompt = """
        你是一个耐心的教育助手，擅长用通俗易懂的语言解释复杂概念。
        请根据问题、答案和主题，生成一个清晰、详细的解释。
        """
        
        prompt = f"问题：{question}\n答案：{answer}\n主题：{topic}\n\n请生成一个详细的解释，帮助学生理解这个知识点。"
        
        return self.generate_response(prompt, system_prompt)
    
    def generate_practice_questions(self, topic: str, difficulty: str, count: int = 5) -> list:
        system_prompt = """
        你是一个教育专家，擅长根据主题和难度生成练习题。
        请生成高质量的练习题，包含题目、选项和正确答案。
        """
        
        prompt = f"请为以下主题生成{count}道{difficulty}难度的练习题：{topic}\n\n请以JSON格式输出，包含题目列表，每个题目包含：question_text, options, correct_answer_index"
        
        response = self.generate_response(prompt, system_prompt)
        try:
            import json
            return json.loads(response)
        except:
            return []