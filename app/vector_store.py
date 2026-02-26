"""
Vector Store Management - OpenAI / HuggingFace Embeddings with Hybrid Search
"""
import os
from typing import List
import logging
from rank_bm25 import BM25Okapi

from langchain_community.vectorstores import FAISS, Chroma
from langchain_core.documents import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI 모델명 패턴
_OPENAI_EMBEDDING_PREFIXES = ("text-embedding-", "text-search-", "text-similarity-")


class VectorStoreManager:
    def __init__(
        self,
        store_type: str = "faiss",
        store_path: str = "../data/vectors/index",
        embedding_model: str = "BAAI/bge-m3",
    ):
        self.store_type = store_type
        self.store_path = store_path

        # 임베딩 모델 자동 선택: OpenAI vs HuggingFace
        if embedding_model.startswith(_OPENAI_EMBEDDING_PREFIXES):
            from langchain_openai import OpenAIEmbeddings
            logger.info(f"Loading OpenAI embedding model: {embedding_model}")
            self.embeddings = OpenAIEmbeddings(model=embedding_model)
        else:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            logger.info(f"Loading HuggingFace embedding model: {embedding_model}")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        logger.info("Embedding model loaded successfully")

        self.vectorstore = None
        os.makedirs(store_path, exist_ok=True)

    def create_vectorstore(self, documents: List[Document]) -> None:
        logger.info(f"Creating {self.store_type} vector store with local embeddings...")

        if self.store_type == "faiss":
            # 로컬 임베딩 모델은 배치 처리 필요 없음
            logger.info(f"Total documents: {len(documents)}")
            self.vectorstore = FAISS.from_documents(documents, self.embeddings)
            logger.info(f"Vector store created with {len(documents)} documents")

        elif self.store_type == "chroma":
            # 로컬 임베딩 모델은 배치 처리 필요 없음
            logger.info(f"Total documents: {len(documents)}")
            self.vectorstore = Chroma.from_documents(
                documents, self.embeddings, persist_directory=self.store_path
            )
            logger.info(f"Vector store created with {len(documents)} documents")
        else:
            raise ValueError(f"Unsupported store_type: {self.store_type}")

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

    def ingest_documents(self, documents: List[Document]) -> None:
        """기존 벡터스토어에 새 문서 추가"""
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Use create_vectorstore first.")

        logger.info(f"Adding {len(documents)} documents to existing vector store...")

        if self.store_type == "faiss":
            # FAISS는 새 문서로 임시 벡터스토어 만들고 merge
            temp_vectorstore = FAISS.from_documents(documents, self.embeddings)
            self.vectorstore.merge_from(temp_vectorstore)
            logger.info(f"Added {len(documents)} documents to FAISS")
        elif self.store_type == "chroma":
            # Chroma는 직접 add_documents
            self.vectorstore.add_documents(documents)
            logger.info(f"Added {len(documents)} documents to Chroma")
        else:
            raise ValueError(f"Unsupported store_type: {self.store_type}")

    def search(self, query: str, k: int = 5) -> List[Document]:
        """하이브리드 검색: 시맨틱 검색 + 키워드 검색 (BM25)"""
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized")

        # 1. 시맨틱 검색 (Semantic Search)
        semantic_results = self.vectorstore.similarity_search(query, k=k*2)

        # 2. BM25 키워드 검색
        # 모든 문서 가져오기
        all_docs = []
        if hasattr(self.vectorstore, 'docstore'):
            all_docs = list(self.vectorstore.docstore._dict.values())

        # BM25로 키워드 매칭
        tokenized_docs = [doc.page_content.split() for doc in all_docs]
        bm25 = BM25Okapi(tokenized_docs)
        tokenized_query = query.split()
        bm25_scores = bm25.get_scores(tokenized_query)

        # 상위 k*2 개 선택
        top_bm25_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:k*2]
        bm25_results = [all_docs[i] for i in top_bm25_indices]

        # 3. 결과 합치기 (중복 제거 - page_content 해시 기반)
        seen_hashes = set()
        hybrid_results = []

        # 시맨틱 결과 우선 추가
        for doc in semantic_results:
            doc_hash = hash(doc.page_content)
            if doc_hash not in seen_hashes:
                seen_hashes.add(doc_hash)
                hybrid_results.append(doc)

        # BM25 결과 추가
        for doc in bm25_results:
            doc_hash = hash(doc.page_content)
            if doc_hash not in seen_hashes:
                seen_hashes.add(doc_hash)
                hybrid_results.append(doc)

        # 상위 k개만 반환
        final_results = hybrid_results[:k]

        logger.info(f"Hybrid search found {len(final_results)} documents (semantic: {len(semantic_results)}, bm25: {len(bm25_results)})")
        return final_results