FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04
WORKDIR /workspace

# 시스템 패키지
RUN apt-get update && apt-get install -y \
    git wget \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 의존성 설치 (한 번에)
COPY requirements.txt /workspace/requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir runpod

# 핸들러 복사 (오타 수정!)
COPY handler.py /workspace/handler.py

# 환경변수
ENV PYTHONUNBUFFERED=1
ENV MODEL_NAME=naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-1.5B
ENV HF_HOME=/workspace/.cache/huggingface
ENV TRANSFORMERS_CACHE=/workspace/.cache/huggingface

# 캐시 디렉토리 생성
RUN mkdir -p /workspace/.cache/huggingface

CMD ["python", "-u", "handler.py"]