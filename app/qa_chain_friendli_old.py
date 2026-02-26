from __future__ import annotations
import os
import logging
from typing import List, Any
from openai import OpenAI

logger = logging.getLogger(__name__)


class QAChainFriendli:
    def __init__(self, model_name="LGAI-EXAONE/EXAONE-4.0.1-32B", temperature=0.2):
        self.client = OpenAI(
            api_key=os.getenv("FRIENDLI_TOKEN"),
            base_url="https://api.friendli.ai/serverless/v1",
        )
        self.model_name = model_name
        self.temperature = temperature
        logger.info(f"Friendli QA Chain 초기화 완료 (model: {self.model_name})")

        self.system_prompt = """
           반드시 제공된 컨텍스트(PDF에서 추출한 텍스트)만을 사용하여 답변해야 합니다.
컨텍스트에 없는 내용은 절대로 추측하거나 외부 지식을 이용해 보완하지 마세요.

[역할]
- 사용자가 요청한 CTD 항목을 컨텍스트에서 찾아 “그대로 추출/구조화/요약”합니다.
- 문서에 없는 정보는 추가하지 않습니다.
- 모든 수치, 단위, 기호는 컨텍스트에 있는 그대로 사용합니다.

[핵심 원칙]
- 요청은 “항목 단위”로 처리합니다.
- 어떤 항목은 찾고 어떤 항목은 못 찾을 수 있습니다.
  → 찾은 항목은 출력하고, 못 찾은 항목만 "제공된 문서 컨텍스트에는 해당 정보가 없습니다."로 표시합니다.
  → 전체를 한 번에 표기하지 마세요.
  -컨텍스트에서 섹션 번호(예: 3.2.S.1.1)를 우선 탐색하고, 해당 섹션 범위 내에서만 추출한다.

  [출력 형식 선택 규칙]
  - 특별히 출력 형식을 요구하지 않으면 모든 경우에 텍스트로 출력합니다.
  - 사용자가 명시적으로 표를 요청한 경우에만 표로 출력합니다.

[분자식 표기 규칙]
- 모든 출력에서 분자식 패턴(예: C17H16FN3O2S, · 포함 복합식 등)을 발견하면 반드시 아래첨자(Unicode)로 변환합니다.
  예: C17H16FN3O2S → C₁₇H₁₆FN₃O₂S
  예: C17H16FN3O2S·C4H4O4 → C₁₇H₁₆FN₃O₂S·C₄H₄O₄

[없음 처리]
- 특정 항목을 컨텍스트에서 찾지 못하면 그 항목의 “내용” 칸에 아래 문구만 기입: -
- (주의) 컨텍스트에 없는 항목을 추측해서 채우지 마세요.

[언어]
- 답변은 한국어로 작성합니다.
- 국제일반명칭(INN)은 반드시 영어로만 표기합니다.

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

        table_keywords = ["표로", "표로 정리", "표로 보여", "테이블"]
        table_mode = any(k in question for k in table_keywords)

        format_instruction = ""

        if table_mode:
            comparison_mode = any(k in question for k in ["A,B", "A, B", "A와 B", "비교"])

            if table_mode and comparison_mode:
                format_instruction = """
                 형식: 항목을 행, 비교대상을 열로 구성
                 |---|---|---|
                 """
            # else:
            #     format_instruction = """
            #      형식:
            #      | 항목 | 내용 |
            #      |---|---|
            #      """

        user_content = f"""아래는 PDF에서 추출한 컨텍스트입니다.

        [Context]
        {ctx}

        [Question]
        {question}

        {format_instruction}

        위 Context 정보만 사용하세요."""

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=self.temperature,
                max_tokens=4096,
            )
            answer_text = completion.choices[0].message.content
            return (answer_text or "").strip() or "답변을 생성할 수 없습니다."
        except Exception as e:
            logger.error(f"Friendli API 오류: {e}")
            return f"Friendli API 오류: {str(e)}"
