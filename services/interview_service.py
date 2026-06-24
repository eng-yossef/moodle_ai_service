import uuid
from langgraph.types import Command
from core.graph import build_interview_graph
from core.models import InterviewState

# Global graph (shared across sessions)
interview_graph = build_interview_graph()

class InterviewService:
    def __init__(self):
        self.sessions = {}   # session_id -> config

    def start_interview(self, cv_text: str) -> tuple[str, str]:
        """Create a new interview session, return (session_id, first_question)."""
        session_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": session_id}}
        initial_state = InterviewState(
            cv_text=cv_text,
            messages=[],
            question_count=0,
            phase="init"
        )
        # Invoke graph: it will run until after 'generate_question' (first interrupt)
        self.sessions[session_id] = config
        result_state = interview_graph.invoke(initial_state, config)
        first_question = result_state.get("current_question", "Hello, let's start.")
        return session_id, first_question

    def process_answer(self, session_id: str, user_answer: str) -> dict:
        """Resume the graph with the user's answer, return next step or final evaluation."""
        config = self.sessions.get(session_id)
        if not config:
            raise ValueError("Invalid session ID")
        
        # Resume: pass the user_answer as a Command
        resume_command = Command(resume=user_answer)
        # The graph will continue from 'process_answer' node (which accepts resume value)
        result_state = interview_graph.invoke(resume_command, config)
        
        if result_state.get("phase") == "done":
            return {
                "next_question": None,
                "is_finished": True,
                "final_evaluation": result_state.get("final_evaluation")
            }
        else:
            return {
                "next_question": result_state.get("current_question"),
                "is_finished": False,
                "final_evaluation": None
            }

    def end_interview(self, session_id: str):
        """Clean up session."""
        self.sessions.pop(session_id, None)