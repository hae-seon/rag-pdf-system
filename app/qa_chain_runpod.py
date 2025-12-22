# app/qa_chain_runpod.py
from __future__ import annotations
import os
import requests
import logging
from typing import List, Any

logger = logging.getLogger(__name__)

class QAChainRunPod:
    """RunPod Serverless API를 사용하는 QA Chain"""

    def __init__(self, api_key: str | None = None, endpoint_id: str | None = None, temperature: float = 0.2):
        self.api_key = api_key or os.getenv("RUNPOD_API_KEY")
        self.endpoint_id = endpoint_id or os.getenv("RUNPOD_ENDPOINT_ID")
        self.temperature = temperature

        if not self.api_key:
            raise ValueError("RunPod API Key가 필요합니다. RUNPOD_API_KEY 환경변수를 설정하거나 api_key 파라미터를 전달하세요.")

        if not self.endpoint_id:
            raise ValueError("RunPod Endpoint ID가 필요합니다. RUNPOD_ENDPOINT_ID 환경변수를 설정하거나 endpoint_id 파라미터를 전달하세요.")

        # RunPod Serverless API URL
        self.api_url = f"https://api.runpod.ai/v2/{self.endpoint_id}/runsync"

        logger.info(f"RunPod API 연결 완료 (Endpoint: {self.endpoint_id[:8]}...)")

        # 시스템 프롬프트
        self.system_prompt = """당신은 대한약전 전문 AI 어시스턴트입니다.
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

        # 프롬프트 구성
        prompt = f"""{self.system_prompt}

[Context]
{ctx}

[Question]
{question}

위 Context에 포함된 정보만을 사용하여 한국어로 답변하세요."""

        # RunPod API 요청 페이로드
        payload = {
            "input": {
                "prompt": prompt,
                "max_new_tokens": 1024,
                "temperature": self.temperature,
                "top_p": 0.9,
                "top_k": 50,
                "repetition_penalty": 1.2,
            }
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            logger.info("RunPod API 요청 중...")
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=300  # 5분 타임아웃
            )
            response.raise_for_status()

            result = response.json()

            # RunPod 응답 처리
            if result.get("status") == "COMPLETED":
                output = result.get("output", {})
                answer_text = output.get("text", "") or output.get("generated_text", "")
                logger.info("RunPod API 응답 받음")
                return answer_text.strip() or "답변을 생성할 수 없습니다."
            else:
                error_msg = result.get("error", "알 수 없는 오류")
                logger.error(f"RunPod API 오류: {error_msg}")
                return f"RunPod API 오류: {error_msg}"

        except requests.exceptions.Timeout:
            return "RunPod API 타임아웃 (5분 초과)"
        except requests.exceptions.RequestException as e:
            return f"RunPod API 요청 실패: {str(e)}"
        except Exception as e:
            return f"예상치 못한 오류: {str(e)}"
