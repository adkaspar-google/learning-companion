# Load Articles (webpages) to documents
# Chunks Documents
# Embed Documents
# Store in ChromaDB Vector Store (in memory)

from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader

from langchain_google_vertexai import VertexAIEmbeddings

from learning_companion.config import Config
from learning_companion.retriever import urls

config = Config()
config.set_env_vars()

# Initialize the specific Embeddings Model version
embeddings = VertexAIEmbeddings(model_name="text-embedding-004")


class ChromaRetriever:
    """A class for retrieving documents from a Chroma vectorstore."""

    def __init__(self, urls: List[str] = urls, persist_directory: str = "./.chroma"):
        """Initializes the ChromaRetriever with a list of URLs."""
        self.urls = urls
        self.persist_directory = persist_directory
        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=250, chunk_overlap=0
        )
        self.embedding_function = embeddings
        self._build_vectorstore()

    def _build_vectorstore(self):
        """Builds the Chroma vectorstore from the URLs."""
        docs = [WebBaseLoader(url).load() for url in self.urls]
        docs_list = [item for sublist in docs for item in sublist]
        doc_splits = self.text_splitter.split_documents(docs_list)
        self.vectorstore = Chroma.from_documents(
            documents=doc_splits,
            collection_name="rag-chroma",
            embedding=self.embedding_function,
            persist_directory=self.persist_directory,
        )

    def get_retriever(self):
        """Returns the Chroma retriever."""
        return self.vectorstore.as_retriever()



