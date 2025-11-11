"""
PDF → 청크 → 벡터 인덱스 생성 스크립트 (OpenAI + FAISS)
"""
import os
import logging
from dotenv import load_dotenv

from pdf_processor import PDFProcessor
from vector_store import VectorStoreManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def build_index():
    # .env 로드
    load_dotenv()

    # 🧱 프로젝트 루트 경로 (app 폴더 한 단계 위)
    app_dir = os.path.dirname(os.path.abspath(__file__))      # ...\rag-pdf-system\app
    root_dir = os.path.dirname(app_dir)                       # ...\rag-pdf-system

    # 📂 PDF 폴더 경로
    pdf_dir = os.getenv("PDF_DIR")
    if not pdf_dir:
        pdf_dir = os.path.join(root_dir, "data", "pdfs")
    logger.info(f"📂 PDF_DIR : {pdf_dir}")

    if not os.path.isdir(pdf_dir):
        logger.error(f"❌ PDF 폴더가 없습니다: {pdf_dir}")
        return

    # 폴더 안 PDF 파일 리스트
    pdf_files = [
        os.path.join(pdf_dir, f)
        for f in os.listdir(pdf_dir)
        if f.lower().endswith(".pdf")
    ]

    if not pdf_files:
        logger.error(f"❌ PDF_DIR 안에 PDF 파일이 없습니다: {pdf_dir}")
        return

    # 💾 벡터 저장 경로 (항상 동일한 곳으로 통일)
    vector_path = os.getenv("VECTOR_STORE_PATH")
    if not vector_path:
        vector_path = os.path.join(root_dir, "data", "vectors")
    logger.info(f"💾 VECTOR_PATH : {vector_path}")

    os.makedirs(vector_path, exist_ok=True)

    # 📑 PDF → 청크
    pdf_processor = PDFProcessor(
        chunk_size=int(os.getenv("CHUNK_SIZE", 1000)),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 100)),
    )

    all_chunks = []
    for pdf_path in pdf_files:
        logger.info(f"📄 처리 중: {pdf_path}")
        # ✅ 여기! process_pdfs(X) → process_pdf(O)
        chunks = pdf_processor.process_pdf(pdf_path)
        logger.info(f"   → 청크 {len(chunks)}개 생성")
        all_chunks.extend(chunks)

    logger.info(f"✅ 전체 청크 수: {len(all_chunks)}")

    if not all_chunks:
        logger.error("❌ 생성된 청크가 0개입니다. PDF 내용/파서 확인 필요.")
        return

    # 🔢 벡터스토어 생성
    vector_store = VectorStoreManager(
        store_type=os.getenv("VECTOR_STORE_TYPE", "faiss"),
        store_path=vector_path,
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
    )

    vector_store.create_vectorstore(all_chunks)
    vector_store.save_vectorstore("index")
    logger.info("✅ 벡터 인덱스 생성 & 저장 완료!")

    # 🔍 진짜로 index.faiss 파일이 있는지 체크
    index_dir = os.path.join(vector_path, "index")
    faiss_path = os.path.join(index_dir, "index.faiss")
    pkl_path = os.path.join(index_dir, "index.pkl")

    logger.info(f"📁 인덱스 폴더: {index_dir}")
    logger.info(f"   - 기대하는 FAISS 파일: {faiss_path}")
    logger.info(f"   - 기대하는 PKL 파일  : {pkl_path}")

    if os.path.exists(faiss_path):
        logger.info("✅ index.faiss 파일 존재 확인 완료!")
    else:
        logger.error("❌ index.faiss 파일이 없습니다. 경로 설정 문제입니다.")


if __name__ == "__main__":
    build_index()