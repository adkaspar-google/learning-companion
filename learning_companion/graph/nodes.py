from typing import Any, Dict
from langchain.schema import Document
from langchain_google_vertexai import ChatVertexAI
from learning_companion.graph.state import GraphState
from learning_companion.graph.chains import RetrievalGrader, GenerationChain
from learning_companion.retriever import ChromaRetriever
from learning_companion.web_search import WebDocSearchGoogleCSE

from learning_companion.config import Config

config = Config()
config.set_env_vars()

_MODEL = "gemini-1.5-flash-002"

llm = ChatVertexAI(
    model=_MODEL, convert_system_message_to_human=True, temperature=0
)


class Nodes:
    """
    A utility class encapsulating various node functionalities
    used in a graph-based document processing workflow.
    """

    @staticmethod
    def generate(state: GraphState=GraphState) -> Dict[str, Any]:
        """
        Generates a response based on the given question and documents.

        Args:
            state (GraphState): The current graph state containing the question and documents.

        Returns:
            Dict[str, Any]: The updated graph state including the generated response.
        """
        print("---GENERATE---")
        question = state["question"]
        documents = state["documents"]

        generation = GenerationChain(llm).generate(documents, question)
        return {"documents": documents, "question": question, "generation": generation}

    @staticmethod
    def grade_documents(state: GraphState) -> Dict[str, Any]:
        """
        Grades the relevance of retrieved documents to the question.

        Filters out irrelevant documents and sets a flag for web search if needed.

        Args:
            state (GraphState): The current graph state containing the question and documents.

        Returns:
            Dict[str, Any]: The updated graph state with filtered documents and web_search flag.
        """
        print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
        question = state["question"]
        documents = state["documents"]

        filtered_docs = []
        web_search = False
        for d in documents:
            score = RetrievalGrader(llm).grade(question=question, document=d.page_content)
            grade = score.binary_score
            if grade.lower() == "yes":
                print("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(d)
            else:
                print("---GRADE: DOCUMENT NOT RELEVANT---")
                web_search = True
                continue
        return {"documents": filtered_docs, "question": question, "web_search": web_search}

    @staticmethod
    def retrieve(state: GraphState) -> Dict[str, Any]:
        """
        Retrieves relevant documents based on the given question.

        Args:
            state (GraphState): The current graph state containing the question.

        Returns:
            Dict[str, Any]: The updated graph state including the retrieved documents.
        """
        print("---RETRIEVE---")
        question = state["question"]

        documents = ChromaRetriever().get_retriever().invoke(question)
        return {"documents": documents, "question": question}

    @staticmethod
    def web_search(state: GraphState) -> Dict[str, Any]:
        """
        Performs a web search to find additional relevant documents.

        Args:
            state (GraphState): The current graph state containing the question and existing documents.

        Returns:
            Dict[str, Any]: The updated graph state including the documents found from the web search.
        """
        print("---WEB SEARCH---")
        question = state["question"]
        if "documents" in state.keys():
            documents = state["documents"]
        else:
            documents = []
        web_search_tool = WebDocSearchGoogleCSE(question, k=3)
        docs = web_search_tool.get_documents(verbose=True)
        print(f"DOCS WEBSEARCH: {docs}")
        web_results = "\n".join([d.page_content for d in docs])
        web_results = Document(page_content=web_results)
        if documents is not None:
            documents.append(web_results)
        else:
            documents = [web_results]
        return {"documents": documents, "question": question}