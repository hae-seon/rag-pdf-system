FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04
WORKDIR /workspace

RUN apt-get update && apt-get install -y git wget && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /workspace/requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir runpod && \
    pip install --no-cache-dir -U "transformers>=4.41.0" "huggingface_hub>=0.23.0" "tokenizers>=0.19.1" \
        sentencepiece protobuf safetensors accelerate

COPY handler.py /workspace/handler.py

ENV PYTHONUNBUFFERED=1
ENV MODEL_NAME=naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-1.5B
# 캐시 위치 고정 (서버리스에서 디버깅 편해짐)
ENV HF_HOME=/workspace/.cache/huggingface
ENV TRANSFORMERS_CACHE=/workspace/.cache/huggingface

CMD ["python", "-u", "handler.py"]
