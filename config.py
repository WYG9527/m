import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "learning_data.db")
    LEARNING_RESOURCES_PATH = os.path.join(os.path.dirname(__file__), "data", "learning_resources.json")
    STUDENT_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "students.json")
    
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
config = Config()