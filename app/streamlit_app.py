"""
Streamlit UI for RAG PDF System
"""
import streamlit as st
import os
from main import RAGSystem
from dotenv import load_dotenv

load_dotenv()

# Page config
st.set_page_config(
    page_title="RAG PDF 질의응답 시스템",
    page_icon="📚",
    layout="wide"
)

st.title("📚 RAG PDF 질의응답 시스템")
st.markdown("PDF 문서를 업로드하고 질문해보세요!")

# Initialize session state
if 'rag_system' not in st.session_state:
    st.session_state.rag_system = RAGSystem()
    st.session_state.pdf_loaded = False

# Sidebar
with st.sidebar:
    st.header("⚙️ 설정")
    
    # PDF Upload
    st.subheader("1. PDF 업로드")
    uploaded_file = st.file_uploader("PDF 파일 선택", type=['pdf'])
    
    if uploaded_file and st.button("PDF 처리 시작"):
        with st.spinner("PDF 처리 중..."):
            try:                # Save uploaded file
                pdf_dir = os.getenv("PDF_STORAGE_PATH", "./data/pdfs")
                os.makedirs(pdf_dir, exist_ok=True)
                pdf_path = os.path.join(pdf_dir, uploaded_file.name)
                
                with open(pdf_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Process PDF
                st.session_state.rag_system.ingest_pdf(pdf_path)
                st.session_state.pdf_loaded = True
                st.success("✅ PDF 처리 완료!")
            except Exception as e:
                st.error(f"❌ 오류 발생: {str(e)}")
    
    st.divider()
    
    # Load existing index
    st.subheader("2. 기존 인덱스 로드")
    if st.button("저장된 인덱스 불러오기"):
        try:
            st.session_state.rag_system.load_existing_index()
            st.session_state.pdf_loaded = True
            st.success("✅ 인덱스 로드 완료!")
        except Exception as e:
            st.error(f"❌ 오류 발생: {str(e)}")
    
    st.divider()
    st.info("💡 먼저 PDF를 업로드하거나 기존 인덱스를 로드해주세요.")

# Main area
if st.session_state.pdf_loaded:
    st.success("🎉 시스템 준비 완료! 질문을 입력해주세요.")
    
    # Question input    question = st.text_input("❓ 질문을 입력하세요:", placeholder="예: 이 문서의 주요 내용은 무엇인가요?")
    
    if st.button("🔍 질문하기", type="primary"):
        if question:
            with st.spinner("답변 생성 중..."):
                try:
                    result = st.session_state.rag_system.query(question)
                    
                    # Display answer
                    st.markdown("### 📝 답변")
                    st.info(result['answer'])
                    
                    # Display sources
                    st.markdown("### 📚 참고 문서")
                    for i, source in enumerate(result['sources'], 1):
                        with st.expander(f"출처 {i} - {source['metadata'].get('source_file', 'Unknown')} (페이지 {source['metadata'].get('page', 'N/A')})"):
                            st.text(source['content'])
                
                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")
        else:
            st.warning("⚠️ 질문을 입력해주세요.")
else:
    st.warning("⚠️ 먼저 PDF를 업로드하거나 기존 인덱스를 로드해주세요.")
    
    # Example questions
    st.markdown("### 📖 사용 방법")
    st.markdown("""
    1. **사이드바**에서 PDF 파일을 업로드하거나 기존 인덱스를 로드하세요
    2. 질문을 입력하고 **질문하기** 버튼을 클릭하세요
    3. AI가 문서 내용을 기반으로 답변을 제공합니다
    """)