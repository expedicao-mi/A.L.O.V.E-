import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import urllib.parse
import json
import requests
import csv
from io import StringIO
import ast
import re
import html as html_lib
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import gspread



# ==============================================================================
# ⚙️ CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
LOGO_ALOVE_URL = "https://raw.githubusercontent.com/expedicao-mi/A.L.O.V.E-/main/app_icon.png"
BANNER_TOPO_URL = "https://raw.githubusercontent.com/expedicao-mi/A.L.O.V.E-/main/logo_alove.jpg?v=99"
SENHA_BAFOMETRO = "1000"

st.set_page_config(
    page_title="A.L.O.V.E. Mobile",
    page_icon="🚛",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st_autorefresh(interval=1200000, limit=None, key="refresh_mobile")

if "bafometro_autenticado" not in st.session_state:
    st.session_state.bafometro_autenticado = False

# ==============================================================================
# ⚡ SPLASH SCREEN INSTANTÂNEA (RENDERIZA ANTES DAS CONSULTAS DO GOOGLE SHEETS)
# ==============================================================================
if st.query_params.get("refresh") == "1":
    st.cache_data.clear()
    st.query_params.clear()
    st.session_state.pop("splash_exibida", None)

if "splash_exibida" not in st.session_state:
    st.session_state.splash_exibida = True
    st.markdown("""
        <style>
            [data-testid="stStatusWidget"] { display: none !important; visibility: hidden !important; }
            .alove-loader-bg {
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background: #050911; z-index: 99999999;
                display: flex; flex-direction: column; justify-content: center; align-items: center;
                gap: 10px;
                animation: loaderFadeOut 0.45s 2.85s forwards; pointer-events: none;
            }
            .alove-loader-text {
                font-size: 2.8rem; font-weight: 900; color: #00D672;
                letter-spacing: 6px; text-shadow: 0 0 20px rgba(0,214,114,0.6);
                overflow: hidden; white-space: nowrap; border-right: 4px solid #00D672;
                width: 0;
                animation: loaderTyping 0.95s steps(7, end) forwards, loaderBlink 0.5s step-end infinite alternate;
            }
            .alove-loader-sub {
                font-size: 0.82rem; font-weight: 700; color: #94a3b8;
                letter-spacing: 2.2px; text-transform: uppercase;
                opacity: 0;
                animation: loaderSubIn 0.45s 0.70s forwards;
            }
            @keyframes loaderTyping { from { width: 0 } to { width: 5.5em } }
            @keyframes loaderBlink { 50% { border-color: transparent } }
            @keyframes loaderSubIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
            @keyframes loaderFadeOut { to { opacity: 0; visibility: hidden; display: none; } }
        </style>
        <div class="alove-loader-bg">
            <div class="alove-loader-text">A.L.O.V.E</div>
            <div class="alove-loader-sub">Assistente Virtual da Expedição</div>
        </div>
    """, unsafe_allow_html=True)

def render_html(html_str: str):
    """Remove recuos e linhas em branco que fazem o Streamlit achar que o HTML é um bloco de código."""
    linhas_limpas = [linha.strip() for linha in html_str.splitlines() if linha.strip()]
    st.markdown(" ".join(linhas_limpas), unsafe_allow_html=True)

# ==============================================================================
# 🎨 CSS (LAYOUT VERTICAL COM DESIGN DE APP - SEM TRAVAMENTOS)
# ==============================================================================
st.markdown(f"""
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="A.L.O.V.E.">
    <link rel="apple-touch-icon" href="{LOGO_ALOVE_URL}">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#050911">
    <link rel="icon" type="image/png" href="{LOGO_ALOVE_URL}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        /* 🚀 1. ESTICA O CONTAINER DO STREAMLIT ATÉ O ÚLTIMO PIXEL FÍSICO DO IPHONE */
        html, body {
            background-color: #050911 !important;
            height: 100% !important;
            min-height: 100dvh !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }

        [data-testid="stAppViewContainer"], .stApp {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            height: 100dvh !important;
            min-height: 100dvh !important;
            background: radial-gradient(ellipse at top, #0c1a33 0%, #070d18 55%, #050911 100%) !important;
            background-color: #050911 !important;
            overflow-x: hidden !important;
            overflow-y: auto !important;
            -webkit-overflow-scrolling: touch !important;
            overscroll-behavior-y: contain !important;
        }

        .main, [data-testid="stMain"] {
            background: transparent !important;
            overflow-x: hidden !important;
        }

        /* 🚀 2. FIXA AS COLUNAS DO STREAMLIT PARA NÃO ENCAVALAREM */
        [data-testid="column"], [data-testid="stVerticalBlock"] {
            overflow: hidden !important;
            clear: both !important;
        }

        .clear-fix {
            clear: both;
            display: table;
            content: "";
        }

        /* 🚀 3. ESCONDE CABEÇALHO, RODAPÉ FANTASMA E BOTÕES DO STREAMLIT */
        #MainMenu, footer, header,
        [data-testid="stHeader"],
        [data-testid="stFooter"],
        [data-testid="stBottom"],
        [data-testid="stBottomBlockContainer"],
        [data-testid="manage-app-button"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        .stStatusWidget,
        .stAppDeployButton,
        div[class^="viewerBadge"],
        div[class*="_profileContainer"],
        div[class*="_link_"],
        a[href*="streamlit.io"],
        iframe[title="streamlit_autorefresh.st_autorefresh"],
        div[data-testid="stChatMessageSpinner"],
        div[role="status"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0 !important;
            width: 0 !important;
            pointer-events: none !important;
        }


        /* COLUNA CENTRAL ESTILO APP (COMPENSA O BANNER FIXO SEM BURACO) */
        .block-container {
            padding-top: calc(env(safe-area-inset-top, 0px) + 28px) !important;
            padding-bottom: 3.5rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            max-width: 560px !important;
            margin: 0 auto !important;
        }

        /* GARANTE QUE OS ATALHOS PAREM ABAIXO DO BANNER FIXO SEM TAMPAR O TÍTULO */
        [id^="sec-"] {
            scroll-margin-top: calc(env(safe-area-inset-top, 0px) + 104px) !important;
        }


        /* BANNER PERSISTENTE NO TOPO COM CANTOS ARREDONDADOS E NEON VERDE */
        .topo-banner-mask {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: calc(env(safe-area-inset-top, 0px) + 94px);
            background: linear-gradient(180deg, #050911 82%, rgba(5, 9, 17, 0) 100%);
            z-index: 9998;
            pointer-events: none;
        }
        .topo-banner {
            position: fixed;
            top: calc(env(safe-area-inset-top, 0px) + 6px);
            left: 50%;
            transform: translateX(-50%);
            width: calc(100% - 1.6rem);
            max-width: 534px;
            z-index: 9999;
            background: #050d1a;
            border: 1.5px solid #00D672;
            border-radius: 16px;
            box-shadow: 0 4px 18px rgba(0, 214, 114, 0.28), 0 6px 16px rgba(0, 0, 0, 0.75);
            overflow: hidden;
            text-align: center;
        }
        .topo-banner img {
            width: 100%;
            max-height: 84px;
            object-fit: cover;
            display: block;
            margin: 0 auto;
        }

        /* 🎯 BOTÃO FLUTUANTE DE ATALHOS & PRINT (CANTO INFERIOR DIREITO) */
        .fab-container {
            position: fixed;
            right: 16px;
            bottom: calc(env(safe-area-inset-bottom, 0px) + 18px);
            z-index: 99990;
        }
        .fab-details {
            position: relative;
        }
        .fab-details > summary {
            list-style: none;
            width: 54px;
            height: 54px;
            border-radius: 50%;
            background: #050911;
            padding: 3px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 18px rgba(0, 214, 114, 0.55), 0 4px 14px rgba(0, 0, 0, 0.85);
            border: 2px solid #00D672;
            cursor: pointer;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
            overflow: hidden;
        }
        .fab-details > summary img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 50%;
            display: block;
        }
        .fab-details > summary::-webkit-details-marker { display: none; }
        .fab-menu {
            position: absolute;
            right: 0;
            bottom: 60px;
            width: 225px;
            background: rgba(7, 15, 29, 0.96);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1.5px solid #00D672;
            border-radius: 16px;
            padding: 8px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.85), 0 0 16px rgba(0, 214, 114, 0.25);
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .fab-menu a {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 10px;
            border-radius: 9px;
            color: #e2e8f0;
            text-decoration: none;
            font-size: 0.78rem;
            font-weight: 700;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid transparent;
        }
        .fab-menu a:active {
            background: rgba(0, 214, 114, 0.18);
            border-color: #00D672;
            color: #ffffff;
        }
        .fab-menu a.fab-print-link {
            background: linear-gradient(90deg, rgba(0, 214, 114, 0.18) 0%, rgba(0, 132, 255, 0.18) 100%);
            border: 1px solid #00D672;
            color: #00FF7F;
            font-weight: 800;
            margin-top: 3px;
        }

        /* CARTÕES PADRÃO */
        .card-main {
            background: linear-gradient(180deg, #0b1830 0%, #08111f 100%);
            border: 1.5px solid #12506e; border-radius: 16px; padding: 14px;
            box-shadow: 0 0 14px rgba(0, 180, 255, 0.10); margin-bottom: 14px;
        }
        .card-head { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
        .icon-sq { width: 38px; height: 38px; border-radius: 10px; background: #0d2340; border: 1px solid #12506e; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; }
        .card-title { color: #fff; font-size: 1rem; font-weight: 800; letter-spacing: .3px; text-transform: uppercase; }
        .badge-novas { margin-left: auto; background: #0d2a4a; border: 1px solid #12506e; color: #38bdf8; font-size: .75rem; font-weight: 700; padding: 3px 10px; border-radius: 999px; }

        /* STATUS */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(180deg, #0b1830 0%, #08111f 100%) !important;
            border: 1.5px solid #12506e !important; border-radius: 16px !important;
            box-shadow: 0 0 14px rgba(0, 180, 255, 0.10); margin-bottom: 14px;
        }
        .conn-dot { display: inline-block; width: 14px; height: 14px; border-radius: 50%; margin-right: 10px; animation: pulso 1.8s infinite; }
        .conn-titulo { font-size: 1.15rem; font-weight: 800; letter-spacing: .3px; }
        .conn-sub { color: #9fb3cc; font-size: .85rem; margin-top: 4px; }
        .conn-ritmo { color: #00D672; font-size: .75rem; margin-top: 2px; }
        .stButton > button {
            background: transparent !important; color: #fff !important; font-weight: 700 !important;
            border: 2px solid #00b4ff !important; border-radius: 12px !important; min-height: 3rem;
            box-shadow: 0 0 10px rgba(0, 180, 255, 0.25);
        }

        /* NOTIFICAÇÕES */
        .notif-lista { background: #070f1d; border: 1px solid #12506e; border-radius: 12px; padding: 4px 12px; }
        .notif-item { display: flex; align-items: flex-start; gap: 12px; padding: 11px 0; border-bottom: 1px solid #12304a; }
        .notif-item:last-child { border-bottom: none; }
        .notif-ico { width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.05rem; flex-shrink: 0; }
        .notif-txt { flex: 1; min-width: 0; }
        .notif-tit { color: #fff; font-weight: 700; font-size: .92rem; }
        .notif-desc { color: #9fb3cc; font-size: .8rem; margin-top: 2px; word-break: break-word; }
        .notif-hora { color: #9fb3cc; font-size: .75rem; white-space: nowrap; }
        .notif-hora i { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-left: 6px; }

        /* PÁTIO: KPIs */
        .kpi-duo { display: flex; align-items: center; background: #070f1d; border: 1.5px solid #12506e; border-radius: 14px; padding: 14px 10px; }
        .kpi-box { flex: 1; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .kpi-ico { font-size: 1.9rem; }
        .kpi-big { color: #fff; font-size: 2.3rem; font-weight: 800; line-height: 1; }
        .kpi-big.verde { color: #00E676; }
        .kpi-big span { font-size: 1.4rem; }
        .kpi-lbl { color: #cfe0f5; font-size: .9rem; margin-top: 3px; }
        .kpi-sub { color: #64748b; font-size: .65rem; margin-top: 1px; }
        .kpi-sep { width: 1px; align-self: stretch; background: #12506e; margin: 0 6px; }

        /* PÁTIO: CARTÕES DE STATUS */
        details.st-card {
            --c: #38a9ff; background: #0a1424; background: color-mix(in srgb, var(--c) 9%, #0a1424);
            border: 1.5px solid var(--c); border-left: 6px solid var(--c);
            border-radius: 14px; margin-bottom: 10px; overflow: hidden;
        }
        details.st-card > summary { display: flex; align-items: center; gap: 14px; padding: 12px 14px; cursor: pointer; -webkit-tap-highlight-color: transparent; list-style: none; outline: none; }
        details.st-card > summary::-webkit-details-marker { display: none; }
        .st-ico { width: 52px; height: 52px; border-radius: 50%; border: 2px solid var(--c); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; flex-shrink: 0; background: rgba(255,255,255,0.03); }
        .st-txt { flex: 1; min-width: 0; }
        .st-title { color: #fff; font-weight: 800; font-size: 1.02rem; text-transform: uppercase; letter-spacing: .3px; }
        .st-num { color: #fff; font-size: 1.9rem; font-weight: 800; line-height: 1.15; }
        .st-num span { font-size: .95rem; font-weight: 400; color: #9fb3cc; }
        .chev { color: #38bdf8; font-size: 1.8rem; line-height: 1; transition: transform .25s ease; }
        details.st-card[open] > summary .chev { transform: rotate(90deg); }
        .st-body { background: #070d18; padding: 8px 14px 10px 14px; border-top: 1px solid #12304a; }
        .dest-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px dashed #1c2b42; font-size: .82rem; }
        .dest-row .n { color: #fff; }
        .dest-row .v { color: #38bdf8; }
        .dest-row .v small { color: #64748b; font-size: .8rem; }
        .dest-row.total { border-bottom: none; border-top: 1px solid #12506e; margin-top: 4px; padding-top: 8px; font-weight: 700; }
        .dest-vazio { color: #64748b; font-size: .78rem; padding: 6px 0; }

        /* BLOCOS MASTER (ACCORDIONS) */
        summary { list-style: none; outline: none; }
        summary::-webkit-details-marker { display: none; }
        details.master-box { background: linear-gradient(180deg, #0b1830 0%, #08111f 100%); border-radius: 16px; margin-bottom: 14px; border: 1.5px solid #12506e; border-left: 6px solid; overflow: hidden; }
        details.master-box > summary { cursor: pointer; padding: 14px 16px; position: relative; -webkit-tap-highlight-color: transparent; }
        details.master-box > summary::after { content: '▼'; position: absolute; right: 16px; top: 16px; font-size: 0.8rem; color: #64748b; transition: transform 0.3s ease; }
        details.master-box[open] > summary::after { transform: rotate(180deg); }

        .header-layout { display: flex; align-items: center; margin-bottom: 8px; gap: 8px; }
        .icon-box { width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; }
        .master-metric-title { color: #ffffff; font-size: 0.85rem; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }
        .value-layout { display: flex; align-items: baseline; gap: 6px; margin-bottom: 4px; }
        .master-metric-val { color: #ffffff; font-size: 2.2rem; font-weight: bold; line-height: 1; }
        .master-metric-unit { color: #64748b; font-size: 0.9rem; font-weight: normal; }
        .master-metric-sub { font-size: 0.85rem; font-weight: normal; margin-top: 4px; }
        .master-content { background-color: transparent; padding: 0 16px 16px 16px; }

        /* TABS CSS NATIVO (ESCONDE BOLINHA DO RADIO BUTTON) */
        .css-tabs-view input[type="radio"], .css-tabs-exp input[type="radio"] { display: none !important; }
        .css-tabs-view label { display: inline-block; padding: 8px 20px; background-color: #162438; color: #94a3b8; border-radius: 8px; font-size: 0.9rem; font-weight: bold; margin: 0 4px 14px 4px; cursor: pointer; border: 1px solid #1c2b42; transition: 0.2s; }
        .css-tabs-view input[type="radio"]#view_turnos:checked + label.lbl-v-turnos { background-color: #00D672; color: #0a101d; border-color: #00D672; }
        .css-tabs-view input[type="radio"]#view_destinos:checked + label.lbl-v-destinos { background-color: #38bdf8; color: #0a101d; border-color: #38bdf8; }
        .view-content-exp { display: none; animation: fadeIn 0.3s ease; }
        #view_turnos:checked ~ #content_view_turnos { display: block; }
        #view_destinos:checked ~ #content_view_destinos { display: block; }

        .css-tabs-exp label { display: inline-block; padding: 6px 16px; background-color: #162438; color: #94a3b8; border-radius: 6px; font-size: 0.85rem; font-weight: bold; margin: 0 4px; cursor: pointer; border: 1px solid #1c2b42; transition: 0.2s; }
        .css-tabs-exp input[type="radio"]#tab_ontem:checked + label.lbl-ontem { background-color: #38bdf8; color: #0a101d; border-color: #38bdf8; }
        .css-tabs-exp input[type="radio"]#tab_hoje:checked + label.lbl-hoje { background-color: #00D672; color: #0a101d; border-color: #00D672; }
        .tab-content-exp { display: none; animation: fadeIn 0.3s ease; }
        #tab_ontem:checked ~ #content_ontem { display: block; }
        #tab_hoje:checked ~ #content_hoje { display: block; }

        /* TABS FROTA */
        .f-tag-ok { background-color: #00D672; color: #0a101d; }
        .f-tag-avaria { background-color: #E74C3C; color: #ffffff; }
        .f-tag-aten { background-color: #FFD600; color: #0a101d; }
        .f-tag-title { font-size: 0.85rem; color: #ffffff; font-weight: normal; margin-bottom: 8px; border-bottom: 1px dashed #1c2b42; padding-bottom: 4px; }
        .tag-box { display: inline-block; padding: 6px 10px; margin: 3px; border-radius: 6px; font-weight: normal; font-size: 0.8rem; text-align: center; }
        .f-legenda { margin-top: 14px; background: #05080f; border: 1px solid #1c2b42; border-radius: 8px; padding: 10px 12px; text-align: left; }
        .f-leg-titulo { color: #94a3b8; font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 8px; }
        .f-leg-item { display: flex; align-items: center; gap: 10px; color: #cbd5e1; font-size: .8rem; padding: 3px 0; }
        .f-leg-cor { width: 16px; height: 16px; border-radius: 4px; flex-shrink: 0; }

        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes pulso { 0% { box-shadow: 0 0 0 0 rgba(0,214,114,.55); } 70% { box-shadow: 0 0 0 9px rgba(0,214,114,0); } 100% { box-shadow: 0 0 0 0 rgba(0,214,114,0); } }
    </style>
""", unsafe_allow_html=True)


SHEET_ID = "10FluiIwlynIlPDA74QI8mpHSIrAc-62H1hZNRBsvfCA"

# ==============================================================================
# 🔧 UTILITÁRIOS E EXTRAÇÃO DE DADOS
# ==============================================================================
def forcar_par(valor):
    val_int = int(round(float(valor or 0)))
    return val_int + 1 if val_int % 2 != 0 else val_int

def fmt(n, casas=0):
    try: s = f"{float(n):,.{casas}f}"
    except Exception: return "0"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def safe_to_numeric(val):
    if pd.isna(val) or val == "" or val is None: return 0.0
    if isinstance(val, (int, float)): return float(val)
    s = re.sub(r'[^\d,\.\-]', '', str(val).strip())
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try: return float(s)
    except: return 0.0

@st.cache_data(ttl=20)
def carregar_dados_nuvem(worksheet_name: str, cabecalho=0):
    sheet_encoded = urllib.parse.quote(worksheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_encoded}&headers=1"
    try:
        df = pd.read_csv(url, header=cabecalho, on_bad_lines="skip")
        return df.dropna(how="all", axis=1).dropna(how="all", axis=0)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=15)
def carregar_tabela_cega(worksheet_name: str, coluna_chave: str = "DESTINO"):
    """
    Lê abas do Google Sheets de forma 100% segura usando gspread,
    fazendo busca flexível no nome da aba (ignora acentos, cedilha e espaços),
    identificando a linha do cabeçalho e extraindo o carimbo da Linha 1.
    """
    import os
    import unicodedata

    def norm_txt(s):
        s_str = str(s).strip().upper()
        return "".join(c for c in unicodedata.normalize("NFD", s_str) if unicodedata.category(c) != "Mn")

    try:
        if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
            dados_secret = dict(st.secrets["gcp_service_account"])
            cliente = gspread.service_account_from_dict(dados_secret)
        elif os.path.exists("credentials.json"):
            cliente = gspread.service_account(filename="credentials.json")
        else:
            return pd.DataFrame(), None

        planilha = cliente.open_by_key(SHEET_ID)
        alvo_norm = norm_txt(worksheet_name)
        aba = None

        # 1. Tenta match exato normalizado (ignora acento/cedilha/espaço)
        todas_abas = planilha.worksheets()
        for ws in todas_abas:
            if norm_txt(ws.title) == alvo_norm:
                aba = ws
                break

        # 2. Se não achar exato, tenta match parcial (ex: Preventiva_Inspeção_Core)
        if aba is None:
            termo_busca = alvo_norm.split("_")[0]
            for ws in todas_abas:
                if termo_busca and termo_busca in norm_txt(ws.title):
                    aba = ws
                    break

        if aba is None:
            return pd.DataFrame(), None

        linhas = aba.get_all_values()
        if not linhas:
            return pd.DataFrame(), None

        # 3. Resgata carimbo de atualização se estiver na Linha 1 ou na última coluna
        carimbo_att = None
        if len(linhas) > 0 and len(linhas[0]) >= 2:
            if "ATUALIZADO" in norm_txt(linhas[0][0]):
                carimbo_att = str(linhas[0][1]).strip()

        # 4. Localiza a linha do cabeçalho que contém a coluna_chave
        header_idx = -1
        chave_norm = norm_txt(coluna_chave)
        for i, row in enumerate(linhas[:10]):
            row_vals = [norm_txt(x) for x in row]
            if chave_norm in row_vals:
                header_idx = i
                break

        if header_idx != -1:
            cabecalho = [norm_txt(c) for c in linhas[header_idx]]
            dados = []
            for row in linhas[header_idx + 1:]:
                if not any(str(c).strip() for c in row):
                    continue
                if len(row) < len(cabecalho):
                    row = row + [""] * (len(cabecalho) - len(row))
                elif len(row) > len(cabecalho):
                    row = row[:len(cabecalho)]
                dados.append(row)

            df = pd.DataFrame(dados, columns=cabecalho)
            df = df.loc[:, df.columns != ""].reset_index(drop=True)

            # Se carimbo não estava na Linha 1, busca na coluna ULTIMA_ATUALIZACAO (linha 1 de dados)
            if not carimbo_att and "ULTIMA_ATUALIZACAO" in df.columns and not df.empty:
                carimbo_att = str(df.iloc[0]["ULTIMA_ATUALIZACAO"]).strip()

            return df, carimbo_att

    except Exception:
        pass

    return pd.DataFrame(), None


# ==============================================================================
# 📋 LEITURA BLINDADA DA PRANCHETA (COM GID DIRETO DA ABA)
# ==============================================================================
@st.cache_data(ttl=15)
def carregar_prancheta_direto():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=806839882"
    try:
        df = pd.read_csv(url, dtype=str, keep_default_na=False)
        return df
    except Exception:
        try:
            return carregar_dados_nuvem("Prancheta_Operacao_Core", cabecalho=0)
        except Exception:
            return pd.DataFrame()

def conectar_planilha_prancheta():
    try:
        if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
            dados_secret = dict(st.secrets["gcp_service_account"])
            cliente = gspread.service_account_from_dict(dados_secret)
            return cliente.open_by_key(SHEET_ID).worksheet("Prancheta_Operacao_Core")
        
        import os
        if os.path.exists("credentials.json"):
            cliente = gspread.service_account(filename="credentials.json")
            return cliente.open_by_key(SHEET_ID).worksheet("Prancheta_Operacao_Core")

        st.error("⚠️ Segredo [gcp_service_account] não localizado nos Secrets do Streamlit.")
        return None
    except Exception as e:
        st.error(f"⚠️ Erro ao autenticar no Google Sheets: {e}")
        return None

# ==============================================================================
# 🛠️ TELEMETRIA: LEITURA CIRÚRGICA DOS ÚLTIMOS LOGS DO CORE
# ==============================================================================
@st.cache_data(ttl=15)
def carregar_ultimos_logs_core(qtd_linhas=80):
    """Puxa apenas as últimas 80 linhas da aba Live_Logs_Core para carregar instantâneo no 4G."""
    try:
        import os
        if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
            dados_secret = dict(st.secrets["gcp_service_account"])
            cliente = gspread.service_account_from_dict(dados_secret)
        elif os.path.exists("credentials.json"):
            cliente = gspread.service_account(filename="credentials.json")
        else:
            return pd.DataFrame()

        planilha = cliente.open_by_key(SHEET_ID)
        aba = planilha.worksheet("Live_Logs_Core")
        
        # Pega o total de linhas preenchidas para puxar apenas o final sem ler 14.000 linhas
        total_linhas = len(aba.col_values(1))
        if total_linhas <= 1:
            return pd.DataFrame(columns=["DATA_HORA", "MODULO", "EVENTO"])
            
        linha_inicio = max(2, total_linhas - qtd_linhas)
        valores = aba.get_values(f"A{linha_inicio}:C{total_linhas}")
        
        df = pd.DataFrame(valores, columns=["DATA_HORA", "MODULO", "EVENTO"])
        return df.iloc[::-1].reset_index(drop=True)  # Inverte para o mais recente ficar no topo
    except Exception as e:
        return pd.DataFrame()

def parse_robusto(texto):
    if not texto or str(texto).strip() in ["", "None"]: return {}
    try: return json.loads(str(texto).strip())
    except:
        try: return ast.literal_eval(str(texto).strip())
        except: return {}

def descobrir_letras_turnos(data_alvo):
    data_referencia = date(2026, 9, 22)
    dias_passados = (data_alvo - data_referencia).days
    turnos = {"08_16": "C", "16_00": "B", "madrugada": "D"}
    for letra, dia in [("C", (0 + dias_passados) % 6), ("B", (2 + dias_passados) % 6), ("A", (4 + dias_passados) % 6)]:
        if dia in [0, 1]: turnos["08_16"] = letra
        elif dia in [2, 3]: turnos["16_00"] = letra
    return turnos

def classificar_kpi_mobile(valor, tipo):
    if valor == 0.0: return "#94a3b8"
    if tipo == "alvura": return "#E74C3C" if valor < 88.50 else ("#FFD600" if valor < 88.70 else "#00D672")
    if tipo == "sujidade": return "#E74C3C" if valor > 2.50 else ("#FFD600" if valor > 2.00 else "#00D672")
    if tipo == "viscosidade": return "#E74C3C" if valor < 650.0 else ("#FFD600" if valor < 680.0 else "#00D672")
    if tipo == "ph": return "#E74C3C" if valor > 0 and (valor < 5.50 or valor > 8.50) else ("#FFD600" if valor > 0 and ((5.50 <= valor < 6.00) or (8.00 < valor <= 8.50)) else "#00D672")
    return "#00D672"

# ==============================================================================
# 🚀 CARREGANDO TODOS OS DADOS DA NUVEM
# ==============================================================================
agora_br = datetime.utcnow() - timedelta(hours=4)
hoje_date = agora_br.date()
ontem_date = hoje_date - timedelta(days=1)

# ==============================================================================
# 🚀 CARREGANDO TODOS OS DADOS DA NUVEM (COM CACHE OTIMIZADO CONTRA ESTOURO 429)
# ==============================================================================
agora_br = datetime.utcnow() - timedelta(hours=4)
hoje_date = agora_br.date()
ontem_date = hoje_date - timedelta(days=1)

