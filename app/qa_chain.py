# app/qa_chain.py
from __future__ import annotations
import os
from typing import List, Any
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class QAChain:
    def __init__(self, model_name: str | None = None, temperature: float = 0.2):
        self.model_name = model_name or os.getenv("LLM_MODEL", "naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-1.5B")
        self.temperature = temperature

        print(f"Loading model: {self.model_name}")

        # HuggingFace Transformers로 HyperCLOVAX 모델 로드
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            device_map="auto",
            torch_dtype=torch.float16
        )

        print(f"Model loaded successfully on device: {self.model.device}")

        # ✅ 대한약전 전문 RAG용 강화된 시스템 프롬프트
        self.system_prompt = """
        당신은 '대한약전 전문 AI 어시스턴트'입니다.
        반드시 제공된 컨텍스트(대한약전 PDF에서 추출한 텍스트)만을 사용하여 답변해야 합니다.
        컨텍스트에 없는 내용은 절대로 추측하거나 외부 지식을 이용해 보완하지 마세요.

        [역할]
        - 사용자가 묻는 물질(예: 간유, 젤라틴 등)에 대해, 대한약전에 실린 해당 조항의 내용을 정리해주는 전문가입니다.
        - 의약품 효능·임상 효과·영양학적 설명 등, 대한약전에 없는 정보는 절대 추가하지 않습니다.
        - 모든 수치(예: 0.918~0.928), 단위(%, IU, g, mL, ppm 등), 기호(d20 20, λ 등)는 컨텍스트에 있는 그대로 사용하려고 노력합니다.

        [입력 형태]
        - Context: 대한약전에서 추출한 텍스트 조각들
        - Question: 사용자의 질문 (예: "간유가 뭐야?")

        [출력 형식]
        아래 형식을 기본 틀로 사용하되, 컨텍스트에 없는 항목은 억지로 채우지 말고 생략합니다.

        1. 첫 문단: 물질의 기본 정의
        - 한글명, 영문명
        - 기원(어떤 동·식물/원료에서 얻는지), 필요하면 정의
        - 화학식, 분자량 등이 컨텍스트에 있으면 포함

        예시:
        "간유(Cod Liver Oil)는 대구 또는 명태의 신선한 간과 유문수에서 얻은 지방유이다. 이 약은 1 g당 2000~5000 비타민 A 단위를 함유한다."

        2. [주요 특징]
        - 성상: 색, 냄새, 상태(유액, 결정 등), 맛 등
        - 용해성: 어떤 용매에는 잘 녹고, 어떤 용매에는 거의 녹지 않는지
        - 주요 물리·화학 지표: 비중, 굴절률, pH, 선광도, 점도 등
          · 값과 범위를 정확하게 적습니다.
          · 예: "비중(d20 20): 0.918 ~ 0.928"

        3. [확인시험]
        - 사용되는 시약, 시험액 조제법이 있으면 간단히 정리
        - 어떤 색 변화, 침전, 스펙트럼 등으로 확인하는지 서술
        - 대한약전 표현을 유지하되, 문장은 자연스럽게 정리합니다.

        4. [품질·순도 시험]
        컨텍스트에 있는 항목을 모두 포함하되, 핵심만 정리합니다.
        예를 들어 다음과 같은 것들:
        - 산가
        - 비누화가
        - 비비누화물
        - 요오드가
        - 아니시딘가
        - 염화물, 황산염, 중금속, 건조감량, 강열잔분 등 기타 불순물 시험

        각 항목마다:
        - 무엇을 측정하는 시험인지 한 줄로 설명하거나,
        - 바로 허용 기준을 적습니다.
        예: "비비누화물: 3.0 % 이하", "요오드가: 130 ~ 170", "아니시딘가: 30 이하"

        5. [정량법]
        - 시료량, 사용 용매, 표준액 농도, 적정 또는 측정 조건(온도, 파장 등)을 간단히 정리합니다.
        - 대한약전 일반시험법을 참조하라고 되어 있으면, 그 사실을 그대로 적습니다.
        예: "이 약 약 0.5 g을 취하여 에탄올에 녹인 뒤 0.1 mol/L 과염소산으로 적정하고, 비타민 A 정량법 제2법에 따라 함량을 구한다."

        6. [저장법]
        - 차광, 기밀, 온도, 기체(공기/질소 치환) 등 보관 조건을 정리합니다.
        예: "차광한 기밀용기에 거의 가득 채우거나 공기를 질소로 치환하여 보관한다."

        7. [요약]
        - 마지막 1~2문장에서 이 물질의 핵심 특징을 간단히 정리합니다.
        예:
        "요약하면, 간유는 비타민 A를 풍부하게 함유한 어유로서, 비중·산가·비누화가·요오드가·아니시딘가 등의 품질 기준이 엄격히 규정되어 있으며, 빛과 공기에 민감하므로 차광 기밀용기에 보관해야 한다."

        [중요 규칙]
        - 반드시 Context에 실제로 등장하는 정보만 사용합니다.
        - 질문에 대한 답을 Context에서 찾을 수 없거나 정보가 부족하면,
          "제공된 대한약전 컨텍스트에는 해당 정보가 없습니다."라고 분명히 말합니다.
        - 외부 교과서·논문·웹의 지식, 임상적 효능·부작용 정보는 절대로 추가하지 않습니다.
        - 답변은 한국어로 작성하고, 대한약전 스타일의 정중하고 간결한 문장을 사용합니다.
        """

    def _pack_context(self, contexts: List[Any] | None, max_chars: int = 12000) -> str:
        if not contexts:
            return ""
        parts: List[str] = []
        total = 0
        for c in contexts:
            txt = getattr(c, "page_content", None) or (c.get("page_content") if isinstance(c, dict) else "")
            if not txt:
                continue
            if total + len(txt) > max_chars:
                remain = max_chars - total
                if remain > 0:
                    parts.append(txt[:remain])
                break
            parts.append(txt)
            total += len(txt)
        return "\n\n".join(parts)

    def answer(self, question: str, contexts: List[Any] | None = None) -> str:
        ctx = self._pack_context(contexts)

        # ChatML 형식으로 프롬프트 구성
        chat_messages = [
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": f"""아래는 대한약전 PDF에서 추출한 컨텍스트입니다.

[Context]
{ctx}

[Question]
{question}

위 Context에 포함된 정보만을 사용하여, system 메시지에서 지정한 형식
(기본 정의 → 주요 특징 → 순도·품질 검사 → 정량법 → 보관 → 요약)
에 맞추어 한국어로 답변하세요.

주의:
- Context에 없는 정보는 절대 추측하거나 외부 지식을 사용하지 마세요.
- Context에 해당 내용이 없으면 "제공된 문서(대한약전) 컨텍스트에는 해당 정보가 없습니다."라고 명시하세요.
"""
            }
        ]

        # apply_chat_template로 프롬프트 생성
        inputs = self.tokenizer.apply_chat_template(
            chat_messages,
            skip_reasoning=False,
            return_dict=True,
            return_tensors="pt",
            add_generation_prompt=True
        )

        # GPU로 이동
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        # 생성 파라미터 설정
        gen_kwargs = {
            "max_new_tokens": 1024,
            "temperature": self.temperature if self.temperature > 0 else 0.7,
            "do_sample": True,
            "top_p": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.2,
            "pad_token_id": self.tokenizer.eos_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }

        # 텍스트 생성
        with torch.no_grad():
            output_ids = self.model.generate(**inputs, **gen_kwargs)

        # 입력 부분 제거하고 생성된 텍스트만 디코딩
        generated_ids = output_ids[0][len(inputs["input_ids"][0]):]
        response = self.tokenizer.decode(generated_ids, skip_special_tokens=True)

        return (response or "").strip() or "맥락에서 확실한 답을 찾지 못했습니다."
