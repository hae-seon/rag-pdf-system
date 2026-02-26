# app/debug_chunks.py
import os
from dotenv import load_dotenv
from pdf_processor import PDFProcessor

def debug_chunks():
    load_dotenv()

    # 프로젝트 루트 계산 (build_index.py랑 똑같이)
    app_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(app_dir)

    # PDF 하나 골라서 테스트 (원하는 파일명으로 바꿔줘!)
    pdf_dir = os.getenv("PDF_DIR") or os.path.join(root_dir, "data", "pdfs")
    pdf_name = "생동계획서샘플신청자료.pdf"  # 👈 여기 테스트할 PDF 이름
    pdf_path = os.path.join(pdf_dir, pdf_name)

    print(f"📄 테스트 PDF: {pdf_path}")

    # CHUNK_SIZE / OVERLAP은 .env에서 가져옴
    chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 100))
    print(f"🔧 chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")

    processor = PDFProcessor(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks = processor.process_pdf(pdf_path)
    print(f"✅ 총 청크 개수: {len(chunks)}")

    # 앞쪽 몇 개만 확인해보기
    for i, doc in enumerate(chunks[:10], start=1):
        text = doc.page_content
        meta = doc.metadata
        print("=" * 80)
        print(f"[청크 {i}] 길이: {len(text)} chars, 페이지: {meta.get('page', '?')}")
        print(text[:400])  # 앞 400자만 보기
        print()

if __name__ == "__main__":
    debug_chunks()