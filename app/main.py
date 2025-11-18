"""
Main Application - RAG PDF System (OpenAI QA + OpenAI Embeddings)
"""
import os
import logging
from dotenv import load_dotenv

from pdf_processor import PDFProcessor
from vector_store import VectorStoreManager
from qa_chain import QAChain  # OpenAI Chat 버전

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
            # OpenAI 임베딩 기본값으로 교체
            embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        )

        self.qa_chain: QAChain | None = None

    def _ensure_qa_chain(self):
        if self.qa_chain is None:
            self.qa_chain = QAChain(
                model_name=os.getenv("LLM_MODEL", "qwen2"),
                temperature=float(os.getenv("LLM_TEMPERATURE", 0.2)),
            )

    def ingest_pdf(self, pdf_path: str) -> None:
        """Process a PDF, build/save the vector index."""
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

        logger.info("PDF ingestion completed.")

    def load_existing_index(self) -> None:
        """Load an existing vector store."""
        logger.info("Loading existing vector store...")
        self.vector_store.load_vectorstore()
        if not self.vector_store.vectorstore:
            raise RuntimeError("Vector store failed to load or is empty.")
        logger.info("Vector store loaded.")

    def query(self, question: str) -> dict:
        """Run a QA query using retrieval + LLM."""
        if not question or not question.strip():
            raise ValueError("Question is empty.")
        if self.vector_store.vectorstore is None:
            raise RuntimeError("Vector store not ready. Load index or ingest PDF first.")

        # 1) Retrieve
        k = int(os.getenv("TOP_K", 5))
        docs = self.vector_store.search(question.strip(), k=k)

        # 2) Generate (OpenAI)
        self._ensure_qa_chain()
        answer = self.qa_chain.answer(question.strip(), contexts=docs)

        # 3) Build sources payload (Streamlit에서 기대하는 형태)
        sources = []
        for d in docs:
            sources.append({
                "content": d.page_content,
                "metadata": {
                    # 프로젝트에 따라 키가 다를 수 있어 안전하게 채움
                    "page": d.metadata.get("page") if isinstance(d.metadata, dict) else None,
                    "source_file": d.metadata.get("source") if isinstance(d.metadata, dict) else None,
                }
            })

        return {"answer": answer, "sources": sources}


if __name__ == "__main__":
    print("RAG System initialized. Ready to use!")
