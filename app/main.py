"""
Main Application - RAG PDF System (Gemini version)
"""
import os
import logging
from dotenv import load_dotenv

from pdf_processor import PDFProcessor
from vector_store import VectorStoreManager
from qa_chain import QAChain

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class RAGSystem:
    def __init__(self) -> None:
        # PDF chunking
        self.pdf_processor = PDFProcessor(
            chunk_size=int(os.getenv("CHUNK_SIZE", 1000)),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 100)),
        )

        # Vector store (default: FAISS)
        self.vector_store = VectorStoreManager(
            store_type=os.getenv("VECTOR_STORE_TYPE", "faiss"),
            store_path=os.getenv("VECTOR_STORE_PATH", "./data/vectors"),
            # Default to Gemini embeddings
            embedding_model=os.getenv("EMBEDDING_MODEL", "models/embedding-001"),
        )

        self.qa_chain: QAChain | None = None

    def ingest_pdf(self, pdf_path: str) -> None:
        """Process a PDF, build/save the vector index, and init QA chain."""
        if not pdf_path or not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        logger.info(f"Starting PDF ingestion: {pdf_path}")

        # 1) Process PDF -> chunks
        chunks = self.pdf_processor.process_pdf(pdf_path)
        if not chunks:
            raise ValueError("No text chunks extracted from the PDF.")

        # 2) Build vector store
        self.vector_store.create_vectorstore(chunks)
        self.vector_store.save_vectorstore()

        # 3) Init QA chain (Gemini as default)
        self.qa_chain = QAChain(
            self.vector_store.vectorstore,
            model_name=os.getenv("LLM_MODEL", "gemini-pro"),
            temperature=float(os.getenv("LLM_TEMPERATURE", 0.2)),
            max_tokens=int(os.getenv("MAX_TOKENS", 1000)),
        )

        logger.info("PDF ingestion completed.")

    def load_existing_index(self) -> None:
        """Load an existing vector store and init QA chain."""
        logger.info("Loading existing vector store...")
        self.vector_store.load_vectorstore()
        if not self.vector_store.vectorstore:
            raise RuntimeError("Vector store failed to load or is empty.")

        self.qa_chain = QAChain(
            self.vector_store.vectorstore,
            model_name=os.getenv("LLM_MODEL", "gemini-pro"),
            temperature=float(os.getenv("LLM_TEMPERATURE", 0.2)),
            max_tokens=int(os.getenv("MAX_TOKENS", 1000)),
        )
        logger.info("Vector store loaded and QA chain initialized.")

    def query(self, question: str) -> dict:
        """Run a QA query using the initialized chain."""
        if self.qa_chain is None:
            raise ValueError("System not initialized. Load index or ingest PDF first.")
        if not question or not question.strip():
            raise ValueError("Question is empty.")
        return self.qa_chain.ask(question.strip())


if __name__ == "__main__":
    print("RAG System initialized. Ready to use!")
