
from typing import List, TypedDict


class GraphState(TypedDict):
    """
    Represents the state of our graph.
    Each Node gets and returns the State
    Using it for internal Cross-communication

    Attributes:
        question: question
        generation: LLM generation
        web_search: whether to add search
        documents: list of documents
    """
    question: str
    generation: str
    web_search: bool
    documents: List[str]
