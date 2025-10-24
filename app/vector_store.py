"""
Vector Store Management - Gemini Version
"""
import os
from typing import List
from langchain.vectorstores import FAISS, Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStoreManager:
    def __init__(self, store_type: str = "faiss", 
                 store_path: str = "./data/vectors",
                 embedding_model: str = "models/embedding-001"):
        self.store_type = store_type
        self.store_path = store_path
        
        # Use Google Gemini Embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=embedding_model,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        self.vectorstore = None
        os.makedirs(store_path, exist_ok=True)
    
    def create_vectorstore(self, documents: List[Document]) -> None:
        try:
            logger.info(f"Creating {self.store_type} vector store with Gemini embeddings...")
            if self.store_type == "faiss":                self.vectorstore = FAISS.from_documents(documents, self.embeddings)
            elif self.store_type == "chroma":
                self.vectorstore = Chroma.from_documents(
                    documents, self.embeddings, persist_directory=self.store_path
                )
            logger.info(f"Vector store created with {len(documents)} documents")
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            raise
    
    def save_vectorstore(self, name: str = "index") -> None:
        try:
            if self.store_type == "faiss":
                save_path = os.path.join(self.store_path, name)
                self.vectorstore.save_local(save_path)
                logger.info(f"FAISS index saved to {save_path}")
            elif self.store_type == "chroma":
                logger.info("Chroma DB persisted")
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
            raise
    
    def load_vectorstore(self, name: str = "index") -> None:
        try:
            if self.store_type == "faiss":
                load_path = os.path.join(self.store_path, name)
                self.vectorstore = FAISS.load_local(
                    load_path, self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"FAISS index loaded from {load_path}")
            elif self.store_type == "chroma":
                self.vectorstore = Chroma(                    persist_directory=self.store_path,
                    embedding_function=self.embeddings
                )
                logger.info("Chroma DB loaded")
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            raise
    
    def search(self, query: str, k: int = 5) -> List[Document]:
        try:
            if self.vectorstore is None:
                raise ValueError("Vector store not initialized")
            results = self.vectorstore.similarity_search(query, k=k)
            logger.info(f"Found {len(results)} similar documents")
            return results
        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise
