import os
import traceback
from dotenv import load_dotenv
from openai import OpenAI
from prompts import SYSTEM_PROMPT
from logger import get_logger
from typing import Generator

load_dotenv()

log = get_logger(__name__)


def analyze_program_stream(
    program_text: str,
    program_name: str = "Учебная программа",
    scenario: str = "А — Проектируемая программа",
) -> Generator[str, None, None]:
    base_url = os.getenv("LLM_BASE_URL", "http://ai-1.msk.21-school.ru:11436/v1")
    model    = os.getenv("LLM_MODEL", "qwen3.5:9b")

    client = OpenAI(api_key="ollama", base_url=base_url, timeout=300)

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

    log.info("gap-analysis started | program=%s scenario=%s model=%s url=%s",
             program_name, scenario, model, base_url)

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=4000,
            stream=False,
            think=False
        )

        total_chars = 0
        inside_think = False
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if not delta:
                continue
            # фильтруем <think>...</think> блоки thinking-моделей
            if "<think>" in delta:
                inside_think = True
            if inside_think:
                if "</think>" in delta:
                    inside_think = False
                continue
            total_chars += len(delta)
            yield delta

        log.info("gap-analysis finished | program=%s chars=%d", program_name, total_chars)

    except Exception:
        log.error("gap-analysis failed | program=%s\n%s", program_name, traceback.format_exc())
        raise