# Aumentamos o TTL para 60 segundos para respeitar o limite de requisições do Google Sheets
@st.cache_data(ttl=60)
def carregar_dados_mobile_otimizados():
    d_dash = carregar_dados_nuvem("Mobile_Dashboard", cabecalho=0)
    d_qual = carregar_dados_nuvem("Mobile_Qualidade", cabecalho=0)
    d_alert = carregar_dados_nuvem("Mobile_Alertas", cabecalho=0)
    d_cache = carregar_dados_nuvem("Cache_Painel", cabecalho=0)
    d_virada = carregar_dados_nuvem("Status_Virada_Turnos", cabecalho=0)
    d_baf = carregar_dados_nuvem("Bafometro_Status", cabecalho=0)
    if d_baf.empty:
        d_baf = carregar_dados_nuvem("Auditoria_Bafometro", cabecalho=0)
    d_frot = carregar_dados_nuvem("Historico_DKRO", cabecalho=0)
    d_bal, _ = carregar_tabela_cega("Balanco_Expedicao_Destino", "DESTINO")
    d_pat, h_pat = carregar_tabela_cega("Patio_Destino_Status", "DESTINO")
    d_tr, _ = carregar_tabela_cega("Status_TR", "PLACA")
    d_sinal, h_sinal = carregar_tabela_cega("Sinal_de_Vida", "APLICATIVO")
    d_prev, h_prev = carregar_tabela_cega("Preventiva_Inspecao", "TAG")
    d_pran = carregar_prancheta_direto()
    return d_dash, d_qual, d_alert, d_cache, d_virada, d_bal, d_baf, d_frot, d_pran, d_pat, h_pat, d_tr, d_sinal, h_sinal, d_prev, h_prev

df_dash, df_qual, df_alertas, df_cache, df_status_virada, df_balanco_dest, df_bafometro, df_frota, df_prancheta, df_patio_dest, hora_att_patio, df_status_tr, df_sinal_vida, hora_att_sinal, df_prev_insp, hora_att_prev = carregar_dados_mobile_otimizados()




cache_dict = {str(row.iloc[0]).strip(): str(row.iloc[1]).strip() for _, row in df_cache.iterrows()} if not df_cache.empty else {}
dados_segregados = parse_robusto(cache_dict.get("dados_segregados", "{}"))

# ==============================================================================
# ⚙️ PROCESSAMENTO: DASHBOARD & PREVISÕES
# ==============================================================================
ultima_att = None
vol_hoje = vol_ontem = prev_carr = prod_hoje_calc = prev_prod = estoque_total = 0
status_transbordo = ritmo_torre = "NORMAL"

if not df_dash.empty:
    df_dash.columns = [str(c).strip().upper() for c in df_dash.columns]
    row_d = df_dash.iloc[0]

    def pegar_val(chave_termo, padrao=0):
        for col_name in df_dash.columns:
            if chave_termo in col_name:
                return row_d.get(col_name, padrao)
        return padrao

    ultima_att = str(pegar_val("DATA_HORA", "")).strip() or None
    vol_hoje = forcar_par(safe_to_numeric(pegar_val("EXPEDICAO_HOJE", 0)))
    vol_ontem = forcar_par(safe_to_numeric(pegar_val("EXPEDICAO_ONTEM", 0)))
    prev_carr = forcar_par(safe_to_numeric(pegar_val("PREV_EXPEDICAO", 0)))
    prod_hoje_calc = forcar_par(safe_to_numeric(pegar_val("PRODUCAO_HOJE", 0)))
    prev_prod = forcar_par(safe_to_numeric(pegar_val("PREV_PRODUCAO", 0)))
    estoque_total = forcar_par(safe_to_numeric(pegar_val("ESTOQUE_TOTAL", 0)))
    status_transbordo = str(pegar_val("STATUS_TRANSBORDO", "NORMAL"))

    ritmo_torre_bruto = str(pegar_val("RITMO_TORRE", "NORMAL")).upper()
    ritmo_torre = "RITMO DE ATUALIZAÇÃO: RÁPIDO" if "12" in ritmo_torre_bruto or "ACELERADO" in ritmo_torre_bruto else ritmo_torre_bruto

if prev_prod == 0 and prod_hoje_calc > 0:
    horas_corridas = max(0.1, agora_br.hour + (agora_br.minute / 60.0))
    prev_prod = forcar_par((prod_hoje_calc / horas_corridas) * 24.0)

if prev_carr == 0 and vol_hoje > 0:
    horas_corridas = max(0.1, agora_br.hour + (agora_br.minute / 60.0))
    prev_carr = forcar_par((vol_hoje / horas_corridas) * 24.0)

try: dt_att = datetime.strptime(ultima_att[:19], "%d/%m/%Y %H:%M:%S")
except: dt_att = agora_br

minutos_inativos = (agora_br - dt_att).total_seconds() / 60.0

if minutos_inativos <= 15:
    conn_txt = "ATUALIZADO"
    conn_cor = "#00D672"
else:
    conn_txt = "DESATUALIZADO"
    conn_cor = "#E74C3C"

conn_hora = dt_att.strftime("%H:%M:%S") if dt_att.date() == hoje_date else dt_att.strftime("%d/%m %H:%M")

# ==============================================================================
# ⚙️ PROCESSAMENTO: PÁTIO (MATRIZ PATIO_DESTINO_STATUS + ABA STATUS_TR)
# ==============================================================================
mapa_status_colunas = [
    ("Prog/Chegando", "PR", "PR_VEIC", "PR_TON", "#38a9ff", "🚙"),
    ("Checklist", "00", "00_VEIC", "00_TON", "#FFD600", "📋"),
    ("Apoio", "01", "01_VEIC", "01_TON", "#E67E22", "🚛"),
    ("Fila de Carregamento", "FC", "FC_VEIC", "FC_TON", "#00D672", "✅"),
    ("Termo SAP", "TR", "TR_VEIC", "TR_TON", "#95A5A6", "📄")
]

dados_patio = {}
destinos_por_status = {}

if not df_patio_dest.empty:
    df_patio_dest.columns = [str(c).strip().upper() for c in df_patio_dest.columns]

for tit, chv, col_v, col_t, cor, ico in mapa_status_colunas:
    dest_list = []
    v_qtd = 0
    v_ton = 0

    if chv != "TR" and not df_patio_dest.empty and "DESTINO" in df_patio_dest.columns:
        for _, row in df_patio_dest.iterrows():
            d_nome = str(row.get("DESTINO", "")).strip()
            if not d_nome or "TOTAL" in d_nome.upper() or d_nome.upper() in ["NAN", "NONE"]:
                continue
                
            qtd_carretas = int(safe_to_numeric(row.get(col_v, 0)))
            toneladas = forcar_par(safe_to_numeric(row.get(col_t, 0)))

            if qtd_carretas > 0 or toneladas > 0:
                dest_list.append({
                    "destino": d_nome,
                    "veic": qtd_carretas,
                    "ton": toneladas
                })
    elif chv == "TR" and not df_status_tr.empty and "PLACA" in df_status_tr.columns:
        # Agrupa os veículos da aba Status_TR por Destino
        agr_tr = {}
        for _, r_tr in df_status_tr.iterrows():
            pl_tr = str(r_tr.get("PLACA", "")).strip()
            if not pl_tr or pl_tr.upper() in ["NAN", "NONE", "PLACA"]:
                continue
            d_tr = str(r_tr.get("DESTINO", "NÃO IDENTIFICADO")).strip()
            if not d_tr or d_tr.upper() in ["N/I", "NAN", ""]:
                d_tr = "EM ANÁLISE / N/I"
            t_tr = safe_to_numeric(r_tr.get("TONELADAS", 45.0))
            if t_tr <= 0: t_tr = 45.0
            if d_tr not in agr_tr:
                agr_tr[d_tr] = {"veic": 0, "ton": 0.0}
            agr_tr[d_tr]["veic"] += 1
            agr_tr[d_tr]["ton"] += t_tr
        for d_k, info_k in agr_tr.items():
            dest_list.append({
                "destino": d_k,
                "veic": info_k["veic"],
                "ton": forcar_par(info_k["ton"])
            })

    dest_list.sort(key=lambda x: x["veic"], reverse=True)
    
    if dest_list:
        v_qtd = sum(x["veic"] for x in dest_list)
        v_ton = forcar_par(sum(x["ton"] for x in dest_list))
    else:
        v_qtd = int(safe_to_numeric(pegar_val(col_v, 0))) if 'pegar_val' in locals() else 0
        v_ton = forcar_par(safe_to_numeric(pegar_val(col_t, 0))) if 'pegar_val' in locals() else 0

    dados_patio[chv] = {"veiculos": v_qtd, "peso": v_ton}
    destinos_por_status[chv] = dest_list

total_veiculos_fisicos = dados_patio["00"]["veiculos"] + dados_patio["01"]["veiculos"] + dados_patio["FC"]["veiculos"]
vol_patio_disponivel = forcar_par(dados_patio["00"]["peso"] + dados_patio["01"]["peso"] + dados_patio["FC"]["peso"])

# ==============================================================================
# ⚙️ PROCESSAMENTO: PRODUÇÃO & VIRADA
# ==============================================================================
viradas_info = {}
if not df_status_virada.empty:
    for _, row_st in df_status_virada.iterrows():
        linha = str(row_st.get("LINHA", "")).strip().upper()
        viradas_info[linha] = {
            "prox_mat": str(row_st.get("PROXIMO_MATERIAL", "--")),
            "prev_virada": str(row_st.get("PREVISAO_VIRADA", "--")),
            "saldo_rest": forcar_par(safe_to_numeric(row_st.get("SALDO_RESTANTE_T", row_st.get("SALDO_RESTANTE", 0)))),
            "status_email": str(row_st.get("STATUS_EMAIL_TROCA", "N/D"))
        }

qualidade_json = parse_robusto(cache_dict.get("qualidade", "{}"))

dados_maquinas = {"MS1": {}, "MS2": {}}
for m_nome in ["MS1", "MS2"]:
    q_m = qualidade_json.get(m_nome, qualidade_json.get(m_nome.lower(), {}))
    if isinstance(q_m, dict) and q_m:
        q_tipo = str(q_m.get("qualidade_tipo", "EQ")).strip().upper() or "EQ"
        dados_maquinas[m_nome] = {
            "material": str(q_m.get("material", "--")).strip(),
            "qualidade_tipo": q_tipo,
            "teor": safe_to_numeric(q_m.get("teor", 0)),
            "alvura": safe_to_numeric(q_m.get("alvura", 0)),
            "sujidade": safe_to_numeric(q_m.get("sujidade", 0)),
            "viscosidade": safe_to_numeric(q_m.get("viscosidade", 0)),
            "ph": safe_to_numeric(q_m.get("ph", 0)),
            "producao": forcar_par(safe_to_numeric(q_m.get("producao", 0))),
            "l1": forcar_par(safe_to_numeric(q_m.get("l1", 0))),
            "l2": forcar_par(safe_to_numeric(q_m.get("l2", 0))),
            "desclassificando": q_tipo in ["SQ", "OS", "BQ"]
        }

soma_prod_json = dados_maquinas["MS1"].get("producao", 0) + dados_maquinas["MS2"].get("producao", 0)
if soma_prod_json > 0:
    prod_hoje_calc = forcar_par(soma_prod_json)


# ==============================================================================
# ⚙️ PROCESSAMENTO: EXPEDIÇÃO (BALANÇO DESTINOS)
# ==============================================================================
balanco_destinos = []
total_expedicao_meta, total_expedicao_real = 0.0, 0.0

if not df_balanco_dest.empty:
    for _, r_b in df_balanco_dest.iterrows():
        dest_nome = str(r_b.get("DESTINO", "")).strip()
        if not dest_nome or dest_nome.upper() in ["NAN", "NONE", "DESTINO"]: continue

        meta_val = forcar_par(safe_to_numeric(r_b.get("META_DIA_T", 0)))
        real_val = forcar_par(safe_to_numeric(r_b.get("EXPEDIDO_ZLE_T", 0)))
        saldo_val = forcar_par(safe_to_numeric(r_b.get("SALDO_A_EXPEDIR_T", 0)))

        try: ating_val = float(str(r_b.get("ATINGIMENTO_%", 0)).replace('%', '').replace(',', '.'))
        except: ating_val = 0.0

        if "TOTAL" in dest_nome.upper():
            total_expedicao_meta, total_expedicao_real = meta_val, real_val
        else:
            balanco_destinos.append({
                "destino": dest_nome, "meta": meta_val, "realizado": real_val,
                "saldo": saldo_val, "atingimento": ating_val
            })

# (Splash Screen já renderizada instantaneamente no topo antes das consultas)


