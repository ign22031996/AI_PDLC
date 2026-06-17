import os
from dotenv import load_dotenv
from langfuse.openai import OpenAI
from prompts import SYSTEM_PROMPT
from typing import Generator

load_dotenv()


def analyze_program_stream(
    program_text: str,
    program_name: str = "Учебная программа",
    scenario: str = "А — Проектируемая программа",
) -> Generator[str, None, None]:
    api_key  = os.getenv("OPENAI_API_KEY", "ollama")
    base_url = os.getenv("OPENAI_BASE_URL", "http://10.77.88.5:11435/v1")
    model    = os.getenv("OPENAI_MODEL", "qwen3.5:4b")

    client = OpenAI(api_key=api_key, base_url=base_url, timeout=300)

    user_prompt = f"""Проанализируй следующие материалы образовательной программы по AI PDLC Competency Matrix v2.

Название программы: {program_name}
Сценарий анализа: {scenario}

Используй логику и формат таблицы строго для своего сценария:
- Сценарий А (Проектируемая программа) → таблица с колонкой «Цель», рекомендации всегда при разрыве.
- Сценарий Б (Текущая программа) → таблица без «Потенциал», только «Факт» и рекомендации что нужно усилить.

=== СОДЕРЖАНИЕ ПРОГРАММЫ ===
{program_text}

Сформируй полный отчёт строго по указанному формату Markdown.
Оценивай только то, что явно присутствует в материалах.
Не придумывай компетенции которых нет — ставь N0 если компетенция отсутствует.
"""

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=4000,
        stream=True,
        name=f"gap-analysis: {program_name}",
        extra_body={"think": False},
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
