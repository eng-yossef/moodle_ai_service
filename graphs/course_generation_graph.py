from typing import Dict, Any
from langgraph.graph import StateGraph, END
from models.state import CourseState
from agents.document_analysis_agent import DocumentAnalysisAgent
from agents.curriculum_agent import CurriculumAgent
from agents.lecture_generation_agent import LectureGenerationAgent
from agents.assessment_agent import AssessmentAgent
from agents.publishing_agent import PublishingAgent

class CourseGenerationGraph:
    def __init__(self):
        self.doc_agent = DocumentAnalysisAgent()
        self.cur_agent = CurriculumAgent()
        self.lec_agent = LectureGenerationAgent()
        self.ass_agent = AssessmentAgent()
        self.pub_agent = PublishingAgent()
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(CourseState)

        def extract_text(state: CourseState) -> CourseState:
            # state.raw_text already set
            return state

        def split_curriculum(state: CourseState) -> CourseState:
            # Assume state.raw_text and state.num_lectures are available
            # For simplicity, we get from state (we can store extra fields)
            return state

        def generate_lectures(state: CourseState) -> CourseState:
            return state

        def generate_quizzes(state: CourseState) -> CourseState:
            return state

        def export(state: CourseState) -> CourseState:
            return state

        builder.add_node("extract", extract_text)
        builder.add_node("curriculum", split_curriculum)
        builder.add_node("lectures", generate_lectures)
        builder.add_node("quizzes", generate_quizzes)
        builder.add_node("export", export)

        builder.set_entry_point("extract")
        builder.add_edge("extract", "curriculum")
        builder.add_edge("curriculum", "lectures")
        builder.add_edge("lectures", "quizzes")
        builder.add_edge("quizzes", "export")
        builder.add_edge("export", END)

        return builder.compile()

    async def run(self, state: CourseState) -> CourseState:
        # Actually run the graph; we need to feed state
        # For simplicity, we'll just call the service directly
        # This is a placeholder; graph usage can be integrated later
        return state