@st.cache_data(ttl=1800)
def obter_clima_tres_lagoas():
    """Busca clima atual + previsão horária (24h) + previsão diária (5 dias) para Três Lagoas - MS."""
    def mapear_wmo(code, is_day=1):
        if code == 0:
            return ("☀️" if is_day else "🌙"), "Céu Limpo"
        if code in [1, 2]:
            return ("⛅" if is_day else "☁️"), "Parcialmente Nublado"
        if code == 3:
            return "☁️", "Nublado"
        if code in [45, 48]:
            return "🌫️", "Neblina"
        if code in [51, 53, 55]:
            return "🌦️", "Garoa Leve"
        if code in [61, 63, 65, 80, 81, 82]:
            return "🌧️", "Pancadas de Chuva"
        if code in [95, 96, 99]:
            return "⛈️", "Trovoadas"
        return "⛅", "Estável"

    def dir_vento(deg):
        dirs = ["N", "NE", "L", "SE", "S", "SO", "O", "NO"]
        return dirs[int((float(deg) + 22.5) // 45) % 8]

    dias_pt = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

    try:
        url_w = (
            "https://api.open-meteo.com/v1/forecast?"
            "latitude=-20.7849&longitude=-51.7007"
            "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m,is_day"
            "&hourly=temperature_2m,precipitation_probability,weather_code,is_day"
            "&daily=weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset"
            "&timezone=America%2FCampo_Grande&forecast_days=5"
        )
        resp = requests.get(url_w, timeout=4).json()
        cur = resp.get("current", {})
        hourly = resp.get("hourly", {})
        daily = resp.get("daily", {})

        temp_atual = int(round(float(cur.get("temperature_2m", 0))))
        umid_atual = int(round(float(cur.get("relative_humidity_2m", 0))))
        vento_vel = int(round(float(cur.get("wind_speed_10m", 0))))
        vento_dir = dir_vento(cur.get("wind_direction_10m", 0))
        code_atual = int(cur.get("weather_code", 0))
        is_day = int(cur.get("is_day", 1))
        ico_atual, desc_atual = mapear_wmo(code_atual, is_day)

        sunrise_raw = (daily.get("sunrise") or [""])[0]
        sunset_raw = (daily.get("sunset") or [""])[0]
        nascer_sol = sunrise_raw.split("T")[1][:5] if "T" in sunrise_raw else "--:--"
        por_sol = sunset_raw.split("T")[1][:5] if "T" in sunset_raw else "--:--"

        # Processa próximas 24 horas a partir da hora atual de Três Lagoas (UTC-4)
        agora_tl = datetime.utcnow() - timedelta(hours=4)
        hora_chave_atual = agora_tl.strftime("%Y-%m-%dT%H:00")

        times_h = hourly.get("time", [])
        temps_h = hourly.get("temperature_2m", [])
        probs_h = hourly.get("precipitation_probability", [])
        codes_h = hourly.get("weather_code", [])
        isday_h = hourly.get("is_day", [])

        idx_ini_h = 0
        for idx_t, t_str in enumerate(times_h):
            if t_str >= hora_chave_atual:
                idx_ini_h = idx_t
                break

        previsao_24h = []
        for idx_h in range(idx_ini_h, min(len(times_h), idx_ini_h + 24)):
            t_raw = times_h[idx_h]
            hora_lbl = t_raw.split("T")[1][:5] if "T" in t_raw else t_raw[-5:]
            temp_h_v = int(round(float(temps_h[idx_h]))) if idx_h < len(temps_h) else 0
            prob_h_v = int(round(float(probs_h[idx_h] or 0))) if idx_h < len(probs_h) else 0
            code_h_v = int(codes_h[idx_h]) if idx_h < len(codes_h) else 0
            day_h_v = int(isday_h[idx_h]) if idx_h < len(isday_h) else 1
            ico_h, _ = mapear_wmo(code_h_v, day_h_v)

            previsao_24h.append({
                "hora": "Agora" if idx_h == idx_ini_h else hora_lbl,
                "is_agora": (idx_h == idx_ini_h),
                "ico": ico_h,
                "temp": f"{temp_h_v}°",
                "chuva": prob_h_v
            })

                # Processa 5 dias
        previsao_5d = []
        chuva_hoje = code_atual in [51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99] or any(h["chuva"] >= 45 for h in previsao_24h[:12])
        chuva_prox_dias = False
        datas_d = daily.get("time", [])
        codes_d = daily.get("weather_code", [])
        maxs_d = daily.get("temperature_2m_max", [])
        mins_d = daily.get("temperature_2m_min", [])

        for i in range(min(5, len(datas_d))):
            dt_obj = datetime.strptime(datas_d[i], "%Y-%m-%d")
            d_sem = dias_pt[dt_obj.weekday()]
            d_dm = dt_obj.strftime("%d/%m")
            c_d = int(codes_d[i]) if i < len(codes_d) else 0
            if c_d in [51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99]:
                if i == 0:
                    chuva_hoje = True
                else:
                    chuva_prox_dias = True
            ico_d, desc_d = mapear_wmo(c_d, 1)
            mx_d = int(round(float(maxs_d[i]))) if i < len(maxs_d) else 0
            mn_d = int(round(float(mins_d[i]))) if i < len(mins_d) else 0
            previsao_5d.append({
                "sem": d_sem, "dm": d_dm, "ico": ico_d,
                "max": f"{mx_d}°C", "min": f"{mn_d}°C", "desc": desc_d
            })

        # Régua Operacional Dinâmica (Prioridade: Chuva Hoje > Vento > Calor/Seco > Chuva Futura > Firme)
        if chuva_hoje:
            aviso_ico, aviso_cor = "🌧️", "#FF8C00"
            aviso_op = "Alerta pátio (Hoje): risco de chuva nas próximas horas — priorizar enlonamento e atenção ao piso."
        elif vento_vel >= 30:
            aviso_ico, aviso_cor = "💨", "#FF8C00"
            aviso_op = f"Atenção vento ({vento_vel} km/h {vento_dir}): rajadas no pátio — redobrar cuidado no enlonamento."
        elif temp_atual >= 34 or umid_atual <= 35:
            aviso_ico, aviso_cor = "☀️", "#FFD600"
            aviso_op = f"Calor intenso ({temp_atual}°C | Umid. {umid_atual}%): reforçar hidratação no pátio e atenção térmica na frota."
        elif chuva_prox_dias:
            aviso_ico, aviso_cor = "🌦️", "#38bdf8"
            aviso_op = "Tempo firme hoje; previsão de chuva nos próximos dias — acompanhar janela de embarque."
        else:
            aviso_ico, aviso_cor = "✅", "#00D672"
            aviso_op = "Tempo firme e estável em Três Lagoas — condições favoráveis para operação no pátio."

        return {
            "temp": f"{temp_atual}°C",
            "ico": ico_atual,
            "desc": desc_atual,
            "umid": f"{umid_atual}%",
            "vento": f"{vento_vel} km/h",
            "vento_dir": vento_dir,
            "nascer": nascer_sol,
            "por": por_sol,
            "horas": previsao_24h,
            "dias": previsao_5d,
            "aviso": aviso_op,
            "aviso_ico": aviso_ico,
            "aviso_cor": aviso_cor
        }
    except Exception:
        return {
            "temp": "--°C", "ico": "⛅", "desc": "Indisponível",
            "umid": "--%", "vento": "-- km/h", "vento_dir": "",
            "nascer": "--:--", "por": "--:--", "horas": [], "dias": [],
            "aviso": "Consulta meteorológica temporariamente indisponível.",
            "aviso_ico": "ℹ️", "aviso_cor": "#64748b"
        }


clima_tl = obter_clima_tres_lagoas()

dias_pt_topo = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
meses_pt_topo = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
data_topo_str = f"{dias_pt_topo[hoje_date.weekday()]}, {hoje_date.day:02d} de {meses_pt_topo[hoje_date.month - 1]}"

# Montagem dos Cards Por Horário (24h deslizável no dedo)
cards_24h_html = ""
for h_item in clima_tl["horas"]:
    borda_h = "1.5px solid #00D672" if h_item["is_agora"] else "1px solid #163252"
    bg_h = "linear-gradient(180deg, rgba(0,214,114,0.14) 0%, #070f1d 100%)" if h_item["is_agora"] else "#070f1d"
    cor_hora_txt = "#00D672" if h_item["is_agora"] else "#cbd5e1"
    cor_chuva = "#38bdf8" if h_item["chuva"] >= 35 else "#64748b"

    cards_24h_html += f"""
    <div style="flex:0 0 58px; background:{bg_h}; border:{borda_h}; border-radius:10px; padding:7px 4px; text-align:center;">
        <div style="font-size:0.64rem; font-weight:800; color:{cor_hora_txt};">{h_item['hora']}</div>
        <div style="font-size:1.15rem; margin:4px 0;">{h_item['ico']}</div>
        <div style="font-size:0.80rem; font-weight:900; color:#ffffff;">{h_item['temp']}</div>
        <div style="font-size:0.58rem; font-weight:700; color:{cor_chuva}; margin-top:3px;">💧{h_item['chuva']}%</div>
    </div>
    """

if not cards_24h_html:
    cards_24h_html = '<div style="color:#94a3b8; font-size:0.75rem; padding:12px; text-align:center; width:100%;">Previsão horária indisponível no momento.</div>'

# Montagem dos Cards Por Dia (5 Dias)
cards_5d_html = ""
for d_item in clima_tl["dias"]:
    cards_5d_html += f"""
    <div style="flex:1; min-width:0; background:#070f1d; border:1px solid #163252; border-radius:10px; padding:7px 3px; text-align:center;">
        <div style="font-size:0.68rem; font-weight:800; color:#ffffff;">{d_item['sem']}</div>
        <div style="font-size:0.56rem; color:#94a3b8; margin-bottom:4px;">{d_item['dm']}</div>
        <div style="font-size:1.15rem; margin:2px 0;">{d_item['ico']}</div>
        <div style="font-size:0.74rem; font-weight:900; color:#ffffff; margin-top:3px;">{d_item['max']}</div>
        <div style="font-size:0.66rem; font-weight:800; color:#38bdf8;">{d_item['min']}</div>
        <div style="font-size:0.50rem; color:#94a3b8; margin-top:3px; line-height:1.15;">{html_lib.escape(d_item['desc'])}</div>
    </div>
    """

if not cards_5d_html:
    cards_5d_html = '<div style="color:#94a3b8; font-size:0.75rem; padding:12px; text-align:center; width:100%;">Previsão estendida indisponível no momento.</div>'

# 1. Banner Oficial Persistente no Topo (Arredondado + Neon Verde)
st.markdown(f'<div id="sec-topo"></div><div class="topo-banner-mask"></div><div class="topo-banner"><img src="{BANNER_TOPO_URL}"></div>', unsafe_allow_html=True)

# 1.5 Botão Flutuante com Ícone Oficial A.L.O.V.E. (Renderizado no topo p/ abrir instantâneo no Android)
html_fab_topo = f"""
<div class="fab-container">
    <details class="fab-details" id="fabMenuDetails">
        <summary title="Atalhos Rápidos"><img src="{LOGO_ALOVE_URL}" alt="A.L.O.V.E."></summary>
        <div class="fab-menu">
            <a href="#sec-topo" onclick="this.closest('details').removeAttribute('open')">⬆️ Topo & Clima</a>
            <a href="#sec-prev" onclick="this.closest('details').removeAttribute('open')">📅 Previsões do Dia</a>
            <a href="#sec-prod" onclick="this.closest('details').removeAttribute('open')">🏭 Produção Celulose</a>
            <a href="#sec-est" onclick="this.closest('details').removeAttribute('open')">📦 Estoque Armazém</a>
            <a href="#sec-exp" onclick="this.closest('details').removeAttribute('open')">🚚 Expedição Realizada</a>
            <a href="#sec-ped" onclick="this.closest('details').removeAttribute('open')">📑 Pedidos ZLE087</a>
            <a href="#sec-patio" onclick="this.closest('details').removeAttribute('open')">🚛 Pátio da Fábrica</a>
            <a href="#sec-frota" onclick="this.closest('details').removeAttribute('open')">🚜 Frota & Equipamentos</a>
            <a href="#sec-manut" onclick="this.closest('details').removeAttribute('open')">🔧 Preventiva & Inspeção</a>
            <a href="#sec-glp" onclick="this.closest('details').removeAttribute('open')">⛽ Consumo de GLP</a>
            <a href="#sec-baf" onclick="this.closest('details').removeAttribute('open')">🩺 Auditoria Bafômetro</a>
            <a href="#print-seletor" class="fab-print-link" onclick="this.closest('details').removeAttribute('open')">📸 Print de Bloco</a>
        </div>
    </details>
</div>
"""
render_html(html_fab_topo)

# 2. Faixa Fina Expansível de Clima com Pílulas (Por Horário vs Por Dia)
html_clima_barra = f"""
<style>
    .clm-wrapper input[type="radio"] {{ display: none !important; }}

    details.clima-strip > summary .clm-chev {{
        transition: transform 0.25s ease;
        display: inline-block;
    }}
    details.clima-strip[open] > summary .clm-chev {{
        transform: rotate(180deg);
    }}

    /* Pílulas de Seleção: Por Horário vs Por Dia */
    .clm-pill-bar {{
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-bottom: 10px;
    }}
    .clm-pill-bar label {{
        flex: 1;
        text-align: center;
        padding: 7px 8px;
        font-size: 0.74rem;
        font-weight: 800;
        color: #94a3b8;
        background: #070f1d;
        border: 1.5px solid #163252;
        border-radius: 999px;
        cursor: pointer;
        transition: all 0.2s ease;
        white-space: nowrap;
        -webkit-tap-highlight-color: transparent;
    }}
    #tab_clm_hora:checked ~ details .lbl-clm-hora {{
        background: #00D672 !important;
        color: #050911 !important;
        border-color: #00D672 !important;
        box-shadow: 0 0 10px rgba(0, 214, 114, 0.38);
    }}
    #tab_clm_dia:checked ~ details .lbl-clm-dia {{
        background: #38bdf8 !important;
        color: #050911 !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.38);
    }}

    .clm-view-hora, .clm-view-dia {{ display: none; }}
    #tab_clm_hora:checked ~ details .clm-view-hora {{ display: block; }}
    #tab_clm_dia:checked ~ details .clm-view-dia {{ display: block; }}
</style>

<div class="clm-wrapper" style="margin-bottom:12px; border:1.5px solid #00D672; border-radius:13px; background:linear-gradient(180deg, #0b1c33 0%, #070f1d 100%); box-shadow:0 0 14px rgba(0, 214, 114, 0.16); overflow:hidden;">
    <input type="radio" name="clm_view" id="tab_clm_hora" checked>
    <input type="radio" name="clm_view" id="tab_clm_dia">

    <details class="clima-strip" style="border:none; background:transparent;">
        <summary style="list-style:none; cursor:pointer; padding:8px 12px; display:flex; align-items:center; justify-content:space-between; gap:8px; outline:none; -webkit-tap-highlight-color:transparent;">
            <div style="display:flex; align-items:center; gap:7px; min-width:0;">
                <span style="font-size:0.85rem;">📍</span>
                <span style="color:#ffffff; font-size:0.78rem; font-weight:800; white-space:nowrap;">Três Lagoas - MS</span>
                <span style="color:#64748b; font-size:0.72rem; font-weight:600; white-space:nowrap;">• {data_topo_str}</span>
            </div>
            <div style="display:flex; align-items:center; gap:8px; flex-shrink:0;">
                <span style="font-size:1.05rem;">{clima_tl['ico']}</span>
                <span style="color:#00D672; font-size:0.88rem; font-weight:900; font-family:monospace;">{clima_tl['temp']}</span>
                <span class="clm-chev" style="color:#00D672; font-size:0.70rem; padding-left:2px;">▼</span>
            </div>
        </summary>

        <div style="padding:10px 12px 12px 12px; border-top:1px solid #163252;">
            <!-- PAINEL ATUAL -->
            <div style="display:flex; align-items:center; justify-content:space-between; gap:8px; background:rgba(5,9,17,0.75); border:1px solid #163252; border-radius:12px; padding:10px; margin-bottom:10px;">
                <div style="display:flex; align-items:center; gap:8px; padding-right:10px; border-right:1px solid #163252;">
                    <span style="font-size:2.1rem;">{clima_tl['ico']}</span>
                    <div>
                        <div style="font-size:1.75rem; font-weight:900; color:#ffffff; line-height:1;">{clima_tl['temp']}</div>
                        <div style="font-size:0.65rem; color:#cbd5e1; margin-top:3px; font-weight:600;">{html_lib.escape(clima_tl['desc'])}</div>
                    </div>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:7px 10px; flex:1;">
                    <div style="display:flex; align-items:center; gap:5px;">
                        <span style="font-size:0.85rem;">💧</span>
                        <div>
                            <div style="font-size:0.56rem; color:#94a3b8;">Umidade</div>
                            <div style="font-size:0.72rem; color:#ffffff; font-weight:800;">{clima_tl['umid']}</div>
                        </div>
                    </div>
                    <div style="display:flex; align-items:center; gap:5px;">
                        <span style="font-size:0.85rem;">💨</span>
                        <div>
                            <div style="font-size:0.56rem; color:#94a3b8;">Vento</div>
                            <div style="font-size:0.72rem; color:#ffffff; font-weight:800;">{clima_tl['vento']} <span style="color:#00D672; font-size:0.60rem;">{clima_tl['vento_dir']}</span></div>
                        </div>
                    </div>
                    <div style="display:flex; align-items:center; gap:5px;">
                        <span style="font-size:0.85rem;">🌅</span>
                        <div>
                            <div style="font-size:0.56rem; color:#94a3b8;">Nascer do Sol</div>
                            <div style="font-size:0.72rem; color:#ffffff; font-weight:800;">{clima_tl['nascer']}</div>
                        </div>
                    </div>
                    <div style="display:flex; align-items:center; gap:5px;">
                        <span style="font-size:0.85rem;">🌇</span>
                        <div>
                            <div style="font-size:0.56rem; color:#94a3b8;">Pôr do Sol</div>
                            <div style="font-size:0.72rem; color:#ffffff; font-weight:800;">{clima_tl['por']}</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- PÍLULAS DE ALTERNÂNCIA -->
            <div class="clm-pill-bar">
                <label for="tab_clm_hora" class="lbl-clm-hora">⏰ Por Horário (24h)</label>
                <label for="tab_clm_dia" class="lbl-clm-dia">📅 Por Dia (5 Dias)</label>
            </div>

            <!-- VISÃO 1: POR HORÁRIO (DESLIZE HORIZONTAL) -->
            <div class="clm-view-hora">
                <div style="display:flex; gap:6px; overflow-x:auto; padding-bottom:4px; margin-bottom:7px; -webkit-overflow-scrolling:touch;">
                    {cards_24h_html}
                </div>
            </div>

            <!-- VISÃO 2: POR DIA (5 DIAS) -->
            <div class="clm-view-dia">
                <div style="display:flex; gap:5px; margin-bottom:9px;">
                    {cards_5d_html}
                </div>
            </div>

            <!-- RODAPÉ DE ALERTA OPERACIONAL DINÂMICO -->
            <div style="display:flex; align-items:center; justify-content:space-between; gap:9px; background:#050911; border:1px solid #163252; border-left:3.5px solid {clima_tl['aviso_cor']}; border-radius:10px; padding:8px 10px;">
                <span style="font-size:1.05rem; flex-shrink:0;">{clima_tl['aviso_ico']}</span>
                <div style="font-size:0.64rem; color:#e2e8f0; line-height:1.3; flex:1;">{html_lib.escape(clima_tl['aviso'])}</div>
                <div style="font-size:0.68rem; font-weight:800; color:#00D672; text-align:right; line-height:1.05; flex-shrink:0;">Eldorado<br><span style="color:#94a3b8; font-size:0.56rem;">Brasil</span></div>
            </div>

        </div>
    </details>
</div>
"""
render_html(html_clima_barra)





# ==============================================================================
# 🖨️ RENDERIZAÇÃO 1: STATUS DO SISTEMA (NOC TELEMETRY - SEMPRE FECHADO AO ABRIR)
# ==============================================================================
modulos_config = [
    {"chave": "CORE",  "nome": "CORE",  "sub": "Motor SAP",    "ico": "🤖", "status": "OFFLINE", "pulso": "--:--", "diag": "Sem comunicação com o motor SAP"},
    {"chave": "TORRE", "nome": "TORRE", "sub": "Controle YMS", "ico": "📡", "status": "OFFLINE", "pulso": "--:--", "diag": "Painel do assistente sem sinal"},
    {"chave": "TOTEM", "nome": "TOTEM", "sub": "Autoatend.",   "ico": "📱", "status": "OFFLINE", "pulso": "--:--", "diag": "Totem sem sinal ou desligado"},
    {"chave": "TV",    "nome": "TV",    "sub": "Painel Pátio", "ico": "📺", "status": "OFFLINE", "pulso": "--:--", "diag": "TV sem resposta na rede"},
]

sinal_expirado = False
hora_sinal_exibir = conn_hora
if hora_att_sinal:
    try:
        dt_sinal = datetime.strptime(hora_att_sinal[:19], "%d/%m/%Y %H:%M:%S")
        hora_sinal_exibir = dt_sinal.strftime("%H:%M:%S") if dt_sinal.date() == hoje_date else dt_sinal.strftime("%d/%m %H:%M")
        if (agora_br - dt_sinal).total_seconds() / 60.0 > 20:
            sinal_expirado = True
    except Exception:
        pass

if not df_sinal_vida.empty and "APLICATIVO" in df_sinal_vida.columns:
    for _, rs in df_sinal_vida.iterrows():
        app_nome = str(rs.get("APLICATIVO", "")).strip().upper()
        st_app = str(rs.get("STATUS", "OFFLINE")).strip().upper()
        pulso_app = str(rs.get("ÚLTIMO_PULSO", rs.get("ULTIMO_PULSO", "--:--"))).strip() or "--:--"
        diag_raw = str(rs.get("DIAGNÓSTICO", rs.get("DIAGNOSTICO", ""))).strip()
        diag_limpo = re.sub(r'^[🟢🔴🟡⚠️✅❌\s]+', '', diag_raw).strip()

        for mod in modulos_config:
            if mod["chave"] in app_nome:
                if sinal_expirado:
                    mod["status"] = "OFFLINE"
                    mod["pulso"] = pulso_app
                    mod["diag"] = f"Pulso congelado desde {hora_sinal_exibir}"
                else:
                    mod["status"] = "ONLINE" if "ONLINE" in st_app else "OFFLINE"
                    mod["pulso"] = pulso_app
                    if diag_limpo:
                        mod["diag"] = diag_limpo

qtd_online = sum(1 for m in modulos_config if m["status"] == "ONLINE")
if sinal_expirado or qtd_online == 0:
    st_geral_txt, st_geral_cor = "SISTEMA OFFLINE", "#E74C3C"
elif qtd_online < 4:
    st_geral_txt, st_geral_cor = f"OPERAÇÃO PARCIAL ({qtd_online}/4)", "#FFD600"
else:
    st_geral_txt, st_geral_cor = "SISTEMA 100% ONLINE", "#00D672"

barra_saude_html = ""
cards_noc_html = ""

for mod in modulos_config:
    is_on = mod["status"] == "ONLINE"
    c_main = "#00D672" if is_on else "#E74C3C"
    c_glow = "rgba(0, 214, 114, 0.22)" if is_on else "rgba(231, 76, 60, 0.12)"
    bg_card = "linear-gradient(180deg, rgba(0,214,114,0.09) 0%, #070d18 100%)" if is_on else "linear-gradient(180deg, rgba(231,76,60,0.07) 0%, #070d18 100%)"
    borda_card = "#00D672" if is_on else "#261924"

    # Segmento da barra superior (visível com o card fechado)
    barra_saude_html += f"""
    <div style="flex:1; background:#060b14; border:1px solid {borda_card}; border-radius:8px; padding:6px 4px; text-align:center;">
        <div style="height:4px; border-radius:999px; background:{c_main}; box-shadow:0 0 8px {c_main}; margin-bottom:5px;"></div>
        <div style="color:{'#ffffff' if is_on else '#64748b'}; font-size:0.68rem; font-weight:800; letter-spacing:0.4px;">{mod['nome']}</div>
    </div>
    """

    # Card detalhado (visível quando você toca para abrir)
    cards_noc_html += f"""
    <div style="background:{bg_card}; border:1.5px solid {borda_card}; border-radius:14px; padding:12px; box-shadow:0 4px 14px {c_glow}; display:flex; flex-direction:column; justify-content:space-between; gap:8px;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div style="display:flex; align-items:center; gap:8px;">
                <div style="width:32px; height:32px; border-radius:9px; background:#0b1526; border:1px solid {borda_card}; display:flex; align-items:center; justify-content:center; font-size:1.05rem;">
                    {mod['ico']}
                </div>
                <div>
                    <div style="color:#ffffff; font-size:0.84rem; font-weight:800; line-height:1.1;">{mod['nome']}</div>
                    <div style="color:#64748b; font-size:0.65rem; font-weight:600;">{mod['sub']}</div>
                </div>
            </div>
            <span style="width:9px; height:9px; border-radius:50%; background:{c_main}; box-shadow:0 0 8px {c_main}; margin-top:3px;"></span>
        </div>

        <div style="color:#cbd5e1; font-size:0.72rem; line-height:1.25; min-height:28px;">
            {html_lib.escape(mod['diag'])}
        </div>

        <div style="border-top:1px solid #14243b; padding-top:6px; display:flex; justify-content:space-between; align-items:center;">
            <span style="color:{c_main}; font-size:0.65rem; font-weight:800; letter-spacing:0.4px;">{mod['status']}</span>
            <span style="color:#e2e8f0; font-family:monospace; font-size:0.74rem; font-weight:700;">🕒 {html_lib.escape(mod['pulso'])}</span>
        </div>
    </div>
    """

html_status_sistema = f"""
<style>
    details.noc-box > summary .noc-chev {{
        transition: transform 0.25s ease;
        display: inline-block;
    }}
    details.noc-box[open] > summary .noc-chev {{
        transform: rotate(180deg);
    }}
</style>
<div class="card-main" style="margin-bottom: 14px; padding: 14px 15px; border: 1.5px solid #163252; border-radius: 16px; background: linear-gradient(180deg, #0d1d38 0%, #070d18 100%); box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);">
    <details class="noc-box" style="border: none; background: transparent;">
        <summary style="list-style: none; cursor: pointer; outline: none; -webkit-tap-highlight-color: transparent;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 36px; height: 36px; border-radius: 10px; background: rgba(0, 180, 255, 0.12); border: 1px solid #00b4ff; display: flex; align-items: center; justify-content: center; font-size: 1.15rem; box-shadow: 0 0 12px rgba(0, 180, 255, 0.2);">
                        🛡️
                    </div>
                    <div>
                        <div style="color: #ffffff; font-size: 0.92rem; font-weight: 800; letter-spacing: 0.5px;">TELEMETRIA DO ECOSSISTEMA</div>
                        <div style="color: {st_geral_cor}; font-size: 0.76rem; font-weight: 800; margin-top: 2px;">
                            ● {st_geral_txt} <span style="color: #64748b; font-weight: 500;">• {hora_sinal_exibir}</span>
                        </div>
                    </div>
                </div>

                <div style="display: flex; align-items: center; gap: 8px;">
                    <a href="?refresh=1" target="_self" onclick="event.stopPropagation(); document.body.insertAdjacentHTML('beforeend', '<div style=\'position:fixed;inset:0;background:#050911;z-index:99999999;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:10px;\'><div style=\'font-size:2.8rem;font-weight:900;color:#00D672;letter-spacing:6px;text-shadow:0 0 20px rgba(0,214,114,0.6);\'>A.L.O.V.E</div><div style=\'font-size:0.82rem;font-weight:700;color:#94a3b8;letter-spacing:2.2px;text-transform:uppercase;\'>Assistente Virtual da Expedição</div></div>');" 
                       style="width: 38px; height: 38px; border: 1.5px solid #00b4ff; border-radius: 10px; background: #070d18; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; color: #ffffff; text-decoration: none; box-shadow: 0 0 10px rgba(0, 180, 255, 0.25);">
                       🔄
                    </a>

                    <span class="noc-chev" style="color: #64748b; font-size: 0.8rem; padding: 4px;">▼</span>
                </div>
            </div>

            <!-- BARRA DE INTEGRIDADE DOS 4 PILARES (VISÍVEL MESMO FECHADO) -->
            <div style="display: flex; gap: 6px;">
                {barra_saude_html}
            </div>
        </summary>

        <!-- PAINEL EXPANDIDO 2x2 -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 12px; padding-top: 12px; border-top: 1px solid #163252;">
            {cards_noc_html}
        </div>
        <div style="margin-top: 10px; text-align: center; font-size: 0.68rem; color: #64748b;">
            Fonte: <b style="color: #94a3b8;">A.L.O.V.E Core</b> • Toque no cabeçalho para recolher
        </div>
    </details>
</div>
"""
render_html(html_status_sistema)


# ==============================================================================
# 🖨️ RENDERIZAÇÃO 2: AVISOS & PRANCHETA (COM BOTÕES IDÊNTICOS À FOTO 3)
# ==============================================================================
# 1. Processamento das Notificações
alertas_lista = []
if not df_alertas.empty:
    for _, ra in df_alertas.iterrows():
        nivel = str(ra.get("NIVEL", "")).strip().upper()
        texto = str(ra.get("ALERTA", "")).strip()
        if not texto or texto.lower() == "nan": continue
        dh = str(ra.get("DATA_HORA", "")).strip()
        hora = dh.split(" ")[1][:5] if " " in dh else "--:--"
        texto_limpo = re.sub(r'^[^\w\[\(]+', '', texto)
        alertas_lista.append((nivel, texto_limpo, hora))

ordem_nivel = {"CRITICO": 0, "ATENCAO": 1, "NORMAL": 2}
alertas_lista.sort(key=lambda a: ordem_nivel.get(a[0], 3))

ESTILO_NIVEL = {
    "CRITICO": ("#E74C3C", "rgba(231,76,60,.18)", "🚨", "Alerta crítico"),
    "ATENCAO": ("#FFD600", "rgba(255,214,0,.16)", "⚠️", "Atenção"),
    "NORMAL":  ("#00D672", "rgba(0,214,114,.16)", "✅", "Operação normal"),
}

def render_notif(nivel, texto, hora):
    cor, bg, ico, titulo = ESTILO_NIVEL.get(nivel, ESTILO_NIVEL["ATENCAO"])
    return (
        f'<div class="notif-item">'
        f'<div class="notif-ico" style="background:{bg}; color:{cor};">{ico}</div>'
        f'<div class="notif-txt"><div class="notif-tit">{titulo}</div><div class="notif-desc">{html_lib.escape(texto)}</div></div>'
        f'<div class="notif-hora">{hora}<i style="background:{cor};"></i></div>'
        f'</div>'
    )

conteudo_notifs = "".join(render_notif(*a) for a in alertas_lista) if alertas_lista else '<div style="color:#64748b; font-size:0.82rem; padding:12px; text-align:center;">Nenhuma notificação ativa no momento.</div>'
total_notifs = len(alertas_lista)

# 2. Processamento da Prancheta Operacional
recados_mobile = []
if not df_prancheta.empty:
    for idx_df, rp in df_prancheta.iterrows():
        linha_sheets = idx_df + 2
        valores_linha = [str(x).strip() for x in rp.tolist()]
        if not any(valores_linha): continue

        msg_val, aut_val, st_val = "", "Cristiano", "ATIVO"
        if len(valores_linha) >= 1:
            msg_val = valores_linha[0]
        if len(valores_linha) >= 2:
            aut_val = valores_linha[1]
        recados_mobile.append({"msg": msg_val, "autor": aut_val, "linha": linha_sheets})



                    
# ==============================================================================
# 🖨️ RENDERIZAÇÃO 3.5: PREVISÕES DO DIA (PRODUÇÃO & CARREGAMENTO)
# ==============================================================================
html_previsoes = f"""
<div id="sec-prev"></div>
<div class="card-main" style="margin-bottom: 14px;">
    <div class="card-head" style="margin-bottom: 10px;">
        <div class="icon-sq" style="background: rgba(0, 180, 255, 0.15); border-color: #00b4ff;">📅</div>
        <div class="card-title">Previsões do Dia</div>
        <div class="badge-novas" style="color: #00D672; border-color: #00D672;">24 Horas</div>
    </div>
    <div class="kpi-duo">
        <div class="kpi-box">
            <div class="kpi-ico">🏭</div>
            <div>
                <div class="kpi-big">{fmt(prev_prod)} <span>t</span></div>
                <div class="kpi-lbl">Prev. Produção</div>
                <div class="kpi-sub">Projeção 24h</div>
            </div>
        </div>
        <div class="kpi-sep"></div>
        <div class="kpi-box">
            <div class="kpi-ico">🚚</div>
            <div>
                <div class="kpi-big verde">{fmt(prev_carr)} <span>t</span></div>
                <div class="kpi-lbl">Prev. Carregamento</div>
                <div class="kpi-sub">Projeção 24h</div>
            </div>
        </div>
    </div>
</div>
"""
render_html(html_previsoes)

# ==============================================================================
# 🖨️ RENDERIZAÇÃO 4: PRODUÇÃO DE CELULOSE (CLASSE EQ/SQ/OS REFLETIDA NO CARD)
# ==============================================================================
html_prod_content = ""
for maq in ["MS1", "MS2"]:
    q_dados = dados_maquinas.get(maq, {})
    if q_dados:
        mat_maq = q_dados.get("material", "--")
        q_tipo = q_dados.get("qualidade_tipo", "EQ")
        p_maq = q_dados.get("producao", 0)
        q_suj = q_dados.get('sujidade', 0.0)
        q_visc = q_dados.get('viscosidade', 0.0)
        q_alvura = q_dados.get('alvura', 0.0)
        q_ph = q_dados.get('ph', 0.0)
        l1 = q_dados.get('l1', 0)
        l2 = q_dados.get('l2', 0)

        c_alv = classificar_kpi_mobile(q_alvura, "alvura")
        c_suj = classificar_kpi_mobile(q_suj, "sujidade")
        c_vis = classificar_kpi_mobile(q_visc, "viscosidade")
        c_ph = classificar_kpi_mobile(q_ph, "ph")

        # Cor da máquina e da pílula guiada pela classificação real da linha 6 (EQ / SQ / OS)
        if q_tipo in ["OS", "BQ"]:
            cor_status_maq = "#E74C3C"
            bg_pill_tipo = "rgba(231, 76, 60, 0.18)"
            led_status = "🔴"
        elif q_tipo == "SQ":
            cor_status_maq = "#FFD600"
            bg_pill_tipo = "rgba(255, 214, 0, 0.18)"
            led_status = "🟡"
        else:
            cor_status_maq = "#00D672"
            bg_pill_tipo = "rgba(0, 214, 114, 0.18)"
            led_status = "🟢"

        lbl_l1 = "Linha A" if maq == "MS1" else "Linha C"
        lbl_l2 = "Linha B" if maq == "MS1" else "Linha D"

        info_v = viradas_info.get(maq, {})
        p_mat = info_v.get("prox_mat", "--") if info_v else "--"
        p_prev = info_v.get("prev_virada", "--") if info_v else "--"

        html_prod_content += f"""
        <div style="background-color: #0c1524; border: 1.5px solid #1c2b42; border-left: 5px solid {cor_status_maq}; border-radius: 14px; padding: 14px 16px; margin-bottom: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.25);">
            <!-- TOPO: IDENTIFICAÇÃO, MATERIAL + CLASSE E LINHAS -->
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <!-- LADO ESQUERDO: MÁQUINA + MAT + CLASSE (EQ/SQ/OS) -->
                <div style="display:flex; flex-direction:column; gap:5px;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="color:#ffffff; font-weight:800; font-size:1.15rem; letter-spacing:0.3px;">⚙️ {maq}</span>
                        <span style="font-size:0.95rem;">{led_status}</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
                        <span style="color:#FF9F1C; font-weight:800; font-size:1.02rem;">📦 MAT: {mat_maq}</span>
                        <span style="background:{bg_pill_tipo}; color:{cor_status_maq}; border:1px solid {cor_status_maq}; font-size:0.72rem; font-weight:900; padding:1px 7px; border-radius:6px; letter-spacing:0.5px;">{q_tipo}</span>
                    </div>
                </div>

                <!-- LADO DIREITO: LINHAS INDIVIDUAIS COM BARRA VERTICAL -->
                <div style="display:flex; flex-direction:column; gap:4px; border-left:2.5px solid {cor_status_maq}; padding-left:10px;">
                    <div style="font-size:0.92rem; color:#ffffff;">
                        <span style="color:{cor_status_maq}; font-size:0.75rem;">●</span> <b>{lbl_l1}:</b> <span style="color:#38bdf8; font-weight:bold; margin-left:4px;">{fmt(l1)} t</span>
                    </div>
                    <div style="font-size:0.92rem; color:#ffffff;">
                        <span style="color:{cor_status_maq}; font-size:0.75rem;">●</span> <b>{lbl_l2}:</b> <span style="color:#38bdf8; font-weight:bold; margin-left:4px;">{fmt(l2)} t</span>
                    </div>
                </div>
            </div>

            <!-- MEIO: PARÂMETROS LABORATORIAIS / QUALIDADE -->
            <div style="display:flex; justify-content:space-between; text-align:center; border-top:1px dashed #1c2b42; padding-top:12px; margin-bottom:10px;">
                <div>
                    <div style="font-size:0.68rem; color:#64748b; font-weight:700; letter-spacing:0.4px;">ALVURA</div>
                    <div style="font-size:1.15rem; font-weight:800; color:{c_alv}; margin:2px 0;">{fmt(q_alvura, 2)}%</div>
                    <div style="font-size:0.65rem; color:#475569;">(Mín: 88,5)</div>
                </div>
                <div>
                    <div style="font-size:0.68rem; color:#64748b; font-weight:700; letter-spacing:0.4px;">SUJIDADE</div>
                    <div style="font-size:1.15rem; font-weight:800; color:{c_suj}; margin:2px 0;">{fmt(q_suj, 2)}</div>
                    <div style="font-size:0.65rem; color:#475569;">(Máx: 2,5)</div>
                </div>
                <div>
                    <div style="font-size:0.68rem; color:#64748b; font-weight:700; letter-spacing:0.4px;">VISCOSID.</div>
                    <div style="font-size:1.15rem; font-weight:800; color:{c_vis}; margin:2px 0;">{fmt(q_visc)}</div>
                    <div style="font-size:0.65rem; color:#475569;">(Mín: 650)</div>
                </div>
                <div>
                    <div style="font-size:0.68rem; color:#64748b; font-weight:700; letter-spacing:0.4px;">pH</div>
                    <div style="font-size:1.15rem; font-weight:800; color:{c_ph}; margin:2px 0;">{fmt(q_ph, 1)}</div>
                    <div style="font-size:0.65rem; color:#475569;">(5,5 - 8,5)</div>
                </div>
            </div>

            <!-- RODAPÉ COMPACTO: PREVISÃO DE VIRADA -->
            <div style="border-top:1px solid #14243b; padding-top:8px; text-align:center; font-size:0.8rem; color:#94a3b8;">
                PROX MAT: <b style="color:#ffffff;">{p_mat}</b> &nbsp;|&nbsp; PREV: <b style="color:#ffffff;">{p_prev}</b>
            </div>
        </div>
        """
    else:
        html_prod_content += f"<div style='color:gray; padding:10px 0;'>Aguardando dados da {maq}...</div>"

html_prod_completo = f"""
<div id="sec-prod"></div>
<details class="master-box" style="border-left-color: #E5B800;">
    <summary>
        <div class="header-layout">
            <div class="icon-box" style="background-color: rgba(229, 184, 0, 0.15); color: #E5B800;">🏭</div>
            <div class="master-metric-title">Produção de Celulose</div>
        </div>
        <div class="value-layout">
            <div class="master-metric-val">{fmt(prod_hoje_calc)}</div>
            <div class="master-metric-unit">TON</div>
        </div>
        <div class="master-metric-sub" style="color: #E5B800;">MS1: {fmt(dados_maquinas['MS1'].get('producao', 0))} t | MS2: {fmt(dados_maquinas['MS2'].get('producao', 0))} t</div>
        <div class="master-metric-sub" style="color: #64748b;">Prev. Fechamento: {fmt(prev_prod)} t</div>
    </summary>
    <div class="master-content" style="padding-top:16px;">
        {html_prod_content}
    </div>
</details>
"""
render_html(html_prod_completo)


# ==============================================================================
# 🖨️ RENDERIZAÇÃO 5: ESTOQUE FÍSICO (TABELA ABERTA + RODAPÉ ON-GRADE VS OFF-GRADE)
# ==============================================================================
CAPACIDADE_MAX_ARMAZEM = 25000.0

raw_seg_str = str(cache_dict.get("dados_segregados", "{}")).strip()
if '""' in raw_seg_str and not dados_segregados:
    dados_segregados = parse_robusto(raw_seg_str.replace('""', '"'))

itens_estoque = []
tot_on_grade = 0.0   # EQ
tot_off_grade = 0.0  # SQ, BQ, OS

# Cores exatas solicitadas por classe na tabela aberta
CORES_CLASSE_ESTOQUE = {
    "EQ": ("#00FF7F", "rgba(0, 255, 127, 0.16)"),   # Verde Neon
    "SQ": ("#FFD600", "rgba(255, 214, 0, 0.16)"),   # Amarelo
    "BQ": ("#FF8C00", "rgba(255, 140, 0, 0.18)"),   # Laranja
    "OS": ("#FF2E2E", "rgba(255, 46, 46, 0.18)"),   # Vermelho
}

if dados_segregados:
    for m_raw, v_raw in dados_segregados.items():
        t_val = forcar_par(safe_to_numeric(v_raw))
        if t_val <= 0:
            continue
        m_str = str(m_raw).strip().upper()

        match_cls = re.search(r'\(([^)]+)\)', m_str)
        if match_cls:
            classe_real = match_cls.group(1).strip().upper()
        elif "OS" in m_str:
            classe_real = "OS"
        elif "BQ" in m_str:
            classe_real = "BQ"
        elif "SQ" in m_str:
            classe_real = "SQ"
        else:
            classe_real = "EQ"

        cod_mat = re.sub(r'\([^)]*\)', '', m_str).strip() or m_str.split()[0]

        if classe_real == "EQ":
            tot_on_grade += t_val
        else:
            tot_off_grade += t_val

        cor_item, bg_item = CORES_CLASSE_ESTOQUE.get(classe_real, ("#38bdf8", "rgba(56, 189, 248, 0.16)"))

        itens_estoque.append({
            "material": cod_mat,
            "classe": classe_real,
            "ton": t_val,
            "cor": cor_item,
            "bg": bg_item
        })

soma_segregada_real = forcar_par(tot_on_grade + tot_off_grade)
if soma_segregada_real > 0:
    estoque_total = soma_segregada_real
else:
    est_linha4 = forcar_par(safe_to_numeric(cache_dict.get("estoque_total", 0)))
    if est_linha4 > 0:
        estoque_total = est_linha4

pct_ocupacao_est = min(100.0, max(0.0, (estoque_total / CAPACIDADE_MAX_ARMAZEM * 100.0)))
espaco_livre_est = max(0.0, CAPACIDADE_MAX_ARMAZEM - estoque_total)

itens_estoque.sort(key=lambda x: (-x["ton"], x["material"], x["classe"]))
max_ton_item = max([x["ton"] for x in itens_estoque], default=1.0)

tot_geral_calc = soma_segregada_real if soma_segregada_real > 0 else (estoque_total if estoque_total > 0 else 1.0)
pct_on_grade = max(0.0, (tot_on_grade / tot_geral_calc) * 100.0)
pct_off_grade = max(0.0, (tot_off_grade / tot_geral_calc) * 100.0)

linhas_tabela_est = ""
if itens_estoque:
    for item in itens_estoque:
        cor_c = item["cor"]
        bg_c = item["bg"]
        pct_barra_item = min(100.0, max(4.0, (item["ton"] / max_ton_item) * 100.0))

        linhas_tabela_est += f"""
        <tr style="border-bottom: 1px dashed #1c2b42;">
            <td style="padding: 9px 6px; text-align: left; font-weight: 800; color: #ffffff; font-size: 0.84rem;">
                📦 {html_lib.escape(item['material'])}
            </td>
            <td style="padding: 9px 6px; text-align: center;">
                <span style="background: {bg_c}; color: {cor_c}; border: 1px solid {cor_c}; font-size: 0.68rem; font-weight: 900; padding: 2px 8px; border-radius: 6px; letter-spacing: 0.4px; box-shadow: 0 0 8px {cor_c}33;">
                    {html_lib.escape(item['classe'])}
                </span>
            </td>
            <td style="padding: 9px 6px; text-align: right;">
                <div style="color: {cor_c}; font-weight: 800; font-size: 0.84rem; font-family: monospace;">
                    {fmt(item['ton'])} <span style="font-size: 0.70rem; color: #94a3b8; font-weight: normal;">t</span>
                </div>
                <div style="width: 100%; height: 3px; background: #14243b; border-radius: 999px; overflow: hidden; margin-top: 3px;">
                    <div style="width: {pct_barra_item:.1f}%; height: 100%; background: {cor_c}; border-radius: 999px;"></div>
                </div>
            </td>
        </tr>
        """
else:
    linhas_tabela_est = '<tr><td colspan="3" style="color:#64748b; font-size:0.8rem; text-align:center; padding:14px;">Aguardando dados segregados...</td></tr>'

html_est = f"""
<div id="sec-est"></div>
<details class="master-box" style="border-left-color: #00FF7F;">
    <summary>
        <div class="header-layout">
            <div class="icon-box" style="background-color: rgba(0, 255, 127, 0.15); color: #00FF7F;">📦</div>
            <div class="master-metric-title">Estoque Físico no Armazém</div>
        </div>

        <div class="value-layout" style="margin-bottom: 2px;">
            <div class="master-metric-val">{fmt(estoque_total)}</div>
            <div class="master-metric-unit">TON</div>
        </div>

        <div style="margin-top: 6px; margin-bottom: 2px;">
            <div style="font-size: 0.75rem; color: #cbd5e1; margin-bottom: 5px;">
                Ocupação: <b style="color: #ffffff;">{fmt(estoque_total)} t</b> de <b style="color: #ffffff;">{fmt(CAPACIDADE_MAX_ARMAZEM)} t</b> ({pct_ocupacao_est:.0f}%) 📦
            </div>
            <div style="width: 100%; height: 7px; background: #14243b; border-radius: 999px; overflow: hidden;">
                <div style="width: {pct_ocupacao_est:.1f}%; height: 100%; background: linear-gradient(90deg, #38bdf8 0%, #00FF7F 100%); border-radius: 999px; box-shadow: 0 0 10px rgba(0,255,127,0.45);"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #64748b; margin-top: 4px;">
                <span>Espaço Livre: <b style="color: #38bdf8;">{fmt(espaco_livre_est)} t</b></span>
                <span>Capacidade: 25.000 t</span>
            </div>
        </div>
    </summary>

    <div class="master-content" style="padding-top: 12px;">
        <!-- 1. MEIO: TABELA ABERTA DE MATERIAIS (EQ Verde Neon | SQ Amarelo | BQ Laranja | OS Vermelho) -->
        <div style="background: #070d18; border: 1.5px solid #142842; border-radius: 12px; padding: 6px 10px; margin-bottom: 10px;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="border-bottom: 1.5px solid #1c2b42; color: #64748b; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.5px;">
                        <th style="padding: 8px 6px; text-align: left;">Material</th>
                        <th style="padding: 8px 6px; text-align: center;">Classe</th>
                        <th style="padding: 8px 6px; text-align: right;">Qtd. Ton</th>
                    </tr>
                </thead>
                <tbody>
                    {linhas_tabela_est}
                </tbody>
            </table>
        </div>

        <!-- 2. RODAPÉ: BARRA DE CLASSE (MATERIAL ON-GRADE vs MATERIAL OFF-GRADE) -->
        <div style="background: #070d18; border: 1.5px solid #142842; border-radius: 12px; padding: 10px 12px;">
            <div style="display: flex; width: 100%; height: 8px; background: #14243b; border-radius: 999px; overflow: hidden; margin-bottom: 10px;">
                <div style="width: {pct_on_grade:.1f}%; background: #00FF7F; box-shadow: 0 0 8px rgba(0,255,127,0.5);"></div>
                <div style="width: {pct_off_grade:.1f}%; background: linear-gradient(90deg, #FFD600 0%, #FF8C00 60%, #FF2E2E 100%);"></div>
            </div>
            <div style="display: flex; justify-content: space-between; gap: 8px; text-align: center;">
                <div style="flex: 1; background: #050911; border: 1px solid #142842; border-left: 3px solid #00FF7F; border-radius: 8px; padding: 8px 6px;">
                    <div style="font-size: 0.66rem; color: #00FF7F; font-weight: 800; text-transform: uppercase;">Material On-Grade </div>
                    <div style="font-size: 1.05rem; color: #ffffff; font-weight: 800; margin-top: 3px;">
                        {fmt(tot_on_grade)} <span style="font-size: 0.72rem; color: #64748b; font-weight: normal;">t ({pct_on_grade:.0f}%)</span>
                    </div>
                </div>
                <div style="flex: 1; background: #050911; border: 1px solid #142842; border-left: 3px solid #FF8C00; border-radius: 8px; padding: 8px 6px;">
                    <div style="font-size: 0.66rem; color: #FF8C00; font-weight: 800; text-transform: uppercase;">Material Off-Grade </div>
                    <div style="font-size: 1.05rem; color: #ffffff; font-weight: 800; margin-top: 3px;">
                        {fmt(tot_off_grade)} <span style="font-size: 0.72rem; color: #64748b; font-weight: normal;">t ({pct_off_grade:.0f}%)</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</details>
"""
render_html(html_est)


# ==============================================================================
# 🖨️ RENDERIZAÇÃO 6: EXPEDIÇÃO REALIZADA (COMPLETO / MOBILE BLINDADO)
# ==============================================================================
def func_exp_dados(dt_a):
    ls = descobrir_letras_turnos(dt_a)
    try:
        url_csv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
        r = requests.get(url_csv, timeout=10)
        r.encoding = 'utf-8'
        lins = list(csv.reader(StringIO(r.text)))
        c00, c08, c16, cfim = 0.0, 0.0, 0.0, 0.0
        h00 = datetime.combine(dt_a, datetime.min.time())
        h08, h16, hfim = h00.replace(hour=8), h00.replace(hour=16), h00.replace(hour=23, minute=59, second=59)
        for row in lins[1:]:
            if len(row) > 3:
                try:
                    dtr = datetime.strptime(row[0].strip(), "%d/%m/%Y %H:%M:%S")
                    v = safe_to_numeric(row[3])
                    if dtr <= h00: c00 = v
                    if dtr <= h08: c08 = v
                    if dtr <= h16: c16 = v
                    if dtr <= hfim: cfim = v
                except: pass
        v1 = forcar_par(c08) if c08 < c00 else forcar_par(max(0.0, c08 - c00))
        v2 = forcar_par(c16) if c16 < c08 else forcar_par(max(0.0, c16 - c08))
        v3 = forcar_par(cfim) if cfim < c16 else forcar_par(max(0.0, cfim - c16))
        
        if dt_a == hoje_date:
            if agora_br.hour < 8: v2, v3 = 0, 0
            elif agora_br.hour < 16: v3 = 0
            
        tns = []
        if dt_a.weekday() in [6, 0]:
            tns.append({"letra": f"Turno {ls.get('madrugada','D')}", "v": 0, "str_vol": "EM FOLGA", "horario": "00h - 08h"})
        else:
            tns.append({"letra": f"Turno {ls.get('madrugada','D')}", "v": v1, "str_vol": f"{fmt(v1)} t", "horario": "00h - 08h"})
        
        tns.append({"letra": f"Turno {ls.get('08_16','C')}", "v": v2, "str_vol": f"{fmt(v2)} t", "horario": "08h - 16h"})
        tns.append({"letra": f"Turno {ls.get('16_00','B')}", "v": v3, "str_vol": f"{fmt(v3)} t", "horario": "16h - 00h"})
        return tns
    except: return []

tns_hoje = func_exp_dados(hoje_date)
tns_ontem = func_exp_dados(ontem_date)

# Cálculo da Barra de Progresso
pct_prog = min(100.0, max(0.0, (vol_hoje / prev_carr * 100.0))) if prev_carr > 0 else 0.0

# ----------------------------------------------------
# CARDS DOS TURNOS DE HOJE (SEM HORÁRIO DUPLICADO)
# ----------------------------------------------------
cards_hoje_html = ""
for i, t in enumerate(tns_hoje):
    is_atv = False
    if hoje_date == agora_br.date():
        if agora_br.hour < 8 and i == 0: is_atv = True
        elif 8 <= agora_br.hour < 16 and i == 1: is_atv = True
        elif agora_br.hour >= 16 and i == 2: is_atv = True

    v_str = t.get("str_vol", f"{fmt(t['v'])} t")

    if is_atv:
        cards_hoje_html += f"""
        <div style="flex: 1; background: #0c1524; border: 1.5px solid #FF9F1C; border-radius: 12px; padding: 12px 6px; text-align: center; box-shadow: 0 0 14px rgba(255, 159, 28, 0.22);">
            <div style="font-size: 0.85rem; font-weight: 800; color: #FF9F1C;">{t['letra']}</div>
            <div style="font-size: 0.72rem; font-weight: 800; color: #00D672; margin: 3px 0 4px 0;">[ATIVO 🟢]</div>
            <div style="font-size: 0.65rem; color: #64748b; margin-bottom: 8px;">{t['horario']}</div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #FF9F1C; line-height: 1;">{v_str}</div>
        </div>
        """
    else:
        val_color = "#E74C3C" if v_str == "EM FOLGA" else ("#ffffff" if t['v'] > 0 else "#64748b")
        cards_hoje_html += f"""
        <div style="flex: 1; background: #070d18; border: 1px solid #1c2b42; border-radius: 12px; padding: 12px 6px; text-align: center;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #cbd5e1;">{t['letra']}</div>
            <div style="font-size: 0.68rem; color: #64748b; margin: 3px 0 8px 0;">{t['horario']}</div>
            <div style="font-size: 1.2rem; font-weight: 800; color: {val_color}; line-height: 1;">{v_str}</div>
        </div>
        """

# ----------------------------------------------------
# CARDS DOS TURNOS DE ONTEM (D-1)
# ----------------------------------------------------
cards_ontem_html = ""
for t in tns_ontem:
    v_str_o = t.get("str_vol", f"{fmt(t['v'])} t")
    val_color_o = "#E74C3C" if v_str_o == "EM FOLGA" else ("#ffffff" if t['v'] > 0 else "#64748b")
    cards_ontem_html += f"""
    <div style="flex: 1; background: #070d18; border: 1px solid #1c2b42; border-radius: 12px; padding: 12px 6px; text-align: center;">
        <div style="font-size: 0.85rem; font-weight: 700; color: #38bdf8;">{t['letra']}</div>
        <div style="font-size: 0.68rem; color: #64748b; margin: 3px 0 8px 0;">{t['horario']}</div>
        <div style="font-size: 1.2rem; font-weight: 800; color: {val_color_o}; line-height: 1;">{v_str_o}</div>
    </div>
    """

# ----------------------------------------------------
# TABELA DE DESTINOS + TOTAIS NO RODAPÉ
# ----------------------------------------------------
tabela_linhas_html = ""
if balanco_destinos:
    def regra_ordenacao(d):
        nome = str(d.get('destino', '')).upper()
        if "MI" in nome or "LATAM" in nome: return 999999
        try: return int(re.search(r'\d+', nome).group())
        except: return 0

    balanco_destinos_ordenado = sorted(balanco_destinos, key=regra_ordenacao, reverse=True)
    tabela_linhas_html = """
    <div style="background-color: #070d18; border: 1.5px solid #1c2b42; border-radius: 12px; padding: 10px; overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; font-size: 0.75rem; text-align: center; color: #ffffff;">
            <thead>
                <tr style="border-bottom: 1px solid #1c2b42; color: #64748b;">
                    <th style="text-align: left; padding: 8px 4px;">Destino</th>
                    <th style="text-align: center; padding: 8px 4px; color: #38bdf8;">Plano</th>
                    <th style="text-align: center; padding: 8px 4px; color: #00D672;">Carr.</th>
                    <th style="text-align: center; padding: 8px 4px; color: #E5B800;">Falta</th>
                    <th style="text-align: center; padding: 8px 4px;">%</th>
                </tr>
            </thead>
            <tbody>
    """
    for d in balanco_destinos_ordenado:
        ating = d['atingimento']
        cor_ating = "#00D672" if ating >= 100 else ("#38bdf8" if ating > 0 else "#64748b")
        if d['saldo'] <= 0 and d['realizado'] > 0:
            saldo_str, cor_saldo = "0", "#00D672"
        else:
            saldo_str, cor_saldo = fmt(d['saldo']), "#E5B800"

        nome_cru = str(d['destino']).upper()
        if "MI" in nome_cru or "LATAM" in nome_cru:
            dest_nome = "MI / LATAM"
        else:
            parts = nome_cru.split('-')
            dest_nome = f"{parts[0].strip()} - {parts[1].strip()}" if len(parts) >= 2 else nome_cru

        tabela_linhas_html += f"""
            <tr style="border-bottom: 1px dashed #1c2b42;">
                <td style="text-align: left; padding: 10px 4px; font-weight: bold;">{dest_nome}</td>
                <td style="text-align: center; padding: 10px 4px; color: #38bdf8;">{fmt(d['meta'])}</td>
                <td style="text-align: center; padding: 10px 4px; color: #00D672;">{fmt(d['realizado'])}</td>
                <td style="text-align: center; padding: 10px 4px; color: {cor_saldo};">{saldo_str}</td>
                <td style="text-align: center; padding: 10px 4px; color: {cor_ating};">{ating:.0f}%</td>
            </tr>
        """
    tabela_linhas_html += "</tbody></table></div>"
else:
    tabela_linhas_html = '<div style="color:#64748b; font-size:0.8rem; text-align:center; padding:12px;">Nenhum destino ativo reportado.</div>'

# ------------------------------------------------------------------------------
# 🎯 CÁLCULO E MONTAGEM DO RODAPÉ (3 CARDS COM PENDENTE EM LARANJA)
# ------------------------------------------------------------------------------
total_expedicao_falta = forcar_par(max(0.0, total_expedicao_meta - total_expedicao_real))

totais_rodape_html = f"""
<div style="display:flex; justify-content:space-between; align-items:center; background-color:#070d18; border:1.5px solid #142842; border-radius:12px; padding:12px 8px; margin-top:12px; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.25);">
    <!-- CARD 1: PLANO TOTAL -->
    <div style="flex: 1;">
        <div style="font-size:0.68rem; color:#64748b; font-weight:bold; text-transform:uppercase;">Plano Total</div>
        <div style="font-size:1.25rem; color:#ffffff; font-weight:bold; margin-top:2px;">{fmt(total_expedicao_meta)} <span style="font-size:0.75rem; color:#64748b; font-weight:normal;">t</span></div>
    </div>
    
    <!-- CARD 2: TOTAL CARREGADO -->
    <div style="flex: 1; border-left:1px solid #1c2b42; border-right:1px solid #1c2b42; padding: 0 4px;">
        <div style="font-size:0.68rem; color:#38bdf8; font-weight:bold; text-transform:uppercase;">Carregado</div>
        <div style="font-size:1.25rem; color:#38bdf8; font-weight:bold; margin-top:2px;">{fmt(total_expedicao_real)} <span style="font-size:0.75rem; color:#64748b; font-weight:normal;">t</span></div>
    </div>

    <!-- CARD 3: TOTAL PENDENTE (LARANJA) -->
    <div style="flex: 1;">
        <div style="font-size:0.68rem; color:#FF9F1C; font-weight:bold; text-transform:uppercase;">Pendente</div>
        <div style="font-size:1.25rem; color:#FF9F1C; font-weight:bold; margin-top:2px;">{fmt(total_expedicao_falta)} <span style="font-size:0.75rem; color:#64748b; font-weight:normal;">t</span></div>
    </div>
</div>
"""

html_destinos = f"{tabela_linhas_html}{totais_rodape_html}"

# ----------------------------------------------------
# MONTAGEM MASTER (SWITCH DESLIZANTE IOS COM AUTO-RESET PARA HOJE)
# ----------------------------------------------------
html_exp_completo = f"""
<div id="sec-exp"></div>
<style>
    /* CONTROLES OCULTOS DE NAVEGAÇÃO */
    .exp-wrapper input[type="radio"] {{ display: none !important; }}

    /* DOIS BLOCOS DE SELEÇÃO CENTRALIZADOS */
    .exp-tab-bar {{
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 14px;
        padding: 0 4px;
    }}
    .exp-tab-bar label {{
        flex: 1;
        max-width: 180px;
        text-align: center;
        padding: 9px 10px;
        font-size: 0.80rem;
        font-weight: 800;
        color: #94a3b8;
        background: #070d18;
        border: 1.5px solid #1c2b42;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.25s ease;
        white-space: nowrap;
        -webkit-tap-highlight-color: transparent;
    }}
    #nav_turnos:checked ~ details .lbl-turnos {{
        background: #00D672 !important;
        color: #0a101d !important;
        border-color: #00D672 !important;
        box-shadow: 0 0 10px rgba(0, 214, 114, 0.35);
    }}
    #nav_destinos:checked ~ details .lbl-destinos {{
        background: #38bdf8 !important;
        color: #0a101d !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.35);
    }}

            /* 🍏 SWITCH DESLIZANTE IOS NATIVO (TOQUE AMPLIADO MOBILE) */
    details:not([open]) .ios-slider-capsule {{
        display: none !important;
    }}
    details[open] .ios-slider-capsule {{
        display: inline-flex !important;
        position: relative !important;
        align-items: center !important;
        background: #060b14 !important;
        border: 1.5px solid #142842 !important;
        border-radius: 999px !important;
        padding: 3px !important;
        margin-right: 24px !important;
        width: 174px !important;
        height: 38px !important;
        box-sizing: border-box !important;
        flex-shrink: 0 !important;
        user-select: none !important;
        -webkit-user-select: none !important;
        transition: all 0.3s ease;
    }}

    .ios-slider-thumb {{
        position: absolute;
        top: 3px;
        left: 3px;
        width: 82px;
        height: 29px;
        background: #00D672;
        border-radius: 999px;
        box-shadow: 0 0 10px rgba(0, 214, 114, 0.45);
        transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
        z-index: 1;
        pointer-events: none;
    }}

    #day_ontem:checked ~ details .ios-slider-thumb {{
        transform: translateX(83px);
    }}

    /* Textos dos botões sobrepostos */
    .ios-slider-btn {{
        position: relative;
        flex: 1;
        text-align: center;
        font-size: 0.78rem;
        font-weight: 800;
        line-height: 29px;
        cursor: pointer;
        z-index: 2;
        transition: color 0.25s ease;
        white-space: nowrap;
        -webkit-tap-highlight-color: transparent;
    }}


    #day_hoje:checked ~ details .btn-txt-hoje {{ color: #0a101d !important; }}
    #day_hoje:checked ~ details .btn-txt-ontem {{ color: #64748b !important; }}

    #day_ontem:checked ~ details .btn-txt-hoje {{ color: #64748b !important; }}
    #day_ontem:checked ~ details .btn-txt-ontem {{ color: #0a101d !important; }}

    /* 🎯 EFEITO: QUANDO CLICAR EM "PLANO VS EXP.", VOLTA DESLIZANDO SOZINHO PRO HOJE */
    #nav_destinos:checked ~ details .ios-slider-thumb {{
        transform: translateX(0px) !important;
    }}
    #nav_destinos:checked ~ details .btn-txt-hoje {{
        color: #0a101d !important;
    }}
    #nav_destinos:checked ~ details .btn-txt-ontem {{
        color: #334155 !important;
        pointer-events: none !important;
    }}
    #nav_destinos:checked ~ details .ios-slider-capsule {{
        opacity: 0.70 !important;
    }}

    /* EXIBIÇÃO DE CONTEÚDO */
    .exp-view-turnos, .exp-view-destinos {{ display: none; }}
    #nav_turnos:checked ~ details .exp-view-turnos {{ display: block; }}
    #nav_destinos:checked ~ details .exp-view-destinos {{ display: block; }}

    .box-hoje, .box-ontem {{ display: none; }}
    #day_hoje:checked ~ details .box-hoje {{ display: block; }}
    #day_ontem:checked ~ details .box-ontem {{ display: block; }}
</style>

<div class="exp-wrapper">
    <input type="radio" name="exp_view" id="nav_turnos" checked>
    <input type="radio" name="exp_view" id="nav_destinos">
    <input type="radio" name="exp_day" id="day_hoje" checked>
    <input type="radio" name="exp_day" id="day_ontem">

    <details class="master-box" style="border-left-color: #00D672;" >
        <summary>
            <!-- CABEÇALHO COM TÍTULO E SWITCH DESLIZANTE IOS -->
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; gap:4px;">
                <div class="header-layout" style="margin-bottom:0; min-width:0; flex-shrink:1;">
                    <div class="icon-box" style="background-color: rgba(0, 214, 114, 0.15); color: #00D672; flex-shrink:0;">🚚</div>
                    <div class="master-metric-title" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">Expedição Realizada</div>
                </div>
                
                <!-- CÁPSULA DESLIZANTE ESTILO IPHONE -->
                <div class="ios-slider-capsule" onclick="event.stopPropagation();">
                    <div class="ios-slider-thumb"></div>
                    <label for="day_hoje" class="ios-slider-btn btn-txt-hoje">Hoje 📅</label>
                    <label for="day_ontem" class="ios-slider-btn btn-txt-ontem">Ontem ⏪</label>
                </div>
            </div>

            <!-- VALOR PRINCIPAL -->
            <div class="value-layout" style="margin-bottom:2px;">
                <div class="master-metric-val">{fmt(vol_hoje)}</div>
                <div class="master-metric-unit">TON</div>
            </div>

            <!-- CONSOLIDADO D-1 EM VERDE -->
            <div class="master-metric-sub" style="color: #00D672; font-weight: 700; margin-bottom: 8px;">
                Consolidado Ontem (D-1): {fmt(vol_ontem)} t
            </div>

            <!-- BARRA DE PROGRESSO COM METAS -->
            <div style="margin-top: 4px; margin-bottom: 2px;">
                <div style="font-size: 0.75rem; color: #cbd5e1; margin-bottom: 5px;">
                    Progresso: <b style="color: #ffffff;">{fmt(vol_hoje)} t</b> de <b style="color: #ffffff;">{fmt(prev_carr)} t</b> ({pct_prog:.0f}%) 🎯
                </div>
                <div style="width: 100%; height: 7px; background: #14243b; border-radius: 999px; overflow: hidden;">
                    <div style="width: {pct_prog:.1f}%; height: 100%; background: linear-gradient(90deg, #0084FF 0%, #00D672 100%); border-radius: 999px; box-shadow: 0 0 10px rgba(0,214,114,0.45);"></div>
                </div>
                <div style="text-align: right; font-size: 0.72rem; color: #64748b; margin-top: 4px;">
                    Prev. Fechamento: {fmt(prev_carr)} t
                </div>
            </div>
        </summary>

        <div class="master-content" style="padding-top: 14px;">
            <!-- DOIS BLOCOS DE SELEÇÃO CENTRALIZADOS -->
            <div class="exp-tab-bar">
                <label for="nav_turnos" class="lbl-turnos">⏰ Exp. p/ Turno</label>
                <label for="nav_destinos" class="lbl-destinos">📊 Plano vs Exp.</label>
            </div>

            <!-- PAINEL 1: TURNOS -->
            <div class="exp-view-turnos">
                <!-- SEÇÃO HOJE -->
                <div class="box-hoje">
                    <div style="font-size: 0.72rem; font-weight: 800; color: #00D672; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 10px;">
                        TURNOS EM OPERAÇÃO HOJE:
                    </div>
                    <div style="display: flex; gap: 8px;">
                        {cards_hoje_html}
                    </div>
                </div>

                <!-- SEÇÃO ONTEM -->
                <div class="box-ontem">
                    <div style="font-size: 0.72rem; font-weight: 800; color: #38bdf8; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 10px;">
                        TURNOS EM OPERAÇÃO ONTEM:
                    </div>
                    <div style="display: flex; gap: 8px;">
                        {cards_ontem_html}
                    </div>
                </div>
            </div>

            <!-- PAINEL 2: DESTINOS (TABELA COM TOTAIS NO RODAPÉ) -->
            <div class="exp-view-destinos" style="text-align: left;">
                {html_destinos}
            </div>
        </div>
    </details>
</div>
"""
render_html(html_exp_completo)


# ==============================================================================
# 🖨️ RENDERIZAÇÃO 6.5: ANÁLISE DE PEDIDOS (ZLE087 - DESTINO, MATERIAL & HORA BASE)
# ==============================================================================
@st.cache_data(ttl=30)
def carregar_pedidos_zle087():
    try:
        df, carimbo = carregar_tabela_cega("Status_Pedidos_ZLE087", coluna_chave="FLUXO")
        
        if df.empty:
            url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Status_Pedidos_ZLE087"
            df_raw = pd.read_csv(url, header=None, dtype=str)
            if df_raw.empty:
                return pd.DataFrame(), "--:--"
            
            idx_header = None
            for i in range(min(6, len(df_raw))):
                row_vals = [str(x).strip().upper() for x in df_raw.iloc[i].tolist()]
                if any("FLUXO" in x for x in row_vals):
                    idx_header = i
                    break
            
            if idx_header is not None:
                cols = [str(c).strip().upper() for c in df_raw.iloc[idx_header].tolist()]
                df = df_raw.iloc[idx_header + 1:].copy()
                df.columns = cols
            else:
                return pd.DataFrame(), "--:--"

        hora_att_ped = carimbo if carimbo else "--:--"
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df, hora_att_ped
    except Exception:
        return pd.DataFrame(), "--:--"

df_pedidos, hora_att_ped = carregar_pedidos_zle087()

pedidos_transf = []
pedidos_mi = []
tot_saldo_transf = 0.0
tot_saldo_mi = 0.0

if not df_pedidos.empty:
    def obter_val(registro, termos_obrigatorios, termos_proibidos=[]):
        for k in registro.index:
            k_upper = str(k).strip().upper()
            if all(t in k_upper for t in termos_obrigatorios):
                if not any(p in k_upper for p in termos_proibidos):
                    val = registro.get(k)
                    if pd.notna(val) and str(val).strip() not in ["", "nan", "None"]:
                        return val
        return None

    for _, r in df_pedidos.iterrows():
        fluxo = str(obter_val(r, ["FLUXO"]) or "").strip().upper()
        destino = str(obter_val(r, ["DESTINO"]) or "").strip()
        ped_atual = str(obter_val(r, ["PEDIDO"], ["PROX"]) or "").strip()
        mat_atual = str(obter_val(r, ["MAT"], ["PROX"]) or "").strip()
        
        qtd_ini = safe_to_numeric(obter_val(r, ["QTD"]) or 0)
        saldo = safe_to_numeric(obter_val(r, ["SALDO"], ["PROX"]) or 0)
        
        prox_ped = str(obter_val(r, ["PROX", "PED"]) or "--").strip()
        prox_mat = str(obter_val(r, ["PROX", "MAT"]) or "--").strip()
        saldo_prox = str(obter_val(r, ["SALDO", "PROX"]) or "--").strip()

        if not destino or destino.lower() in ["nan", "none", ""]:
            continue

        item = {
            "destino": destino,
            "pedido": ped_atual,
            "material": mat_atual,
            "qtd_ini": qtd_ini,
            "saldo": saldo,
            "prox_ped": prox_ped,
            "prox_mat": prox_mat,
            "saldo_prox": saldo_prox,
            "is_fim": (saldo <= 100.0 and saldo > 0)
        }

        if "TRANSF" in fluxo:
            pedidos_transf.append(item)
            tot_saldo_transf += saldo
        else:
            pedidos_mi.append(item)
            tot_saldo_mi += saldo

pedidos_transf.sort(key=lambda x: (not x["is_fim"], x["destino"]))
pedidos_mi.sort(key=lambda x: (not x["is_fim"], x["destino"]))
tot_saldo_geral = tot_saldo_transf + tot_saldo_mi

def cor_badge_material_pedido(mat_str):
    m = str(mat_str).upper()
    if "OS" in m:
        return "#FF2E2E", "rgba(255, 46, 46, 0.16)"
    if "BQ" in m:
        return "#FF8C00", "rgba(255, 140, 0, 0.16)"
    if "SQ" in m:
        return "#FFD600", "rgba(255, 214, 0, 0.16)"
    return "#00FF7F", "rgba(0, 255, 127, 0.16)"

def gerar_cards_pedidos(lista_itens, cor_primaria):
    if not lista_itens:
        return '<div style="color:#64748b; font-size:0.82rem; text-align:center; padding:16px;">Nenhum pedido ativo encontrado.</div>'
    
    html = ""
    for item in lista_itens:
        cor_mat, bg_mat = cor_badge_material_pedido(item["material"])

        if item["is_fim"]:
            borda_card = "#FF2E2E"
            bg_card = "linear-gradient(180deg, rgba(255, 46, 46, 0.09) 0%, #070d18 100%)"
            cor_saldo = "#FF2E2E"
            tag_alerta = '<span style="background:rgba(255,46,46,0.2); border:1px solid #FF2E2E; color:#ff8080; font-size:0.62rem; font-weight:900; padding:2px 6px; border-radius:5px; letter-spacing:0.3px;">⚠️ FIM DE PEDIDO</span>'
        else:
            borda_card = cor_primaria
            bg_card = "#070d18"
            cor_saldo = "#38bdf8"
            tag_alerta = ""

        pct_atend = 0.0
        if item["qtd_ini"] > 0:
            carr = max(0.0, item["qtd_ini"] - item["saldo"])
            pct_atend = min(100.0, max(0.0, (carr / item["qtd_ini"]) * 100.0))

        info_prox = ""
        if item["prox_ped"] not in ("--", "", "nan") and "SEM PR" not in item["prox_mat"].upper():
            info_prox = f"""
            <div style="background:#050911; border-top:1px solid #162840; margin:10px -13px -11px -13px; padding:7px 13px; border-radius:0 0 11px 11px; display:flex; justify-content:space-between; align-items:center; font-size:0.70rem; color:#94a3b8; gap:6px;">
                <span>🔜 Próx: <b style="color:#e2e8f0;">{html_lib.escape(item['prox_ped'])}</b> &bull; <b style="color:#cbd5e1;">{html_lib.escape(item['prox_mat'])}</b></span>
                <span style="color:#38bdf8; font-weight:800; white-space:nowrap;">{html_lib.escape(item['saldo_prox'])}</span>
            </div>
            """

        html += f"""
        <div style="background:{bg_card}; border:1.5px solid #1a314d; border-left:5px solid {borda_card}; border-radius:13px; padding:11px 13px; margin-bottom:12px; box-shadow:0 4px 12px rgba(0,0,0,0.32);">
            <div style="display:flex; justify-content:space-between; align-items:center; gap:8px; margin-bottom:8px;">
                <div style="min-width:0;">
                    <div style="color:#ffffff; font-weight:900; font-size:0.95rem; letter-spacing:0.2px; line-height:1.2;">
                        {html_lib.escape(item['destino'])}
                    </div>
                    <div style="display:flex; align-items:center; gap:6px; margin-top:3px;">
                        <span style="font-size:0.70rem; color:#64748b; font-family:monospace;">Ordem: <b style="color:#cbd5e1;">{html_lib.escape(item['pedido'])}</b></span>
                        {tag_alerta}
                    </div>
                </div>

                <div style="background:{bg_mat}; border:1.5px solid {cor_mat}; border-radius:9px; padding:5px 10px; text-align:center; flex-shrink:0; box-shadow:0 0 10px {cor_mat}26;">
                    <div style="font-size:0.56rem; color:{cor_mat}; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; line-height:1;">MATERIAL</div>
                    <div style="font-size:0.86rem; color:#ffffff; font-weight:900; margin-top:2px; white-space:nowrap;">{html_lib.escape(item['material'])}</div>
                </div>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; background:#050911; border:1px solid #132338; border-radius:8px; padding:6px 10px; margin-bottom:7px;">
                <div>
                    <div style="font-size:0.60rem; color:#64748b; font-weight:700; text-transform:uppercase;">Saldo Atual</div>
                    <div style="font-size:0.95rem; font-weight:900; color:{cor_saldo}; font-family:monospace;">{fmt(item['saldo'])} <span style="font-size:0.68rem; font-weight:normal;">t</span></div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:0.60rem; color:#64748b; font-weight:700; text-transform:uppercase;">Meta Ordem</div>
                    <div style="font-size:0.82rem; font-weight:700; color:#cbd5e1; font-family:monospace;">{fmt(item['qtd_ini'])} t</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.60rem; color:#64748b; font-weight:700; text-transform:uppercase;">Atendido</div>
                    <div style="font-size:0.85rem; font-weight:800; color:#00FF7F;">{pct_atend:.0f}%</div>
                </div>
            </div>

            <div style="width:100%; height:4px; background:#14243b; border-radius:999px; overflow:hidden;">
                <div style="width:{pct_atend:.1f}%; height:100%; background:linear-gradient(90deg, #38bdf8, {borda_card}); border-radius:999px;"></div>
            </div>

            {info_prox}
        </div>
        """
    return html

html_cards_transf = gerar_cards_pedidos(pedidos_transf, "#0084FF")
html_cards_mi = gerar_cards_pedidos(pedidos_mi, "#00D672")

txt_base_ped = f" | 🕒 Base: {hora_att_ped.split(' ')[1][:5]}" if hora_att_ped and " " in hora_att_ped else (f" | 🕒 Base: {hora_att_ped[:5]}" if hora_att_ped and hora_att_ped != "--:--" else "")

html_bloco_pedidos = f"""
<style>
    .ped-wrapper input[type="radio"] {{ display: none !important; }}

    .ped-tab-bar {{
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 14px;
        padding: 0 2px;
    }}
    .ped-tab-bar label {{
        flex: 1;
        text-align: center;
        padding: 10px 8px;
        font-size: 0.80rem;
        font-weight: 800;
        color: #94a3b8;
        background: #070d18;
        border: 1.5px solid #1c2b42;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
        white-space: nowrap;
        -webkit-tap-highlight-color: transparent;
    }}
    #tab_transf:checked ~ details .lbl-transf {{
        background: #0084FF !important;
        color: #ffffff !important;
        border-color: #0084FF !important;
        box-shadow: 0 0 10px rgba(0, 132, 255, 0.4);
    }}
    #tab_mi:checked ~ details .lbl-mi {{
        background: #00D672 !important;
        color: #0a101d !important;
        border-color: #00D672 !important;
        box-shadow: 0 0 10px rgba(0, 214, 114, 0.4);
    }}

    .ped-view-transf, .ped-view-mi {{ display: none; }}
    #tab_transf:checked ~ details .ped-view-transf {{ display: block; }}
    #tab_mi:checked ~ details .ped-view-mi {{ display: block; }}
</style>

<div id="sec-ped"></div>
<div class="ped-wrapper">
    <input type="radio" name="ped_view" id="tab_transf" checked>
    <input type="radio" name="ped_view" id="tab_mi">

    <details class="master-box" style="border-left-color: #0084FF; margin-bottom: 14px;">
       <summary>
            <div class="header-layout" style="margin-bottom:4px; padding-right:18px;">
                <div class="icon-box" style="background-color: rgba(0, 132, 255, 0.15); color: #0084FF; flex-shrink:0;">📑</div>
                <div class="master-metric-title">Análise de Pedidos (ZLE087{txt_base_ped})</div>
            </div>

            <div class="value-layout" style="margin-bottom:8px;">
                <div class="master-metric-val">{fmt(tot_saldo_geral)}</div>
                <div class="master-metric-unit">TON PENDENTES</div>
            </div>

            <div style="display: flex; gap: 8px; margin-top: 4px;">
                <div style="flex: 1; background: #070d18; border: 1.5px solid #142842; border-left: 3px solid #0084FF; border-radius: 10px; padding: 8px 9px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 4px;">
                        <span style="font-size: 0.68rem; color: #94a3b8; font-weight: 800; text-transform: uppercase; white-space: nowrap;">🚛 Transf.</span>
                        <span style="background: rgba(0, 132, 255, 0.15); color: #38bdf8; font-size: 0.65rem; font-weight: 800; padding: 2px 6px; border-radius: 4px; white-space: nowrap;">{len(pedidos_transf)} ped.</span>
                    </div>
                    <div style="font-size: 0.95rem; font-weight: 800; color: #ffffff; margin-top: 4px;">
                        {fmt(tot_saldo_transf)} <span style="font-size: 0.70rem; color: #64748b; font-weight: normal;">t</span>
                    </div>
                </div>

                <div style="flex: 1; background: #070d18; border: 1.5px solid #142842; border-left: 3px solid #00D672; border-radius: 10px; padding: 8px 9px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 4px;">
                        <span style="font-size: 0.68rem; color: #94a3b8; font-weight: 800; text-transform: uppercase; white-space: nowrap;">🏢 MI / LATAM</span>
                        <span style="background: rgba(0, 214, 114, 0.15); color: #00D672; font-size: 0.65rem; font-weight: 800; padding: 2px 6px; border-radius: 4px; white-space: nowrap;">{len(pedidos_mi)} ped.</span>
                    </div>
                    <div style="font-size: 0.95rem; font-weight: 800; color: #ffffff; margin-top: 4px;">
                        {fmt(tot_saldo_mi)} <span style="font-size: 0.70rem; color: #64748b; font-weight: normal;">t</span>
                    </div>
                </div>
            </div>
        </summary>

        <div class="master-content" style="padding-top: 14px;">
            <div class="ped-tab-bar">
                <label for="tab_transf" class="lbl-transf">🚛 Transferência ({len(pedidos_transf)})</label>
                <label for="tab_mi" class="lbl-mi">🏢 MI / LATAM ({len(pedidos_mi)})</label>
            </div>

            <div class="ped-view-transf">
                {html_cards_transf}
            </div>

            <div class="ped-view-mi">
                {html_cards_mi}
            </div>
        </div>
    </details>
</div>
"""
render_html(html_bloco_pedidos)


# ==============================================================================
# 🖨️ RENDERIZAÇÃO 7: PÁTIO DA FÁBRICA (FECHADO AO INICIAR + ÍCONE CAMINHÃO AZUL/RELÓGIO)
# ==============================================================================
txt_att_patio = f" | 🕒 Base: {hora_att_patio.split(' ')[1][:5]}" if hora_att_patio and " " in hora_att_patio else ""

icone_caminhao_prog_svg = """
<svg width="28" height="28" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- Baú e Cabine do Caminhão em Azul Ciano -->
    <rect x="2" y="9" width="15" height="11" rx="2" fill="#38a9ff" fill-opacity="0.25" stroke="#38a9ff" stroke-width="2"/>
    <path d="M17 12H22.5L26 16V20H17V12Z" fill="#38a9ff" fill-opacity="0.25" stroke="#38a9ff" stroke-width="2" stroke-linejoin="round"/>
    <!-- Rodas -->
    <circle cx="8" cy="22" r="2.3" fill="#0a1424" stroke="#38a9ff" stroke-width="2"/>
    <circle cx="22" cy="22" r="2.3" fill="#0a1424" stroke="#38a9ff" stroke-width="2"/>
    <!-- Relógio de Programação no canto superior direito -->
    <circle cx="25" cy="7" r="5.5" fill="#070d18" stroke="#38bdf8" stroke-width="1.8"/>
    <path d="M25 4.5V7L26.8 8" stroke="#ffffff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""

html_patio = f"""
<div id="sec-patio"></div>
<details class="master-box" style="border-left-color: #38a9ff;">
    <summary>
        <div class="header-layout">
            <div class="icon-box" style="background-color: rgba(56, 169, 255, 0.15); color: #38a9ff;">🏭</div>
            <div class="master-metric-title">Pátio da Fábrica (Tempo Real{txt_att_patio})</div>
        </div>
        <div class="value-layout">
            <div class="master-metric-val">{total_veiculos_fisicos}</div>
            <div class="master-metric-unit">Veículos Físicos</div>
        </div>
        <div class="master-metric-sub" style="color: #38a9ff;">Carga Disponível: {fmt(vol_patio_disponivel)} t</div>
        <div class="master-metric-sub" style="color: #64748b;">(Checklist + Apoio + Fila)</div>
    </summary>
    <div class="master-content" style="padding-top:16px;">
"""

for tit, chv, col_v, col_t, cor, ico in mapa_status_colunas:
    lista_destinos = destinos_por_status.get(chv, [])
    v_qtd = dados_patio[chv]["veiculos"]
    v_ton = dados_patio[chv]["peso"]

    ico_render = icone_caminhao_prog_svg if chv == "PR" else ico

    linhas_dest_html = ""
    if lista_destinos:
        for item in lista_destinos:
            linhas_dest_html += f'<div class="dest-row"><span class="n">{html_lib.escape(item["destino"])}</span><span class="v">{item["veic"]} veíc. <small>({fmt(item["ton"])} t)</small></span></div>'
        linhas_dest_html += f'<div class="dest-row total"><span class="n">TOTAL</span><span class="v">{v_qtd} veíc. <small>({fmt(v_ton)} t)</small></span></div>'
    else:
        linhas_dest_html = '<div class="dest-vazio">Nenhum veículo alocado neste status.</div>'

    html_patio += f"""
    <details class="st-card" style="--c:{cor};">
        <summary>
            <div class="st-ico">{ico_render}</div>
            <div class="st-txt">
                <div class="st-title">{tit}</div>
                <div class="st-num">{v_qtd} <span>veíc. / {fmt(v_ton)} t</span></div>
            </div>
            <div class="chev">›</div>
        </summary>
        <div class="st-body">{linhas_dest_html}</div>
    </details>
    """

html_patio += "</div></details>"
render_html(html_patio)





# ==============================================================================
# 🖨️ RENDERIZAÇÃO 8: FROTA & EQUIPAMENTOS (8A) + PREVENTIVA & INSPEÇÃO (8B)
# ==============================================================================
equip_por_tipo = {}
todos_equip_lista = []
qtd_total_disp = 0
qtd_total_indisp = 0

qtd_venc_prev = 0
qtd_prox_prev = 0
qtd_venc_insp = 0
qtd_prox_insp = 0

def parse_num_frota_ptbr(val_raw):
    if val_raw is None or pd.isna(val_raw):
        return 0.0
    s = re.sub(r'[^\d,\.\-]', '', str(val_raw).strip())
    if not s or s in ["-", "."]:
        return 0.0
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    elif "." in s:
        partes = s.split(".")
        if len(partes[-1]) == 3:
            s = s.replace(".", "")
    try:
        return float(s)
    except Exception:
        return 0.0

def formatar_horimetro_ou_data(val_raw):
    s = str(val_raw).strip()
    if not s or s.upper() in ["NAN", "NONE", "--", "-"] or "/" in s:
        return "--"
    num = parse_num_frota_ptbr(s)
    if num > 0:
        return f"{fmt(num)} h"
    return "--"

def analisar_saldo_manut(saldo_raw, is_por_dia=False):
    """
    Régua oficial (Preventiva Col. H e Inspeção Col. N):
      <= 0      -> VENCIDA (Texto Vermelho #FF2E2E + Borda Laranja #FF8C00)
      1 a 50    -> PRÓX. AO VENCIMENTO (Vermelho #FF2E2E)
      51 a 100  -> ATENÇÃO (Laranja #FF8C00)
      101 +     -> EM DIA (Verde #00FF7F)
    Retorna: (texto_exibicao, rotulo_status, cor_texto, cor_borda, bg_rgba, peso_ordem)
    """
    s = str(saldo_raw).strip()
    if not s or s.upper() in ["NAN", "NONE", "--", "-", "SEM META"]:
        return "--", "SEM META", "#64748b", "#64748b", "rgba(100, 116, 139, 0.14)", 4

    val = parse_num_frota_ptbr(s)
    unidade = "d" if is_por_dia else "h"
    val_fmt = f"{fmt(val)} {unidade}"

    if val <= 0:
        return val_fmt, "VENCIDA", "#FF2E2E", "#FF8C00", "rgba(255, 46, 46, 0.22)", 0
    if val <= 50:
        return val_fmt, "PRÓX. AO VENCIMENTO", "#FF2E2E", "#FF2E2E", "rgba(255, 46, 46, 0.16)", 1
    if val <= 100:
        return val_fmt, "ATENÇÃO", "#FF8C00", "#FF8C00", "rgba(255, 140, 0, 0.16)", 2
    return val_fmt, "EM DIA", "#00FF7F", "#00FF7F", "rgba(0, 255, 127, 0.14)", 3

def limpar_om_sap(om_raw):
    s = str(om_raw).strip()
    if not s or s.upper() in ["NAN", "NONE", "--", "-"]:
        return "--"
    nums = re.findall(r'\d+', s)
    return nums[0] if nums else s

def ordem_tipo_equipamento(tipo_str):
    t = str(tipo_str).upper()
    if "EMPILHADEIRA" in t: return 0
    if "TALHA" in t or "PONTE" in t: return 1
    if "TRANSPALETEIRA" in t: return 2
    if "VARREDEIRA" in t: return 3
    if "LAVADORA" in t: return 4
    if "BICICLETA" in t or "BIKE" in t: return 5
    return 6

def icone_tipo_equipamento(tipo_str):
    t = str(tipo_str).upper()
    if "EMPILHADEIRA" in t: return "🚜"
    if "TALHA" in t or "PONTE" in t: return "🏗️"
    if "TRANSPALETEIRA" in t: return "📦"
    if "VARREDEIRA" in t or "LAVADORA" in t: return "🧹"
    if "BICICLETA" in t or "BIKE" in t: return "🚲"
    return "⚙️"

EQUIPAMENTOS_OCULTOS = {"EMP-012", "90-EMP-012"}

if not df_prev_insp.empty:
    df_prev_insp.columns = [str(c).strip().upper() for c in df_prev_insp.columns]
    col_tag = "TAG" if "TAG" in df_prev_insp.columns else df_prev_insp.columns[0]

    for _, rp in df_prev_insp.iterrows():
        tag = str(rp.get(col_tag, "")).strip().upper()
        if not tag or tag in ["NAN", "NONE", "TAG", "EQUIPAMENTO"]:
            continue
        if tag in EQUIPAMENTOS_OCULTOS or "EMP-012" in tag:
            continue

        tipo_eq = str(rp.get("TIPO_EQUIPAMENTO", rp.get("TIPO", "Outros"))).strip() or "Outros"
        disp = str(rp.get("DISPONIBILIDADE", rp.get("STATUS", "ONLINE"))).strip().upper()
        st_op = str(rp.get("STATUS_OPERACAO", "")).strip().upper()

        horim_raw = str(rp.get("HORIMETRO_ATUAL", "--")).strip()
        horim_str = formatar_horimetro_ou_data(horim_raw)
        is_por_dia = ("/" in horim_raw) or ("TALHA" in tipo_eq.upper()) or ("BICICLETA" in tipo_eq.upper())

        # Coluna H: SALDO_PREVENTIVA | Coluna N: SALDO_INSPECAO_125H
        saldo_prev_raw = rp.get("SALDO_PREVENTIVA", "--")
        saldo_insp_raw = rp.get("SALDO_INSPECAO_125H", "--")

        txt_saldo_p, lbl_p, cor_txt_p, cor_brd_p, bg_p, sev_p = analisar_saldo_manut(saldo_prev_raw, is_por_dia=is_por_dia)
        txt_saldo_i, lbl_i, cor_txt_i, cor_brd_i, bg_i, sev_i = analisar_saldo_manut(saldo_insp_raw, is_por_dia=False)

        # Coluna J: TIPO_PREVENTIVA | Coluna P: TIPO_INSPECAO
        tipo_prev_txt = str(rp.get("TIPO_PREVENTIVA", "--")).strip()
        if tipo_prev_txt.upper() in ["NAN", "NONE", ""]: tipo_prev_txt = "--"

        tipo_insp_txt = str(rp.get("TIPO_INSPECAO", "--")).strip()
        if tipo_insp_txt.upper() in ["NAN", "NONE", ""]: tipo_insp_txt = "--"

        # Coluna K: OM_PREVENTIVA | Coluna Q: OM_INSPECAO
        om_p = limpar_om_sap(rp.get("OM_PREVENTIVA", "--"))
        om_i = limpar_om_sap(rp.get("OM_INSPECAO", "--"))

        # Contabiliza Vencidas (sev == 0) e Próx. ao Vencimento (sev == 1)
        if sev_p == 0:
            qtd_venc_prev += 1
        elif sev_p == 1:
            qtd_prox_prev += 1

        if sev_i == 0:
            qtd_venc_insp += 1
        elif sev_i == 1:
            qtd_prox_insp += 1

        is_indisponivel = ("OFFLINE" in disp) or ("INDISP" in disp) or ("MANUT" in st_op)
        if is_indisponivel:
            qtd_total_indisp += 1
        else:
            qtd_total_disp += 1

        obj_eq = {
            "tag": tag,
            "tipo": tipo_eq,
            "ordem_tipo": ordem_tipo_equipamento(tipo_eq),
            "is_indisponivel": is_indisponivel,
            "horimetro": horim_str,
            "txt_saldo_p": txt_saldo_p,
            "lbl_p": lbl_p,
            "cor_txt_p": cor_txt_p,
            "cor_brd_p": cor_brd_p,
            "bg_p": bg_p,
            "sev_p": sev_p,
            "tipo_prev": tipo_prev_txt,
            "om_prev": om_p,
            "txt_saldo_i": txt_saldo_i,
            "lbl_i": lbl_i,
            "cor_txt_i": cor_txt_i,
            "cor_brd_i": cor_brd_i,
            "bg_i": bg_i,
            "sev_i": sev_i,
            "tipo_insp": tipo_insp_txt,
            "om_insp": om_i,
        }

        todos_equip_lista.append(obj_eq)
        equip_por_tipo.setdefault(tipo_eq, []).append(obj_eq)

tipos_ordenados_frota = sorted(equip_por_tipo.keys(), key=lambda k: (ordem_tipo_equipamento(k), k))
txt_base_prev = f" | 🕒 Base: {hora_att_prev.split(' ')[1][:5]}" if hora_att_prev and " " in hora_att_prev else ""

# ------------------------------------------------------------------------------
# BLOCO 8A: FROTA & EQUIPAMENTOS (SOMENTE NOMENCLATURA | HORÍMETRO | STATUS)
# ------------------------------------------------------------------------------
html_tabelas_disponibilidade = ""
if tipos_ordenados_frota:
    for tp in tipos_ordenados_frota:
        itens_tp = sorted(equip_por_tipo[tp], key=lambda x: (not x["is_indisponivel"], x["tag"]))
        linhas_eq_html = ""
        for item in itens_tp:
            if item["is_indisponivel"]:
                pill_html = '<span style="display:inline-block; min-width:86px; text-align:center; background:#E74C3C; color:#ffffff; font-size:0.68rem; font-weight:800; padding:3px 10px; border-radius:999px;">Indisponível</span>'
            else:
                pill_html = '<span style="display:inline-block; min-width:86px; text-align:center; background:#2EE65B; color:#051409; font-size:0.68rem; font-weight:900; padding:3px 10px; border-radius:999px;">Disponível</span>'

            linhas_eq_html += f"""
            <tr style="border-top:1px solid #162840;">
                <td style="padding:8px 10px; text-align:left; font-weight:800; color:#ffffff; font-size:0.82rem;">
                    {html_lib.escape(item['tag'])}
                </td>
                <td style="padding:8px 6px; text-align:center; color:#e2e8f0; font-size:0.80rem; font-family:monospace;">
                    🕒 {html_lib.escape(item['horimetro'])}
                </td>
                <td style="padding:8px 10px; text-align:right;">
                    {pill_html}
                </td>
            </tr>
            """

        html_tabelas_disponibilidade += f"""
        <div style="background:#070d18; border:1.5px solid #162d47; border-radius:14px; margin-bottom:12px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.28);">
            <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 12px; background:#0a1424;">
                <div style="display:flex; align-items:center; gap:9px;">
                    <span style="width:4px; height:20px; background:#2EE65B; border-radius:3px; display:inline-block;"></span>
                    <span style="color:#ffffff; font-size:0.92rem; font-weight:900; text-transform:uppercase; letter-spacing:0.3px;">{html_lib.escape(tp)}</span>
                </div>
                <span style="background:#14253d; color:#cbd5e1; font-size:0.74rem; font-weight:800; padding:3px 10px; border-radius:999px;">{len(itens_tp)} un.</span>
            </div>

            <table style="width:100%; border-collapse:collapse;">
                <thead>
                    <tr style="background:#092418; border-top:1px solid #144d32; border-bottom:1px solid #144d32; color:#e2e8f0; font-size:0.72rem; font-weight:800;">
                        <th style="padding:6px 10px; text-align:left; border-right:1px solid #144d32;">Nomenclatura</th>
                        <th style="padding:6px 6px; text-align:center; border-right:1px solid #144d32;">Horímetro</th>
                        <th style="padding:6px 10px; text-align:center;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {linhas_eq_html}
                </tbody>
            </table>
        </div>
        """
else:
    html_tabelas_disponibilidade = '<div style="color:#64748b; font-size:0.8rem; text-align:center; padding:14px;">Aguardando dados de equipamentos...</div>'

html_frota_disp = f"""
<div id="sec-frota"></div>
<details class="master-box" style="border-left-color:#2EE65B; margin-bottom:14px;">
    <summary>
        <div class="header-layout">
            <div class="icon-box" style="background-color:rgba(46,230,91,.15); color:#2EE65B;">🚜</div>
            <div class="master-metric-title">Frota & Equipamentos{txt_base_prev}</div>
        </div>
        <div class="value-layout">
            <div class="master-metric-val" style="color:#2EE65B;">{qtd_total_disp}</div>
            <div class="master-metric-unit">Equipamentos Disponíveis</div>
        </div>
        <div class="master-metric-sub" style="color:#cbd5e1; font-weight:700;">
            🟢 {qtd_total_disp} Disponíveis &nbsp;|&nbsp; 🔴 {qtd_total_indisp} Indisponíveis
        </div>
    </summary>

    <div class="master-content" style="padding-top:14px;">
        {html_tabelas_disponibilidade}
    </div>
</details>
"""
render_html(html_frota_disp)

# ------------------------------------------------------------------------------
# BLOCO 8B: GESTÃO DE PREVENTIVA & INSPEÇÃO (OM AZUL/BRANCO + TOPO VENC/PRÓX)
# ------------------------------------------------------------------------------
html_aba_preventiva = ""
html_aba_inspecao = ""

if tipos_ordenados_frota:
    for tp in tipos_ordenados_frota:
        ico_tp = icone_tipo_equipamento(tp)

        # --- LISTA 1: PREVENTIVAS (COLUNA H SALDO + COLUNA J TIPO + COLUNA K OM) ---
        itens_prev = sorted(equip_por_tipo[tp], key=lambda x: (x["sev_p"], x["tag"]))
        cards_prev_tp = ""
        for item in itens_prev:
            cor_txt_p = item["cor_txt_p"]
            cor_brd_p = item["cor_brd_p"]
            bg_p = item["bg_p"]
            lbl_p = item["lbl_p"]

            borda_lat_p = cor_brd_p if item["sev_p"] <= 2 else "#1c2b42"
            borda_box_p = f"1.5px solid {cor_brd_p}" if item["sev_p"] == 0 else "1px solid #162840"
            cor_val_p = cor_txt_p if item["sev_p"] <= 3 else "#64748b"

            tipo_p_badge = (
                f'<span style="background:rgba(255,140,0,0.12); border:1px solid rgba(255,140,0,0.45); color:#FF9F1C; font-size:0.65rem; font-weight:800; padding:2px 7px; border-radius:5px; white-space:nowrap;">🛠️ {html_lib.escape(item["tipo_prev"])}</span>'
                if item["tipo_prev"] != "--" else ""
            )

            # Badge da OM em AZUL com letras BRANCAS quando existir; senão "OM n/criada"
            if item["om_prev"] != "--":
                om_p_badge = f'<span style="background:#0084FF; border:1px solid #38bdf8; color:#ffffff; font-family:monospace; font-size:0.68rem; font-weight:800; padding:2px 8px; border-radius:5px; box-shadow:0 0 8px rgba(0,132,255,0.35);">OM {html_lib.escape(item["om_prev"])}</span>'
            elif item["sev_p"] <= 1:
                om_p_badge = '<span style="background:rgba(255,46,46,0.16); border:1px solid #FF2E2E; color:#ff8080; font-size:0.64rem; font-weight:900; padding:2px 7px; border-radius:5px;">OM n/criada</span>'
            else:
                om_p_badge = '<span style="background:#0a1322; border:1px solid #1a2c44; color:#64748b; font-size:0.64rem; font-weight:700; padding:2px 7px; border-radius:5px;">OM n/criada</span>'

            cards_prev_tp += f"""
            <div style="background:#070d18; border:{borda_box_p}; border-left:4px solid {borda_lat_p}; border-radius:10px; padding:9px 11px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; gap:8px;">
                <div style="min-width:0;">
                    <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap; margin-bottom:5px;">
                        <b style="color:#ffffff; font-size:0.88rem; letter-spacing:0.2px;">{html_lib.escape(item['tag'])}</b>
                        {om_p_badge}
                    </div>
                    <div style="margin-bottom:5px;">
                        {tipo_p_badge}
                    </div>
                    <div style="font-size:0.74rem; color:#94a3b8;">
                        Saldo Restante: <b style="color:{cor_val_p}; font-family:monospace; font-size:0.83rem;">{html_lib.escape(item['txt_saldo_p'])}</b>
                    </div>
                </div>
                <span style="background:{bg_p}; color:{cor_txt_p}; border:1.5px solid {cor_brd_p}; font-size:0.62rem; font-weight:900; padding:4px 8px; border-radius:7px; white-space:nowrap; flex-shrink:0; letter-spacing:0.2px;">
                    {lbl_p}
                </span>
            </div>
            """

        html_aba_preventiva += f"""
        <div style="margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem; font-weight:900; color:#FF8C00; text-transform:uppercase; letter-spacing:0.4px; margin-bottom:7px; padding-left:7px; border-left:3px solid #FF8C00;">
                <span>{ico_tp} {html_lib.escape(tp)}</span>
                <span style="color:#64748b; font-size:0.70rem;">{len(itens_prev)} un.</span>
            </div>
            {cards_prev_tp}
        </div>
        """

        # --- LISTA 2: INSPEÇÕES (COLUNA N SALDO + COLUNA P TIPO + COLUNA Q OM) ---
        itens_insp = sorted(equip_por_tipo[tp], key=lambda x: (x["sev_i"], x["tag"]))
        cards_insp_tp = ""
        for item in itens_insp:
            cor_txt_i = item["cor_txt_i"]
            cor_brd_i = item["cor_brd_i"]
            bg_i = item["bg_i"]
            lbl_i = item["lbl_i"]

            borda_lat_i = cor_brd_i if item["sev_i"] <= 2 else "#1c2b42"
            borda_box_i = f"1.5px solid {cor_brd_i}" if item["sev_i"] == 0 else "1px solid #162840"
            cor_val_i = cor_txt_i if item["sev_i"] <= 3 else "#64748b"

            tipo_i_badge = (
                f'<span style="background:rgba(56,189,248,0.12); border:1px solid rgba(56,189,248,0.45); color:#38bdf8; font-size:0.65rem; font-weight:800; padding:2px 7px; border-radius:5px; white-space:nowrap;">📋 {html_lib.escape(item["tipo_insp"])}</span>'
                if item["tipo_insp"] != "--" else ""
            )

            # Badge da OM em AZUL com letras BRANCAS quando existir; senão "OM n/criada"
            if item["om_insp"] != "--":
                om_i_badge = f'<span style="background:#0084FF; border:1px solid #38bdf8; color:#ffffff; font-family:monospace; font-size:0.68rem; font-weight:800; padding:2px 8px; border-radius:5px; box-shadow:0 0 8px rgba(0,132,255,0.35);">OM {html_lib.escape(item["om_insp"])}</span>'
            elif item["sev_i"] <= 1:
                om_i_badge = '<span style="background:rgba(255,46,46,0.16); border:1px solid #FF2E2E; color:#ff8080; font-size:0.64rem; font-weight:900; padding:2px 7px; border-radius:5px;">OM n/criada</span>'
            else:
                om_i_badge = '<span style="background:#0a1322; border:1px solid #1a2c44; color:#64748b; font-size:0.64rem; font-weight:700; padding:2px 7px; border-radius:5px;">OM n/criada</span>'

            cards_insp_tp += f"""
            <div style="background:#070d18; border:{borda_box_i}; border-left:4px solid {borda_lat_i}; border-radius:10px; padding:9px 11px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; gap:8px;">
                <div style="min-width:0;">
                    <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap; margin-bottom:5px;">
                        <b style="color:#ffffff; font-size:0.88rem; letter-spacing:0.2px;">{html_lib.escape(item['tag'])}</b>
                        {om_i_badge}
                    </div>
                    <div style="margin-bottom:5px;">
                        {tipo_i_badge}
                    </div>
                    <div style="font-size:0.74rem; color:#94a3b8;">
                        Saldo Restante: <b style="color:{cor_val_i}; font-family:monospace; font-size:0.83rem;">{html_lib.escape(item['txt_saldo_i'])}</b>
                    </div>
                </div>
                <span style="background:{bg_i}; color:{cor_txt_i}; border:1.5px solid {cor_brd_i}; font-size:0.62rem; font-weight:900; padding:4px 8px; border-radius:7px; white-space:nowrap; flex-shrink:0; letter-spacing:0.2px;">
                    {lbl_i}
                </span>
            </div>
            """

        html_aba_inspecao += f"""
        <div style="margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem; font-weight:900; color:#38bdf8; text-transform:uppercase; letter-spacing:0.4px; margin-bottom:7px; padding-left:7px; border-left:3px solid #38bdf8;">
                <span>{ico_tp} {html_lib.escape(tp)}</span>
                <span style="color:#64748b; font-size:0.70rem;">{len(itens_insp)} un.</span>
            </div>
            {cards_insp_tp}
        </div>
        """
else:
    vazio_manut = '<div style="color:#64748b; font-size:0.8rem; text-align:center; padding:14px;">Aguardando dados de preventiva e inspeção...</div>'
    html_aba_preventiva = vazio_manut
    html_aba_inspecao = vazio_manut

qtd_criticos_prev = qtd_venc_prev + qtd_prox_prev
qtd_criticos_insp = qtd_venc_insp + qtd_prox_insp
tot_alertas_manut = qtd_criticos_prev + qtd_criticos_insp
cor_borda_manut = "#FF2E2E" if tot_alertas_manut > 0 else "#E67E22"

html_prev_insp_bloco = f"""
<div id="sec-manut"></div>
<style>
    .manut-wrapper input[type="radio"] {{ display: none !important; }}

    .manut-tab-bar {{
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 14px;
        padding: 0 2px;
    }}
    .manut-tab-bar label {{
        flex: 1;
        text-align: center;
        padding: 10px 8px;
        font-size: 0.80rem;
        font-weight: 800;
        color: #94a3b8;
        background: #070d18;
        border: 1.5px solid #1c2b42;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
        white-space: nowrap;
        -webkit-tap-highlight-color: transparent;
    }}
    #tab_manut_prev:checked ~ details .lbl-manut-prev {{
        background: #FF8C00 !important;
        color: #0a101d !important;
        border-color: #FF8C00 !important;
        box-shadow: 0 0 10px rgba(255, 140, 0, 0.4);
    }}
    #tab_manut_insp:checked ~ details .lbl-manut-insp {{
        background: #38bdf8 !important;
        color: #0a101d !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
    }}

    .manut-view-prev, .manut-view-insp {{ display: none; }}
    #tab_manut_prev:checked ~ details .manut-view-prev {{ display: block; }}
    #tab_manut_insp:checked ~ details .manut-view-insp {{ display: block; }}
</style>

<div class="manut-wrapper">
    <input type="radio" name="manut_view" id="tab_manut_prev" checked>
    <input type="radio" name="manut_view" id="tab_manut_insp">

    <details class="master-box" style="border-left-color:{cor_borda_manut}; margin-bottom:14px;">
        <summary>
            <div class="header-layout">
                <div class="icon-box" style="background-color:rgba(230,126,34,.15); color:{cor_borda_manut};">🔧</div>
                <div class="master-metric-title">Gestão de Preventiva & Inspeção{txt_base_prev}</div>
            </div>
            <div class="value-layout">
                <div class="master-metric-val" style="color:{cor_borda_manut};">{tot_alertas_manut}</div>
                <div class="master-metric-unit">Pendências Identificadas</div>
            </div>
            <div style="display:flex; flex-direction:column; gap:3px; margin-top:4px; font-size:0.78rem; color:#cbd5e1;">
                <div>🛠️ <b>Preventiva:</b> <span style="color:#FF2E2E; font-weight:800;">{qtd_venc_prev} Vencidas</span> &bull; <span style="color:#FF8C00; font-weight:800;">{qtd_prox_prev} Próx. Vencimento</span></div>
                <div>📋 <b>Inspeção:</b> <span style="color:#FF2E2E; font-weight:800;">{qtd_venc_insp} Vencidas</span> &bull; <span style="color:#FF8C00; font-weight:800;">{qtd_prox_insp} Próx. Vencimento</span></div>
            </div>
        </summary>

        <div class="master-content" style="padding-top:14px;">
            <div class="manut-tab-bar">
                <label for="tab_manut_prev" class="lbl-manut-prev">🛠️ Preventiva ({qtd_criticos_prev})</label>
                <label for="tab_manut_insp" class="lbl-manut-insp">📋 Inspeção ({qtd_criticos_insp})</label>
            </div>

            <div class="manut-view-prev">
                {html_aba_preventiva}
            </div>

            <div class="manut-view-insp">
                {html_aba_inspecao}
            </div>
        </div>
    </details>
</div>
"""
render_html(html_prev_insp_bloco)


# ==============================================================================
# 🖨️ RENDERIZAÇÃO 8C: CONSUMO DE GLP (SELETOR DE MÊS COM PIZZA + HISTÓRICO)
# ==============================================================================
@st.cache_data(ttl=30)
def carregar_consolidado_glp():
    import os
    import unicodedata

    def norm_g(s):
        s_str = str(s).strip().upper()
        return "".join(c for c in unicodedata.normalize("NFD", s_str) if unicodedata.category(c) != "Mn")

    linhas_raw = []
    try:
        if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
            cliente = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        elif os.path.exists("credentials.json"):
            cliente = gspread.service_account(filename="credentials.json")
        else:
            cliente = None

        if cliente is not None:
            planilha = cliente.open_by_key(SHEET_ID)
            for ws in planilha.worksheets():
                if "CONSOLIDADO" in norm_g(ws.title) and "GLP" in norm_g(ws.title):
                    linhas_raw = ws.get_all_values()
                    break
    except Exception:
        linhas_raw = []

    if not linhas_raw:
        url_csv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Consolidado_GLP"
        try:
            r = requests.get(url_csv, timeout=10)
            r.encoding = "utf-8"
            linhas_raw = list(csv.reader(StringIO(r.text)))
        except Exception:
            linhas_raw = []

    return linhas_raw

linhas_glp_raw = carregar_consolidado_glp()

glp_meses = []
glp_maquinas = []
hora_att_glp = ""

if linhas_glp_raw:
    for r_chk in linhas_glp_raw[:15]:
        for cel in r_chk:
            cel_s = str(cel).strip()
            m_dh = re.search(r'(\d{2}/\d{2}/\d{2,4}\s+\d{2}:\d{2})', cel_s)
            if m_dh:
                hora_att_glp = m_dh.group(1).split(" ")[1][:5]
                break
        if hora_att_glp:
            break

    header_row_glp = 0
    for r_i, row in enumerate(linhas_glp_raw[:5]):
        row_u = [str(c).strip().upper() for c in row]
        if any("EQUIPAMENTO" in c for c in row_u) or any("LITROS" in c for c in row_u):
            header_row_glp = r_i
            break

    for row in linhas_glp_raw[header_row_glp + 1:]:
        # Tabela Esquerda: Consolidado Mensal (Colunas A a G)
        if len(row) > 2:
            mes_val = str(row[0]).strip()
            lit_m_val = safe_to_numeric(row[1]) if len(row) > 1 else 0.0
            kg_m_val = safe_to_numeric(row[2])
            if mes_val and mes_val.upper() not in ["NAN", "NONE", "", "MÊS", "MES", "ANO"] and (lit_m_val > 0 or kg_m_val > 0):
                t1_v = safe_to_numeric(row[3]) if len(row) > 3 else 0.0
                t2_v = safe_to_numeric(row[4]) if len(row) > 4 else 0.0
                t3_v = safe_to_numeric(row[5]) if len(row) > 5 else 0.0
                st_m_v = str(row[6]).strip() if len(row) > 6 else ""
                glp_meses.append({
                    "mes": mes_val,
                    "litros": lit_m_val,
                    "kg": kg_m_val,
                    "t1": t1_v,
                    "t2": t2_v,
                    "t3": t3_v,
                    "status": st_m_v,
                    "is_atual": "ATUAL" in st_m_v.upper()
                })

        # Tabela Direita: Consumo por Máquina (Coluna I=8 até Coluna M=12, Coluna J=9 Abastecimentos)
        if len(row) > 8:
            eq_nome = str(row[8]).strip().upper()
            if eq_nome and eq_nome not in ["NAN", "NONE", "", "EQUIPAMENTO", "TOTAL"] and eq_nome not in EQUIPAMENTOS_OCULTOS and "EMP-012" not in eq_nome:
                ab_v = int(round(safe_to_numeric(row[9]))) if len(row) > 9 else 0
                lit_e_v = safe_to_numeric(row[10]) if len(row) > 10 else 0.0
                kg_e_v = safe_to_numeric(row[11]) if len(row) > 11 else 0.0
                med_e_v = safe_to_numeric(row[12]) if len(row) > 12 else 0.0
                glp_maquinas.append({
                    "equip": eq_nome,
                    "abast": ab_v,
                    "litros": lit_e_v,
                    "kg": kg_e_v,
                    "media": med_e_v
                })

# Ordena meses cronologicamente (do mais antigo à esquerda para o mais recente/aberto à direita)
meses_cronologicos = list(reversed(glp_meses)) if (len(glp_meses) > 1 and glp_meses[0]["is_atual"]) else list(glp_meses)

# Identifica o índice do mês em aberto (padrão inicial selecionado)
idx_mes_padrao = next((i for i, m in enumerate(meses_cronologicos) if m["is_atual"]), max(0, len(meses_cronologicos) - 1))
mes_atual_obj = meses_cronologicos[idx_mes_padrao] if meses_cronologicos else None

kg_mes_atual = mes_atual_obj["kg"] if mes_atual_obj else 0.0
litros_mes_atual = mes_atual_obj["litros"] if mes_atual_obj else 0.0
rotulo_mes_atual = mes_atual_obj["mes"] if mes_atual_obj else "Mês Atual"

hora_exibir_glp = hora_att_glp if hora_att_glp else conn_hora[:5]
txt_base_glp = f" | 🕒 Atualizado em: {hora_exibir_glp}" if hora_exibir_glp else ""

# ==============================================================================
# MONTAGEM DINÂMICA DOS SELETORES DE MÊS + GRÁFICO DE PIZZA POR MÊS SELECIONADO
# ==============================================================================
radios_meses_glp = ""
css_meses_glp = ""
labels_meses_glp = ""
cards_pizza_meses_glp = ""

if meses_cronologicos:
    for idx_m, m_obj in enumerate(meses_cronologicos):
        checked_attr = "checked" if idx_m == idx_mes_padrao else ""
        radios_meses_glp += f'<input type="radio" name="glp_mes_sel" id="glp_m_{idx_m}" {checked_attr}>\n'

        cor_ativa_mes = "#00FF7F" if m_obj["is_atual"] else "#FF9F1C"
        css_meses_glp += f"""
        #glp_m_{idx_m}:checked ~ details .lbl-gm-{idx_m} {{
            background: {cor_ativa_mes} !important;
            color: #0a101d !important;
            border-color: {cor_ativa_mes} !important;
            box-shadow: 0 0 10px {cor_ativa_mes}55;
        }}
        .gm-pizza-{idx_m} {{ display: none; animation: fadeIn 0.25s ease; }}
        #glp_m_{idx_m}:checked ~ details .gm-pizza-{idx_m} {{ display: block; }}
        #glp_m_{idx_m}:checked ~ details .bar-m-highlight-{idx_m} {{
            outline: 2px solid #ffffff;
            outline-offset: 2px;
        }}
        """

        ico_m_lbl = "🟢 " if m_obj["is_atual"] else ""
        labels_meses_glp += f'<label for="glp_m_{idx_m}" class="lbl-gm-{idx_m}">{ico_m_lbl}{html_lib.escape(m_obj["mes"])}</label>'

        # Cálculos do gráfico de pizza para ESTE mês específico
        t1_v = m_obj["t1"]
        t2_v = m_obj["t2"]
        t3_v = m_obj["t3"]
        soma_t = (t1_v + t2_v + t3_v) if (t1_v + t2_v + t3_v) > 0 else 1.0
        p_t1 = max(0.0, (t1_v / soma_t) * 100.0)
        p_t2 = max(0.0, (t2_v / soma_t) * 100.0)
        p_t3 = max(0.0, (t3_v / soma_t) * 100.0)

        svg_pizza_m = f"""
        <svg width="112" height="112" viewBox="0 0 42 42" style="transform: rotate(-90deg); display: block;">
            <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#162438" stroke-width="6"></circle>
            <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#38bdf8" stroke-width="6"
                    stroke-dasharray="{p_t1:.1f} {100.0 - p_t1:.1f}" stroke-dashoffset="0"></circle>
            <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#00FF7F" stroke-width="6"
                    stroke-dasharray="{p_t2:.1f} {100.0 - p_t2:.1f}" stroke-dashoffset="-{p_t1:.1f}"></circle>
            <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#FF9F1C" stroke-width="6"
                    stroke-dasharray="{p_t3:.1f} {100.0 - p_t3:.1f}" stroke-dashoffset="-{p_t1 + p_t2:.1f}"></circle>
        </svg>
        """

        if m_obj["is_atual"]:
            borda_card_p = "#00FF7F"
            tit_status_p = f"🟢 MÊS EM ABERTO &bull; {html_lib.escape(m_obj['mes'])}"
            cor_tit_p = "#00FF7F"
            badge_dir_p = '<span style="background:rgba(0,255,127,0.14); border:1px solid #00FF7F; color:#00FF7F; font-size:0.60rem; font-weight:800; padding:3px 8px; border-radius:999px;">EM ANDAMENTO</span>'
        else:
            borda_card_p = "#FF9F1C"
            tit_status_p = f"🔒 MÊS FECHADO &bull; {html_lib.escape(m_obj['mes'])}"
            cor_tit_p = "#FF9F1C"
            badge_dir_p = '<span style="background:rgba(255,159,28,0.14); border:1px solid #FF9F1C; color:#FF9F1C; font-size:0.60rem; font-weight:800; padding:3px 8px; border-radius:999px;">CONSOLIDADO</span>'

        cards_pizza_meses_glp += f"""
        <div class="gm-pizza-{idx_m}" style="background:#070d18; border:1.5px solid #142842; border-left:4px solid {borda_card_p}; border-radius:14px; padding:12px 14px; margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; gap:6px;">
                <div>
                    <div style="font-size:0.68rem; color:{cor_tit_p}; font-weight:900; text-transform:uppercase; letter-spacing:0.4px;">{tit_status_p}</div>
                    <div style="font-size:1.15rem; color:#ffffff; font-weight:900; margin-top:2px;">
                        {fmt(m_obj['kg'], 1)} kg <span style="font-size:0.74rem; color:#64748b; font-weight:normal;">({fmt(m_obj['litros'], 1)} L)</span>
                    </div>
                </div>
                {badge_dir_p}
            </div>

            <div style="display:flex; align-items:center; justify-content:space-around; gap:12px; padding-top:4px;">
                <div style="position:relative; width:112px; height:112px; flex-shrink:0;">
                    {svg_pizza_m}
                </div>

                <div style="display:flex; flex-direction:column; gap:7px; flex:1; min-width:135px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.74rem;">
                        <span style="color:#cbd5e1; font-weight:700;"><span style="color:#38bdf8;">●</span> 00h às 08h</span>
                        <b style="color:#38bdf8; font-family:monospace;">{fmt(t1_v, 1)} kg <small style="color:#64748b;">({p_t1:.0f}%)</small></b>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.74rem;">
                        <span style="color:#cbd5e1; font-weight:700;"><span style="color:#00FF7F;">●</span> 08h às 16h</span>
                        <b style="color:#00FF7F; font-family:monospace;">{fmt(t2_v, 1)} kg <small style="color:#64748b;">({p_t2:.0f}%)</small></b>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.74rem;">
                        <span style="color:#cbd5e1; font-weight:700;"><span style="color:#FF9F1C;">●</span> 16h às 00h</span>
                        <b style="color:#FF9F1C; font-family:monospace;">{fmt(t3_v, 1)} kg <small style="color:#64748b;">({p_t3:.0f}%)</small></b>
                    </div>
                </div>
            </div>
        </div>
        """
else:
    cards_pizza_meses_glp = '<div style="color:#64748b; font-size:0.8rem; text-align:center; padding:14px;">Aguardando dados consolidados de GLP...</div>'

# Gráfico de Barras Comparativo Mês a Mês (com destaque no mês selecionado)
def montar_barras_meses_glp(lista_meses, chave_campo, cor_barra):
    if not lista_meses:
        return '<div style="color:#64748b; font-size:0.8rem; margin:auto;">Sem histórico mensal.</div>'
    max_val = max([m.get(chave_campo, 0.0) for m in lista_meses], default=1.0) or 1.0

    html_b = ""
    for idx_b, m_obj in enumerate(lista_meses):
        v_num = m_obj.get(chave_campo, 0.0)
        h_px = max(8, int((v_num / max_val) * 76))
        c_atual = "#00FF7F" if m_obj["is_atual"] else cor_barra
        tag_ab = '<div style="color:#00FF7F; font-size:0.56rem; font-weight:900; margin-top:2px;">ABERTO</div>' if m_obj["is_atual"] else '<div style="color:#64748b; font-size:0.56rem; margin-top:2px;">FECHADO</div>'

        html_b += f"""
        <label for="glp_m_{idx_b}" style="flex:1; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; min-width:56px; cursor:pointer; -webkit-tap-highlight-color:transparent;">
            <div style="color:{c_atual}; font-size:0.70rem; font-weight:800; margin-bottom:5px; white-space:nowrap;">
                {fmt(v_num, 0)} kg
            </div>
            <div class="bar-m-highlight-{idx_b}" style="width:32px; height:{h_px}px; background:{c_atual}; border-radius:6px 6px 0 0; box-shadow:0 0 10px {c_atual}44; transition:all 0.2s ease;"></div>
            <div style="width:100%; border-top:1.5px solid #1c2b42; padding-top:5px; text-align:center;">
                <div style="color:#ffffff; font-size:0.74rem; font-weight:800;">{html_lib.escape(m_obj['mes'])}</div>
                {tag_ab}
            </div>
        </label>
        """
    return html_b

barras_glp_total = montar_barras_meses_glp(meses_cronologicos, "kg", "#FF9F1C")
barras_glp_t1 = montar_barras_meses_glp(meses_cronologicos, "t1", "#38bdf8")
barras_glp_t2 = montar_barras_meses_glp(meses_cronologicos, "t2", "#00D672")
barras_glp_t3 = montar_barras_meses_glp(meses_cronologicos, "t3", "#FFD600")

html_glp_mensal = f"""
<!-- BARRA DE SELEÇÃO DO MÊS (TROCA O GRÁFICO DE PIZZA ACIMA) -->
<div style="margin-bottom:10px;">
    <div style="font-size:0.65rem; font-weight:800; color:#94a3b8; text-transform:uppercase; letter-spacing:0.4px; margin-bottom:5px; padding-left:2px;">
        📅 Selecione o Mês para Detalhar Períodos:
    </div>
    <div class="glp-mes-bar">
        {labels_meses_glp}
    </div>
