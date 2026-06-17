import os
import traceback
import httpx
from dotenv import load_dotenv
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
    base_url = os.getenv("LLM_BASE_URL", "http://10.77.88.5:11436")
    model    = os.getenv("LLM_MODEL", "qwen3.5:9b")

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

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 4000,
        },
    }

    try:
        with httpx.Client(timeout=300) as client:
            response = client.post(f"{base_url}/api/chat", json=payload)
            response.raise_for_status()

        data    = response.json()
        content = data.get("message", {}).get("content", "")

        log.info("gap-analysis finished | program=%s chars=%d", program_name, len(content))
        yield content

    except Exception:
        log.error("gap-analysis failed | program=%s\n%s", program_name, traceback.format_exc())
        raise
