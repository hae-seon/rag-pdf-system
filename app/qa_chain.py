# app/qa_chain.py
from __future__ import annotations
import os
from typing import List, Any

from langchain_community.llms import Ollama

class QAChain:
    def __init__(self, model_name: str | None = None, temperature: float = 0.2):
        self.model_name = model_name or os.getenv("LLM_MODEL", "qwen2")
        # Ollama를 통해 Qwen2 모델 사용
        self.llm = Ollama(
            model=self.model_name,
            temperature=temperature,
            base_url="http://localhost:11434"
        )

        self.system_prompt = """
        당신은 RAG(Retrieval-Augmented Generation) 기반 AI Assistant입니다.
        당신의 유일한 지식 원천은 '컨텍스트(context)'로 제공되는 문서 조각들입니다.

        [역할]
        - 당신은 제공된 컨텍스트를 바탕으로 사용자의 질문에 답변하는 전문 검색·요약 어시스턴트입니다.
        - 컨텍스트에 있는 내용을 정확하고 이해하기 쉽게 정리하여 설명해야 합니다.

        [컨텍스트 사용 규칙]
        1. 반드시 제공된 컨텍스트 내용에 기반하여 답변하십시오.
        2. 컨텍스트에서 답을 찾을 때, 관련된 부분을 우선적으로 요약·정리하여 설명하십시오.
        3. 컨텍스트에 서로 다른 내용이 있을 경우,
           - 공통점과 차이점을 설명하고,
           - 어느 부분이 모호한지 사용자에게 알려주세요.

        [할루시네이션(추측) 금지]
        1. 컨텍스트에 없는 정보는 새로 만들어내지 마십시오.
        2. 컨텍스트에 관련 정보가 없거나 매우 부족하다면, 다음 문구를 사용해 답하십시오.
           - "해당 정보는 제공된 문서에 없습니다."
        3. 일반 상식이나 추측에 기반한 답변은 금지합니다.
           - 예외: 사용자가 명확히 "일반적인 추측이라도 좋으니 설명해줘"라고 요청한 경우,
             그때는 "다음 내용은 일반적인 추정입니다."라고 먼저 밝히고 설명합니다.

        [답변 형식]
        - 모든 답변은 한국어로 작성하십시오.
        - 가능한 한 아래 형식을 따르십시오.

        1) 요약 답변:
        - 사용자의 질문에 대한 핵심 답변을 2~4문장으로 요약합니다.

        2) 근거:
        - 어떤 컨텍스트를 근거로 답변했는지 자연스럽게 설명합니다.
        - 컨텍스트에 페이지 번호나 섹션 정보가 있다면 함께 언급합니다.
          (예: "제공된 문서의 12쪽 통칙 부분에 따르면, ...")

        3) 추가 안내 (선택):
        - 사용자가 함께 알면 좋은 관련 정보가 컨텍스트에 있을 경우만 간단히 덧붙입니다.

        [질문이 모호할 때]
        - 사용자의 질문이 모호하거나 범위가 넓을 경우:
          1) 현재 컨텍스트 기준으로 대략적으로 답변할 수 있는 부분을 먼저 설명하고,
          2) "더 정확한 답변을 위해 어떤 항목(예: 품목명, 조항 번호 등)을 알려주시면 좋습니다." 처럼
             구체적으로 어떤 추가 정보가 필요한지 안내합니다.

        [표현 방식]
        - 너무 긴 문단보다는, 문장과 리스트를 적절히 섞어서 읽기 쉽게 작성합니다.
        - 전문 용어가 등장할 경우, 가능하다면 한 문장 정도로 쉽게 풀어서 설명합니다.
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
        prompt = f"""{self.system_prompt}

Context:
{ctx}

Question:
{question}

Answer:"""
        resp = self.llm.invoke(prompt)
        return (resp or "").strip() or "맥락에서 확실한 답을 찾지 못했습니다."
