FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04
WORKDIR /workspace

# 시스템 패키지
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# RunPod 전용 requirements 복사
COPY requirements-runpod.txt /workspace/requirements.txt

# 의존성 설치 (torch는 베이스 이미지에 이미 포함)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir runpod

# 핸들러 복사
COPY handler.py /workspace/handler.py

# 환경변수 설정
ENV PYTHONUNBUFFERED=1
ENV MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
ENV HF_HOME=/workspace/.cache/huggingface
ENV TRANSFORMERS_CACHE=/workspace/.cache/huggingface

# 캐시 디렉토리 생성
RUN mkdir -p /workspace/.cache/huggingface

# 실행
CMD ["python", "-u", "handler.py"]