"""
RunPod Serverless Handler for RAG PDF System
HyperCLOVA X Model
"""
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import runpod

# 전역 변수로 모델 로드 (컨테이너 시작 시 한 번만 로드)
MODEL_NAME = os.getenv("MODEL_NAME", "naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-1.5B")
print(f"Loading model: {MODEL_NAME}")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    device_map="auto",
    torch_dtype=torch.float16
)

print(f"Model loaded successfully on device: {model.device}")

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
    Generate answer using HyperCLOVA model
    """
    # 프롬프트 구성
    full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

    # Tokenize
    inputs = tokenizer(full_prompt, return_tensors="pt").to(model.device)

    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    # Decode
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Remove input prompt from output
    if full_prompt in generated_text:
        answer = generated_text.replace(full_prompt, "").strip()
    else:
        answer = generated_text.strip()

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
        # Get input
        job_input = event.get("input", {})
        prompt = job_input.get("prompt", "")

        if not prompt:
            return {"error": "No prompt provided"}

        # Get generation parameters
        max_new_tokens = job_input.get("max_new_tokens", 1024)
        temperature = job_input.get("temperature", 0.2)
        top_p = job_input.get("top_p", 0.9)
        top_k = job_input.get("top_k", 50)
        repetition_penalty = job_input.get("repetition_penalty", 1.2)

        # Generate answer
        answer = generate_answer(
            prompt=prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty
        )

        # Return result
        return {
            "text": answer,
            "generated_text": answer
        }

    except Exception as e:
        return {"error": str(e)}


# RunPod Serverless 시작
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
