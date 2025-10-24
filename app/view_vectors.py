# view_vectors.py
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()  # ✅ .env 파일 자동 로드

# ✅ 경로는 main.py에서 지정한 vector_store_path 그대로
VECTOR_PATH = "../data/vectors/index"

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 인덱스 로드
db = FAISS.load_local(VECTOR_PATH, embeddings, allow_dangerous_deserialization=True)

# 벡터 개수
print(f"총 벡터 수: {len(db.index_to_docstore_id)}")

# 일부 청크 미리보기
docs = db.similarity_search("test", k=5)
for i, d in enumerate(docs, start=1):
    print(f"\n[{i}] 페이지/소스: {d.metadata}")
    print(f"내용:\n{d.page_content[:300]}...")
