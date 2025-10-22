from fastapi import APIRouter
from uuid import uuid4
from app.models import StartRequest, GraphResponse, ResumeRequest
from app.learning_path_planner.graph import graph
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def run_graph_and_response(input_state, config):
    result = graph.invoke(input_state, config)
    thread_id = config["configurable"]["thread_id"]
    message_threads = result.get("messages", {})
    
    logger.info(message_threads)

    return GraphResponse(
        thread_id=thread_id,
        messages=message_threads
    )


@router.post("/graph/start", response_model=GraphResponse)
def start_graph(request: StartRequest):
    thread_id = str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {"topic": request.learning_topic}

    return run_graph_and_response(initial_state, config)

@router.post("/graph/resume", response_model=GraphResponse)
def resume_graph(request: ResumeRequest):
    config = {"configurable": {"thread_id": request.thread_id}}        
    state = {"messages": [HumanMessage(content=request.human_answer)]}
    print(f"State to update: {state}")
    graph.update_state(config, state)

    return run_graph_and_response(None, config)
