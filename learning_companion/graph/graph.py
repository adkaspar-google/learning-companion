from enum import Enum
from langchain_google_vertexai import ChatVertexAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph

from learning_companion.graph.chains import QuestionRouter, HallucinationGrader, AnswerGrader, RouteQueryModel
from learning_companion.graph.nodes import Nodes

from learning_companion.config import Config

config = Config()
config.set_env_vars()

_MODEL = "gemini-1.5-flash-002"

RETRIEVE = "retrieve"
GRADE_DOCUMENTS = "grade_documents"
GENERATE = "generate"
WEBSEARCH = "websearch"

class Actions(Enum):
    RETRIEVE = "retrieve"
    GRADE_DOCUMENTS = "grade_documents"
    GENERATE = "generate"
    WEBSEARCH = "websearch"


memory = SqliteSaver.from_conn_string(":memory:")
memory = MemorySaver()

model_name = _MODEL
llm = ChatVertexAI(model=model_name, convert_system_message_to_human=True)

def decide_to_generate(state):
    print("---ASSESS GRADED DOCUMENTS---")

    if state["web_search"]:
        print(
            "---DECISION: NOT ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, INCLUDE WEB SEARCH---"
        )
        return WEBSEARCH
    else:
        print("---DECISION: GENERATE---")
        return GENERATE


def grade_generation_grounded_in_documents_and_question(state: GraphState) -> str:
    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = HallucinationGrader(llm).grade(documents, generation)

    if hallucination_grade := score.binary_score:
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        print("---GRADE GENERATION vs QUESTION---")
        score = AnswerGrader(llm).grade(question, generation)
        if answer_grade := score.binary_score:
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"


def route_question(state: GraphState) -> str:
    print("---ROUTE QUESTION---")
    question = state["question"]
    router: QuestionRouter = QuestionRouter(llm)
    source: RouteQueryModel = router.route(question)
    if source.datasource == WEBSEARCH:
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return WEBSEARCH
    elif source.datasource == "vectorstore":
        print("---ROUTE QUESTION TO RAG---")
        return RETRIEVE


workflow = StateGraph(GraphState)
workflow.add_node(RETRIEVE, Nodes.retrieve)
workflow.add_node(GRADE_DOCUMENTS, Nodes.grade_documents)
workflow.add_node(GENERATE, Nodes.generate)
workflow.add_node(WEBSEARCH, Nodes.web_search)


workflow.set_conditional_entry_point(
    route_question,
    {
        WEBSEARCH: WEBSEARCH,
        RETRIEVE: RETRIEVE,
    },
)
workflow.add_edge(RETRIEVE, GRADE_DOCUMENTS)
workflow.add_conditional_edges(
    GRADE_DOCUMENTS,
    decide_to_generate,
    {
        WEBSEARCH: WEBSEARCH,
        GENERATE: GENERATE,
    },
)
workflow.add_edge(WEBSEARCH, GENERATE)
workflow.add_conditional_edges(
    GENERATE,
    grade_generation_grounded_in_documents_and_question,
    {
        "not supported": GENERATE,
        "useful": END,
        "not useful": WEBSEARCH,
    },
)


app = workflow.compile(checkpointer=memory)

draw = app.get_graph().draw_mermaid_png(output_file_path="graph.png")