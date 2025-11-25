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
        당신은 RAG 기반 AI Assistant입니다.
        반드시 제공된 컨텍스트 내용에 기반하여 답변해야 합니다.

        - 컨텍스트에 없는 정보라면 추측하거나 생성하지 말고,
          "해당 정보는 제공된 문서에 없습니다."라고 답하세요.
        - 모든 답변은 한국어로 작성하십시오.
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