</div>

<!-- CARD DINÂMICO DO GRÁFICO DE PIZZA (MÊS SELECIONADO) -->
{cards_pizza_meses_glp}

<!-- GRÁFICO COMPARATIVO MÊS A MÊS (CLIQUE NA BARRA OU NO BOTÃO DO MÊS) -->
<div style="background:#070d18; border:1.5px solid #142842; border-radius:14px; padding:12px 10px;">
    <div style="font-size:0.72rem; font-weight:800; color:#e2e8f0; text-transform:uppercase; letter-spacing:0.4px; margin-bottom:8px; padding-left:4px;">
        📊 Comparativo Mês a Mês (Toque na barra p/ abrir)
    </div>

    <div class="glp-per-bar">
        <label for="glp_p_tot" class="lbl-gp-tot">Total Mês</label>
        <label for="glp_p_t1" class="lbl-gp-t1">00h-08h</label>
        <label for="glp_p_t2" class="lbl-gp-t2">08h-16h</label>
        <label for="glp_p_t3" class="lbl-gp-t3">16h-00h</label>
    </div>

    <div class="gp-box-tot" style="display:flex; justify-content:space-around; align-items:flex-end; height:142px; gap:6px; padding:10px 4px 2px 4px;">
        {barras_glp_total}
    </div>
    <div class="gp-box-t1" style="display:flex; justify-content:space-around; align-items:flex-end; height:142px; gap:6px; padding:10px 4px 2px 4px;">
        {barras_glp_t1}
    </div>
    <div class="gp-box-t2" style="display:flex; justify-content:space-around; align-items:flex-end; height:142px; gap:6px; padding:10px 4px 2px 4px;">
        {barras_glp_t2}
    </div>
    <div class="gp-box-t3" style="display:flex; justify-content:space-around; align-items:flex-end; height:142px; gap:6px; padding:10px 4px 2px 4px;">
        {barras_glp_t3}
    </div>
