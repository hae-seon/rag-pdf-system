# app/qa_chain.py
from __future__ import annotations
import os
from typing import List, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage  # ← langchain_core 사용!

class QAChain:
    def __init__(self, model_name: str | None = None, temperature: float = 0.2):
        self.model_name = model_name or os.getenv("LLM_MODEL", "gpt-4o-mini")
        # OPENAI_API_KEY는 환경변수로 설정되어 있어야 합니다.
        self.llm = ChatOpenAI(model=self.model_name, temperature=temperature)

        self.system_prompt = (
            "You are a helpful assistant that answers strictly based on the provided context. "
            "If the answer is not in the context, say you don't know. Answer in Korean."
        )

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
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Context:\n{ctx}\n\nQuestion:\n{question}"),
        ]
        resp = self.llm.invoke(messages)
        return (resp.content or "").strip() or "맥락에서 확실한 답을 찾지 못했습니다."
