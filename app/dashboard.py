"""Dashboard executivo e técnico do projeto ENADE 2023."""

from __future__ import annotations

import html
import json
import re
from math import ceil
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "reports" / "tables"
PROCESSED = ROOT / "data" / "processed"
MODELS = ROOT / "models"

COLORS = {
    "background": "#07111F",
    "surface": "#0E1B2D",
    "surface_high": "#13243A",
    "border": "#203753",
    "text": "#F1F5F9",
    "muted": "#94A3B8",
    "teal": "#2DD4BF",
    "blue": "#60A5FA",
    "cyan": "#22D3EE",
    "amber": "#FBBF24",
    "rose": "#FB7185",
}

MODEL_COLORS = {
    "Regressão Logística": COLORS["teal"],
    "HistGradientBoosting": COLORS["blue"],
    "Random Forest": COLORS["amber"],
}

PLOT_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
    "scrollZoom": False,
}

st.set_page_config(
    page_title="ENADE 2023 | Inteligência por curso",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    """Aplica uma camada visual estável usando seletores públicos do Streamlit."""
    st.markdown(
        f"""
        <style>
        :root {{
            --bg: {COLORS['background']};
            --surface: {COLORS['surface']};
            --surface-high: {COLORS['surface_high']};
            --border: {COLORS['border']};
            --text: {COLORS['text']};
            --muted: {COLORS['muted']};
            --accent: {COLORS['teal']};
        }}

        html, body, [class*="css"] {{
            font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}

        [data-testid="stAppViewContainer"] {{
            background:
                radial-gradient(circle at 76% -12%, rgba(45, 212, 191, .10), transparent 30%),
                radial-gradient(circle at 16% 18%, rgba(96, 165, 250, .07), transparent 28%),
                var(--bg);
        }}

        [data-testid="stMainBlockContainer"] {{
            max-width: 1480px;
            padding: 2.4rem 3rem 4rem;
        }}

        [data-testid="stHeader"] {{ background: transparent; }}
        [data-testid="stToolbar"], #MainMenu, footer {{ display: none !important; }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0B1728 0%, #0A1422 100%);
            border-right: 1px solid var(--border);
        }}

        [data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
            padding: 1.4rem 1rem;
        }}

        [data-baseweb="select"] > div {{
            background: #0A1525 !important;
            border-color: var(--border) !important;
            border-radius: 12px !important;
            min-height: 48px;
        }}

        [data-baseweb="tag"] {{
            background: rgba(45, 212, 191, .14) !important;
            border: 1px solid rgba(45, 212, 191, .25) !important;
            color: #CCFBF1 !important;
            border-radius: 8px !important;
        }}

        [data-testid="stSidebar"] .stButton > button {{
            width: 100%;
            border-radius: 10px;
            border: 1px solid var(--border);
            background: transparent;
            color: #CBD5E1;
        }}

        [data-testid="stSidebar"] .stButton > button:hover {{
            border-color: var(--accent);
            color: #CCFBF1;
        }}

        .side-brand {{
            display: flex;
            align-items: center;
            gap: .75rem;
            margin-bottom: 1.8rem;
        }}

        .brand-mark {{
            width: 42px;
            height: 42px;
            display: grid;
            place-items: center;
            border-radius: 12px;
            background: linear-gradient(135deg, var(--accent), #38BDF8);
            color: #042F2E;
            font-weight: 900;
            letter-spacing: -.04em;
            box-shadow: 0 10px 28px rgba(45, 212, 191, .18);
        }}

        .brand-copy strong {{ display: block; color: var(--text); font-size: .95rem; }}
        .brand-copy span {{ color: var(--muted); font-size: .74rem; }}

        .sidebar-title {{
            margin: .25rem 0 1rem;
            color: #CBD5E1;
            font-size: .73rem;
            font-weight: 800;
            letter-spacing: .11em;
            text-transform: uppercase;
        }}

        .filter-note {{
            margin-top: 1rem;
            padding: .9rem 1rem;
            border: 1px solid rgba(96, 165, 250, .20);
            background: rgba(96, 165, 250, .07);
            border-radius: 12px;
            color: #AFC6DF;
            font-size: .78rem;
            line-height: 1.55;
        }}

        .sidebar-status {{
            display: flex;
            align-items: center;
            gap: .5rem;
            margin-top: 1.25rem;
            color: var(--muted);
            font-size: .75rem;
        }}

        .status-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent);
            box-shadow: 0 0 0 4px rgba(45, 212, 191, .10);
        }}

        .hero {{
            position: relative;
            overflow: hidden;
            padding: 2rem 2.1rem;
            border: 1px solid var(--border);
            border-radius: 22px;
            background: linear-gradient(135deg, rgba(19, 36, 58, .96), rgba(10, 24, 40, .86));
            box-shadow: 0 24px 70px rgba(0, 0, 0, .20);
            margin-bottom: 1.25rem;
        }}

        .hero::after {{
            content: "";
            position: absolute;
            width: 290px;
            height: 290px;
            right: -90px;
            top: -170px;
            border-radius: 50%;
            border: 46px solid rgba(45, 212, 191, .06);
        }}

        .eyebrow {{
            color: #7DD3FC;
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin-bottom: .65rem;
        }}

        .hero h1 {{
            max-width: 900px;
            margin: 0;
            color: var(--text);
            font-size: clamp(2rem, 3.5vw, 3.2rem);
            line-height: 1.07;
            letter-spacing: -.045em;
        }}

        .hero p {{
            max-width: 760px;
            margin: .85rem 0 1.2rem;
            color: #AFC0D4;
            font-size: .95rem;
            line-height: 1.6;
        }}

        .hero-meta {{ display: flex; flex-wrap: wrap; gap: .55rem; }}
        .pill {{
            display: inline-flex;
            align-items: center;
            gap: .4rem;
            padding: .42rem .72rem;
            border: 1px solid var(--border);
            border-radius: 999px;
            background: rgba(7, 17, 31, .42);
            color: #CBD5E1;
            font-size: .74rem;
            font-weight: 650;
        }}
        .pill-accent {{ border-color: rgba(45, 212, 191, .34); color: #99F6E4; }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: .85rem;
            margin: 1.1rem 0 1.7rem;
        }}

        .kpi-card {{
            min-height: 128px;
            padding: 1.05rem 1.15rem;
            border: 1px solid var(--border);
            border-radius: 16px;
            background: linear-gradient(160deg, rgba(19, 36, 58, .88), rgba(11, 25, 43, .74));
        }}

        .kpi-card.selected {{
            border-color: rgba(45, 212, 191, .70);
            box-shadow: 0 0 0 1px rgba(45, 212, 191, .16), 0 14px 34px rgba(0, 0, 0, .16);
        }}

        .kpi-icon {{ color: var(--accent); font-size: .82rem; margin-bottom: .55rem; }}
        .kpi-label {{ color: var(--muted); font-size: .72rem; font-weight: 750; text-transform: uppercase; letter-spacing: .07em; }}
        .kpi-value {{ color: var(--text); font-size: 1.8rem; font-weight: 760; letter-spacing: -.04em; margin: .18rem 0 .1rem; }}
        .kpi-foot {{ color: #7F93AA; font-size: .72rem; }}

        .kpi-help {{
            color: var(--muted);
            font-size: .73rem;
            margin: -.25rem 0 .8rem;
        }}

        .page-status {{
            padding-top: .55rem;
            text-align: center;
            color: var(--muted);
            font-size: .8rem;
        }}

        [data-testid="stTabs"] [data-baseweb="tab-list"] {{
            gap: .35rem;
            border-bottom: 1px solid var(--border);
        }}

        [data-testid="stTabs"] [data-baseweb="tab"] {{
            height: 50px;
            padding: 0 1rem;
            color: var(--muted);
            border-radius: 10px 10px 0 0;
            font-weight: 650;
        }}

        [data-testid="stTabs"] [aria-selected="true"] {{ color: #CCFBF1 !important; }}

        [data-testid="stVerticalBlockBorderWrapper"] {{
            background: rgba(14, 27, 45, .68);
            border-color: var(--border) !important;
            border-radius: 16px !important;
        }}

        .section-kicker {{
            margin: .4rem 0 .15rem;
            color: var(--accent);
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .11em;
            text-transform: uppercase;
        }}

        .section-title {{
            margin: 0 0 .2rem;
            color: var(--text);
            font-size: 1.12rem;
            font-weight: 720;
            letter-spacing: -.015em;
        }}

        .section-copy {{
            color: var(--muted);
            font-size: .78rem;
            margin-bottom: .4rem;
        }}

        .insight-box {{
            padding: 1rem 1.1rem;
            border-left: 3px solid var(--accent);
            border-radius: 0 12px 12px 0;
            background: rgba(45, 212, 191, .055);
            color: #B8CADC;
            font-size: .82rem;
            line-height: 1.6;
            margin: .6rem 0 1rem;
        }}

        .empty-state {{
            text-align: center;
            padding: 3.5rem 1rem;
            border: 1px dashed #315174;
            border-radius: 16px;
            color: var(--muted);
            background: rgba(14, 27, 45, .45);
        }}

        .empty-state strong {{ display: block; color: var(--text); font-size: 1.05rem; margin-bottom: .4rem; }}

        .method-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .8rem;
            margin: .8rem 0 1rem;
        }}
        .method-card {{
            padding: 1rem;
            border: 1px solid var(--border);
            border-radius: 14px;
            background: rgba(14, 27, 45, .66);
        }}
        .method-card strong {{ display: block; color: var(--text); margin-bottom: .4rem; font-size: .84rem; }}
        .method-card span {{ color: var(--muted); font-size: .76rem; line-height: 1.5; }}

        [data-testid="stDownloadButton"] button {{
            border-radius: 10px;
            border-color: var(--border);
            background: rgba(19, 36, 58, .72);
        }}

        @media (max-width: 1000px) {{
            [data-testid="stMainBlockContainer"] {{ padding: 1.5rem 1.2rem 3rem; }}
            .kpi-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
            .method-grid {{ grid-template-columns: 1fr; }}
        }}
        @media (max-width: 620px) {{
            .hero {{ padding: 1.35rem; border-radius: 16px; }}
            .kpi-grid {{ grid-template-columns: 1fr; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data():
    """Carrega somente artefatos derivados e agregados por curso."""
    train = pd.read_parquet(PROCESSED / "train_cursos.parquet")
    test = pd.read_parquet(PROCESSED / "test_cursos.parquet")
    data = pd.concat([train.assign(CONJUNTO="treino"), test.assign(CONJUNTO="teste")], ignore_index=True)
    metrics = pd.read_csv(TABLES / "metricas_modelos.csv")
    importance = pd.read_csv(TABLES / "importancia_features.csv")
    predictions = pd.read_csv(TABLES / "predicoes_teste.csv")
    model_meta = json.loads((MODELS / "metadata_modelo.json").read_text(encoding="utf-8"))
    prep_meta = json.loads((PROCESSED / "metadata_preparacao.json").read_text(encoding="utf-8"))
    return data, metrics, importance, predictions, model_meta, prep_meta


def style_figure(fig, height: int = 390, legend_position: str = "top"):
    """Padroniza todos os gráficos para a linguagem visual do dashboard."""
    legend = (
        dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title=dict(text=""))
        if legend_position == "top"
        else dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02, title=dict(text=""))
    )
    fig.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=30, b=18),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CBD5E1", size=12),
        title=dict(text="", subtitle=dict(text="")),
        legend=legend,
        hoverlabel=dict(bgcolor="#13243A", bordercolor="#2C496A", font_color="#F8FAFC"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#28415E", tickfont=dict(color="#94A3B8"))
    fig.update_yaxes(gridcolor="rgba(148,163,184,.12)", zeroline=False, tickfont=dict(color="#94A3B8"))
    return fig


GROUP_NAMES = {
    "5": "Medicina Veterinária",
    "6": "Odontologia",
    "12": "Medicina",
    "17": "Agronomia",
    "19": "Farmácia",
    "21": "Arquitetura e Urbanismo",
    "23": "Enfermagem",
    "27": "Fonoaudiologia",
    "28": "Nutrição",
    "36": "Fisioterapia",
    "51": "Zootecnia",
    "55": "Biomedicina",
    "69": "Tecnologia em Radiologia",
    "90": "Tecnologia em Agronegócios",
    "91": "Tecnologia em Gestão Hospitalar",
    "92": "Tecnologia em Gestão Ambiental",
    "95": "Tecnologia em Estética e Cosmética",
    "5710": "Engenharia Civil",
    "5806": "Engenharia Elétrica",
    "5814": "Engenharia de Controle e Automação",
    "5902": "Engenharia Mecânica",
    "6002": "Engenharia de Alimentos",
    "6008": "Engenharia Química",
    "6208": "Engenharia de Produção",
    "6307": "Engenharia Ambiental",
    "6405": "Engenharia Florestal",
    "6410": "Tecnologia em Segurança do Trabalho",
    "6411": "Engenharia de Computação",
}

QUESTION_NAMES = {
    "08": "Renda familiar",
    "10": "Situação de trabalho",
    "15": "Ação afirmativa",
    "17": "Escola no ensino médio",
    "21": "Familiar com ensino superior",
    "22": "Leitura extraclasse",
    "23": "Horas de estudo",
    "25": "Motivo de escolha do curso",
    "26": "Motivo de escolha da IES",
}

FEATURE_NAMES = {
    "N_INSCRITOS": "Quantidade de inscritos",
    "IDADE_MEDIA": "Idade média",
    "IDADE_MEDIANA": "Idade mediana",
    "IDADE_DP": "Variação da idade",
    "IDADE_Q25": "Idade — 1º quartil",
    "IDADE_Q75": "Idade — 3º quartil",
    "PROP_TURNO_1": "Proporção no turno matutino",
    "PROP_TURNO_2": "Proporção no turno vespertino",
    "PROP_TURNO_3": "Proporção no turno integral",
    "PROP_TURNO_4": "Proporção no turno noturno",
    "AVALIACAO_PROCESSO_MEDIA": "Avaliação média do processo formativo",
    "ANOS_DESDE_INICIO_GRAD_MEDIANA": "Tempo mediano desde o ingresso",
    "ANOS_DESDE_FIM_EM_MEDIANA": "Tempo mediano desde o ensino médio",
}


def friendly_feature(raw_name: str) -> str:
    """Transforma nomes do pipeline em rótulos adequados para leitura executiva."""
    name = re.sub(r"^(numeric|categorical)__", "", str(raw_name))
    if name in FEATURE_NAMES:
        return FEATURE_NAMES[name]
    group = re.fullmatch(r"CO_GRUPO_(.+)", name)
    if group:
        code = group.group(1)
        return f"Área • {GROUP_NAMES.get(code, code)}"
    question = re.fullmatch(r"PROP_QE_I(\d{2})_(.+)", name)
    if question:
        topic = QUESTION_NAMES.get(question.group(1), f"Questão {question.group(1)}")
        return f"{topic} • resposta {question.group(2)}"
    if name.startswith("CO_MODALIDADE_"):
        return "Modalidade • " + {"0": "EaD", "1": "Presencial"}.get(name.rsplit("_", 1)[-1], name)
    if name.startswith("CO_REGIAO_CURSO_"):
        return "Região do curso"
    return name.replace("_", " ").title()


def chart_header(kicker: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="section-kicker">{html.escape(kicker)}</div>
        <div class="section-title">{html.escape(title)}</div>
        <div class="section-copy">{html.escape(copy)}</div>
        """,
        unsafe_allow_html=True,
    )


inject_styles()

try:
    data, metrics, importance, predictions, model_meta, prep_meta = load_data()
except FileNotFoundError:
    st.error("Artefatos ausentes. Execute `./rodar_pipeline.sh` antes do dashboard.")
    st.stop()

region_map = {"1": "Norte", "2": "Nordeste", "3": "Sudeste", "4": "Sul", "5": "Centro-Oeste"}
modality_map = {"0": "EaD", "1": "Presencial"}
data["REGIAO"] = data["CO_REGIAO_CURSO"].astype(str).map(region_map).fillna("Outro")
data["MODALIDADE"] = data["CO_MODALIDADE"].astype(str).map(modality_map).fillna("Outro")

region_options = sorted(data["REGIAO"].unique())
modality_options = sorted(data["MODALIDADE"].unique())

if "region_filter" not in st.session_state:
    st.session_state.region_filter = region_options
if "modality_filter" not in st.session_state:
    st.session_state.modality_filter = modality_options
if "selected_kpi" not in st.session_state:
    st.session_state.selected_kpi = "courses"
if "course_page" not in st.session_state:
    st.session_state.course_page = 1


def reset_course_page() -> None:
    st.session_state.course_page = 1


def select_kpi(kpi: str) -> None:
    st.session_state.selected_kpi = kpi


def previous_course_page() -> None:
    st.session_state.course_page = max(1, st.session_state.course_page - 1)


def next_course_page() -> None:
    st.session_state.course_page += 1


def reset_filters() -> None:
    st.session_state.region_filter = region_options
    st.session_state.modality_filter = modality_options
    reset_course_page()


with st.sidebar:
    st.markdown(
        """
        <div class="side-brand">
            <div class="brand-mark">E23</div>
            <div class="brand-copy"><strong>ENADE Analytics</strong><span>Ciência de dados educacionais</span></div>
        </div>
        <div class="sidebar-title">Explorar recorte</div>
        """,
        unsafe_allow_html=True,
    )
    selected_regions = st.multiselect(
        "Região",
        region_options,
        key="region_filter",
        help="Filtra apenas os gráficos descritivos por localização do curso.",
        on_change=reset_course_page,
    )
    selected_modalities = st.multiselect(
        "Modalidade",
        modality_options,
        key="modality_filter",
        help="Compara cursos presenciais e a distância.",
        on_change=reset_course_page,
    )
    st.button("↺ Restaurar filtros", on_click=reset_filters, width="stretch")
    st.markdown(
        """
        <div class="filter-note">
            Os filtros atualizam o perfil dos cursos. As métricas de ML permanecem fixas para preservar a avaliação no conjunto de teste completo.
        </div>
        <div class="sidebar-status"><span class="status-dot"></span>Pipeline validado • seed 42</div>
        """,
        unsafe_allow_html=True,
    )

filtered = data[data["REGIAO"].isin(selected_regions) & data["MODALIDADE"].isin(selected_modalities)]
best = metrics.loc[metrics["modelo"] == model_meta["melhor_modelo"]].iloc[0]
threshold = prep_meta["limiar_mediana_aprendido_no_treino"]
filtered_share = len(filtered) / len(data) if len(data) else 0
filtered_mean = filtered["NT_GER_MEDIA_CURSO"].mean() if not filtered.empty else float("nan")

st.markdown(
    f"""
    <section class="hero">
        <div class="eyebrow">Inteligência analítica • Ensino Superior</div>
        <h1>Desempenho dos cursos no ENADE 2023</h1>
        <p>Uma leitura agregada, reproduzível e orientada a evidências sobre perfil dos cursos, desempenho e capacidade preditiva dos modelos avaliados.</p>
        <div class="hero-meta">
            <span class="pill pill-accent">● Modelo selecionado: {html.escape(model_meta['melhor_modelo'])}</span>
            <span class="pill">7.723 cursos elegíveis</span>
            <span class="pill">Split 80/20</span>
            <span class="pill">5-fold CV</span>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

mean_text = "—" if pd.isna(filtered_mean) else f"{filtered_mean:.1f}".replace(".", ",")
st.markdown('<div class="kpi-help">Selecione um indicador para ver sua interpretação e os valores complementares.</div>', unsafe_allow_html=True)

kpi_cards = [
    (
        "courses",
        "◈ Recorte atual",
        "Cursos visualizados",
        f"{len(filtered):,}",
        f"{filtered_share:.1%} da base elegível",
        "Ver cursos",
    ),
    (
        "mean",
        "◎ Desempenho agregado",
        "Média de NT_GER",
        mean_text,
        f"Limiar do treino: {threshold:.2f}",
        "Entender média",
    ),
    (
        "f1",
        "✓ Equilíbrio preditivo",
        "F1 no teste",
        f"{best['f1']:.3f}",
        f"Precision {best['precision']:.3f} • Recall {best['recall']:.3f}",
        "Detalhar F1",
    ),
    (
        "roc_auc",
        "↗ Discriminação",
        "ROC-AUC no teste",
        f"{best['roc_auc']:.3f}",
        f"Accuracy {best['accuracy']:.3f}",
        "Detalhar ROC-AUC",
    ),
]

kpi_columns = st.columns(4, gap="medium")
for column, (key, icon, label, value, foot, action) in zip(kpi_columns, kpi_cards):
    selected_class = " selected" if st.session_state.selected_kpi == key else ""
    with column:
        st.markdown(
            f"""
            <div class="kpi-card{selected_class}">
                <div class="kpi-icon">{html.escape(icon)}</div>
                <div class="kpi-label">{html.escape(label)}</div>
                <div class="kpi-value">{html.escape(value)}</div>
                <div class="kpi-foot">{html.escape(foot)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button(
            action,
            key=f"kpi_{key}",
            on_click=select_kpi,
            args=(key,),
            type="primary" if st.session_state.selected_kpi == key else "secondary",
            width="stretch",
        )

selected_kpi = st.session_state.selected_kpi
with st.container(border=True):
    if selected_kpi == "courses":
        chart_header(
            "Detalhe do indicador",
            "Cursos presentes no recorte atual",
            "O valor acompanha os filtros de região e modalidade; a listagem paginada está na aba Visão geral.",
        )
        train_count = int((filtered["CONJUNTO"] == "treino").sum())
        test_count = int((filtered["CONJUNTO"] == "teste").sum())
        st.write(f"O recorte contém **{train_count:,} cursos de treino** e **{test_count:,} cursos de teste**.")
    elif selected_kpi == "mean":
        chart_header(
            "Detalhe do indicador",
            "Resumo da nota geral média por curso",
            "A média é descritiva e muda conforme os filtros; ela não representa Conceito Enade ou nota de aprovação.",
        )
        if filtered.empty:
            st.write("Não há cursos no recorte selecionado.")
        else:
            mean_details = filtered["NT_GER_MEDIA_CURSO"].agg(["mean", "median", "min", "max"])
            st.write(
                f"Média **{mean_details['mean']:.2f}**, mediana **{mean_details['median']:.2f}**, "
                f"mínimo **{mean_details['min']:.2f}** e máximo **{mean_details['max']:.2f}**."
            )
    elif selected_kpi == "f1":
        chart_header(
            "Detalhe do indicador",
            "Equilíbrio entre precision e recall",
            "O F1 resume os dois critérios e foi a métrica usada para comparar e selecionar os modelos.",
        )
        st.write(
            f"No teste intocado, o modelo obteve **precision {best['precision']:.3f}**, "
            f"**recall {best['recall']:.3f}** e **F1 {best['f1']:.3f}**."
        )
    else:
        chart_header(
            "Detalhe do indicador",
            "Capacidade de separar as duas classes",
            "ROC-AUC próximo de 1 indica boa ordenação entre cursos acima e até a mediana, considerando todos os limiares.",
        )
        st.write(
            f"O modelo alcançou **ROC-AUC {best['roc_auc']:.3f}** e "
            f"**accuracy {best['accuracy']:.3f}** no conjunto de teste."
        )

overview_tab, model_tab, governance_tab = st.tabs(
    ["◉ Visão geral", "◈ Desempenho do modelo", "◇ Explicabilidade e governança"]
)

with overview_tab:
    if filtered.empty:
        st.markdown(
            """
            <div class="empty-state"><strong>Nenhum curso neste recorte</strong>Selecione ao menos uma região e uma modalidade ou restaure os filtros.</div>
            """,
            unsafe_allow_html=True,
        )
    else:
        left, right = st.columns([1.12, 1], gap="large")
        with left:
            with st.container(border=True):
                chart_header("Distribuição", "Onde os cursos se concentram?", "A linha tracejada marca o limiar aprendido exclusivamente no treino.")
                fig = px.histogram(
                    filtered,
                    x="NT_GER_MEDIA_CURSO",
                    color="MODALIDADE",
                    nbins=34,
                    barmode="overlay",
                    opacity=0.76,
                    color_discrete_map={"Presencial": COLORS["blue"], "EaD": COLORS["teal"]},
                    labels={"NT_GER_MEDIA_CURSO": "Média de NT_GER", "count": "Cursos", "MODALIDADE": "Modalidade"},
                )
                fig.add_vline(x=threshold, line_dash="dot", line_width=2, line_color=COLORS["rose"])
                for trace in fig.data:
                    modality = str(trace.name)
                    trace.update(
                        marker_line_width=0,
                        hovertemplate=f"Modalidade: {modality}<br>Nota média: %{{x:.1f}}<br>Cursos: %{{y}}<extra></extra>",
                    )
                fig.update_layout(legend_title_text="", yaxis_title="Quantidade de cursos")
                style_figure(fig, 405)
                st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)
        with right:
            with st.container(border=True):
                chart_header("Território", "Desempenho por região", "As etiquetas mostram o número de cursos incluídos em cada região.")
                by_region = (
                    filtered.groupby("REGIAO", as_index=False)
                    .agg(media=("NT_GER_MEDIA_CURSO", "mean"), mediana=("NT_GER_MEDIA_CURSO", "median"), cursos=("CO_CURSO", "nunique"))
                    .sort_values("media", ascending=False)
                )
                by_region["rotulo_cursos"] = by_region["cursos"].map(lambda value: f"{int(value)} cursos")
                fig = px.bar(
                    by_region,
                    x="REGIAO",
                    y="media",
                    text="rotulo_cursos",
                    color="media",
                    color_continuous_scale=[[0, "#1D4E69"], [1, COLORS["teal"]]],
                    labels={"media": "Média de NT_GER", "REGIAO": "Região", "rotulo_cursos": "Cursos"},
                )
                fig.update_traces(
                    texttemplate="%{text}",
                    textposition="outside",
                    cliponaxis=False,
                    hovertemplate="%{x}<br>Média: %{y:.2f}<br>%{text}<extra></extra>",
                )
                fig.update_layout(coloraxis_showscale=False, showlegend=False)
                style_figure(fig, 405)
                st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)

        region_high = by_region.iloc[0]
        st.markdown(
            f"""
            <div class="insight-box">
                <strong>Leitura do recorte:</strong> a região com maior média observada é <strong>{html.escape(region_high['REGIAO'])}</strong>
                ({region_high['media']:.2f}), dentro dos filtros atuais. Essa diferença é descritiva e não representa efeito causal ou ranking oficial.
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            chart_header(
                "Consulta",
                "Cursos do recorte",
                "A tabela respeita os filtros da barra lateral e apresenta apenas informações agregadas por curso.",
            )
            search_column, size_column = st.columns([3, 1], gap="medium")
            with search_column:
                course_search = st.text_input(
                    "Buscar curso",
                    placeholder="Digite o código do curso, da IES ou da área",
                    key="course_search",
                    on_change=reset_course_page,
                )
            with size_column:
                page_size = st.selectbox(
                    "Itens por página",
                    options=[10, 25, 50],
                    index=1,
                    key="course_page_size",
                    on_change=reset_course_page,
                )

            course_rows = filtered[
                [
                    "CO_CURSO",
                    "CO_IES",
                    "CO_GRUPO",
                    "REGIAO",
                    "MODALIDADE",
                    "N_INSCRITOS",
                    "N_RESULTADOS_VALIDOS",
                    "NT_GER_MEDIA_CURSO",
                    "TARGET_ACIMA_MEDIANA_TREINO",
                    "CONJUNTO",
                ]
            ].copy()

            normalized_search = course_search.strip().casefold()
            if normalized_search:
                searchable = (
                    course_rows[["CO_CURSO", "CO_IES", "CO_GRUPO"]]
                    .astype("string")
                    .fillna("")
                    .agg(" ".join, axis=1)
                    .str.casefold()
                )
                course_rows = course_rows.loc[searchable.str.contains(normalized_search, regex=False)].copy()

            course_rows = course_rows.sort_values(["NT_GER_MEDIA_CURSO", "CO_CURSO"], ascending=[False, True])
            total_rows = len(course_rows)
            total_pages = max(1, ceil(total_rows / page_size))
            st.session_state.course_page = min(max(1, st.session_state.course_page), total_pages)
            current_page = st.session_state.course_page
            start = (current_page - 1) * page_size
            page_rows = course_rows.iloc[start : start + page_size].copy()

            page_rows["TARGET_ACIMA_MEDIANA_TREINO"] = page_rows["TARGET_ACIMA_MEDIANA_TREINO"].map(
                {0: "Até a mediana", 1: "Acima da mediana"}
            )
            page_rows["CONJUNTO"] = page_rows["CONJUNTO"].map({"treino": "Treino", "teste": "Teste"})
            page_rows = page_rows.rename(
                columns={
                    "CO_CURSO": "Curso",
                    "CO_IES": "IES",
                    "CO_GRUPO": "Área",
                    "REGIAO": "Região",
                    "MODALIDADE": "Modalidade",
                    "N_INSCRITOS": "Inscritos",
                    "N_RESULTADOS_VALIDOS": "Resultados válidos",
                    "NT_GER_MEDIA_CURSO": "Média NT_GER",
                    "TARGET_ACIMA_MEDIANA_TREINO": "Faixa",
                    "CONJUNTO": "Conjunto",
                }
            )

            if page_rows.empty:
                st.info("Nenhum curso corresponde à busca informada.")
            else:
                st.dataframe(
                    page_rows,
                    hide_index=True,
                    width="stretch",
                    height=min(680, 38 + 35 * len(page_rows)),
                    column_config={
                        "Média NT_GER": st.column_config.NumberColumn(format="%.2f"),
                        "Inscritos": st.column_config.NumberColumn(format="%d"),
                        "Resultados válidos": st.column_config.NumberColumn(format="%d"),
                    },
                )

            previous_column, status_column, next_column = st.columns([1, 2, 1], gap="medium")
            with previous_column:
                st.button(
                    "← Anterior",
                    key="previous_course_page",
                    on_click=previous_course_page,
                    disabled=current_page <= 1,
                    width="stretch",
                )
            with status_column:
                first_visible = start + 1 if total_rows else 0
                last_visible = min(start + page_size, total_rows)
                st.markdown(
                    f'<div class="page-status">Página {current_page} de {total_pages} • '
                    f'{first_visible}-{last_visible} de {total_rows} cursos</div>',
                    unsafe_allow_html=True,
                )
            with next_column:
                st.button(
                    "Próxima →",
                    key="next_course_page",
                    on_click=next_course_page,
                    disabled=current_page >= total_pages,
                    width="stretch",
                )

with model_tab:
    left, right = st.columns([1.18, 1], gap="large")
    with left:
        with st.container(border=True):
            chart_header("Benchmark", "Comparativo dos modelos", "Cinco métricas no teste intocado; a seleção foi feita pelo F1 médio da validação cruzada.")
            metric_labels = {
                "accuracy": "Accuracy",
                "precision": "Precision",
                "recall": "Recall",
                "f1": "F1",
                "roc_auc": "ROC-AUC",
            }
            metric_long = metrics.melt(
                id_vars="modelo",
                value_vars=list(metric_labels),
                var_name="metrica",
                value_name="valor",
            )
            metric_long["metrica"] = metric_long["metrica"].map(metric_labels)
            fig = px.bar(
                metric_long,
                x="metrica",
                y="valor",
                color="modelo",
                barmode="group",
                range_y=[0.75, 1.0],
                color_discrete_map=MODEL_COLORS,
                labels={"metrica": "Métrica", "valor": "Resultado", "modelo": "Modelo"},
            )
            for trace in fig.data:
                model_name = str(trace.name)
                trace.update(
                    texttemplate="%{y:.3f}",
                    textposition="outside",
                    cliponaxis=False,
                    hovertemplate=f"%{{x}}: %{{y:.4f}}<extra>{model_name}</extra>",
                )
            style_figure(fig, 440)
            st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)
    with right:
        with st.container(border=True):
            chart_header("Erros", "Matriz de confusão", "Acertos aparecem na diagonal; o teste contém 1.545 cursos nunca usados no ajuste.")
            confusion = pd.crosstab(predictions["y_true"], predictions["y_pred"]).reindex(index=[0, 1], columns=[0, 1], fill_value=0)
            confusion.index = ["Até a mediana", "Acima da mediana"]
            confusion.columns = ["Até a mediana", "Acima da mediana"]
            fig = px.imshow(
                confusion,
                text_auto=True,
                color_continuous_scale=[[0, "#10243A"], [1, COLORS["teal"]]],
                labels={"x": "Classe prevista", "y": "Classe real", "color": "Cursos"},
                aspect="auto",
            )
            fig.update_traces(hovertemplate="Real: %{y}<br>Previsto: %{x}<br>Cursos: %{z}<extra></extra>")
            style_figure(fig, 440)
            st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)

    with st.container(border=True):
        chart_header("Confiança", "Distribuição das probabilidades", "Separar as massas próximas de 0 e 1 indica maior segurança; valores perto de 0,5 são casos limítrofes.")
        probability_data = predictions.assign(
            classe_real=predictions["y_true"].map({0: "Até a mediana", 1: "Acima da mediana"})
        )
        fig = px.histogram(
            probability_data,
            x="y_proba",
            color="classe_real",
            nbins=34,
            barmode="overlay",
            opacity=0.72,
            color_discrete_map={"Até a mediana": COLORS["blue"], "Acima da mediana": COLORS["teal"]},
            labels={"y_proba": "Probabilidade de desempenho acima da mediana", "count": "Cursos", "classe_real": "Classe real"},
        )
        fig.add_vline(x=0.5, line_dash="dot", line_color=COLORS["amber"])
        for trace in fig.data:
            class_name = str(trace.name)
            trace.update(
                marker_line_width=0,
                hovertemplate=f"Probabilidade: %{{x:.2f}}<br>Cursos: %{{y}}<extra>{class_name}</extra>",
            )
        style_figure(fig, 360)
        st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)

with governance_tab:
    left, right = st.columns([1.25, .75], gap="large")
    with left:
        with st.container(border=True):
            chart_header("Interpretação", "O que mais influencia as previsões?", "Magnitude absoluta dos coeficientes do modelo selecionado. Associação preditiva não implica causalidade.")
            top = importance.head(15).copy()
            top["rotulo"] = top["feature"].map(friendly_feature)
            top = top.sort_values("importance")
            fig = px.bar(
                top,
                x="importance",
                y="rotulo",
                orientation="h",
                color="importance",
                color_continuous_scale=[[0, "#1E4B66"], [1, COLORS["teal"]]],
                labels={"importance": "Importância", "rotulo": "Variável"},
            )
            fig.update_layout(coloraxis_showscale=False)
            fig.update_traces(hovertemplate="%{y}<br>Importância: %{x:.3f}<extra></extra>")
            style_figure(fig, 535)
            st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)
    with right:
        st.markdown('<div class="section-kicker">Protocolo</div><div class="section-title">Como ler este painel</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="method-grid">
                <div class="method-card"><strong>Unidade segura</strong><span>Cada linha representa um curso agregado. Nenhum estudante é reconstituído entre arquivos.</span></div>
                <div class="method-card"><strong>Alvo operacional</strong><span>Classe 1 significa média do curso acima da mediana aprendida somente no treino.</span></div>
                <div class="method-card"><strong>Uso responsável</strong><span>O modelo apoia exploração e priorização analítica, não decisões punitivas ou individuais.</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.warning("Os resultados não equivalem ao Conceito Enade e não estabelecem relações causais.", icon="⚠️")
        st.markdown("##### Exportar evidências")
        st.download_button(
            "↓ Métricas dos modelos",
            data=metrics.to_csv(index=False).encode("utf-8-sig"),
            file_name="metricas_modelos.csv",
            mime="text/csv",
            width="stretch",
        )
        st.download_button(
            "↓ Importância das variáveis",
            data=importance.to_csv(index=False).encode("utf-8-sig"),
            file_name="importancia_features.csv",
            mime="text/csv",
            width="stretch",
        )
        st.download_button(
            "↓ Metadados do modelo",
            data=json.dumps(model_meta, ensure_ascii=False, indent=2),
            file_name="metadata_modelo.json",
            mime="application/json",
            width="stretch",
        )