</div>
"""

# ==============================================================================
# ABA 2 (SEGUNDA): POR MÁQUINA (COLUNA J = ABASTECIMENTOS NO MÊS)
# ==============================================================================
glp_maquinas.sort(key=lambda x: (-x["kg"], x["equip"]))
max_kg_maq = max([x["kg"] for x in glp_maquinas], default=1.0) or 1.0

html_glp_maquinas = ""
if glp_maquinas:
    for m_item in glp_maquinas:
        pct_bar_m = min(100.0, max(3.0, (m_item["kg"] / max_kg_maq) * 100.0)) if m_item["kg"] > 0 else 0.0
        cor_m_glp = "#FF9F1C" if m_item["kg"] > 0 else "#475569"
        txt_abast = f"{m_item['abast']} abast. no mês" if m_item["abast"] != 1 else "1 abast. no mês"

        html_glp_maquinas += f"""
        <div style="background:#070d18; border:1px solid #162840; border-left:4px solid {cor_m_glp}; border-radius:11px; padding:10px 12px; margin-bottom:8px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px; gap:6px;">
                <div style="display:flex; align-items:center; gap:7px; flex-wrap:wrap;">
                    <b style="color:#ffffff; font-size:0.92rem; letter-spacing:0.2px;">🚜 {html_lib.escape(m_item['equip'])}</b>
                    <span style="background:rgba(56,189,248,0.14); border:1px solid #38bdf8; color:#38bdf8; font-size:0.65rem; font-weight:800; padding:2px 7px; border-radius:5px; white-space:nowrap;">
                        ⛽ {txt_abast}
                    </span>
                </div>
                <div style="text-align:right; flex-shrink:0;">
                    <b style="color:{cor_m_glp}; font-size:0.95rem; font-family:monospace;">{fmt(m_item['kg'], 1)} kg</b>
                    <span style="color:#64748b; font-size:0.70rem; margin-left:3px;">({fmt(m_item['litros'], 1)} L)</span>
                </div>
            </div>

            <div style="width:100%; height:4px; background:#14243b; border-radius:999px; overflow:hidden; margin-bottom:6px;">
                <div style="width:{pct_bar_m:.1f}%; height:100%; background:linear-gradient(90deg, #FF9F1C, #FFD600); border-radius:999px;"></div>
            </div>

            <div style="display:flex; justify-content:space-between; font-size:0.70rem; color:#94a3b8;">
                <span>Média p/ ciclo: <b style="color:#e2e8f0; font-family:monospace;">{fmt(m_item['media'], 1)} kg</b></span>
                <span>Participação: <b style="color:#cbd5e1;">{(m_item['kg'] / kg_mes_atual * 100.0) if kg_mes_atual > 0 else 0:.0f}%</b></span>
            </div>
        </div>
        """
else:
    html_glp_maquinas = '<div style="color:#64748b; font-size:0.8rem; text-align:center; padding:14px;">Nenhum consumo por máquina registrado no mês.</div>'

html_glp_completo = f"""
<div id="sec-glp"></div>
<style>
    .glp-wrapper input[type="radio"] {{ display: none !important; }}

    .glp-tab-bar {{
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 14px;
        padding: 0 2px;
    }}
    .glp-tab-bar label {{
        flex: 1;
        text-align: center;
        padding: 10px 8px;
        font-size: 0.80rem;
        font-weight: 800;
        color: #94a3b8;
        background: #070d18;
        border: 1.5px solid #1c2b42;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
        white-space: nowrap;
        -webkit-tap-highlight-color: transparent;
    }}
    #tab_glp_mes:checked ~ details .lbl-glp-mes {{
        background: #FF9F1C !important;
        color: #0a101d !important;
        border-color: #FF9F1C !important;
        box-shadow: 0 0 10px rgba(255, 159, 28, 0.4);
    }}
    #tab_glp_maq:checked ~ details .lbl-glp-maq {{
        background: #38bdf8 !important;
        color: #0a101d !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
    }}

    .glp-view-mes, .glp-view-maq {{ display: none; }}
    #tab_glp_mes:checked ~ details .glp-view-mes {{ display: block; }}
    #tab_glp_maq:checked ~ details .glp-view-maq {{ display: block; }}

    /* Barra de Seleção dos Meses (p/ abrir o Gráfico de Pizza de qualquer mês) */
    .glp-mes-bar {{
        display: flex;
        gap: 6px;
        overflow-x: auto;
        padding-bottom: 2px;
    }}
    .glp-mes-bar label {{
        flex: 1;
        text-align: center;
        padding: 7px 8px;
        font-size: 0.74rem;
        font-weight: 800;
        color: #94a3b8;
        background: #070d18;
        border: 1.5px solid #1c2b42;
        border-radius: 9px;
        cursor: pointer;
        white-space: nowrap;
        transition: all 0.2s ease;
        -webkit-tap-highlight-color: transparent;
    }}
    {css_meses_glp}

    /* Mini-seletores de Período dentro do Histórico Mensal */
    .glp-per-bar {{
        display: flex;
        gap: 5px;
        margin-bottom: 6px;
    }}
    .glp-per-bar label {{
        flex: 1;
        text-align: center;
        padding: 5px 4px;
        font-size: 0.67rem;
        font-weight: 800;
        color: #94a3b8;
        background: #050911;
        border: 1px solid #1c2b42;
        border-radius: 7px;
        cursor: pointer;
        white-space: nowrap;
        -webkit-tap-highlight-color: transparent;
    }}
    #glp_p_tot:checked ~ details .lbl-gp-tot {{ background: #FF9F1C !important; color: #0a101d !important; border-color: #FF9F1C !important; }}
    #glp_p_t1:checked ~ details .lbl-gp-t1 {{ background: #38bdf8 !important; color: #0a101d !important; border-color: #38bdf8 !important; }}
    #glp_p_t2:checked ~ details .lbl-gp-t2 {{ background: #00D672 !important; color: #0a101d !important; border-color: #00D672 !important; }}
    #glp_p_t3:checked ~ details .lbl-gp-t3 {{ background: #FFD600 !important; color: #0a101d !important; border-color: #FFD600 !important; }}

    .gp-box-tot, .gp-box-t1, .gp-box-t2, .gp-box-t3 {{ display: none !important; }}
    #glp_p_tot:checked ~ details .gp-box-tot {{ display: flex !important; }}
    #glp_p_t1:checked ~ details .gp-box-t1 {{ display: flex !important; }}
    #glp_p_t2:checked ~ details .gp-box-t2 {{ display: flex !important; }}
    #glp_p_t3:checked ~ details .gp-box-t3 {{ display: flex !important; }}
