from typing import Literal
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from .models import InterviewState
from core.config import settings
import json

MAX_QUESTIONS = 5

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.5,
    base_url="https://openrouter.ai/api/v1",
    max_tokens=1000,
    api_key=settings.OPENROUTER_API_KEY
)

# ---------- Node 1 ----------
def analyse_cv(state: InterviewState):
    from utils.cv_parser import parse_cv_with_llm

    state["extracted_cv"] = parse_cv_with_llm(state["cv_text"])
    state["phase"] = "interview"
    return state


# ---------- Node 2 ----------
def generate_question(state: InterviewState):
    cv_info = json.dumps(state["extracted_cv"])

    prompt = f"""
You are a technical interviewer.

CV:
{cv_info}

Conversation:
{state.get("messages", [])}

Ask ONE technical interview question based on the candidate's CV.
"""

    response = llm.invoke(prompt)

    question = response.content.strip()

    state["current_question"] = question
    state["messages"].append(AIMessage(content=question))

    return state


# ---------- Node 3 ----------
def process_answer(state: InterviewState):
    """
    Wait for user answer using LangGraph interrupt.
    """

    user_answer = interrupt(
        {
            "question": state["current_question"],
            "type": "answer_required"
        }
    )

    state["user_answer"] = user_answer
    state["messages"].append(
        HumanMessage(content=user_answer)
    )

    state["question_count"] += 1

    return state


# ---------- Node 4 ----------
def evaluate_level(state: InterviewState):
    cv_info = json.dumps(state["extracted_cv"])

    prompt = f"""
You are a senior technical recruiter.

CV:
{cv_info}

Interview Transcript:
{state["messages"]}

Return ONLY valid JSON:

{{
  "level": "Junior|Mid|Senior",
  "feedback": "short summary"
}}
"""

    response = llm.invoke(prompt)

    try:
        evaluation = json.loads(response.content)
    except Exception:
        evaluation = {
            "level": "Unknown",
            "feedback": response.content
        }

    state["final_evaluation"] = evaluation
    state["phase"] = "done"

    return state


# ---------- Router ----------
def should_continue(
    state: InterviewState,
) -> Literal["generate_question", "evaluate_level"]:

    if state["question_count"] >= MAX_QUESTIONS:
        return "evaluate_level"

    return "generate_question"


# ---------- Build Graph ----------
def build_interview_graph():

    builder = StateGraph(InterviewState)

    builder.add_node("analyse_cv", analyse_cv)
    builder.add_node("generate_question", generate_question)
    builder.add_node("process_answer", process_answer)
    builder.add_node("evaluate_level", evaluate_level)

    builder.add_edge(START, "analyse_cv")
    builder.add_edge("analyse_cv", "generate_question")
    builder.add_edge("generate_question", "process_answer")

    builder.add_conditional_edges(
        "process_answer",
        should_continue,
        {
            "generate_question": "generate_question",
            "evaluate_level": "evaluate_level",
        },
    )

    builder.add_edge("evaluate_level", END)

    memory = MemorySaver()

    graph = builder.compile(
        checkpointer=memory
    )

    return graph