import os
import streamlit as st
from main import RAGSystem

st.set_page_config(
    page_title="AI 약전 - 대한약전 AI 검색 시스템",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# 공통 CSS (질문 박스 + 답변 박스 스타일)
# -----------------------------
st.markdown(
    """
    <style>
    /* 메인 배경 */
    .main {
        background-color: #f3f3f3;
        background-image: none;
    }

    /* 전체 컨테이너 여백 조금 줄이기 */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* 질문 타이틀 */
    .question-title {
        text-align: center;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 8px;
        color: #333333;
    }

    /* TextArea 앞에 + 아이콘 */
    div.stTextArea {
        position: relative;
    }
    div.stTextArea::before {
        content: "+";
        position: absolute;
        left: 14px;
        top: 11px;
        font-size: 20px;
        font-weight: 600;
        color: #666666;
        z-index: 10;
    }
    div.stTextArea textarea {
        padding-left: 32px !important;
        border-radius: 8px !important;
        font-size: 15px !important;
        border: 1px solid #d0d0d0 !important;
        background-color: #fcfcfc !important;
    }

    /* 답변/요약/출처 공통 박스 */
    .answer-section {
        background-color: #ffffff;
        border: 1px solid #d5d5d5;
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 14px;
        line-height: 1.5;
        margin-bottom: 10px;
        color: #333333;
    }

    .section-title {
        font-weight: 700;
        margin-bottom: 4px;
        color: #444444;
    }

    .source-path {
        font-size: 12px;
        color: #777777;
        margin-top: 2px;
    }

    /* 사이드바 스타일 (짙은 회색) */
    section[data-testid="stSidebar"] {
        background-color: #3b3b3b;
        color: #f3f3f3;
    }

    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stText,
    section[data-testid="stSidebar"] label {
        color: #f3f3f3 !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: #555555;
    }

    /* 버튼 스타일 통일: 연한 회색 */
    .stButton button {
        border-radius: 6px !important;
        font-weight: 500 !important;
        background-color: #e0e0e0 !important;
        color: #333333 !important;
        border: 1px solid #c0c0c0 !important;
        box-shadow: none !important;
    }
    .stButton button:hover {
        background-color: #d5d5d5 !important;
        border-color: #b5b5b5 !important;
    }

    /* Metric / 제목 폰트 색상 */
    h1, h2, h3, h4, h5 {
        color: #333333;
    }

    /* 컬럼 간격 조정 */
    [data-testid="column"] {
        padding: 0 10px;
    }

    /* 라디오 버튼 라벨 회색 */
    div[role="radiogroup"] > label {
        color: #444444 !important;
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
st.sidebar.title("🏥 AI 약전")
st.sidebar.markdown("대한약전 AI 검색 및 분석 시스템")
st.sidebar.markdown("---")

# 사용자 정보 (로그인 기능은 추후 구현)
st.sidebar.markdown("👤 **사용자**: aid003 홍길동")
st.sidebar.markdown("---")

# -----------------------------
# 사이드바: 주요 메뉴
# -----------------------------
st.sidebar.subheader("📋 메뉴")

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
st.sidebar.subheader("⚙️ 인덱스 관리")

# 0-1. 기존 인덱스 로드 버튼
if st.sidebar.button("🔄 저장된 벡터 인덱스 로드", use_container_width=True, type="secondary"):
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
# 메인 타이틀 (메뉴에 따라 동적 변경)
# -----------------------------
if menu_option == "약전 검색":
    st.title("🔍 AI 대한약전 검색")
elif menu_option == "요약 및 비교":
    st.title("📑 약전 비교 및 요약")

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
            st.metric("총 벡터(청크) 수", total_chunks)
        except Exception:
            st.write("총 벡터 수를 가져올 수 없습니다 (FAISS 구조 변경?).")

    with col2:
        st.write("인덱스 저장 경로:", rag.vector_store.store_path)

    st.markdown("---")

# =============================
# 1) 🔍 약전 검색 메뉴
# =============================
if menu_option == "약전 검색":
    st.markdown(
        '<div class="question-title">AI 대한약전 무엇이든 물어봐 주세요?</div>',
        unsafe_allow_html=True,
    )

    question = st.text_area(
        label="질문 입력",
        label_visibility="collapsed",
        height=70,
        placeholder="여기에 질문을 입력하세요.",
        key="question_input",
    )

    if st.button("질문 실행", type="secondary", key="run_search"):
        if not question.strip():
            st.warning("질문을 입력해주세요.")
        else:
            with st.spinner("생각 중..."):
                try:
                    # 1) 원본 RAG 답변
                    result = rag.query(question)

                    if isinstance(result, dict):
                        answer = result.get("answer") or result.get("result") or str(result)
                    else:
                        answer = str(result)

                    # 2) 요약 생성
                    summary_text = None
                    try:
                        summary_prompt = (
                            "다음 내용을 한국어로 3~4줄 정도로 짧게 요약해줘.\n\n"
                            f"{answer}"
                        )
                        summary_result = rag.query(summary_prompt)

                        if isinstance(summary_result, dict):
                            summary_text = (
                                summary_result.get("answer")
                                or summary_result.get("result")
                                or str(summary_result)
                            )
                        else:
                            summary_text = str(summary_result)
                    except Exception as se:
                        summary_text = f"요약 생성 중 오류가 발생했습니다: {se}"

                    # 3) 출처 (PDF 이름 + 페이지)
                    source_docs = None
                    if isinstance(result, dict):
                        source_docs = result.get("source_documents") or result.get("sources")

                    source_html = ""
                    if source_docs:
                        from collections import defaultdict

                        pdf_pages = defaultdict(set)

                        for doc in source_docs:
                            meta = getattr(doc, "metadata", {}) or {}
                            source_path = meta.get("source", "알 수 없는 경로")
                            page = meta.get("page", None)
                            if page is not None:
                                pdf_pages[source_path].add(page)
                            else:
                                _ = pdf_pages[source_path]

                        lines = []
                        for src, pages in pdf_pages.items():
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

                    # ---- 화면 출력 (컬럼 레이아웃) ----
                    col_answer, col_source = st.columns([2, 1])

                    with col_answer:
                        st.markdown(
                            "<div class='answer-section'>"
                            "<div class='section-title'>[AI 답변]</div>"
                            f"{answer.replace(chr(10), '<br>')}"
                            "</div>",
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            "<div class='answer-section'>"
                            "<div class='section-title'>[결과 요약]</div>"
                            f"{(summary_text or '').replace(chr(10), '<br>')}"
                            "</div>",
                            unsafe_allow_html=True,
                        )

                    with col_source:
                        st.markdown("### 📄 출처 및 인용")
                        if source_html:
                            st.markdown(
                                "<div class='answer-section' style='background-color: #ffffff; max-height: 600px; overflow-y: auto;'>"
                                "<div class='section-title'>[출처 문서]</div>"
                                f"{source_html}"
                                "</div>",
                                unsafe_allow_html=True,
                            )

                            if source_docs:
                                with st.expander("📖 문서 내용 미리보기", expanded=False):
                                    for i, doc in enumerate(source_docs[:3], 1):
                                        st.markdown(f"**문서 {i}**")
                                        st.caption(
                                            doc.page_content[:200] + "..."
                                            if len(doc.page_content) > 200
                                            else doc.page_content
                                        )
                                        st.markdown("---")
                        else:
                            st.info("출처 정보가 없습니다.")

                except Exception as e:
                    st.error(f"질문 처리 중 오류: {e}")

    # 청크 미리보기
    with st.expander("🔎 인덱스 안에 들어있는 청크 미리보기", expanded=False):
        mode = st.radio(
            "보기 모드 선택",
            ["검색으로 보기", "그냥 앞쪽 N개 보기"],
            horizontal=True,
            key="preview_mode",
        )

        if mode == "검색으로 보기":
            query = st.text_input("검색 쿼리", value="test", key="preview_query")
            k = st.slider("가져올 청크 개수 (k)", 1, 20, 5, key="preview_k")

            if st.button("🔍 검색 실행", type="secondary", key="preview_search"):
                try:
                    docs = rag.vector_store.search(query, k=k)

                    if not docs:
                        st.warning("검색 결과가 없습니다.")
                    else:
                        for i, d in enumerate(docs, start=1):
                            st.markdown(f"#### 결과 {i}")
                            meta = d.metadata or {}
                            st.write(f"- page: {meta.get('page', '?')}")
                            st.write(f"- source: {meta.get('source', 'N/A')}")
                            st.code(d.page_content, language="markdown")
                except Exception as e:
                    st.error(f"검색 중 오류: {e}")

        else:
            n = st.slider("앞에서부터 볼 청크 개수", 1, 30, 5, key="preview_n")

            if st.button("📄 청크 목록 보기", type="secondary", key="preview_first_n"):
                try:
                    store = db.docstore._dict
                    items = list(store.items())[:n]

                    if not items:
                        st.warning("docstore 안에 데이터가 없습니다.")
                    else:
                        for i, (key, doc) in enumerate(items, start=1):
                            st.markdown(f"#### 청크 {i} (key={key})")
                            meta = doc.metadata or {}
                            st.write(f"- page: {meta.get('page', '?')}")
                            st.write(f"- source: {meta.get('source', 'N/A')}")
                            st.code(doc.page_content, language="markdown")
                except Exception as e:
                    st.error(f"청크 조회 중 오류: {e}")

# =============================
# 2) 📑 비교 및 요약 메뉴
# =============================
elif menu_option == "요약 및 비교":

    compare_type = st.radio(
        "비교 방식 선택",
        ["국가별 약전 비교", "개정 전/후 비교", "자유 텍스트 비교"],
        horizontal=True,
        key="compare_type_radio"
    )

    st.markdown("---")

    # 2-1) 국가별 약전 비교
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
                ["KP (대한약전 12개정)", "KP (대한약전 11개정)", "KP (대한약전 10개정)"],
                key="country1"
            )

            country2 = st.selectbox(
                "비교 약전",
                ["JP (일본약전 18.0)", "USP (미국약전 44)", "EP (유럽약전 11)"],
                key="country2"
            )

        st.info(
            f"💡 **템플릿 예시**: 약전 12개정의 {medicine_name or '아스피린'}을 "
            f"{compare_method} 방식으로 일본 약전과 비교해 줘?"
        )

        if st.button("🔍 비교 실행", type="primary", key="run_country_compare"):
            if not medicine_name.strip():
                st.warning("의약품/성분명을 입력해주세요.")
            else:
                with st.spinner("비교 중..."):
                    try:
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

                        st.markdown("### 📊 비교 결과")

                        st.markdown(f"**제품명**: {medicine_name} | **비교방법**: {compare_method}")

                        st.markdown(
                            "<div class='answer-section'>"
                            "<div class='section-title'>[국가별 약전 비교 분석]</div>"
                            f"{answer.replace(chr(10), '<br>')}"
                            "</div>",
                            unsafe_allow_html=True,
                        )

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

    # 2-2) 개정 전/후 비교
    elif compare_type == "개정 전/후 비교":
        st.subheader("📋 개정 전/후 비교")

        col1, col2 = st.columns(2)

        with col1:
            revision_type = st.selectbox(
                "비교 대상",
                ["의약품/성분", "시험법", "표준시약 및 시액"],
                key="revision_type"
            )

            item_name = st.text_input(
                f"{revision_type} 이름",
                placeholder=f"예: {'아스피린' if revision_type == '의약품/성분' else '용출시험법'}",
                key="revision_item_name"
            )

        with col2:
            version_before = st.selectbox(
                "개정 전 버전",
                ["대한약전 11개정", "대한약전 10개정", "대한약전 9개정"],
                key="version_before"
            )

            version_after = st.selectbox(
                "개정 후 버전",
                ["대한약전 12개정", "대한약전 11개정", "대한약전 10개정"],
                key="version_after"
            )

        compare_method_rev = st.selectbox(
            "비교방법",
            ["변경대비표", "나란히 비교", "차이점만 표시"],
            key="compare_method_rev"
        )

        if st.button("🔍 개정 비교 실행", type="primary", key="run_revision_compare"):
            if not item_name.strip():
                st.warning(f"{revision_type} 이름을 입력해주세요.")
            else:
                with st.spinner("개정 전/후 비교 중..."):
                    try:
                        prompt = (
                            f"{version_before}의 {item_name}과 {version_after}의 {item_name}을 "
                            f"{compare_method_rev} 방식으로 비교해줘.\n\n"
                            "다음을 중심으로 정리해줘:\n"
                            "1. 주요 변경사항\n"
                            "2. 추가된 내용\n"
                            "3. 삭제된 내용\n"
                            "4. 수정된 내용"
                        )

                        result = rag.query(prompt)

                        if isinstance(result, dict):
                            answer = result.get("answer") or result.get("result") or str(result)
                        else:
                            answer = str(result)

                        st.markdown("### 📊 개정 비교 결과")

                        st.markdown(
                            "<div class='answer-section'>"
                            "<div class='section-title'>[개정 전/후 비교 결과]</div>"
                            f"<b>{revision_type}</b>: {item_name}<br>"
                            f"<b>개정 전</b>: {version_before}<br>"
                            f"<b>개정 후</b>: {version_after}<br><br>"
                            f"{answer.replace(chr(10), '<br>')}"
                            "</div>",
                            unsafe_allow_html=True,
                        )

                    except Exception as e:
                        st.error(f"개정 비교 처리 중 오류: {e}")

    # 2-3) 자유 텍스트 비교
    else:
        st.subheader("📝 자유 텍스트 비교 및 요약")

        mode = st.radio(
            "모드 선택",
            ["두 내용 비교", "한 내용 요약"],
            horizontal=True,
            key="free_compare_mode",
        )

        text1 = st.text_area(
            "내용 A",
            height=150,
            placeholder="비교하거나 요약할 첫 번째 내용을 입력하세요.",
            key="free_text1",
        )

        text2 = ""
        if mode == "두 내용 비교":
            text2 = st.text_area(
                "내용 B",
                height=150,
                placeholder="비교할 두 번째 내용을 입력하세요.",
                key="free_text2",
            )

        if st.button("실행", type="primary", key="run_free_compare"):
            if not text1.strip():
                st.warning("내용 A를 입력해주세요.")
            elif mode == "두 내용 비교" and not text2.strip():
                st.warning("내용 B를 입력해주세요.")
            else:
                with st.spinner("비교/요약 중..."):
                    try:
                        if mode == "두 내용 비교":
                            prompt = (
                                "다음 두 내용을 한국어로 비교·분석해줘.\n\n"
                                "[내용 A]\n"
                                f"{text1}\n\n"
                                "[내용 B]\n"
                                f"{text2}\n\n"
                                "1) 공통점\n"
                                "2) 차이점\n"
                                "3) 중요한 포인트를 정리해줘."
                            )
                        else:  # 한 내용 요약
                            prompt = (
                                "다음 내용을 한국어로 3~5줄 정도로 요약해줘.\n\n"
                                f"{text1}"
                            )

                        result = rag.query(prompt)

                        if isinstance(result, dict):
                            compare_answer = result.get("answer") or result.get("result") or str(result)
                        else:
                            compare_answer = str(result)

                        st.markdown(
                            "<div class='answer-section'>"
                            "<div class='section-title'>[비교/요약 결과]</div>"
                            f"{compare_answer.replace(chr(10), '<br>')}"
                            "</div>",
                            unsafe_allow_html=True,
                        )

                    except Exception as e:
                        st.error(f"비교/요약 처리 중 오류: {e}")
