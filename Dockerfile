# RunPod Serverless Dockerfile for HyperCLOVA X Model
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt /workspace/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir runpod

# Copy handler
COPY handler.py /workspace/handler.py

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MODEL_NAME=naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-1.5B

# Run handler
CMD ["python", "-u", "handler.py"]
