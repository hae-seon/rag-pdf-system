#!/usr/bin/env python
"""
PDF 파일을 기존 벡터 인덱스에 추가하는 스크립트
"""
import sys
import os
from pathlib import Path

# app 디렉토리를 모듈 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / "app"))

from main import RAGSystem

def add_pdf_to_index(pdf_path: str):
    """PDF를 벡터 인덱스에 추가"""
    print(f"PDF 파일 처리 중: {pdf_path}")

    # RAG 시스템 초기화
    rag = RAGSystem()

    # 기존 인덱스 로드
    try:
        rag.load_existing_index()
        print("기존 벡터 인덱스 로드 완료")
    except Exception as e:
        print(f"기존 인덱스 로드 실패 (새로 생성됨): {e}")

    # PDF 처리
    print("PDF 청킹 중...")
    chunks = rag.pdf_processor.process_pdf(pdf_path)
    print(f"추출된 청크 수: {len(chunks)}")

    if not chunks:
        print("❌ PDF에서 추출된 내용이 없습니다.")
        return

    # 벡터스토어에 추가
    print("벡터 임베딩 생성 및 인덱스 추가 중...")
    if rag.vector_store.vectorstore is None:
        rag.vector_store.create_vectorstore(chunks)
    else:
        # 기존 벡터스토어에 새 문서 추가
        from langchain_community.vectorstores import FAISS

        # 배치 처리
        batch_size = 100
        total_docs = len(chunks)

        for i in range(0, total_docs, batch_size):
            batch = chunks[i:i+batch_size]
            print(f"배치 처리 중: {i+1} ~ {min(i+batch_size, total_docs)} / {total_docs}")
            batch_vectorstore = FAISS.from_documents(batch, rag.vector_store.embeddings)
            rag.vector_store.vectorstore.merge_from(batch_vectorstore)
            print(f"{len(batch)}개 문서를 벡터 인덱스에 추가했습니다")

    # 저장
    print("벡터 인덱스 저장 중...")
    rag.vector_store.save_vectorstore()

    print("✅ PDF가 벡터 인덱스에 성공적으로 추가되었습니다!")

if __name__ == "__main__":
    pdf_file = "./data/pdfs/대한민국약전+일부개정고시+변경대비표.pdf"

    if not os.path.exists(pdf_file):
        print(f"❌ 파일을 찾을 수 없습니다: {pdf_file}")
        sys.exit(1)

    add_pdf_to_index(pdf_file)
