"""
RunPod Serverless Handler for RAG PDF System
HyperCLOVA X Model - GPU Optimized (SAFE TOKENIZER)
"""
import os
import torch
import runpod

from transformers import AutoModelForCausalLM, AutoTokenizer


# =========================
# GPU 설정 확인
# =========================
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
    print(
        f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB"
    )
else:
    print("WARNING: CUDA not available! Running on CPU.")
print("=" * 50)

if torch.cuda.is_available():
    torch.cuda.empty_cache()
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"


# =========================
# 모델/토큰
# =========================
MODEL_NAME = os.getenv("MODEL_NAME", "naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-1.5B")
HF_TOKEN = os.getenv("HF_TOKEN")

print(f"\nLoading model: {MODEL_NAME}")
if HF_TOKEN:
    print("Using Hugging Face token for authentication")


# =========================
# ✅ 토크나이저 로딩 (tiktoken fallback 금지)
# =========================
tokenizer = None

# 1) fast tokenizer 우선
try:
    print("Trying AutoTokenizer (fast)...")
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        token=HF_TOKEN,
        trust_remote_code=True,
        use_fast=True,
    )
    print("AutoTokenizer (fast) loaded successfully")
except Exception as e:
    print(f"AutoTokenizer (fast) failed: {e}")

# 2) fast 실패하면 slow로 재시도
if tokenizer is None:
    try:
        print("Trying AutoTokenizer (slow/use_fast=False)...")
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            token=HF_TOKEN,
            trust_remote_code=True,
            use_fast=False,
        )
        print("AutoTokenizer (slow) loaded successfully")
    except Exception as e:
        print(f"AutoTokenizer (slow) failed: {e}")

if tokenizer is None:
    raise RuntimeError(
        "❌ Failed to load a compatible tokenizer for this model.\n"
        "Do NOT fall back to tiktoken. Check MODEL_NAME / HF_TOKEN / model repo tokenizer files."
    )

# pad/eos 안전 세팅
if tokenizer.pad_token_id is None:
    # pad가 없으면 eos로 대체(대부분 생성 모델에서 안전한 편)
    if tokenizer.eos_token_id is not None:
        tokenizer.pad_token = tokenizer.eos_token
    else:
        # eos도 없으면 강제 추가 (매우 드문 케이스)
        tokenizer.add_special_tokens({"eos_token": "</s>", "pad_token": "<pad>"})

print("Tokenizer ready!")
print(f"pad_token_id={tokenizer.pad_token_id}, eos_token_id={tokenizer.eos_token_id}")
print("=" * 50)


# =========================
# 모델 로딩
# =========================
dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    token=HF_TOKEN,
    trust_remote_code=True,
    device_map="auto",
    torch_dtype=dtype,
    low_cpu_mem_usage=True,
)

# (필요시) special token 추가로 vocab이 바뀌었으면 resize
# tokenizer.add_special_tokens로 뭔가 추가했을 때만 resize 필요
if hasattr(model, "resize_token_embeddings") and len(tokenizer) != model.get_input_embeddings().weight.shape[0]:
    model.resize_token_embeddings(len(tokenizer))

print("Model loaded successfully!")
print(f"Model dtype: {dtype}")
if hasattr(model, "hf_device_map"):
    print(f"Device map: {model.hf_device_map}")

if torch.cuda.is_available():
    print(f"GPU memory allocated: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
    print(f"GPU memory reserved: {torch.cuda.memory_reserved(0) / 1024**3:.2f} GB")
print("=" * 50)


# =========================
# 시스템 프롬프트
# =========================
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


def generate_answer(
    prompt: str,
    max_new_tokens: int = 1024,
    temperature: float = 0.2,
    top_p: float = 0.9,
    top_k: int = 50,
    repetition_penalty: float = 1.2,
) -> str:
    full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

    inputs = tokenizer(full_prompt, return_tensors="pt")

    # ✅ device_map="auto" 환경에서 가장 안전: 모델 파라미터 device로 입력 이동
    target_device = next(model.parameters()).device
    inputs = {k: v.to(target_device) for k, v in inputs.items()}

    do_sample = temperature is not None and temperature > 0

    with torch.no_grad():
        autocast_enabled = torch.cuda.is_available() and target_device.type == "cuda"
        with torch.cuda.amp.autocast(enabled=autocast_enabled):
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

    # ✅ 전체를 디코딩하지 말고 "생성된 토큰만" 디코딩
    input_len = inputs["input_ids"].shape[-1]
    gen_tokens = outputs[0][input_len:]
    answer = tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()

    # 메모리 정리
    del inputs, outputs
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return answer


def handler(event):
    try:
        print(f"\n{'='*50}")
        print("Processing new request...")

        job_input = event.get("input", {})
        prompt = job_input.get("prompt", "")
        if not prompt:
            print("ERROR: No prompt provided")
            return {"error": "No prompt provided"}

        max_new_tokens = job_input.get("max_new_tokens", 1024)
        temperature = job_input.get("temperature", 0.2)
        top_p = job_input.get("top_p", 0.9)
        top_k = job_input.get("top_k", 50)
        repetition_penalty = job_input.get("repetition_penalty", 1.2)

        print(f"Prompt length: {len(prompt)} characters")
        print(
            f"Generation params: max_tokens={max_new_tokens}, temp={temperature}, top_p={top_p}, top_k={top_k}, rep_penalty={repetition_penalty}"
        )

        if torch.cuda.is_available():
            print(
                f"GPU memory before generation: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB"
            )

        answer = generate_answer(
            prompt=prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
        )

        print(f"Answer generated: {len(answer)} characters")
        if torch.cuda.is_available():
            print(
                f"GPU memory after generation: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB"
            )

        print(f"{'='*50}\n")

        return {"text": answer, "generated_text": answer}

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