</style>

<div class="glp-wrapper">
    <input type="radio" name="glp_view" id="tab_glp_mes" checked>
    <input type="radio" name="glp_view" id="tab_glp_maq">

    {radios_meses_glp}

    <input type="radio" name="glp_periodo" id="glp_p_tot" checked>
    <input type="radio" name="glp_periodo" id="glp_p_t1">
    <input type="radio" name="glp_periodo" id="glp_p_t2">
    <input type="radio" name="glp_periodo" id="glp_p_t3">

    <details class="master-box" style="border-left-color: #FF9F1C; margin-bottom: 14px;">
        <summary>
            <div class="header-layout" style="padding-right: 18px;">
                <div class="icon-box" style="background-color: rgba(255, 159, 28, 0.15); color: #FF9F1C; flex-shrink:0;">⛽</div>
                <div class="master-metric-title">Consumo de GLP — Frota{txt_base_glp}</div>
            </div>
            <div class="value-layout">
                <div class="master-metric-val" style="color: #FF9F1C;">{fmt(kg_mes_atual, 1)}</div>
                <div class="master-metric-unit">KG ({fmt(litros_mes_atual, 1)} L)</div>
            </div>
            <div class="master-metric-sub" style="color: #cbd5e1; font-weight: 700;">
                Mês Atual ({html_lib.escape(rotulo_mes_atual)}) &bull; {len(glp_maquinas)} Empilhadeiras Monitoradas
            </div>
        </summary>

        <div class="master-content" style="padding-top: 14px;">
            <div class="glp-tab-bar">
                <label for="tab_glp_mes" class="lbl-glp-mes">📊 Consumo Mensal ({len(glp_meses)})</label>
                <label for="tab_glp_maq" class="lbl-glp-maq">🚜 Por Máquina ({len(glp_maquinas)})</label>
            </div>

            <div class="glp-view-mes">
                {html_glp_mensal}
            </div>

            <div class="glp-view-maq">
                {html_glp_maquinas}
            </div>
        </div>
    </details>
