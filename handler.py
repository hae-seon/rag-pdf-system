"""
RunPod Serverless Handler for RAG PDF System
HyperCLOVA X Model - GPU Optimized (FIXED VERSION)
"""
import os
import torch
import runpod
from transformers import AutoModelForCausalLM, AutoTokenizer

# ============================================================
# GPU 설정 확인
# ============================================================
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

# CUDA 메모리 최적화
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"

# ============================================================
# 모델 / 토큰 설정
# ============================================================
MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-1.5B"
)
HF_TOKEN = os.getenv("HF_TOKEN")

print(f"\nLoading model: {MODEL_NAME}")
if HF_TOKEN:
    print("Using Hugging Face token")

# ============================================================
# ✅ 토크나이저 (단일 방식, tiktoken 제거)
# ============================================================
try:
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        token=HF_TOKEN,
        use_fast=True
    )
except Exception:
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        token=HF_TOKEN,
        use_fast=False
    )

# pad_token 보정
if tokenizer.pad_token_id is None:
    tokenizer.pad_token = tokenizer.eos_token

print("Tokenizer loaded successfully")
print("=" * 50)

# ============================================================
# 모델 로딩
# ============================================================
device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    token=HF_TOKEN,
    device_map="auto",
    torch_dtype=dtype,
    low_cpu_mem_usage=True
)

print("Model loaded successfully")
print(f"Device: {device}")
print(f"Dtype: {dtype}")

if hasattr(model, "hf_device_map"):
    print(f"Device map: {model.hf_device_map}")

print("=" * 50)

# ============================================================
# 시스템 프롬프트
# ============================================================
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
- 정보가 없으면 "제공된 문서에 해당 정보가 없습니다" 명시
"""

# ============================================================
# 생성 함수
# ============================================================
def generate_answer(
    prompt: str,
    max_new_tokens: int = 1024,
    temperature: float = 0.2,
    top_p: float = 0.9,
    top_k: float = 50,
    repetition_penalty: float = 1.2,
) -> str:

    full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

    inputs = tokenizer(full_prompt, return_tensors="pt")
    target_device = next(model.parameters()).device
    inputs = {k: v.to(target_device) for k, v in inputs.items()}

    do_sample = temperature is not None and temperature > 0

    with torch.no_grad():
        with torch.cuda.amp.autocast(
            enabled=torch.cuda.is_available() and target_device.type == "cuda"
        ):
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
                temperature=temperature if do_sample else None,
                top_p=top_p if do_sample else None,
                top_k=top_k if do_sample else None,
                repetition_penalty=repetition_penalty,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=True,
            )

    # ✅ 생성된 토큰만 디코딩 (panic 방지 핵심)
    input_len = inputs["input_ids"].shape[-1]
    gen_tokens = outputs[0][input_len:]
    answer = tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()

    del inputs, outputs
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return answer

# ============================================================
# RunPod Handler
# ============================================================
def handler(event):
    try:
        print("=" * 50)
        print("Processing new request")

        job_input = event.get("input", {})
        prompt = job_input.get("prompt", "")

        if not prompt:
            return {"error": "No prompt provided"}

        answer = generate_answer(
            prompt=prompt,
            max_new_tokens=job_input.get("max_new_tokens", 1024),
            temperature=job_input.get("temperature", 0.2),
            top_p=job_input.get("top_p", 0.9),
            top_k=job_input.get("top_k", 50),
            repetition_penalty=job_input.get("repetition_penalty", 1.2),
        )

        return {
            "text": answer,
            "generated_text": answer
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# ============================================================
# RunPod Serverless Start
# ============================================================
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
