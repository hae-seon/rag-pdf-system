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
            # 배치 처리: OpenAI API 토큰 제한(300k)을 피하기 위해 청크를 나눔
            batch_size = 100  # 한 번에 100개 문서씩 처리
            total_docs = len(documents)

            logger.info(f"Total documents: {total_docs}")
            logger.info(f"Processing in batches of {batch_size}")

            # 첫 배치로 벡터스토어 초기화
            first_batch = documents[:batch_size]
            self.vectorstore = FAISS.from_documents(first_batch, self.embeddings)
            logger.info(f"Initialized with first batch: {len(first_batch)} documents")

            # 나머지 배치 추가
            for i in range(batch_size, total_docs, batch_size):
                batch = documents[i:i+batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}: documents {i} to {min(i+batch_size, total_docs)}")
                batch_vectorstore = FAISS.from_documents(batch, self.embeddings)
                self.vectorstore.merge_from(batch_vectorstore)
                logger.info(f"Added {len(batch)} documents to vector store")

        elif self.store_type == "chroma":
            # Chroma도 배치 처리 적용
            batch_size = 100
            total_docs = len(documents)

            logger.info(f"Total documents: {total_docs}")
            logger.info(f"Processing in batches of {batch_size}")

            # 첫 배치로 초기화
            first_batch = documents[:batch_size]
            self.vectorstore = Chroma.from_documents(
                first_batch, self.embeddings, persist_directory=self.store_path
            )

            # 나머지 배치 추가
            for i in range(batch_size, total_docs, batch_size):
                batch = documents[i:i+batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}: documents {i} to {min(i+batch_size, total_docs)}")
                self.vectorstore.add_documents(batch)
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
