import streamlit as st
from main import RAGSystem

st.set_page_config(
    page_title="RAG PDF System - VectorDB 뷰어",
    page_icon="📚",
    layout="wide",
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

st.sidebar.title("RAG PDF System")
st.sidebar.markdown("벡터DB에 **이미 저장된 인덱스만** 사용합니다.")

# -----------------------------
# 인덱스 로드 버튼
# -----------------------------
if not st.session_state["index_loaded"]:
    if st.sidebar.button("🔄 벡터 인덱스 로드하기", use_container_width=True):
        try:
            rag.load_existing_index()
            st.session_state["index_loaded"] = True
            st.sidebar.success("✅ 인덱스 로드 완료")
        except Exception as e:
            st.sidebar.error(f"인덱스 로드 실패: {e}")
else:
    st.sidebar.success("✅ 인덱스 로드됨")


st.title("📚 VectorDB 기반 QA & 청크 미리보기")

if not st.session_state["index_loaded"]:
    st.info("왼쪽 사이드바에서 **[벡터 인덱스 로드하기]** 버튼을 먼저 눌러주세요.")
    st.stop()

# 여기까지 왔으면 벡터스토어는 로드된 상태
db = rag.vector_store.vectorstore

# -----------------------------
# 상단: 전체 정보 요약
# -----------------------------
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

# -----------------------------
# 탭: 질문 / 청크 미리보기
# -----------------------------
tab_qna, tab_preview = st.tabs(["💬 질문하기", "🔎 청크 미리보기"])

# =============================
# 1) 질문 탭 - 이미 있는 VectorDB로만 QA
# =============================
with tab_qna:
    st.subheader("💬 벡터DB 기반 질문하기")

    question = st.text_area(
        "질문을 입력하세요 (PDF 업로드 없이, 기존 인덱스만 사용)",
        height=100,
        placeholder="예) 약전에 대해서 알려줘",
    )


    if st.button("질문 실행", type="primary"):
        if not question.strip():
            st.warning("질문을 입력해주세요.")
        else:
            with st.spinner("생각 중..."):
                try:
                    # RAGSystem.query()가 dict 또는 str을 반환한다고 가정
                    result = rag.query(question)

                    # 반환 타입에 맞춰 안전하게 처리
                    if isinstance(result, dict):
                        answer = result.get("answer") or result.get("result") or str(result)
                    else:
                        answer = str(result)

                    st.markdown("### ✅ 답변")
                    st.write(answer)

                    # 소스 문서도 같이 보여주기 (있으면)
                    source_docs = None
                    if isinstance(result, dict):
                        source_docs = result.get("source_documents") or result.get("sources")

                    if source_docs:
                        st.markdown("### 📎 참고한 청크들")
                        for i, doc in enumerate(source_docs, start=1):
                            st.markdown(f"**참고 청크 {i}**")
                            meta = doc.metadata or {}
                            st.write(f"- page: {meta.get('page', '?')}")
                            st.write(f"- source: {meta.get('source', 'N/A')}")
                            st.code(doc.page_content, language="markdown")
                    else:
                        st.caption("참고 청크 정보가 result에 포함되지 않았습니다.")
                except Exception as e:
                    st.error(f"질문 처리 중 오류: {e}")

# =============================
# 2) 청크 미리보기 탭
# =============================
with tab_preview:
    st.subheader("🔎 인덱스 안에 들어있는 청크 미리보기")

    mode = st.radio(
        "보기 모드 선택",
        ["검색으로 보기", "그냥 앞쪽 N개 보기"],
        horizontal=True,
    )

    if mode == "검색으로 보기":
        query = st.text_input("검색 쿼리", value="test")
        k = st.slider("가져올 청크 개수 (k)", 1, 20, 5)

        if st.button("🔍 검색 실행"):
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

    else:  # 그냥 앞쪽 N개 보기
        n = st.slider("앞에서부터 볼 청크 개수", 1, 30, 5)

        if st.button("📄 청크 목록 보기"):
            try:
                # FAISS 내부 docstore에서 직접 꺼내기
                store = db.docstore._dict  # 기본 FAISS 구조 기준
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