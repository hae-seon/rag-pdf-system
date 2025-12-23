import os
import streamlit as st
from main import RAGSystem
from pdf_utils import pdf_page_to_image

st.set_page_config(
    page_title="AI 약전 - 대한약전 AI 검색 시스템",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 이미지 디자인에 영감을 받은 깔끔한 스타일
st.markdown(
    """
    <style>
    /* 전체 배경 - 밝고 깨끗한 흰색 */
    .main {
        background: #ffffff !important;
        padding: 2rem;
    }

    .stApp {
        background: #ffffff !important;
    }

    [data-testid="stAppViewContainer"] {
        background: #ffffff !important;
    }

    [data-testid="stHeader"] {
        background: #ffffff !important;
    }

    /* 헤더 영역 */
    .main-header {
        text-align: center;
        padding: 3rem 2rem 2rem 2rem;
        margin-bottom: 2rem;
    }

    .main-header h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }

    .main-header p {
        font-size: 1.1rem;
        color: #6c757d;
        margin-top: 0.5rem;
    }

    /* 사이드바 - 밝은 배경 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%) !important;
        border-right: 1px solid #e9ecef;
    }

    section[data-testid="stSidebar"] .stButton button {
        width: 100%;
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }

    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }

    /* 질문 입력 영역 - 중앙 정렬 & 깔끔한 디자인 */
    .question-section {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 900px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
    }

    .question-title {
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        color: #2c3e50;
    }

    div.stTextArea textarea {
        border-radius: 16px !important;
        border: 2px solid #e0e0e0 !important;
        background: #ffffff !important;
        color: #2c3e50 !important;
        font-size: 16px !important;
        padding: 20px !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }

    div.stTextArea textarea:focus {
        border-color: #667eea !important;
        background: #ffffff !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15), 0 4px 16px rgba(0,0,0,0.1);
    }

    div.stTextArea textarea::placeholder {
        color: #adb5bd;
    }

    /* 답변 섹션 - 카드형 디자인 */
    .answer-section {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 16px;
        padding: 2rem;
        font-size: 15px;
        line-height: 1.8;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }

    .section-title {
        color: #2c3e50;
        font-weight: 700;
        font-size: 18px;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e9ecef;
    }

    .source-path {
        font-size: 12px;
        color: #6c757d;
        margin-top: 4px;
    }

    /* 버튼 - 밝고 예쁜 스타일 */
    .stButton button {
        border-radius: 12px;
        font-weight: 600;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }

    .stButton button[kind="secondary"] {
        background: white !important;
        color: #667eea !important;
        border: 2px solid #667eea !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .stButton button[kind="secondary"]:hover {
        background: #667eea !important;
        color: white !important;
    }

    /* Primary 버튼 */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
    }

    /* 메트릭 */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #667eea;
    }

    /* 라디오 버튼 */
    .stRadio > label {
        font-weight: 600;
        color: #2c3e50;
    }

    /* 익스팬더 - 둥근 모서리 */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        font-weight: 600;
        color: #2c3e50;
    }

    /* Spinner - 로딩 애니메이션 색상 */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }

    div[data-testid="stSpinner"] > div {
        border-top-color: #667eea !important;
    }

    .stSpinner {
        color: #2c3e50 !important;
    }

    /* 성공/에러 메시지 - 둥근 디자인 */
    .stSuccess {
        background-color: #d4edda !important;
        color: #155724 !important;
        border-radius: 12px;
        border: none;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.2);
    }

    .stError {
        background-color: #f8d7da;
        color: #721c24;
        border-radius: 12px;
        border: none;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(244, 67, 54, 0.2);
    }

    .stInfo {
        background-color: #d1ecf1;
        color: #0c5460;
        border-radius: 12px;
        border: none;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(33, 150, 243, 0.2);
    }

    /* 구분선 */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #e9ecef;
    }

    /* 컬럼 간격 */
    [data-testid="column"] {
        padding: 0 0.75rem;
    }

    /* 입력 필드 */
    input {
        background: #f8f9fa !important;
        color: #2c3e50 !important;
        border: 2px solid #e9ecef !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
        transition: all 0.3s ease;
    }

    input:focus {
        border-color: #667eea !important;
        background: #ffffff !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15);
    }

    /* 헤더 타이틀 스타일 */
    h1, h2, h3 {
        color: #2c3e50;
        font-weight: 700;
    }

    /* 전체 앱 배경 강제 밝게 */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background-color: #ffffff !important;
    }

    /* 메인 블록 배경 */
    .block-container {
        background-color: #ffffff !important;
        padding-top: 2rem !important;
    }

    /* 모든 섹션 배경 */
    section {
        background-color: transparent !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# RAGSystem 한 번만 생성
# -----------------------------
@st.cache_resource
def get_rag_system():
    return RAGSystem()

rag = get_rag_system()

# index 로드 상태 플래그
if "index_loaded" not in st.session_state:
    st.session_state["index_loaded"] = False

# -----------------------------
# 사이드바: 로고 및 타이틀
# -----------------------------
st.sidebar.markdown(
    """
    <div style="text-align: center; padding: 1.5rem 0;">
        <h1 style="font-size: 2rem; margin-bottom: 0.5rem;">🏥 AI 약전</h1>
        <p style="font-size: 0.9rem; color: #6c757d;">대한약전 AI 검색 시스템</p>
    </div>
    """,
    unsafe_allow_html=True
)
st.sidebar.markdown("---")

# 사용자 정보 (로그인 기능은 추후 구현)
st.sidebar.markdown(
    """
    <div style="padding: 0.75rem; background: #f8f9fa; border-radius: 8px; margin-bottom: 1rem;">
        <p style="margin: 0; font-size: 0.9rem;"><b>👤 사용자</b></p>
        <p style="margin: 0; font-size: 0.85rem; color: #6c757d;">aid003 홍길동</p>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# 사이드바: 주요 메뉴
# -----------------------------
st.sidebar.markdown("### 📋 메뉴")

# 메뉴 선택 (라디오 버튼으로 변경)
if "menu_selection" not in st.session_state:
    st.session_state["menu_selection"] = "약전 검색"

menu_option = st.sidebar.radio(
    "메뉴를 선택하세요",
    ["약전 검색", "요약 및 비교"],
    index=0,
    label_visibility="collapsed"
)

st.session_state["menu_selection"] = menu_option

st.sidebar.markdown("---")

# -----------------------------
# 사이드바: 인덱스 관리
# -----------------------------
st.sidebar.markdown("### ⚙️ 인덱스 관리")

# 0-1. 기존 인덱스 로드 버튼
if st.sidebar.button("🔄 벡터 인덱스 로드", use_container_width=True, type="secondary"):
    try:
        rag.load_existing_index()
        st.session_state["index_loaded"] = True
        st.sidebar.success("✅ 인덱스 로드 완료")
    except Exception as e:
        st.sidebar.error(f"인덱스 로드 실패: {e}")

# 0-2. PDF 업로드
with st.sidebar.expander("📂 PDF 업로드", expanded=False):
    uploaded_files = st.file_uploader(
        "PDF 파일들을 업로드하세요",
        type=["pdf"],
        accept_multiple_files=True,
        key="pdf_uploader"
    )

    if st.button("📥 인덱스에 추가", use_container_width=True, type="secondary", key="upload_btn"):
        if not uploaded_files:
            st.warning("먼저 PDF 파일을 업로드해주세요.")
        else:
            try:
                upload_dir = os.path.join("data", "uploaded_pdfs")
                os.makedirs(upload_dir, exist_ok=True)

                all_chunks = []
                for file in uploaded_files:
                    save_path = os.path.join(upload_dir, file.name)
                    with open(save_path, "wb") as f:
                        f.write(file.getbuffer())

                    docs = rag.pdf_processor.process_pdf(save_path)
                    all_chunks.extend(docs)

                if not all_chunks:
                    st.error("업로드한 PDF에서 추출된 내용이 없습니다.")
                else:
                    if rag.vector_store.vectorstore is None:
                        rag.vector_store.create_vectorstore(all_chunks)
                    else:
                        rag.vector_store.ingest_documents(all_chunks)

                    st.session_state["index_loaded"] = True
                    st.success(f"✅ PDF {len(uploaded_files)}개를 인덱스에 반영했습니다.")
            except Exception as e:
                st.error(f"PDF 업로드/임베딩 중 오류: {e}")

# -----------------------------
# 메인 헤더 (이미지 디자인 스타일)
# -----------------------------
if menu_option == "약전 검색":
    st.markdown(
        """
        <div class="main-header">
            <h1>🏥 방대한 약전 자료를 친절하게 이해하세요</h1>
            <p>AI 대한약전 검색 시스템으로 빠르고 정확한 정보를 찾아보세요</p>
        </div>
        """,
        unsafe_allow_html=True
    )
elif menu_option == "요약 및 비교":
    st.markdown(
        """
        <div class="main-header">
            <h1>📑 약전 비교 및 요약</h1>
            <p>국가별, 개정 전후, 자유 텍스트 비교 분석</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# 아직 인덱스가 전혀 없으면 멈춤
if (not st.session_state["index_loaded"]) and (rag.vector_store.vectorstore is None):
    st.info(
        "왼쪽 사이드바에서 **[저장된 벡터 인덱스 로드]** 버튼을 누르거나,\n"
        "**PDF 파일을 업로드**하여 인덱스를 먼저 만들어주세요."
    )
    st.stop()

# 여기까지 왔으면 벡터스토어는 로드된 상태
db = rag.vector_store.vectorstore

# -----------------------------
# 상단: 전체 정보 요약 (약전 검색 메뉴에서만 표시)
# -----------------------------
if menu_option == "약전 검색":
    col1, col2 = st.columns(2)

    with col1:
        try:
            total_chunks = len(db.index_to_docstore_id)
            st.metric("📊 총 벡터(청크) 수", f"{total_chunks:,}")
        except Exception:
            st.metric("📊 총 벡터(청크) 수", "N/A")

    with col2:
        st.metric("💾 인덱스 상태", "로드 완료 ✓")

    st.markdown("<br>", unsafe_allow_html=True)

# =============================
# 1) 🔍 약전 검색 메뉴
# =============================
if menu_option == "약전 검색":
    # 질문 입력 영역을 카드 형태로 감싸기
    st.markdown(
        """
        <div class="question-section">
            <div class="question-title">💬 AI 대한약전 무엇이든 물어봐 주세요</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    question = st.text_area(
        label="질문 입력",
        label_visibility="collapsed",
        height=100,
        placeholder="소스를 검색하거나 입력하세요 (예: 아스피린의 성상과 특성은?)",
        key="question_input",
    )

    # 버튼을 중앙에 배치
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        search_clicked = st.button("🔍 질문 실행", type="primary", key="run_search", use_container_width=True)

    if search_clicked:
        if not question.strip():
            st.warning("질문을 입력해주세요.")
        else:
            with st.spinner("생각 중..."):
                try:
                    # ===== 디버깅 로그 =====
                    import traceback
                    print("\n" + "="*50)
                    print("🔍 [DEBUG] RAG Query 시작")
                    print(f"질문: {question}")
                    print("="*50)

                    # 1) 원본 RAG 답변
                    print("[STEP 1] RAG query 호출 중...")
                    result = rag.query(question)
                    print(f"[STEP 1] ✅ RAG query 완료")
                    print(f"[STEP 1] result 타입: {type(result)}")
                    print(f"[STEP 1] result 내용 (첫 200자): {str(result)[:200]}")

                    if isinstance(result, dict):
                        print(f"[STEP 1] result keys: {result.keys()}")
                        answer = result.get("answer") or result.get("result") or str(result)
                    else:
                        answer = str(result)

                    print(f"[STEP 1] answer 길이: {len(answer)} 글자")
                    print(f"[STEP 1] answer 미리보기: {answer[:100]}...")

                    # 2) 요약 생성
                    print("\n[STEP 2] 요약 생성 시작...")
                    summary_text = None
                    try:
                        summary_prompt = (
                            "다음 내용을 한국어로 3~4줄 정도로 짧게 요약해줘.\n\n"
                            f"{answer}"
                        )
                        print("[STEP 2] 요약 query 호출 중...")
                        summary_result = rag.query(summary_prompt)
                        print(f"[STEP 2] ✅ 요약 완료")
                        print(f"[STEP 2] summary_result 타입: {type(summary_result)}")

                        if isinstance(summary_result, dict):
                            summary_text = (
                                summary_result.get("answer")
                                or summary_result.get("result")
                                or str(summary_result)
                            )
                        else:
                            summary_text = str(summary_result)
                        print(f"[STEP 2] summary_text 길이: {len(summary_text)} 글자")
                    except Exception as se:
                        print(f"[STEP 2] ❌ 요약 생성 실패: {se}")
                        traceback.print_exc()
                        summary_text = f"요약 생성 중 오류가 발생했습니다: {se}"

                    # 3) 출처 (PDF 이름 + 페이지)
                    print("\n[STEP 3] 출처 정보 추출 시작...")
                    source_docs = None
                    if isinstance(result, dict):
                        source_docs = result.get("source_documents") or result.get("sources")
                        print(f"[STEP 3] source_docs 타입: {type(source_docs)}")
                        print(f"[STEP 3] source_docs 개수: {len(source_docs) if source_docs else 0}")
                    else:
                        print("[STEP 3] result가 dict가 아니므로 source_docs 추출 불가")

                    source_html = ""
                    if source_docs:
                        from collections import defaultdict

                        pdf_pages = defaultdict(set)

                        for idx, doc in enumerate(source_docs):
                            print(f"\n[STEP 3] 문서 {idx+1} 처리 중...")
                            print(f"[STEP 3]   doc 타입: {type(doc)}")

                            # doc가 dict인 경우와 객체인 경우 모두 처리
                            if isinstance(doc, dict):
                                print("[STEP 3]   doc는 dict")
                                meta = doc.get("metadata", {})
                                print(f"[STEP 3]   metadata keys: {meta.keys() if meta else 'None'}")
                                source_path = meta.get("source_file") or meta.get("source", "알 수 없는 경로")
                                page = meta.get("page", None)
                            else:
                                print("[STEP 3]   doc는 객체")
                                meta = getattr(doc, "metadata", {}) or {}
                                print(f"[STEP 3]   metadata: {meta}")
                                source_path = meta.get("source_file") or meta.get("source", "알 수 없는 경로")
                                page = meta.get("page", None)

                            print(f"[STEP 3]   source_path: {source_path}")
                            print(f"[STEP 3]   page: {page}")

                            if page is not None:
                                pdf_pages[source_path].add(page)
                            else:
                                _ = pdf_pages[source_path]

                        print(f"\n[STEP 3] pdf_pages 수집 완료: {len(pdf_pages)}개 파일")

                        lines = []
                        for src, pages in pdf_pages.items():
                            if src and src != "알 수 없는 경로":
                                filename = os.path.basename(src)
                                if pages:
                                    page_list = ", ".join(str(p) for p in sorted(pages))
                                    lines.append(
                                        f"<b>{filename}</b> (page: {page_list})"
                                        f"<div class='source-path'>원본 경로: {src}</div>"
                                    )
                                else:
                                    lines.append(
                                        f"<b>{filename}</b>"
                                        f"<div class='source-path'>원본 경로: {src}</div>"
                                    )
                        source_html = "<br>".join(lines)

                    # ---- 화면 출력 ----
                    print("\n[STEP 4] 화면 출력 시작...")
                    # AI 답변 (결과 요약 데이터 표시)
                    print("[STEP 4] AI 답변 출력 중...")
                    st.markdown(
                        "<div class='answer-section'>"
                        "<div class='section-title'>[AI 답변]</div>"
                        f"{(summary_text or answer).replace(chr(10), '<br>')}"
                        "</div>",
                        unsafe_allow_html=True,
                    )
                    print("[STEP 4] ✅ AI 답변 출력 완료")

                    # 📄 출처 및 PDF 캡처 (클릭형 expander)
                    print("[STEP 4] 출처 및 인용 섹션 출력 중...")
                    st.markdown("---")
                    st.markdown("### 📄 출처 및 인용")

                    if source_docs:
                        print(f"[STEP 4] source_docs 있음 ({len(source_docs)}개)")
                        # 출처별로 그룹화
                        from collections import defaultdict
                        source_groups = defaultdict(list)

                        for doc in source_docs:
                            # doc가 dict인 경우와 객체인 경우 모두 처리
                            if isinstance(doc, dict):
                                meta = doc.get("metadata", {})
                                source_path = meta.get("source_file") or meta.get("source", None)
                                page = meta.get("page", None)
                            else:
                                meta = getattr(doc, "metadata", {}) or {}
                                source_path = meta.get("source_file") or meta.get("source", None)
                                page = meta.get("page", None)

                            if source_path and page is not None:
                                source_groups[source_path].append(page)

                        # 각 출처별로 expander 생성
                        for source_path, pages in source_groups.items():
                            filename = os.path.basename(source_path)
                            unique_pages = sorted(set(pages))
                            page_list_str = ", ".join(str(p + 1) for p in unique_pages)

                            # 📄 출처 클릭하면 PDF 캡처본 표시
                            with st.expander(f"📄 {filename} (페이지: {page_list_str})", expanded=False):
                                st.caption(f"원본 경로: {source_path}")
                                st.markdown("---")

                                # 각 페이지의 PDF 이미지 표시
                                for page in unique_pages[:3]:  # 최대 3페이지까지
                                    try:
                                        st.markdown(f"**📸 페이지 {page + 1}**")
                                        page_image = pdf_page_to_image(source_path, page, dpi=150)

                                        if page_image:
                                            st.image(page_image, width=400, caption=f"페이지 {page + 1}")
                                        else:
                                            st.warning(f"페이지 {page + 1}: PDF 이미지 변환 실패")
                                    except Exception as img_error:
                                        st.error(f"페이지 {page + 1} 변환 오류: {str(img_error)}")

                                    st.markdown("---")
                    else:
                        st.info("출처 정보가 없습니다.")

                    # 문서 내용 미리보기
                    if source_docs:
                        with st.expander("📖 문서 내용 미리보기", expanded=False):
                            for i, doc in enumerate(source_docs[:3], 1):
                                st.markdown(f"**문서 {i}**")
                                # doc가 dict인 경우와 객체인 경우 모두 처리
                                if isinstance(doc, dict):
                                    content = doc.get("content", "")
                                else:
                                    content = getattr(doc, "page_content", "")
                                st.caption(content[:200] + "..." if len(content) > 200 else content)
                                st.markdown("---")

                except Exception as e:
                    st.error(f"질문 처리 중 오류: {e}")
                    st.code(traceback.format_exc())  # ✅ 전체 에러 로그(스택트레이스) 출력

# =============================
# 2) 📑 비교 및 요약 메뉴
# =============================
elif menu_option == "요약 및 비교":

    # 비교 방식 선택
    compare_type = st.radio(
        "비교 방식 선택",
        ["국가별 약전 비교", "개정 전/후 비교"],
        horizontal=True,
        key="compare_type_radio"
    )

    st.markdown("---")

    # =============================
    # 2-1) 국가별 약전 비교
    # =============================
    if compare_type == "국가별 약전 비교":
        st.subheader("🌏 국가별 약전 비교")

        col1, col2 = st.columns(2)

        with col1:
            medicine_name = st.text_input(
                "의약품/성분명",
                placeholder="예: 아스피린",
                key="medicine_name"
            )

            compare_method = st.selectbox(
                "비교방법",
                ["변경대비표", "나란히 비교", "차이점만 표시"],
                key="compare_method"
            )

        with col2:
            country1 = st.selectbox(
                "기준 약전",
                ["KP (대한약전 12개정)", "KP (대한약전 11개정)", "KP (대한약전 10개정)",
                 "JP (일본약전 18.0)", "USP (미국약전 44)", "EP (유럽약전 11)"],
                key="country1"
            )

            country2 = st.selectbox(
                "비교 약전",
                ["JP (일본약전 18.0)", "USP (미국약전 44)", "EP (유럽약전 11)",
                 "KP (대한약전 12개정)", "KP (대한약전 11개정)", "KP (대한약전 10개정)"],
                key="country2"
            )



        if st.button("🔍 비교 실행", type="primary", key="run_country_compare"):
            if not medicine_name.strip():
                st.warning("의약품/성분명을 입력해주세요.")
            else:
                with st.spinner("비교 중..."):
                    try:
                        # 비교 쿼리 생성
                        prompt = (
                            f"{country1}의 {medicine_name}과 {country2}의 {medicine_name}을 "
                            f"{compare_method} 방식으로 비교해줘.\n\n"
                            "다음 항목을 포함해서 정리해줘:\n"
                            "1. 제품명 및 화학식\n"
                            "2. 성상 및 물리적 특성\n"
                            "3. 주요 차이점\n"
                            "4. 공통점"
                        )

                        result = rag.query(prompt)

                        if isinstance(result, dict):
                            answer = result.get("answer") or result.get("result") or str(result)
                        else:
                            answer = str(result)

                        # 결과 표시 (테이블 형식)
                        st.markdown("### 📊 비교 결과")

                        # 테이블 헤더
                        st.markdown(f"**제품명**: {medicine_name} | **비교방법**: {compare_method}")

                        # 비교 테이블
                        import pandas as pd

                        # 간단한 테이블 형식으로 표시
                        compare_data = {
                            "항목": ["약전", "설명"],
                            country1: [country1, "기준 약전 내용"],
                            country2: [country2, "비교 약전 내용"],
                            "출처": ["출처 정보", "비교 분석"]
                        }

                        # 답변 내용 표시
                        st.markdown(
                            "<div class='answer-section'>"
                            "<div class='section-title'>[국가별 약전 비교 분석]</div>"
                            f"{answer.replace(chr(10), '<br>')}"
                            "</div>",
                            unsafe_allow_html=True,
                        )

                        # 출처 정보 가져오기
                        if isinstance(result, dict):
                            source_docs = result.get("source_documents") or result.get("sources")
                            if source_docs:
                                st.markdown("**📄 참고 문서**")
                                for i, doc in enumerate(source_docs[:3], 1):
                                    meta = getattr(doc, "metadata", {}) or {}
                                    source_path = meta.get("source", "알 수 없음")
                                    page = meta.get("page", "?")
                                    filename = os.path.basename(source_path)
                                    st.caption(f"{i}. {filename} (페이지 {page})")

                    except Exception as e:
                        st.error(f"비교 처리 중 오류: {e}")

    # =============================
    # 2-2) 개정 전/후 비교 (변경대비표 활용)
    # =============================
    elif compare_type == "개정 전/후 비교":
        st.subheader("📋 개정 전/후 비교")
        st.info("💡 대한민국약전 일부개정고시 변경대비표를 기반으로 검색합니다")

        item_name = st.text_input(
            "의약품/성분명 또는 검색어",
            placeholder="예: 아스피린, 용출시험법, 잔류용매 등",
            key="revision_item_name"
        )

        if st.button("🔍 변경사항 검색", type="primary", key="run_revision_compare"):
            if not item_name.strip():
                st.warning("검색어를 입력해주세요.")
            else:
                with st.spinner("변경대비표에서 검색 중..."):
                    try:
                        # 1) 변경대비표 PDF에서 상세 정보 검색 (더 구체적인 프롬프트)
                        prompt = (
                            f"대한민국약전 일부개정고시 변경대비표에서 '{item_name}'에 대한 변경사항을 찾아서 다음을 정확히 구분해서 답변해줘:\n\n"
                            "=== 제품명 ===\n"
                            "품목명을 정확히 알려줘\n\n"
                            "=== 현행 (개정 전) ===\n"
                            "현재 약전에 기재된 내용을 모두 알려줘\n\n"
                            "=== 개정안 (개정 후) ===\n"
                            "새로 개정된 내용을 모두 알려줘\n\n"
                            "반드시 위 형식으로 구분해서 답변해줘."
                        )

                        result = rag.query(prompt)

                        if isinstance(result, dict):
                            answer = result.get("answer") or result.get("result") or str(result)
                            source_docs = result.get("source_documents") or result.get("sources")
                        else:
                            answer = str(result)
                            source_docs = None

                        # 2) 변경사항 분석 (삭제, 수정, 추가 항목)
                        analysis_prompt = (
                            f"다음 개정 전/후 비교 내용을 분석해서 다음 형식으로 정리해줘:\n\n"
                            f"{answer}\n\n"
                            "=== 변경사항 분석 ===\n"
                            "1. 삭제된 내용: (있으면 나열, 없으면 '없음')\n"
                            "2. 수정된 내용: (있으면 나열, 없으면 '없음')\n"
                            "3. 추가된 내용: (있으면 나열, 없으면 '없음')\n"
                            "4. 요약: 3줄 이내로 핵심 변경사항 요약\n\n"
                            "반드시 위 형식으로 답변해줘."
                        )

                        analysis_result = rag.query(analysis_prompt)

                        if isinstance(analysis_result, dict):
                            analysis = analysis_result.get("answer") or analysis_result.get("result") or ""
                        else:
                            analysis = str(analysis_result)

                        # 3) 제품명 추출 (AI에게 직접 물어보기)
                        product_name = item_name  # 기본값
                        try:
                            product_name_prompt = (
                                f"다음 내용에서 제품명 또는 품목명만 추출해서 알려줘. 다른 설명 없이 제품명만 답변해:\n\n{answer[:500]}"
                            )
                            product_name_result = rag.query(product_name_prompt)

                            if isinstance(product_name_result, dict):
                                extracted_name = product_name_result.get("answer") or product_name_result.get("result") or ""
                            else:
                                extracted_name = str(product_name_result)

                            # 추출된 제품명이 너무 길지 않으면 사용
                            if extracted_name and len(extracted_name.strip()) < 100:
                                product_name = extracted_name.strip()
                        except:
                            # 실패하면 answer에서 직접 파싱 시도
                            if "=== 제품명 ===" in answer:
                                try:
                                    extracted = answer.split("=== 제품명 ===")[1].split("===")[0].strip()
                                    if extracted and len(extracted) < 100:
                                        product_name = extracted
                                except:
                                    pass
                            elif "제품명:" in answer:
                                try:
                                    extracted = answer.split("제품명:")[1].split("\n")[0].strip()
                                    if extracted and len(extracted) < 100:
                                        product_name = extracted
                                except:
                                    pass
                            elif "품목명:" in answer:
                                try:
                                    extracted = answer.split("품목명:")[1].split("\n")[0].strip()
                                    if extracted and len(extracted) < 100:
                                        product_name = extracted
                                except:
                                    pass

                        # 결과 표시
                        st.markdown("### 📊 개정 전/후 비교표")

                        # 제품명 표시
                        st.markdown(f"**제품명**: {product_name}")
                        st.markdown("---")

                        # 표 형식으로 개정 전/후 비교 (HTML 테이블 사용)
                        st.markdown(
                            """
                            <style>
                            .comparison-table {
                                width: 100%;
                                border-collapse: collapse;
                                margin: 1rem 0;
                                background: white;
                                border-radius: 8px;
                                overflow: hidden;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                            }
                            .comparison-table th {
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white;
                                padding: 1rem;
                                text-align: center;
                                font-weight: 600;
                                font-size: 16px;
                            }
                            .comparison-table td {
                                padding: 1.5rem;
                                border: 1px solid #e9ecef;
                                vertical-align: top;
                                line-height: 1.8;
                            }
                            .comparison-table .label-cell {
                                background: #f8f9fa;
                                font-weight: 600;
                                width: 150px;
                                text-align: center;
                            }
                            .comparison-table .content-cell {
                                background: white;
                            }
                            </style>
                            """,
                            unsafe_allow_html=True
                        )

                        # 개정 전/후 내용을 파싱
                        before_content = "현행 내용을 찾는 중..."
                        after_content = "개정안 내용을 찾는 중..."

                        # answer에서 개정 전/후 분리 (더 정확하게)
                        try:
                            if "=== 현행" in answer and "=== 개정안" in answer:
                                parts = answer.split("=== 개정안")
                                before_part = parts[0].split("=== 현행")[-1].strip()
                                after_part = parts[1].split("===")[0].strip() if "===" in parts[1] else parts[1].strip()

                                before_content = before_part.replace("\n", "<br>")
                                after_content = after_part.replace("\n", "<br>")
                            elif "현행" in answer and "개정안" in answer:
                                parts = answer.split("개정안")
                                before_part = parts[0].split("현행")[-1].strip()
                                after_part = parts[1].strip()

                                before_content = before_part.replace("\n", "<br>")
                                after_content = after_part.replace("\n", "<br>")
                        except Exception as e:
                            st.warning(f"내용 파싱 중 오류: {e}")

                        # 비교표 출력
                        comparison_html = f"""
                        <table class="comparison-table">
                            <thead>
                                <tr>
                                    <th>제품명</th>
                                    <th colspan="2">{product_name}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td class="label-cell">현행<br>(개정 전)</td>
                                    <td class="content-cell" colspan="2">{before_content}</td>
                                </tr>
                                <tr>
                                    <td class="label-cell">개정안<br>(개정 후)</td>
                                    <td class="content-cell" colspan="2">{after_content}</td>
                                </tr>
                            </tbody>
                        </table>
                        """
                        st.markdown(comparison_html, unsafe_allow_html=True)

                        # 변경사항 분석
                        st.markdown("---")
                        st.markdown(
                            "<div class='answer-section'>"
                            "<div class='section-title'>🔍 변경사항 분석</div>"
                            f"{analysis.replace(chr(10), '<br>')}"
                            "</div>",
                            unsafe_allow_html=True,
                        )

                        # 📄 출처 및 PDF 이미지 (약전 검색과 동일한 방식)
                        st.markdown("---")
                        st.markdown("### 📄 출처 및 인용")

                        if source_docs:
                            # 출처별로 그룹화
                            from collections import defaultdict
                            source_groups = defaultdict(list)

                            for doc in source_docs:
                                # doc가 dict인 경우와 객체인 경우 모두 처리
                                if isinstance(doc, dict):
                                    meta = doc.get("metadata", {})
                                    source_path = meta.get("source_file") or meta.get("source", None)
                                    page = meta.get("page", None)
                                else:
                                    meta = getattr(doc, "metadata", {}) or {}
                                    source_path = meta.get("source_file") or meta.get("source", None)
                                    page = meta.get("page", None)

                                if source_path and page is not None:
                                    source_groups[source_path].append(page)

                            # 각 출처별로 expander 생성
                            for source_path, pages in source_groups.items():
                                filename = os.path.basename(source_path)
                                unique_pages = sorted(set(pages))
                                page_list_str = ", ".join(str(p + 1) for p in unique_pages)

                                # 📄 출처 클릭하면 PDF 캡처본 표시
                                with st.expander(f"📄 {filename} (페이지: {page_list_str})", expanded=False):
                                    st.caption(f"원본 경로: {source_path}")
                                    st.markdown("---")

                                    # 각 페이지의 PDF 이미지 표시
                                    for page in unique_pages[:3]:  # 최대 3페이지까지
                                        try:
                                            st.markdown(f"**📸 페이지 {page + 1}**")
                                            page_image = pdf_page_to_image(source_path, page, dpi=150)

                                            if page_image:
                                                st.image(page_image, width=400, caption=f"페이지 {page + 1}")
                                            else:
                                                st.warning(f"페이지 {page + 1}: PDF 이미지 변환 실패")
                                        except Exception as img_error:
                                            st.error(f"페이지 {page + 1} 변환 오류: {str(img_error)}")

                                        st.markdown("---")
                        else:
                            st.info("출처 정보가 없습니다.")

                        # 전체 AI 답변 (상세 내용)
                        with st.expander("📋 전체 상세 내용 보기", expanded=False):
                            st.markdown("**원본 답변:**")
                            st.markdown(answer)
                            st.markdown("---")
                            st.markdown("**변경사항 분석:**")
                            st.markdown(analysis)

                    except Exception as e:
                        st.error(f"검색 중 오류: {e}")

# =============================
# 3) 기타 메뉴들 (준비 중)
# =============================
elif menu_option == "시험결과분석":
    st.info("🚧 시험결과분석 기능은 준비 중입니다.")

elif menu_option == "신규약전설정":
    st.info("🚧 신규약전설정 기능은 준비 중입니다.")

elif menu_option == "외국약전법역":
    st.info("🚧 외국약전법역 기능은 준비 중입니다.")