</div>
"""
render_html(html_glp_completo)






# ==============================================================================
# 🖨️ RENDERIZAÇÃO 9: AUDITORIA BAFÔMETRO (H&S - ATUALIZADO EM COLUNA A)
# ==============================================================================
df_baf_atual = carregar_dados_nuvem("Bafometro_Status", cabecalho=0)
if df_baf_atual.empty and not df_bafometro.empty:
    df_baf_atual = df_bafometro.copy()

# 1. Identificação do Nome do Turno Real Vigente
letras_turnos_atuais = descobrir_letras_turnos(hoje_date)
if agora_br.hour < 8:
    letra_vigente = letras_turnos_atuais.get("madrugada", "D")
    periodo_rotulo = "Madrugada"
elif 8 <= agora_br.hour < 16:
    letra_vigente = letras_turnos_atuais.get("08_16", "C")
    periodo_rotulo = "Manhã"
else:
    letra_vigente = letras_turnos_atuais.get("16_00", "B")
    periodo_rotulo = "Tarde"

# 2. Extração do Horário da Coluna A (DATA_HORA) e Separação dos Colaboradores
lista_aprovados = []
lista_trocas = []
lista_pendentes = []
hora_base_baf = ""

if not df_baf_atual.empty:
    df_baf_atual.columns = [str(c).strip().upper() for c in df_baf_atual.columns]

    # Puxa a data/hora da Coluna A (DATA_HORA ou primeira coluna)
    col_dh_baf = "DATA_HORA" if "DATA_HORA" in df_baf_atual.columns else df_baf_atual.columns[0]
    valores_dh = [str(x).strip() for x in df_baf_atual[col_dh_baf].dropna().tolist() if str(x).strip() not in ["", "nan", "None", "DATA_HORA"]]
    if valores_dh:
        ultimo_dh_baf = valores_dh[-1]
        if " " in ultimo_dh_baf:
            hora_base_baf = ultimo_dh_baf.split(" ")[1][:5]
        else:
            hora_base_baf = ultimo_dh_baf[:5]

    c_turno = next((c for c in df_baf_atual.columns if "TURNO" in c), None)
    if c_turno:
        v_turnos = [str(x).strip() for x in df_baf_atual[c_turno].dropna().tolist() if str(x).strip() not in ["", "nan", "None", "TURNO"]]
        if v_turnos:
            periodo_rotulo = v_turnos[-1].capitalize()

    for _, r_baf in df_baf_atual.iterrows():
        colab = str(r_baf.get("COLABORADOR", "")).strip()
        if not colab or colab.upper() in ["NAN", "NONE", "", "COLABORADOR"]:
            continue

        funcao = str(r_baf.get("FUNCAO", r_baf.get("FUNÇÃO", "--"))).strip()
        status = str(r_baf.get("STATUS", "")).strip().upper()
        resultado = str(r_baf.get("RESULTADO", "")).strip().upper()

        dado_colab = {"nome": colab, "funcao": funcao, "status": status, "res": resultado}

        if any(x in status for x in ["TROCA", "NÃO CADAST", "NAO CADAST"]) or "TROCA" in resultado:
            lista_trocas.append(dado_colab)
        elif any(x in status for x in ["PEND", "FALTA", "NÃO REALIZ", "NAO REALIZ"]) or any(x in resultado for x in ["PEND", "FALTA"]):
            lista_pendentes.append(dado_colab)
        elif any(x in status for x in ["REALIZ", "APROV", "OK"]) or any(x in resultado for x in ["APROV", "OK", "0.00", "0,00", "NEGATIVO"]):
            lista_aprovados.append(dado_colab)
        else:
            lista_pendentes.append(dado_colab)

total_registrados_baf = len(lista_aprovados) + len(lista_trocas) + len(lista_pendentes)
nome_turno_completo = f"Turno {letra_vigente} ({periodo_rotulo})"
txt_base_baf = f" | 🕒 Atualizado em: {hora_base_baf}" if hora_base_baf else ""
cor_borda_baf = "#E74C3C" if len(lista_pendentes) > 0 else "#00D672"

# 3. Ordem de Hierarquia das Funções
def obter_ordem_funcao(funcao_str):
    f_up = funcao_str.upper()
    if "LÍDER" in f_up or "LIDER" in f_up: return 1
    elif "ASS" in f_up or "ASSIST" in f_up: return 2
    elif "EMP" in f_up or "OPERADOR" in f_up: return 3
    elif "AUX" in f_up: return 4
    elif "MEC" in f_up or "MECÂNICO" in f_up or "MECANICO" in f_up: return 5
    return 6

def agrupar_e_renderizar_aprovados(colaboradores):
    if not colaboradores:
        return "<div style='color:#64748b; font-size:0.75rem; padding:6px 8px;'>Nenhum colaborador nesta seção.</div>"
    colaboradores_ordenados = sorted(colaboradores, key=lambda x: (obter_ordem_funcao(x["funcao"]), x["nome"]))
    grupos = {
        1: ("LÍDER", []),
        2: ("ASSISTENTE", []),
        3: ("OPERADOR DE EMPILHADEIRA", []),
        4: ("AUXILIAR DE EXPEDIÇÃO", []),
        5: ("MECÂNICO", []),
        6: ("OUTRAS FUNÇÕES", [])
    }
    for c in colaboradores_ordenados:
        grupos[obter_ordem_funcao(c["funcao"])][1].append(c)
    html_out = ""
    for _, (rotulo, membros) in grupos.items():
        if not membros:
            continue
        html_out += f'<div style="font-size:0.70rem; font-weight:800; color:#94a3b8; letter-spacing:0.4px; margin-top:8px; margin-bottom:4px; padding-left:4px; border-left:2px solid #00D672;">{rotulo} ({len(membros)})</div>'
        for item in membros:
            html_out += f'<div style="display:flex; justify-content:space-between; align-items:center; padding:5px 8px; border-bottom:1px dashed #1c2b42; font-size:0.78rem;"><div><b style="color:#ffffff;">{html_lib.escape(item["nome"])}</b><div style="color:#64748b; font-size:0.67rem;">{html_lib.escape(item["funcao"])}</div></div><span style="color:#00D672; font-weight:800; font-size:0.72rem;">{html_lib.escape(item["res"] or item["status"])}</span></div>'
    return html_out

def renderizar_itens_simples(lista_dados, cor_texto, texto_padrao):
    if not lista_dados:
        return "<div style='color:#64748b; font-size:0.75rem; padding:6px 8px;'>Nenhum colaborador nesta seção.</div>"
    h = ""
    for item in sorted(lista_dados, key=lambda x: x["nome"]):
        badge_txt = item["res"] if item["res"] and item["res"] not in ["--", "NAN", "NONE"] else (item["status"] or texto_padrao)
        h += f'<div style="display:flex; justify-content:space-between; align-items:center; padding:6px 8px; border-bottom:1px dashed #1c2b42; font-size:0.78rem;"><div><b style="color:#ffffff;">{html_lib.escape(item["nome"])}</b><div style="color:#64748b; font-size:0.67rem;">{html_lib.escape(item["funcao"])}</div></div><span style="color:{cor_texto}; font-weight:800; font-size:0.72rem;">{html_lib.escape(badge_txt)}</span></div>'
    return h

# 4. Renderização do Card Bafômetro (Sempre fechado ao carregar + Atualizado em da Coluna A)
html_baf_final = f"""
<div id="sec-baf"></div>
<details class="master-box" style="border-left-color: {cor_borda_baf}; margin-bottom: 14px;">
    <summary>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; padding-right: 18px;">
            <div class="header-layout" style="margin-bottom: 0;">
                <div class="icon-box" style="background-color: rgba(255, 255, 255, 0.12); color: {cor_borda_baf}; flex-shrink:0;">🩺</div>
                <div class="master-metric-title">Auditoria Bafômetro (H&S{txt_base_baf})</div>
            </div>
        </div>
        <div class="value-layout" style="margin-bottom: 2px;">
            <div class="master-metric-val">{total_registrados_baf}</div>
            <div class="master-metric-unit">Colaboradores Auditados</div>
        </div>
        <div class="master-metric-sub" style="color: #cbd5e1; font-weight: bold;">
            {nome_turno_completo} &nbsp;|&nbsp; <span style="color:#E74C3C;">🔴 {len(lista_pendentes)} Pendentes</span> &bull; <span style="color:#38bdf8;">🔄 {len(lista_trocas)} Trocas</span> &bull; <span style="color:#00D672;">🟢 {len(lista_aprovados)} OK</span>
        </div>
    </summary>

    <div class="master-content" style="padding-top: 14px;">
        <!-- SEÇÃO 1 (TOPO): NÃO REALIZADOS / PENDENTES -->
        <div style="background:#070d18; border:1px solid #142842; border-left:3.5px solid #E74C3C; border-radius:10px; padding:10px; margin-bottom:10px;">
            <div style="font-size:0.75rem; font-weight:800; color:#E74C3C; text-transform:uppercase; margin-bottom:6px;">
                🚨 NÃO REALIZADOS / PENDENTES ({len(lista_pendentes)})
            </div>
            {renderizar_itens_simples(lista_pendentes, '#E74C3C', 'PENDENTE')}
        </div>

        <!-- SEÇÃO 2: TROCAS -->
        <div style="background:#070d18; border:1px solid #142842; border-left:3.5px solid #38bdf8; border-radius:10px; padding:10px; margin-bottom:10px;">
            <div style="font-size:0.75rem; font-weight:800; color:#38bdf8; text-transform:uppercase; margin-bottom:6px;">
                🔄 TROCAS / NÃO CADASTRADOS ({len(lista_trocas)})
            </div>
            {renderizar_itens_simples(lista_trocas, '#38bdf8', 'TROCA')}
        </div>

        <!-- SEÇÃO 3: APROVADOS -->
        <div style="background:#070d18; border:1px solid #142842; border-left:3.5px solid #00D672; border-radius:10px; padding:10px; margin-bottom: 6px;">
            <div style="font-size:0.75rem; font-weight:800; color:#00D672; text-transform:uppercase; margin-bottom:4px;">
                ✅ APROVADOS ({len(lista_aprovados)})
            </div>
            {agrupar_e_renderizar_aprovados(lista_aprovados)}
        </div>
    </div>
</details>
"""
render_html(html_baf_final)


# ==============================================================================
# 🖨️ RENDERIZAÇÃO 10: COMPARATIVO ANUAL (LENDO ABA PARAMETROS_ANO - SEMPRE FECHADO)
# ==============================================================================
def parse_num_planilha_ano(val_raw):
    if val_raw is None or pd.isna(val_raw):
        return 0.0
    s = re.sub(r'[^\d,\.\-]', '', str(val_raw).strip())
    if not s or s in ["-", "."]:
        return 0.0
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    elif "." in s:
        partes = s.split(".")
        # Se o trecho após o ponto tem exatamente 3 dígitos (ex: 3.468 ou 1.604.858), é milhar PT-BR
        if len(partes[-1]) == 3:
            s = s.replace(".", "")
    try:
        return float(s)
    except Exception:
        return 0.0

df_param_ano, _ = carregar_tabela_cega("Parametros_Ano", "PARAMETRO")
if df_param_ano.empty:
    df_param_ano = carregar_dados_nuvem("Parametros_Ano", cabecalho=0)

params_ano_map = {}
data_ref_ano = ""

if not df_param_ano.empty:
    df_param_ano.columns = [str(c).strip().upper() for c in df_param_ano.columns]
    for _, r_pa in df_param_ano.iterrows():
        chave_p = str(r_pa.get("PARAMETRO", "")).strip().upper()
        if not chave_p or chave_p in ["NAN", "NONE", "PARAMETRO"]:
            continue
        params_ano_map[chave_p] = parse_num_planilha_ano(r_pa.get("VALOR", 0))
        dt_p = str(r_pa.get("DATA", "")).strip()
        if dt_p and dt_p not in ["-", "--", "nan", "None"] and not data_ref_ano:
            data_ref_ano = dt_p

d_res = max(1, (date(hoje_date.year, 12, 31) - hoje_date).days)

# Resgata parâmetros oficiais da aba Parametros_Ano
carr_base_ano = params_ano_map.get("CARREGAMENTO_BASE", 0.0)
prod_base_ano = params_ano_map.get("PRODUCAO_BASE", 0.0)
meta_est_ano = forcar_par(params_ano_map.get("META_ESTOQUE_ANO", 3468.0))
if meta_est_ano < 100:
    meta_est_ano = 3468
carr_dia_aba = params_ano_map.get("CARREGAMENTO_DIA", 0.0)
prod_dia_aba = params_ano_map.get("PRODUCAO_DIA", 0.0)
tot_carr_aba = params_ano_map.get("TOTAL_CARREGAMENTO", 0.0)
tot_prod_aba = params_ano_map.get("TOTAL_PRODUCAO", 0.0)

if carr_base_ano > 0:
    ca_at = forcar_par(max(tot_carr_aba, carr_base_ano + max(vol_hoje, carr_dia_aba)))
else:
    ca_at = forcar_par(tot_carr_aba if tot_carr_aba > 0 else (1604858.0 + vol_hoje))

if prod_base_ano > 0:
    pa_at = forcar_par(max(tot_prod_aba, prod_base_ano + max(prod_hoje_calc, prod_dia_aba)))
else:
    pa_at = forcar_par(tot_prod_aba if tot_prod_aba > 0 else (1607494.0 + prod_hoje_calc))

df_pc = forcar_par(abs(pa_at - ca_at))

if ca_at >= pa_at:
    tv, cv = f"+{fmt(df_pc)} t (Expedição Superando)", "#00D672"
else:
    tv, cv = f"+{fmt(df_pc)} t (Produção Superando)", "#FF9F1C"

mdc = forcar_par(5200.0 + (max(0.0, estoque_total - meta_est_ano) / d_res))
ppf = forcar_par(pa_at + (d_res * 5200.0))
pcf = forcar_par(ca_at + ((estoque_total + (d_res * 5200.0)) - meta_est_ano))

txt_base_ano = f" | 🕒 Base: {data_ref_ano}" if data_ref_ano else ""

h_an = f"""
<details class="master-box" style="border-left-color:#007BFF;">
    <summary>
        <div class="header-layout">
            <div class="icon-box" style="background-color:rgba(0,123,255,.15); color:#007BFF;">📊</div>
            <div class="master-metric-title">Comparativo Produção vs Expedição{txt_base_ano}</div>
        </div>
        <div class="value-layout">
            <div class="master-metric-val">{fmt(ca_at)}</div>
            <div class="master-metric-unit">t Expedidas</div>
        </div>
        <div class="master-metric-sub" style="color:#007BFF;">Meta Diária Necessária: {fmt(mdc)} t/dia</div>
    </summary>
    <div class="master-content" style="padding-top:16px;">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px;">
            <div style="background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:10px;">
                <div style="font-size:0.75rem; color:#007BFF; font-weight:bold;">EXPEDIÇÃO ANUAL</div>
                <div style="font-size:1.4rem; font-weight:bold; color:#fff; margin:4px 0;">{fmt(ca_at)} <span style="font-size:0.8rem; color:#64748b; font-weight:normal;">t</span></div>
                <div style="font-size:0.7rem; color:#64748b;">Proj. 31/12: <span style="color:#007BFF;">{fmt(pcf)} t</span></div>
            </div>
            <div style="background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:10px;">
                <div style="font-size:0.75rem; color:#00D672; font-weight:bold;">PRODUÇÃO ANUAL</div>
                <div style="font-size:1.4rem; font-weight:bold; color:#fff; margin:4px 0;">{fmt(pa_at)} <span style="font-size:0.8rem; color:#64748b; font-weight:normal;">t</span></div>
                <div style="font-size:0.7rem; color:#64748b;">Proj. 31/12: <span style="color:#00D672;">{fmt(ppf)} t</span></div>
            </div>
        </div>
        <div style="background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:12px; font-size:0.82rem; color:#cbd5e1; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;">
            <span>Variação: <span style="color:{cv}; font-weight:bold;">{tv}</span></span>
            <span>Estoque Meta: <span style="color:#38bdf8; font-weight:bold;">{fmt(meta_est_ano)} t</span></span>
        </div>
    </div>
</details>
"""
render_html(h_an)



# ==============================================================================
# 🖨️ RENDERIZAÇÃO 11: TELEMETRIA & LOGS DO CORE (PAINEL DEVELOPER)
# ==============================================================================
with st.expander("🛠️ Console de Telemetria & Logs do Core (Dev)", expanded=False):
    col_dev_btn, _ = st.columns([1, 2])
    with col_dev_btn:
        if st.button("🔄 Atualizar Logs", key="btn_refresh_logs", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    df_logs = carregar_ultimos_logs_core()

    if df_logs.empty:
        st.info("Nenhum log disponível na aba Live_Logs_Core no momento.")
    else:
        # 1. Indicador de Pulso (Heartbeat)
        ultimo_log_str = str(df_logs.iloc[0]["DATA_HORA"]).strip()
        try:
            dt_ult = datetime.strptime(ultimo_log_str[:19], "%d/%m/%Y %H:%M:%S")
            minutos_atras = max(0.0, (agora_br - dt_ult).total_seconds() / 60.0)
        except Exception:
            minutos_atras = 0.0

                # Função para identificar APENAS falhas e erros reais do Core
        def eh_erro_ou_alerta_real(texto):
            t = str(texto).upper()
            # Se for log de sincronização rotineira do SAP, IGNORA (é fluxo normal!)
            if "SINCRONIZAÇÃO CONCLUÍDA" in t or "SINCRONIZACAO CONCLUIDA" in t:
                return False
            # Termos que representam quedas, falhas e intervenções reais
            termos_falha = [
                "ERRO", "FALHA", "CRÍTICO", "CRITICO", "DEADLOCK", 
                "HARD KILL", "MODO DE RECUPERAÇÃO", "MODO DE RECUPERACAO", 
                "REINICIANDO EM", "SEM CONEXÃO", "SEM CONEXAO"
            ]
            if any(termo in t for termo in termos_falha):
                return True
            if "❌" in t and "EXCLUÍDA" not in t and "EXCLUIDA" not in t:
                return True
            if "🚨" in t and "TEMPO CRÍTICO" not in t:
                return True
            return False

        # 2. Contador de Erros Reais
        mask_erros = df_logs["EVENTO"].apply(eh_erro_ou_alerta_real)
        erros_df = df_logs[mask_erros]
        qtd_erros = len(erros_df)


        # 3. Filtros Rápidos Mobile
        f_c1, f_c2 = st.columns([1, 1])
        with f_c1:
            so_erros = st.toggle("🚨 Apenas Alertas / Erros", value=False)
        with f_c2:
            modulos = ["TODOS"] + sorted([m for m in df_logs["MODULO"].dropna().unique().tolist() if m])
            mod_sel = st.selectbox("Módulo:", modulos, label_visibility="collapsed")

        df_show = df_logs.copy()
        if so_erros:
            df_show = df_show[df_show["EVENTO"].astype(str).str.contains("❌|🚨|⚠️|ERRO|CRÍTICO|Falha", case=False, na=False)]
        if mod_sel != "TODOS":
            df_show = df_show[df_show["MODULO"] == mod_sel]

        # 4. Container com Rolagem Estilo Terminal Hacker
        st.caption(f"Exibindo {len(df_show)} eventos recentes:")
        container_terminal = st.container(height=360)
        with container_terminal:
            for _, r_log in df_show.iterrows():
                ev = str(r_log["EVENTO"])
                mod = str(r_log["MODULO"])
                hora_log = str(r_log["DATA_HORA"]).split(" ")[-1] if " " in str(r_log["DATA_HORA"]) else str(r_log["DATA_HORA"])

                # Cores dinâmicas por gravidade
                if any(x in ev.upper() for x in ["❌", "🚨", "ERRO", "CRÍTICO", "FALHA"]):
                    borda_c, txt_c, bg_c = "#EF4444", "#FCA5A5", "#241010"
                elif any(x in ev.upper() for x in ["⚠️", "ATENÇÃO", "PAUSA"]):
                    borda_c, txt_c, bg_c = "#F59E0B", "#FDE68A", "#261A08"
                elif "✅" in ev:
                    borda_c, txt_c, bg_c = "#10B981", "#A7F3D0", "#081E15"
                else:
                    borda_c, txt_c, bg_c = "#12506e", "#CBD5E1", "#08111f"

                st.markdown(
                    f"""
                    <div style="background:{bg_c}; border-left: 3px solid {borda_c}; border-radius: 6px; padding: 6px 10px; margin-bottom: 6px; font-family: monospace; font-size: 0.72rem; line-height: 1.3;">
                        <span style="color:#64748B;">[{hora_log}]</span> 
                        <b style="color:#38bdf8;">[{mod}]</b><br>
                        <span style="color:{txt_c};">{html_lib.escape(ev)}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ==============================================================================
