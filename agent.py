import os
import traceback
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from langfuse import Langfuse
from prompts import SYSTEM_PROMPT
from logger import get_logger
from typing import Generator

load_dotenv()

log = get_logger(__name__)
langfuse = Langfuse()


def analyze_program_stream(
    program_text: str,
    program_name: str = "Учебная программа",
    scenario: str = "А — Проектируемая программа",
) -> Generator[str, None, None]:
    credentials = os.getenv("GIGACHAT_CREDENTIALS", "")
    model       = os.getenv("GIGACHAT_MODEL", "GigaChat")
    verify_ssl  = os.getenv("GIGACHAT_VERIFY_SSL", "false").lower() == "true"
    scope       = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

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

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_prompt},
    ]

    log.info("gap-analysis started | program=%s scenario=%s model=%s", program_name, scenario, model)

    trace      = langfuse.trace(name=f"gap-analysis:{program_name}")
    generation = trace.generation(
        name="gigachat-stream",
        model=model,
        input=messages,
    )

    full_chunks: list[str] = []

    try:
        chat = Chat(
            messages=[
                Messages(role=MessagesRole.SYSTEM, content=SYSTEM_PROMPT),
                Messages(role=MessagesRole.USER,   content=user_prompt),
            ],
            temperature=0.2,
            max_tokens=4000,
        )

        with GigaChat(
            credentials=credentials,
            scope=scope,
            verify_ssl_certs=verify_ssl,
            timeout=300,
        ) as giga:
            for chunk in giga.stream(chat):
                if chunk.choices:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_chunks.append(delta)
                        yield delta

        output = "".join(full_chunks)
        generation.end(output=output)
        langfuse.flush()
        log.info("gap-analysis finished | program=%s chars=%d", program_name, len(output))

    except Exception:
        log.error("gap-analysis failed | program=%s\n%s", program_name, traceback.format_exc())
        generation.end(level="ERROR", status_message=traceback.format_exc())
        langfuse.flush()
        raise
