"""
Vector Store Management - OpenAI Version
"""
import os
from typing import List
import logging

from langchain_community.vectorstores import FAISS, Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStoreManager:
    def __init__(
        self,
        store_type: str = "faiss",
        store_path: str = "./data/vectors",
        embedding_model: str = "text-embedding-3-small",
    ):
        self.store_type = store_type
        self.store_path = store_path

        # ▶ OpenAI Embeddings (OPENAI_API_KEY는 .env/환경변수에 설정)
        self.embeddings = OpenAIEmbeddings(model=embedding_model)

        self.vectorstore = None
        os.makedirs(store_path, exist_ok=True)

    def create_vectorstore(self, documents: List[Document]) -> None:
        logger.info(f"Creating {self.store_type} vector store with OpenAI embeddings...")
        if self.store_type == "faiss":
            self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        elif self.store_type == "chroma":
            self.vectorstore = Chroma.from_documents(
                documents, self.embeddings, persist_directory=self.store_path
            )
        else:
            raise ValueError(f"Unsupported store_type: {self.store_type}")
        logger.info(f"Vector store created with {len(documents)} documents")

    def save_vectorstore(self, name: str = "index") -> None:
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized")
        if self.store_type == "faiss":
            save_path = os.path.join(self.store_path, name)
            self.vectorstore.save_local(save_path)
            logger.info(f"FAISS index saved to {save_path}")
        elif self.store_type == "chroma":
            # Chroma는 persist_directory로 자동 저장
            logger.info("Chroma DB persisted")
        else:
            raise ValueError(f"Unsupported store_type: {self.store_type}")

    def load_vectorstore(self, name: str = "index") -> None:
        if self.store_type == "faiss":
            load_path = os.path.join(self.store_path, name)
            self.vectorstore = FAISS.load_local(
                load_path,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
            logger.info(f"FAISS index loaded from {load_path}")
        elif self.store_type == "chroma":
            self.vectorstore = Chroma(
                persist_directory=self.store_path,
                embedding_function=self.embeddings,
            )
            logger.info("Chroma DB loaded")
        else:
            raise ValueError(f"Unsupported store_type: {self.store_type}")

    def search(self, query: str, k: int = 5) -> List[Document]:
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized")
        results = self.vectorstore.similarity_search(query, k=k)
        logger.info(f"Found {len(results)} similar documents")
        return results
