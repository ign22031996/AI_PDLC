import streamlit as st
from dotenv import load_dotenv
from parser import build_program_text
from agent import analyze_program_stream
import datetime
import base64
import os

load_dotenv()

def _logo_b64() -> str:
    path = os.path.join(os.path.dirname(__file__), "static", "logo.webp")
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

LOGO_B64 = _logo_b64()

st.set_page_config(
    page_title="AI PDLC Gap-Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background: #FFFFFF !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stSidebar"] { display: none; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }

    .block-container {
        padding-top: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100%;
    }

    /* ── Навбар — белый, как на 21-school.ru ── */
    .nav {
        background: #FFFFFF;
        border-bottom: 1px solid #E8E8E8;
        padding: 0 48px;
        height: 76px;
        display: flex;
        align-items: center;
        gap: 40px;
    }
    .nav-logo-crop {
        flex-shrink: 0;
        display: flex;
        align-items: center;
    }
    .nav-logo-crop img {
        height: 60px;
        width: auto;
    }
    .nav-link { color: #555; font-size: 15px; font-weight: 500; }
    .nav-link-active { color: #111 !important; font-weight: 600; }
    .nav-cta {
        margin-left: auto;
        background: #2DCA72;
        color: #000;
        font-size: 14px;
        font-weight: 700;
        padding: 10px 24px;
        border-radius: 8px;
    }

    /* ── Центрирующая обёртка ── */
    .center-wrap {
        max-width: 1100px;
        margin: 0 auto;
        padding: 0 48px;
    }

    /* ── Hero ── */
    .hero {
        padding: 64px 0 48px;
        border-bottom: 1px solid #EBEBEB;
    }
    .hero-eyebrow {
        font-size: 12px;
        font-weight: 700;
        color: #2DCA72;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 18px;
    }
    .hero-title {
        font-size: 50px;
        font-weight: 900;
        color: #111;
        line-height: 1.05;
        letter-spacing: -1.5px;
        margin: 0 0 18px;
    }
    .hero-sub {
        font-size: 16px;
        color: #666;
        line-height: 1.7;
        max-width: 480px;
        margin: 0 0 28px;
    }
    .hero-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        color: #999;
    }
    .hero-meta-dot {
        width: 7px; height: 7px;
        background: #2DCA72;
        border-radius: 50%;
        display: inline-block;
    }
    .hero-stats {
        display: flex;
        gap: 40px;
        margin-top: 36px;
        padding-top: 28px;
        border-top: 1px solid #EBEBEB;
    }
    .stat-num   { font-size: 30px; font-weight: 800; color: #111; line-height: 1; }
    .stat-label { font-size: 12px; color: #999; margin-top: 5px; font-weight: 500; }

    /* ── Карточки ── */
    .card {
        background: #FAFAFA;
        border: 1px solid #E8E8E8;
        border-radius: 14px;
        padding: 26px;
        margin-bottom: 14px;
        transition: border-color .2s, box-shadow .2s;
    }
    .card:hover { border-color: #2DCA72; box-shadow: 0 2px 16px rgba(45,202,114,.08); }
    .card-tag {
        font-size: 10px; font-weight: 700;
        color: #2DCA72; letter-spacing: 1.6px;
        text-transform: uppercase; margin-bottom: 10px;
    }
    .card-h { font-size: 19px; font-weight: 700; color: #111; margin: 0 0 8px; }
    .card-p { font-size: 14px; color: #777; line-height: 1.65; margin: 0 0 16px; }
    .feat     { font-size: 14px; color: #444; margin-bottom: 9px; display: flex; align-items: flex-start; gap: 10px; }
    .feat-ico { color: #2DCA72; font-weight: 800; flex-shrink: 0; font-size: 13px; min-width: 18px; }

    /* ── Инпуты ── */
    [data-testid="stTextInput"] label { color: #555 !important; font-size: 13px !important; font-weight: 500 !important; }
    [data-testid="stTextInput"] input {
        background: #FAFAFA !important;
        border: 1.5px solid #E0E0E0 !important;
        border-radius: 8px !important;
        color: #111 !important;
        font-size: 14px !important;
    }
    [data-testid="stTextInput"] input:focus { border-color: #2DCA72 !important; box-shadow: none !important; }

    [data-testid="stFileUploader"] {
        background: #FAFAFA !important;
        border: 1.5px dashed #DEDEDE !important;
        border-radius: 10px !important;
    }
    [data-testid="stFileUploader"] label { color: #555 !important; font-size: 13px !important; }

    /* ── Кнопки ── */
    .stButton > button {
        background: #111111 !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 14px 24px !important;
        width: 100% !important;
        transition: background .15s !important;
    }
    .stButton > button:hover { background: #2DCA72 !important; color: #000 !important; }
    .stButton > button:disabled { background: #E8E8E8 !important; color: #aaa !important; }

    [data-testid="stDownloadButton"] > button {
        background: #2DCA72 !important;
        color: #000 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 14px 24px !important;
        width: 100% !important;
    }
    [data-testid="stDownloadButton"] > button:hover { background: #25b363 !important; }

    /* ── Tabs ── */
    [data-testid="stTabs"] button { color: #999 !important; font-weight: 500 !important; }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #111 !important;
        border-bottom-color: #2DCA72 !important;
    }

    hr { border: none; border-top: 1px solid #EBEBEB; margin: 40px 0; }

    .result-label {
        font-size: 10px; font-weight: 700; color: #2DCA72;
        letter-spacing: 1.6px; text-transform: uppercase; margin-bottom: 18px;
    }
    [data-testid="stMarkdown"] table { border-collapse: collapse; width: 100%; }
    [data-testid="stMarkdown"] th { background: #F5F5F5; color: #111; padding: 10px 14px; font-size: 13px; border: 1px solid #E8E8E8; }
    [data-testid="stMarkdown"] td { color: #444; padding: 9px 14px; font-size: 13px; border: 1px solid #EBEBEB; }
    [data-testid="stMarkdown"] tr:hover td { background: #FAFAFA; }
</style>
""", unsafe_allow_html=True)

# ── Навбар ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="nav">
    <div class="nav-logo-crop">
        <img src="data:image/webp;base64,{LOGO_B64}" />
    </div>
    <span class="nav-link nav-link-active">Gap-Analyzer</span>
    <span class="nav-link">Компетенции</span>
    <span class="nav-link">Инструкция</span>
    <span class="nav-cta">Школа 21</span>
</div>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
now = datetime.datetime.now().strftime("%d.%m.%Y, %H:%M")

# ── Hero ───────────────────────────────────────────────────────────────────────
_h1, hero_l, hero_r, _h2 = st.columns([1, 3, 2, 1])

with hero_l:
    st.markdown(f"""
    <div class="hero">
        <div class="hero-eyebrow">AI PDLC Competency Matrix v2</div>
        <h1 class="hero-title">Gap-Analyzer<br>учебных программ</h1>
        <p class="hero-sub">
            Загрузите паспорт программы — агент оценит её по 6 компетенциям
            AI PDLC, найдёт разрывы и сформирует экспертный отчёт.
        </p>
        <div class="hero-meta">
            <span class="hero-meta-dot"></span>
            Сервис активен · {now}
        </div>
        <div class="hero-stats">
            <div><div class="stat-num">6</div><div class="stat-label">Компетенций</div></div>
            <div><div class="stat-num">10</div><div class="stat-label">Уровней N0→S3</div></div>
            <div><div class="stat-num">E0–E4</div><div class="stat-label">Шкала evidence</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with hero_r:
    st.markdown(f"""
    <div style="padding-top:48px; display:flex; justify-content:center; align-items:flex-start;">
        <img src="data:image/webp;base64,{LOGO_B64}"
             style="width:220px; height:auto;" />
    </div>
    """, unsafe_allow_html=True)

# ── Основной контент ───────────────────────────────────────────────────────────
st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

_c1, col_l, col_r, _c2 = st.columns([1, 3, 2, 1], gap="medium")

with col_l:
    st.markdown("""
    <div class="card">
        <div class="card-tag">Шаг 01 / Тип программы</div>
        <div class="card-h">Выберите сценарий анализа</div>
        <div class="card-p">
            Агент использует разную логику оценки в зависимости от типа программы.
        </div>
    </div>
    """, unsafe_allow_html=True)

    scenario = st.radio(
        label="Тип программы",
        options=["Проектируемая программа", "Текущая программа"],
        captions=[
            "Сценарий А — анализ учебного плана, который разрабатывается",
            "Сценарий Б — оценка уже существующих проектов и чек-листов",
        ],
        label_visibility="collapsed",
    )

    st.markdown("""
    <div class="card" style="margin-top:14px;">
        <div class="card-tag">Шаг 02 / Загрузка файлов</div>
        <div class="card-h">Материалы программы</div>
        <div class="card-p">
            Паспорт Excel обязателен. Модули (.md) и чек-листы (.yml) повышают точность анализа.
        </div>
    </div>
    """, unsafe_allow_html=True)

    program_name = st.text_input("Название программы", placeholder="Например: Интенсив AI для аналитиков")
    xlsx_file    = st.file_uploader("Паспорт программы (.xlsx)", type=["xlsx"])
    md_files     = st.file_uploader("Описание модулей (.md) — можно несколько", type=["md"], accept_multiple_files=True)
    yaml_files   = st.file_uploader("Чек-листы проектов (.yml) — можно несколько", type=["yml", "yaml"], accept_multiple_files=True)

    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("Запустить анализ →", disabled=xlsx_file is None, use_container_width=True)

with col_r:
    st.markdown("""
    <div class="card">
        <div class="card-tag">Режим / 01</div>
        <div class="card-h">Gap-Анализ</div>
        <div class="card-p">
            Агент проверит программу по матрице AI PDLC v2,
            найдёт разрывы и предложит задания для доработки.
        </div>
        <div class="feat"><span class="feat-ico">✓</span> Competency Coverage Map</div>
        <div class="feat"><span class="feat-ico">✓</span> Уровни N0 → S3 · Evidence E0–E4</div>
        <div class="feat"><span class="feat-ico">✓</span> Детальный анализ разрывов</div>
        <div class="feat"><span class="feat-ico">✓</span> Рекомендации и новые задания</div>
        <div class="feat"><span class="feat-ico">✓</span> Сертификационное заключение</div>
    </div>
    <div class="card">
        <div class="card-tag">6 Компетенций AI PDLC</div>
        <div class="feat"><span class="feat-ico">01</span> Prompting</div>
        <div class="feat"><span class="feat-ico">02</span> Prompt Engineering</div>
        <div class="feat"><span class="feat-ico">03</span> Context Management</div>
        <div class="feat"><span class="feat-ico">04</span> Creating Tools</div>
        <div class="feat"><span class="feat-ico">05</span> Creating Skills</div>
        <div class="feat"><span class="feat-ico">06</span> Agent Teams</div>
    </div>
    """, unsafe_allow_html=True)

# ── Анализ ─────────────────────────────────────────────────────────────────────
if analyze_btn and xlsx_file:
    name = program_name.strip() or xlsx_file.name.replace(".xlsx", "")
    scenario_label = "А — Проектируемая программа" if scenario == "Проектируемая программа" else "Б — Текущая программа"
    try:
        md_list   = [(f.name, f.read()) for f in (md_files or [])]
        yaml_list = [(f.name, f.read()) for f in (yaml_files or [])]
        program_text = build_program_text(xlsx_file.read(), md_list, yaml_list)

        st.markdown("<hr>", unsafe_allow_html=True)
        _r1, res_col, _r2 = st.columns([1, 6, 1])
        with res_col:
            st.markdown('<div class="result-label">Результат / Отчёт</div>', unsafe_allow_html=True)
            with st.spinner("Агент анализирует..."):
                report = st.write_stream(
                    analyze_program_stream(program_text, name, scenario_label)
                )
            st.session_state["report"] = report
            st.session_state["report_name"] = name
    except Exception as e:
        st.error(f"Ошибка при анализе: {e}")

# ── Кнопка скачать (показывается после завершения стрима) ──────────────────────
if "report" in st.session_state:
    _r1, res_col, _r2 = st.columns([1, 6, 1])
    with res_col:
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="Скачать отчёт (.md) →",
            data=st.session_state["report"].encode("utf-8"),
            file_name=f"report_{st.session_state['report_name'].replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
