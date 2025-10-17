from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
from app.learning_path_planner.lpp_workflow import ask_clarifying_questions, generate_learning_path, extract_json

app = FastAPI(title="Personalized Learning Path API")

# Data models
class TopicInput(BaseModel):
    topic: str

class GenerateInput(BaseModel):
    topic: str
    conversation_history: list
    user_answers: str


@app.post("/assess")
def assess(input_data: TopicInput):
    messages, questions = ask_clarifying_questions(input_data.topic)
    return {"questions": questions, "conversation_history": [m.dict() for m in messages]}


@app.post("/generate")
def generate(input_data: GenerateInput):
    content = generate_learning_path(input_data.topic, input_data.conversation_history, input_data.user_answers)
    json_data = extract_json(content)
    return {"learning_path": json_data, "raw_response": content}