# 📸 GERADOR DE PRINT RETRATO MOBILE (LETRAS GRANDES + ZERO PESO NO ANDROID)
# ==============================================================================
import os
import base64
from io import BytesIO
import PIL
from PIL import Image, ImageDraw, ImageFont

def _carregar_fonte_png(tamanho, bold=True):
    pil_dir = os.path.dirname(PIL.__file__)
    caminhos = [
        os.path.join(pil_dir, "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for c_f in caminhos:
        if os.path.exists(c_f):
            try:
                return ImageFont.truetype(c_f, tamanho)
            except Exception:
                pass
    try:
        return ImageFont.load_default(size=tamanho)
    except Exception:
        return ImageFont.load_default()

def gerar_card_mobile_png(chave_bloco: str) -> bytes:
    """Gera imagem vertical 720px (formato celular) com tipografia grande e visual idêntico ao Mobile."""
    cor_tema = (0, 214, 114)
    titulo = ""
    kpi_big = ""
    kpi_unit = ""
    sub_1 = ""
    sub_2 = ""
    pct_barra = None
    secoes = []

    if chave_bloco == "prev":
        cor_tema = (0, 180, 255)
        titulo = "PREVISÕES DO DIA (24H)"
        kpi_big = f"{fmt(prev_prod)} t | {fmt(prev_carr)} t"
        kpi_unit = ""
        sub_1 = "Projeção Consolidada de Fechamento 24 Horas"
        secoes = [
            ("SEC", "PROJEÇÃO DE PRODUÇÃO", (0, 180, 255)),
            ("ROW", "Prev. Fechamento (24h)", f"{fmt(prev_prod)} t", (255, 255, 255)),
            ("ROW", "Realizado até agora", f"{fmt(prod_hoje_calc)} t", (229, 184, 0)),
            ("SEC", "PROJEÇÃO DE CARREGAMENTO", (0, 230, 118)),
            ("ROW", "Prev. Fechamento (24h)", f"{fmt(prev_carr)} t", (0, 230, 118)),
            ("ROW", "Expedido até agora", f"{fmt(vol_hoje)} t", (56, 189, 248)),
        ]

    elif chave_bloco == "prod":
        cor_tema = (229, 184, 0)
        titulo = "PRODUÇÃO DE CELULOSE"
        kpi_big = fmt(prod_hoje_calc)
        kpi_unit = "TON"
        sub_1 = f"MS1: {fmt(dados_maquinas['MS1'].get('producao', 0))} t  |  MS2: {fmt(dados_maquinas['MS2'].get('producao', 0))} t"
        sub_2 = f"Prev. Fechamento: {fmt(prev_prod)} t"
        for m_k in ["MS1", "MS2"]:
            qm = dados_maquinas.get(m_k, {})
            if qm:
                qt = qm.get("qualidade_tipo", "EQ")
                c_q = (231, 76, 60) if qt in ["OS", "BQ"] else ((255, 214, 0) if qt == "SQ" else (0, 214, 114))
                info_v = viradas_info.get(m_k, {})
                secoes.append(("SEC", f"{m_k} • MAT {qm.get('material', '--')} [{qt}] — {fmt(qm.get('producao', 0))} t", c_q))
                secoes.append(("ROW", "Linhas A/B ou C/D", f"{fmt(qm.get('l1', 0))} t  |  {fmt(qm.get('l2', 0))} t", (56, 189, 248)))
                secoes.append(("ROW", "Alvura  /  Sujidade", f"{fmt(qm.get('alvura', 0), 2)}%  |  {fmt(qm.get('sujidade', 0), 2)}", (255, 255, 255)))
                secoes.append(("ROW", "Viscosidade  /  pH", f"{fmt(qm.get('viscosidade', 0))}  |  pH {fmt(qm.get('ph', 0), 1)}", (255, 255, 255)))
                secoes.append(("ROW", "Próxima Virada", f"MAT {info_v.get('prox_mat', '--')} • {info_v.get('prev_virada', '--')}", (255, 159, 28)))

    elif chave_bloco == "est":
        cor_tema = (0, 255, 127)
        titulo = "ESTOQUE FÍSICO NO ARMAZÉM"
        kpi_big = fmt(estoque_total)
        kpi_unit = "TON"
        sub_1 = f"Ocupação: {fmt(estoque_total)} t de 25.000 t ({pct_ocupacao_est:.0f}%)"
        sub_2 = f"Espaço Livre: {fmt(espaco_livre_est)} t  |  Cap.: 25.000 t"
        pct_barra = pct_ocupacao_est
        secoes.append(("SEC", "CLASSE DE QUALIDADE", (0, 255, 127)))
        secoes.append(("ROW", "On-Grade (EQ)", f"{fmt(tot_on_grade)} t ({pct_on_grade:.0f}%)", (0, 255, 127)))
        secoes.append(("ROW", "Off-Grade (SQ/BQ/OS)", f"{fmt(tot_off_grade)} t ({pct_off_grade:.0f}%)", (255, 140, 0)))
        secoes.append(("SEC", "MATERIAIS EM ESTOQUE", (56, 189, 248)))
        for it_e in itens_estoque:
            c_cls = (0, 255, 127) if it_e["classe"] == "EQ" else ((255, 214, 0) if it_e["classe"] == "SQ" else ((255, 140, 0) if it_e["classe"] == "BQ" else (255, 46, 46)))
            secoes.append(("ROW", f"MAT {it_e['material']}  [{it_e['classe']}]", f"{fmt(it_e['ton'])} t", c_cls))

    elif chave_bloco == "exp":
        cor_tema = (0, 214, 114)
        titulo = "EXPEDIÇÃO REALIZADA"
        kpi_big = fmt(vol_hoje)
        kpi_unit = "TON"
        sub_1 = f"Consolidado Ontem (D-1): {fmt(vol_ontem)} t"
        sub_2 = f"Progresso: {fmt(vol_hoje)} t de {fmt(prev_carr)} t ({pct_prog:.0f}%)"
        pct_barra = pct_prog
        secoes.append(("SEC", "TURNOS EM OPERAÇÃO HOJE", (0, 214, 114)))
        for th in tns_hoje:
            v_s = th.get("str_vol", f"{fmt(th['v'])} t")
            c_t = (231, 76, 60) if v_s == "EM FOLGA" else (255, 255, 255)
            secoes.append(("ROW", f"{th['letra']} ({th['horario']})", v_s, c_t))
        if balanco_destinos:
            secoes.append(("SEC", "PLANO VS EXPEDIDO POR DESTINO", (56, 189, 248)))
            for bd in balanco_destinos:
                c_bd = (0, 214, 114) if bd["atingimento"] >= 100 else (56, 189, 248)
                nome_d_curto = bd["destino"][:24]
                secoes.append(("ROW", f"{nome_d_curto} ({bd['atingimento']:.0f}%)", f"{fmt(bd['realizado'])}/{fmt(bd['meta'])} t", c_bd))
            secoes.append(("ROW", "TOTAL PENDENTE", f"{fmt(total_expedicao_falta)} t", (255, 159, 28)))

    elif chave_bloco == "ped":
        cor_tema = (0, 132, 255)
        titulo = "ANÁLISE DE PEDIDOS (ZLE087)"
        kpi_big = fmt(tot_saldo_geral)
        kpi_unit = "TON PENDENTES"
        sub_1 = f"Transf.: {fmt(tot_saldo_transf)} t ({len(pedidos_transf)} ped.)"
        sub_2 = f"MI / LATAM: {fmt(tot_saldo_mi)} t ({len(pedidos_mi)} ped.)"
        if pedidos_transf:
            secoes.append(("SEC", f"TRANSFERÊNCIA ({len(pedidos_transf)} PED.)", (0, 132, 255)))
            for pt in pedidos_transf:
                c_p = (255, 46, 46) if pt["is_fim"] else (56, 189, 248)
                secoes.append(("ROW", f"{pt['destino'][:20]} • {pt['material']}", f"{fmt(pt['saldo'])} t", c_p))
        if pedidos_mi:
            secoes.append(("SEC", f"MI / LATAM ({len(pedidos_mi)} PED.)", (0, 214, 114)))
            for pm in pedidos_mi:
                c_m = (255, 46, 46) if pm["is_fim"] else (0, 214, 114)
                secoes.append(("ROW", f"{pm['destino'][:20]} • {pm['material']}", f"{fmt(pm['saldo'])} t", c_m))

    elif chave_bloco == "patio":
        cor_tema = (56, 169, 255)
        titulo = "PÁTIO DA FÁBRICA (TEMPO REAL)"
        kpi_big = str(total_veiculos_fisicos)
        kpi_unit = "VEÍCULOS FÍSICOS"
        sub_1 = f"Carga Disponível: {fmt(vol_patio_disponivel)} t"
        secoes.append(("SEC", "VEÍCULOS POR ETAPA", (56, 169, 255)))
        for tit_p, chv_p, _, _, _, _ in mapa_status_colunas:
            dp = dados_patio.get(chv_p, {"veiculos": 0, "peso": 0})
            secoes.append(("ROW", tit_p, f"{dp['veiculos']} veíc. ({fmt(dp['peso'])} t)", (255, 255, 255)))

    elif chave_bloco == "frota":
        cor_tema = (46, 230, 91)
        titulo = "FROTA & EQUIPAMENTOS"
        kpi_big = str(qtd_total_disp)
        kpi_unit = "DISPONÍVEIS"
        sub_1 = f"Disponíveis: {qtd_total_disp}  |  Indisponíveis: {qtd_total_indisp}"
        secoes.append(("SEC", "STATUS POR CATEGORIA", (46, 230, 91)))
        for tp_f in tipos_ordenados_frota:
            ltp = equip_por_tipo.get(tp_f, [])
            d_c = sum(1 for x in ltp if not x["is_indisponivel"])
            i_c = sum(1 for x in ltp if x["is_indisponivel"])
            c_f = (231, 76, 60) if i_c > 0 else (46, 230, 91)
            secoes.append(("ROW", tp_f, f"{d_c} Disp. / {i_c} Indisp.", c_f))

    elif chave_bloco == "manut":
        cor_tema = (255, 46, 46) if tot_alertas_manut > 0 else (230, 126, 34)
        titulo = "PREVENTIVA & INSPEÇÃO"
        kpi_big = str(tot_alertas_manut)
        kpi_unit = "PENDÊNCIAS"
        sub_1 = f"Prev.: {qtd_venc_prev} Venc. • {qtd_prox_prev} Próx. Venc."
        sub_2 = f"Insp.: {qtd_venc_insp} Venc. • {qtd_prox_insp} Próx. Venc."
        criticos = [e for e in todos_equip_lista if e["sev_p"] <= 1 or e["sev_i"] <= 1]
        secoes.append(("SEC", "EQUIPAMENTOS CRÍTICOS", (255, 140, 0)))
        for eq_c in criticos:
            pts = []
            if eq_c["sev_p"] <= 1:
                pts.append(f"Prev: {eq_c['txt_saldo_p']}")
            if eq_c["sev_i"] <= 1:
                pts.append(f"Insp: {eq_c['txt_saldo_i']}")
            secoes.append(("ROW", eq_c["tag"], " | ".join(pts), (255, 46, 46)))
        if not criticos:
            secoes.append(("ROW", "Status Geral", "Nenhuma pendência crítica", (0, 255, 127)))

    elif chave_bloco == "glp":
        cor_tema = (255, 159, 28)
        titulo = "CONSUMO DE GLP — FROTA"
        kpi_big = f"{fmt(kg_mes_atual, 1)}"
        kpi_unit = f"KG ({fmt(litros_mes_atual, 1)} L)"
        sub_1 = f"Mês Atual ({rotulo_mes_atual}) • {len(glp_maquinas)} Empilhadeiras"
        if mes_atual_obj:
            secoes.append(("SEC", f"POR TURNO ({rotulo_mes_atual})", (0, 255, 127)))
            secoes.append(("ROW", "00h às 08h", f"{fmt(mes_atual_obj['t1'], 1)} kg", (56, 189, 248)))
            secoes.append(("ROW", "08h às 16h", f"{fmt(mes_atual_obj['t2'], 1)} kg", (0, 255, 127)))
            secoes.append(("ROW", "16h às 00h", f"{fmt(mes_atual_obj['t3'], 1)} kg", (255, 159, 28)))
        secoes.append(("SEC", "POR EMPILHADEIRA", (255, 159, 28)))
        for mq_g in glp_maquinas:
            secoes.append(("ROW", f"{mq_g['equip']} ({mq_g['abast']} ab.)", f"{fmt(mq_g['kg'], 1)} kg", (255, 255, 255)))

    elif chave_bloco == "baf":
        cor_tema = (231, 76, 60) if len(lista_pendentes) > 0 else (0, 214, 114)
        titulo = "AUDITORIA BAFÔMETRO (H&S)"
        kpi_big = str(total_registrados_baf)
        kpi_unit = "AUDITADOS"
        sub_1 = f"{nome_turno_completo}"
        sub_2 = f"Pendentes: {len(lista_pendentes)} | Trocas: {len(lista_trocas)} | OK: {len(lista_aprovados)}"
        secoes.append(("SEC", "RESUMO DO TURNO", cor_tema))
        secoes.append(("ROW", "Aprovados / Realizados", f"{len(lista_aprovados)} colab.", (0, 214, 114)))
        secoes.append(("ROW", "Trocas / Não Cadastrados", f"{len(lista_trocas)} colab.", (56, 189, 248)))
        secoes.append(("ROW", "Não Realizados / Pendentes", f"{len(lista_pendentes)} colab.", (231, 76, 60)))
        if lista_pendentes:
            secoes.append(("SEC", "COLABORADORES PENDENTES", (231, 76, 60)))
            for pb in lista_pendentes:
                secoes.append(("ROW", pb["nome"][:24], pb["funcao"][:18], (255, 128, 128)))

    else:
        cor_tema = (0, 123, 255)
        titulo = "COMPARATIVO ANUAL"
        kpi_big = f"{fmt(ca_at)}"
        kpi_unit = "t EXPEDIDAS"
        sub_1 = f"Meta Diária Necessária: {fmt(mdc)} t/dia"
        sub_2 = tv
        secoes = [
            ("SEC", "ACUMULADO NO ANO", (0, 123, 255)),
            ("ROW", "Expedição Anual", f"{fmt(ca_at)} t", (0, 123, 255)),
            ("ROW", "Produção Anual", f"{fmt(pa_at)} t", (0, 214, 114)),
            ("SEC", "PROJEÇÃO 31/12", (56, 189, 248)),
            ("ROW", "Proj. Expedição", f"{fmt(pcf)} t", (56, 189, 248)),
            ("ROW", "Proj. Produção", f"{fmt(ppf)} t", (167, 243, 208)),
            ("ROW", "Estoque Meta Ano", f"{fmt(meta_est_ano)} t", (255, 255, 255)),
        ]

    if not secoes:
        secoes.append(("ROW", "Status", "Aguardando dados", (148, 163, 184)))

    # Fontes GRANDES calibradas para 720px de largura (leitura perfeita no WhatsApp do celular)
    f_brand = _carregar_fonte_png(30, True)
    f_brand_sub = _carregar_fonte_png(17, False)
    f_tit = _carregar_fonte_png(23, True)
    f_kpi = _carregar_fonte_png(64 if len(kpi_big) <= 8 else 44, True)
    f_unit = _carregar_fonte_png(24, True)
    f_sub = _carregar_fonte_png(20, False)
    f_sec = _carregar_fonte_png(19, True)
    f_row = _carregar_fonte_png(22, False)
    f_row_b = _carregar_fonte_png(23, True)
    f_foot = _carregar_fonte_png(16, False)

    largura = 720
    alt_cab = 320 + (32 if sub_2 else 0) + (28 if pct_barra is not None else 0)
    alt_linhas = sum(46 if s[0] == "SEC" else 60 for s in secoes)
    altura = alt_cab + alt_linhas + 64

    img = Image.new("RGB", (largura, altura), (5, 9, 17))
    draw = ImageDraw.Draw(img)

    # Moldura externa neon arredondada
    draw.rounded_rectangle([12, 12, largura - 12, altura - 12], radius=24, fill=(11, 24, 48), outline=cor_tema, width=4)

    # Cabeçalho Institucional A.L.O.V.E. | Eldorado Brasil
    draw.rounded_rectangle([26, 26, largura - 26, 118], radius=16, fill=(7, 15, 29), outline=(22, 50, 82), width=2)
    draw.text((44, 40), "A.L.O.V.E. | Eldorado Brasil", font=f_brand, fill=(0, 230, 118))
    draw.text((44, 82), "Três Lagoas - MS  •  " + agora_br.strftime("%d/%m/%Y às %H:%M"), font=f_brand_sub, fill=(148, 163, 184))

    # Bloco KPI Gigante estilo Mobile
    y_c = 138
    draw.rounded_rectangle([26, y_c, 36, y_c + 128], radius=5, fill=cor_tema)
    draw.text((52, y_c), titulo, font=f_tit, fill=cor_tema)
    draw.text((52, y_c + 34), kpi_big, font=f_kpi, fill=(255, 255, 255))
    if kpi_unit:
        bbox_k = draw.textbbox((0, 0), kpi_big, font=f_kpi)
        draw.text((52 + (bbox_k[2] - bbox_k[0]) + 12, y_c + 68), kpi_unit, font=f_unit, fill=(148, 163, 184))

    y_c += 116
    if sub_1:
        draw.text((52, y_c), sub_1, font=f_sub, fill=(226, 232, 240))
        y_c += 30
    if sub_2:
        draw.text((52, y_c), sub_2, font=f_sub, fill=(148, 163, 184))
        y_c += 30
    if pct_barra is not None:
        y_c += 6
        draw.rounded_rectangle([52, y_c, largura - 38, y_c + 14], radius=7, fill=(20, 36, 59))
        w_fill = int(((largura - 90) * min(100.0, max(3.0, pct_barra))) / 100.0)
        draw.rounded_rectangle([52, y_c, 52 + w_fill, y_c + 14], radius=7, fill=cor_tema)
        y_c += 26

    y_c += 14
    for tipo_s, esq_s, dir_s, cor_s in secoes:
        if tipo_s == "SEC":
            y_c += 6
            draw.text((30, y_c + 6), str(esq_s), font=f_sec, fill=cor_s)
            y_c += 40
        else:
            draw.rounded_rectangle([26, y_c, largura - 26, y_c + 52], radius=12, fill=(7, 13, 24), outline=(26, 49, 77), width=1)
            draw.text((42, y_c + 13), str(esq_s)[:30], font=f_row, fill=(226, 232, 240))
            bbox_r = draw.textbbox((0, 0), str(dir_s), font=f_row_b)
            draw.text((largura - 42 - (bbox_r[2] - bbox_r[0]), y_c + 12), str(dir_s), font=f_row_b, fill=cor_s)
            y_c += 60

    draw.text((30, altura - 42), "A.L.O.V.E. Mobile  •  Expedição de Celulose", font=f_foot, fill=(100, 116, 139))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


mapa_blocos_reais = {
    "prev":  "📅 Previsões do Dia",
    "prod":  "🏭 Produção de Celulose",
    "est":   "📦 Estoque Físico no Armazém",
    "exp":   "🚚 Expedição Realizada",
    "ped":   "📑 Análise de Pedidos (ZLE087)",
    "patio": "🚛 Pátio da Fábrica",
    "frota": "🚜 Frota & Equipamentos",
    "manut": "🔧 Preventiva & Inspeção",
    "glp":   "⛽ Consumo de GLP",
    "baf":   "🩺 Auditoria Bafômetro (H&S)",
    "anual": "📊 Comparativo Anual",
}

# Modal leve (0KB de peso extra no carregamento inicial do Android!)
botoes_escolha_print = ""
for chave_b, rotulo_b in mapa_blocos_reais.items():
    botoes_escolha_print += f"""
    <a href="?print_card={chave_b}" target="_self"
       style="display:flex; align-items:center; justify-content:space-between; background:#070f1d; border:1.5px solid #163252; border-radius:12px; padding:12px 14px; color:#ffffff; text-decoration:none; font-size:0.86rem; font-weight:800;">
        <span>{rotulo_b}</span>
        <span style="color:#00D672; font-size:0.82rem;">Gerar Print ›</span>
    </a>
    """

html_seletor_print = f"""
<style>
    .zero-reload-overlay {{
        display: none;
        position: fixed;
        inset: 0;
        background: rgba(3, 7, 14, 0.96);
        z-index: 999998;
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
        padding: calc(env(safe-area-inset-top, 10px) + 14px) 12px calc(env(safe-area-inset-bottom, 16px) + 40px) 12px;
    }}
    .zero-reload-overlay:target {{
        display: block;
    }}
    .zero-reload-inner {{
        max-width: 540px;
        margin: 0 auto;
    }}
</style>

<div id="print-seletor" class="zero-reload-overlay">
    <div class="zero-reload-inner" style="background:linear-gradient(180deg, #0b1c33 0%, #060d18 100%); border:1.5px solid #00D672; border-radius:18px; padding:16px; box-shadow:0 0 28px rgba(0,214,114,0.28);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; padding-bottom:10px; border-bottom:1px solid #163252;">
            <div>
                <div style="color:#00D672; font-size:0.95rem; font-weight:900; letter-spacing:0.4px;">📸 GERAR PRINT DO MOBILE</div>
                <div style="color:#94a3b8; font-size:0.74rem; margin-top:2px;">Toque no bloco para gerar a imagem:</div>
            </div>
            <a href="#sec-topo" style="width:36px; height:36px; border-radius:10px; background:#070f1d; border:1.5px solid #E74C3C; color:#ffffff; font-weight:900; text-decoration:none; display:flex; align-items:center; justify-content:center; font-size:1rem;">✕</a>
        </div>
        <div style="display:flex; flex-direction:column; gap:8px;">
            {botoes_escolha_print}
        </div>
    </div>
</div>
"""
render_html(html_seletor_print)

# Renderiza APENAS a imagem solicitada quando clicada (0ms de peso no resto do tempo)
card_req = st.query_params.get("print_card", "")
if card_req in mapa_blocos_reais:
    png_bytes = gerar_card_mobile_png(card_req)
    png_b64 = base64.b64encode(png_bytes).decode("ascii")
    nome_arq_png = f"ALOVE_{card_req}_{agora_br.strftime('%d%m_%H%M')}.png"

    html_view_unica = f"""
    <div style="position:fixed; inset:0; background:#050911; z-index:999999; overflow-y:auto; -webkit-overflow-scrolling:touch; padding: calc(env(safe-area-inset-top, 10px) + 14px) 12px calc(env(safe-area-inset-bottom, 16px) + 40px) 12px;">
        <div style="max-width:520px; margin:0 auto;">
            <div style="display:flex; justify-content:space-between; align-items:center; gap:8px; margin-bottom:10px; background:#0b1830; border:1.5px solid #163252; border-radius:12px; padding:9px 12px;">
                <a href="?#print-seletor" target="_self" style="color:#38bdf8; font-size:0.80rem; font-weight:800; text-decoration:none;">◀ Trocar</a>
                <button type="button" id="btnShareSinglePng" data-nome="{nome_arq_png}"
                        style="background:linear-gradient(90deg, #00D672 0%, #00b4ff 100%); color:#050911; border:none; border-radius:8px; padding:8px 14px; font-size:0.82rem; font-weight:900; cursor:pointer; box-shadow:0 0 12px rgba(0,214,114,0.35);">
                    📲 Enviar no WhatsApp
                </button>
                <a href="?" target="_self" style="color:#ff8080; font-size:0.80rem; font-weight:800; text-decoration:none;">✕ Fechar</a>
            </div>
            <img id="imgSinglePng" src="data:image/png;base64,{png_b64}" style="width:100%; display:block; border-radius:16px; box-shadow:0 8px 28px rgba(0,0,0,0.85);">
        </div>
    </div>
    """
    render_html(html_view_unica)

    components.html("""
    <script>
    (function() {
        const parentDoc = window.parent.document;
        const parentWin = window.parent;
        const btn = parentDoc.getElementById('btnShareSinglePng');
        if (btn && btn.dataset.bound !== "1") {
            btn.dataset.bound = "1";
            btn.addEventListener('click', async function() {
                try {
                    const imgEl = parentDoc.getElementById('imgSinglePng');
                    const b64Data = imgEl.src.split(',')[1];
                    const byteChars = atob(b64Data);
                    const byteNums = new Array(byteChars.length);
                    for (let i = 0; i < byteChars.length; i++) {
                        byteNums[i] = byteChars.charCodeAt(i);
                    }
                    const blob = new Blob([new Uint8Array(byteNums)], { type: 'image/png' });
                    const nomeArq = btn.dataset.nome || 'ALOVE_Print.png';
                    const file = new File([blob], nomeArq, { type: 'image/png' });
                    if (parentWin.navigator.canShare && parentWin.navigator.canShare({ files: [file] })) {
                        await parentWin.navigator.share({ files: [file], title: 'A.L.O.V.E. Mobile' });
                    } else {
                        const url = URL.createObjectURL(blob);
                        const a = parentDoc.createElement('a');
                        a.href = url;
                        a.download = nomeArq;
                        parentDoc.body.appendChild(a);
                        a.click();
                        a.remove();
                        URL.revokeObjectURL(url);
                    }
                } catch (e) {}
            });
        }
    })();
    </script>
    """, height=0)

st.markdown("<br><center><span style='color:#64748b; font-size:0.75rem; letter-spacing:0.5px;'>A.L.O.V.E - Mobile / Developed by Cristiano Ciriaco</span></center>", unsafe_allow_html=True)
