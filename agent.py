import os
import json
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
        "stream": True,
        "options": {
            "temperature": 0.2,
            "num_predict": 4000,
        },
    }

    try:
        content_chunks: list[str] = []

        with httpx.Client(timeout=300) as client:
            with client.stream("POST", f"{base_url}/api/chat", json=payload) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    delta = chunk.get("message", {}).get("content", "")
                    if delta:
                        content_chunks.append(delta)
                        yield delta
                    if chunk.get("done"):
                        log.info("ollama done | eval_count=%s done_reason=%s",
                                 chunk.get("eval_count"), chunk.get("done_reason"))
                        break

        total = sum(len(c) for c in content_chunks)
        log.info("gap-analysis finished | program=%s chars=%d", program_name, total)

    except Exception:
        log.error("gap-analysis failed | program=%s\n%s", program_name, traceback.format_exc())
        raise
