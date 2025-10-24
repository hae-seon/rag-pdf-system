# RAG PDF 질의응답 시스템 (Google Gemini 버전)

PDF 문서를 학습하여 질문에 답변하는 RAG(Retrieval-Augmented Generation) 시스템입니다.
**Google Gemini API**를 사용하여 무료로 사용 가능합니다!

## 🎉 Gemini의 장점

- ✅ **무료 할당량**: 매달 충분한 무료 크레딧 제공
- ✅ **강력한 성능**: GPT에 필적하는 성능
- ✅ **한국어 지원**: 한국어 이해 및 생성 능력 우수
- ✅ **빠른 응답**: 낮은 레이턴시

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. Gemini API 키 받기

1. https://makersuite.google.com/app/apikey 방문
2. "Create API Key" 클릭
3. API 키 복사

### 3. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사:
```bash
copy .env.example .env
```

`.env` 파일에 Gemini API 키 입력:
```
GOOGLE_API_KEY=your-gemini-api-key-here
```
### 4. 실행 방법

#### 🖥️ Streamlit UI 실행 (추천)
```bash
cd app
streamlit run streamlit_app.py
```

브라우저에서 자동으로 열립니다 (기본: http://localhost:8501)

#### 🐍 Python 스크립트로 실행
```python
from app.main import RAGSystem

rag = RAGSystem()
rag.ingest_pdf("./data/pdfs/your_document.pdf")
result = rag.query("질문을 입력하세요")
print(result['answer'])
```

## 📁 프로젝트 구조

```
rag-pdf-system/
├── app/
│   ├── main.py              # 메인 애플리케이션
│   ├── pdf_processor.py     # PDF 처리 모듈
│   ├── vector_store.py      # Gemini 임베딩 + 벡터 저장소
│   ├── qa_chain.py          # Gemini Pro 질의응답
│   └── streamlit_app.py     # Streamlit UI
├── data/
│   ├── pdfs/                # PDF 파일 저장
│   └── vectors/             # 벡터 인덱스 저장
├── requirements.txt         # 패키지 목록
├── .env.example            # 환경 변수 예시
└── README.md               # 이 파일
```

## 🛠️ 주요 기능

- ✅ PDF 문서 자동 처리 및 청킹
- ✅ Gemini 임베딩으로 벡터화
- ✅ FAISS 기반 의미 검색
- ✅ Gemini Pro로 답변 생성
- ✅ 답변 출처 추적 기능
- ✅ 사용하기 쉬운 웹 UI

## ⚙️ 설정 옵션

`.env` 파일에서 다음 설정을 변경할 수 있습니다:

| 설정 | 설명 | 기본값 |
|------|------|--------|
| GOOGLE_API_KEY | Gemini API 키 | (필수) |
| CHUNK_SIZE | 텍스트 청크 크기 | 1000 |
| CHUNK_OVERLAP | 청크 오버랩 | 100 |
| TOP_K | 검색할 문서 수 | 5 |
| LLM_MODEL | Gemini 모델 | gemini-pro |
| LLM_TEMPERATURE | 답변 창의성 (0-1) | 0.2 |
| EMBEDDING_MODEL | 임베딩 모델 | models/embedding-001 |

## 💡 사용 예시

### 1. 새 PDF 처리
```python
rag = RAGSystem()
rag.ingest_pdf("./data/pdfs/manual.pdf")
```

### 2. 기존 인덱스 로드
```python
rag = RAGSystem()
rag.load_existing_index()
```

### 3. 질문하기
```python
result = rag.query("이 문서의 주요 내용은?")
print(result['answer'])
print(result['sources'])  # 출처 확인
```

## 🔧 문제 해결

### Gemini API 키 오류
- API 키가 `.env` 파일에 올바르게 설정되었는지 확인
- https://makersuite.google.com/app/apikey 에서 키 상태 확인
- API 사용량 제한을 초과하지 않았는지 확인

### PDF 처리 오류
- PDF 파일이 텍스트 기반인지 확인 (이미지 PDF는 OCR 필요)
- PDF 파일 경로가 올바른지 확인
- 파일 크기가 너무 크지 않은지 확인 (권장: 10MB 이하)

### 벡터 저장소 오류
- `data/vectors` 디렉토리가 존재하는지 확인
- 기존 인덱스 파일이 손상되지 않았는지 확인
- 충분한 디스크 공간이 있는지 확인

## 📚 기술 스택

- **LangChain**: RAG 파이프라인 구축
- **Google Gemini**: 임베딩 및 LLM (무료!)
- **FAISS**: 벡터 유사도 검색
- **Streamlit**: 웹 UI
- **PyPDF2**: PDF 처리

## 🆚 OpenAI vs Gemini

| 항목 | OpenAI | Gemini |
|------|--------|--------|
| 가격 | 유료 (종량제) | 무료 할당량 충분 |
| 성능 | 매우 우수 | 우수 |
| 한국어 | 우수 | 우수 |
| API 접근 | 신용카드 필요 | 이메일만 필요 |

## 🎯 Gemini 무료 할당량

- **무료 RPM**: 분당 15회 요청
- **무료 TPM**: 분당 32,000 토큰
- **일일 제한**: 1,500 요청

대부분의 개인 프로젝트에 충분합니다!

## 🔜 향후 계획

- [ ] 다중 PDF 동시 처리
- [ ] 대화 히스토리 저장
- [ ] Gemini Vision으로 이미지 PDF 지원
- [ ] 다국어 지원 강화
- [ ] REST API 제공
- [ ] Docker 컨테이너화

## 📝 라이선스

MIT License

## 🤝 기여

이슈와 PR을 환영합니다!

## 📧 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.
