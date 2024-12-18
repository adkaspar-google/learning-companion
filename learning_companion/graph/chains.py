from typing import Literal

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from pydantic import BaseModel, Field
from langchain_google_vertexai import ChatVertexAI

from learning_companion.config import Config

config = Config()
config.set_env_vars()

_MODEL = "gemini-1.5-flash-002"

def create_structured_chain_response(llm, output_schema, system_prompt, user_prompt_template):
    """Creates a structured LLM grader."""
    structured_llm_output = llm.with_structured_output(output_schema)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", user_prompt_template),
        ]
    )
    return prompt | structured_llm_output

class GradeAnswerModel(BaseModel):
    binary_score: bool = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

class AnswerGrader:
    def __init__(self, llm):
        system_prompt = (
            "You are a grader assessing whether an answer addresses / resolves a question \n"
            "Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."
        )
        user_prompt_template = "User question: \n\n {question} \n\n LLM generation: {generation}"
        self.grader = create_structured_chain_response(
            llm, GradeAnswerModel, system_prompt, user_prompt_template
        )

    def grade(self, question: str, generation: str) -> GradeAnswerModel:
        return self.grader.invoke({"question": question, "generation": generation})


class GenerationChain:
    def __init__(self, llm, prompt_hub_path: str = "rlm/rag-prompt"):
        self.llm = llm
        self.prompt = hub.pull(prompt_hub_path)
        self.chain = self.prompt | self.llm | StrOutputParser()

    def generate(self, context: str, question: str) -> str:
        """Generates an answer given context and question"""
        return self.chain.invoke({"context": context, "question": question})


class GradeHallucinationsModel(BaseModel):
    """Binary score for hallucination present in generation answer."""
    binary_score: bool = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )

class HallucinationGrader:
    def __init__(self, llm):
        self.llm = llm
        self.system_prompt = (
            "You are a grader assessing whether an LLM generation is grounded in / "
            "supported by a set of retrieved facts. \n"
            "Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / "
            "supported by the set of facts."
        )
        self.user_prompt_template = "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"

    def grade(self, documents, generation) -> GradeHallucinationsModel:
        return create_structured_chain_response(
            self.llm, GradeHallucinationsModel, self.system_prompt, self.user_prompt_template
        ).invoke({"documents": documents, "generation": generation})


class GradeDocumentsModel(BaseModel):
    """Binary score for relevance check on retrieved documents."""
    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )

class RetrievalGrader:
    def __init__(self, llm):
        self.llm = ChatVertexAI(
            model=_MODEL, convert_system_message_to_human=True, temperature=0
        )
        self.system_prompt = (
            "You are a grader assessing relevance of a retrieved document to a user question. \n"
            "If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant. \n"
            "Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."
        )
        self.user_prompt_template = "Retrieved document: \n\n {document} \n\n User question: {question}"
        self.model = GradeDocumentsModel
        self.structured_llm_output = self.llm.with_structured_output(self.model)
        #self.grader = create_structured_chain_response(
        #    llm, GradeDocumentsModel, system_prompt, user_prompt_template
        #)

    def grade(self, document: str, question: str) -> GradeDocumentsModel:
        #return self.grader.invoke({"document": document, "question": question})
        print(f"LLM configured for structured output: {self.structured_llm_output}")

        # Create the structured chain response
        chain = create_structured_chain_response(
            self.llm, self.model, self.system_prompt, self.user_prompt_template
        )
        print(f"Chain successfully created: {chain}")

        # Invoke the chain with the question
        print(question)
        result = chain.invoke({"document": document , "question": question})
        if result:
            print(f"Raw chain invocation result: {result}")

            # Ensure the output is parsed into RouteQueryModel
            try:
                parsed_result = GradeDocumentsModel.parse_obj(result)
                print(f"Parsed structured result: {parsed_result}")
                return parsed_result
            except Exception as e:
                print(f"Error parsing result into RouteQueryModel: {e}")
                raise ValueError("Failed to parse chain response into RouteQueryModel.") from e
        else:
            return GradeDocumentsModel(binary_score="yes")

class RouteQueryModel(BaseModel):
    """Route a user query to the most relevant datasource."""
    datasource: Literal["vectorstore", "websearch"] = Field(
        ...,
        description="Given a user question choose to route it to web search or a vectorstore.",
    )

class QuestionRouter:
    def __init__(self, llm):
        # Initialize LLM instance
        self.llm = ChatVertexAI(
            model=_MODEL, convert_system_message_to_human=True, temperature=0
        )
        # Define prompts
        self.system_prompt = (
            "You are an expert at routing a user question to a vectorstore or web search. "
            "The main context is LEARNING. "
            "The vectorstore contains documents related to BigQuery or SQL. "
            "Use the vectorstore for questions on these topics. For all else, use web-search."
        )
        self.user_prompt_template = "{question}"

    def route(self, question: str) -> RouteQueryModel:
        # Debug structured output initialization
        structured_llm_output = self.llm.with_structured_output(RouteQueryModel)
        print(f"LLM configured for structured output: {structured_llm_output}")

        # Create the structured chain response
        chain = create_structured_chain_response(
            self.llm, RouteQueryModel, self.system_prompt, self.user_prompt_template
        )
        print(f"Chain successfully created: {chain}")

        # Invoke the chain with the question
        print(question)
        result = chain.invoke({"question": question})
        print(f"Raw chain invocation result: {result}")

        # Ensure the output is parsed into RouteQueryModel
        try:
            parsed_result = RouteQueryModel.parse_obj(result)
            print(f"Parsed structured result: {parsed_result}")
            if parsed_result:
                return parsed_result
            else:
                return RouteQueryModel(datasource="websearch")
        except Exception as e:
            print(f"Error parsing result into RouteQueryModel: {e}, defaulting to websearch")
            return RouteQueryModel(datasource="websearch")
