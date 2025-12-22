"""
RunPod Serverless Handler for RAG PDF System
HyperCLOVA X Model - GPU Optimized
"""
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import runpod

# GPU 설정 확인
print("=" * 50)
print("GPU Configuration Check")
print("=" * 50)
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU count: {torch.cuda.device_count()}")
    print(f"Current GPU: {torch.cuda.current_device()}")
    print(f"GPU name: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
else:
    print("WARNING: CUDA not available! Running on CPU.")
print("=" * 50)

# CUDA 메모리 최적화 설정
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    # 메모리 할당 최적화
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"

# 전역 변수로 모델 로드 (컨테이너 시작 시 한 번만 로드)
MODEL_NAME = os.getenv("MODEL_NAME", "naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-1.5B")
HF_TOKEN = os.getenv("HF_TOKEN")  # Hugging Face token for gated models
print(f"\nLoading model: {MODEL_NAME}")
if HF_TOKEN:
    print("Using Hugging Face token for authentication")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    token=HF_TOKEN,  # Add token for gated repository access
    use_fast=False  # Use slow tokenizer for compatibility
)
print("Tokenizer loaded successfully")

# GPU가 사용 가능하면 GPU로, 아니면 CPU로 로드
device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    device_map="auto",  # 자동으로 최적의 디바이스에 배치
    torch_dtype=dtype,
    low_cpu_mem_usage=True  # 메모리 효율적 로딩
)

print(f"Model loaded successfully!")
print(f"Device: {device}")
print(f"Model dtype: {dtype}")
if hasattr(model, 'hf_device_map'):
    print(f"Device map: {model.hf_device_map}")

# GPU 메모리 사용량 확인
if torch.cuda.is_available():
    print(f"GPU memory allocated: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
    print(f"GPU memory reserved: {torch.cuda.memory_reserved(0) / 1024**3:.2f} GB")
print("=" * 50)

# 시스템 프롬프트
SYSTEM_PROMPT = """당신은 대한약전 전문 AI 어시스턴트입니다.
제공된 컨텍스트만을 사용하여 정확하게 답변하세요.
컨텍스트에 없는 내용은 추측하지 마세요.

답변 형식:
1. 기본 정의 (한글명, 영문명, 화학식, 기원)
2. 주요 특징 (성상, 용해성, 물리화학 지표)
3. 확인시험
4. 품질·순도 시험
5. 정량법
6. 저장법
7. 요약

규칙:
- 컨텍스트의 정보만 사용
- 수치와 단위를 정확히 기재
- 정보가 없으면 "제공된 문서에 해당 정보가 없습니다" 명시"""


def generate_answer(prompt: str, max_new_tokens: int = 1024, temperature: float = 0.2, top_p: float = 0.9, top_k: int = 50, repetition_penalty: float = 1.2) -> str:
    """
    Generate answer using HyperCLOVA model (GPU optimized)
    """
    # 프롬프트 구성
    full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

    # Tokenize - GPU로 직접 이동
    inputs = tokenizer(full_prompt, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}
    else:
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

    # Generate with GPU optimization
    with torch.no_grad():
        with torch.cuda.amp.autocast(enabled=torch.cuda.is_available()):
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repetition_penalty=repetition_penalty,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                use_cache=True  # KV cache 사용으로 속도 향상
            )

    # Decode
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Remove input prompt from output
    if full_prompt in generated_text:
        answer = generated_text.replace(full_prompt, "").strip()
    else:
        answer = generated_text.strip()

    # GPU 메모리 정리 (선택적)
    if torch.cuda.is_available():
        del inputs, outputs
        torch.cuda.empty_cache()

    return answer


def handler(event):
    """
    RunPod Serverless Handler

    Input format:
    {
        "input": {
            "prompt": "질문 내용",
            "max_new_tokens": 1024,
            "temperature": 0.2,
            "top_p": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.2
        }
    }
    """
    try:
        print(f"\n{'='*50}")
        print("Processing new request...")

        # Get input
        job_input = event.get("input", {})
        prompt = job_input.get("prompt", "")

        if not prompt:
            print("ERROR: No prompt provided")
            return {"error": "No prompt provided"}

        print(f"Prompt length: {len(prompt)} characters")

        # Get generation parameters
        max_new_tokens = job_input.get("max_new_tokens", 1024)
        temperature = job_input.get("temperature", 0.2)
        top_p = job_input.get("top_p", 0.9)
        top_k = job_input.get("top_k", 50)
        repetition_penalty = job_input.get("repetition_penalty", 1.2)

        print(f"Generation params: max_tokens={max_new_tokens}, temp={temperature}, top_p={top_p}, top_k={top_k}, rep_penalty={repetition_penalty}")

        # GPU 메모리 상태 출력 (디버깅용)
        if torch.cuda.is_available():
            print(f"GPU memory before generation: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")

        # Generate answer
        print("Generating answer...")
        answer = generate_answer(
            prompt=prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty
        )

        print(f"Answer generated: {len(answer)} characters")

        if torch.cuda.is_available():
            print(f"GPU memory after generation: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")

        print(f"{'='*50}\n")

        # Return result
        return {
            "text": answer,
            "generated_text": answer
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


# RunPod Serverless 시작
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
