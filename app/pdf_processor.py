"""
PDF Processing Module
"""
import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader  # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter # type: ignore
from langchain_core.documents import Document  # type: ignore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def load_pdf(self, pdf_path: str) -> List[Document]:
        """Load a PDF file and return its pages as LangChain Documents."""
        try:
            logger.info(f"Loading PDF: {pdf_path}")
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages")
            return documents
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            raise

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split loaded documents into smaller chunks."""
        try:
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error splitting documents: {e}")
            raise

    def process_pdf(self, pdf_path: str) -> List[Document]:
        """Full pipeline: load → split → add metadata."""
        documents = self.load_pdf(pdf_path)
        chunks = self.split_documents(documents)

        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i
            chunk.metadata["source_file"] = os.path.basename(pdf_path)

        return chunks
