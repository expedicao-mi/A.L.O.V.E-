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

# 1. IMPORTA O REFRESHER
from streamlit_autorefresh import st_autorefresh

# URL direta da logo no seu GitHub para funcionar como ícone da tela inicial
LOGO_ALOVE_URL = "https://raw.githubusercontent.com/expedicao-mi/A.L.O.V.E-/main/app_icon.png"
# Parâmetro falso (?v=99) para forçar o Streamlit/navegador a carregar a imagem nova
LOGO_PAINEL = "https://raw.githubusercontent.com/expedicao-mi/A.L.O.V.E-/main/logo_alove.jpg?v=99"
# 🎨 Banner do topo (igual ao mockup). Suba um banner largo no repo e troque a URL aqui;
# enquanto isso, usa a logo atual.
BANNER_TOPO_URL = LOGO_PAINEL

st.set_page_config(
    page_title="A.L.O.V.E. Mobile",
    page_icon="🚛",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. CRONÔMETRO INVISÍVEL (60.000 ms = 1 minuto)
st_autorefresh(interval=60000, limit=None, key="refresh_mobile")

# ==============================================================================
# 🔑 CONTROLE DE ACESSO - BAFÔMETRO
# ==============================================================================
SENHA_BAFOMETRO = "alove2026"

if "bafometro_autenticado" not in st.session_state:
    st.session_state.bafometro_autenticado = False

# ==============================================================================
# 📱 INJEÇÃO DE METATAGS
# ==============================================================================
st.markdown(f"""
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="A.L.O.V.E.">
    <link rel="apple-touch-icon" href="{LOGO_ALOVE_URL}">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#0a101d">
    <link rel="icon" type="image/png" href="{LOGO_ALOVE_URL}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
""", unsafe_allow_html=True)

# ==============================================================================
# 🎨 CSS (LAYOUT NOVO + COMPONENTES EXISTENTES)
# ==============================================================================
st.markdown("""
    <style>
        /* 1. MATA AS MARCAS DO STREAMLIT */
        #MainMenu, footer, header, [data-testid="manage-app-button"], [data-testid="stToolbar"], [data-testid="stDecoration"], .viewerBadge_container__1QSob, .viewerBadge_link__1S137 {
            display: none !important;
            visibility: hidden !important;
        }

        /* 2. FUNDO */
        html, body, [data-testid="stAppViewContainer"], .stApp, .main {
            background: radial-gradient(ellipse at top, #0c1a33 0%, #070d18 55%, #050911 100%) !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
        }
        [data-testid="stMain"], section.main { scroll-behavior: smooth; }

        /* 3. COLUNA CENTRAL ESTILO APP (no PC fica como um "celular" centralizado) */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 5.5rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            max-width: 560px !important;
            margin: 0 auto !important;
        }

        .anc { scroll-margin-top: 8px; height: 0; }
        input[type="radio"] { display: none; }

        /* ---------- BANNER ---------- */
        .topo-banner { margin: 0 -0.8rem 14px -0.8rem; background: #050d1a; border-bottom: 1px solid #12506e; text-align: center; }
        .topo-banner img { width: 100%; max-height: 130px; object-fit: contain; display: block; margin: 0 auto; }

        /* ---------- CARTÕES PADRÃO DO LAYOUT NOVO ---------- */
        .card-main {
            background: linear-gradient(180deg, #0b1830 0%, #08111f 100%);
            border: 1.5px solid #12506e; border-radius: 16px; padding: 14px;
            box-shadow: 0 0 14px rgba(0, 180, 255, 0.10); margin-bottom: 14px;
        }
        .card-head { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
        .icon-sq { width: 38px; height: 38px; border-radius: 10px; background: #0d2340; border: 1px solid #12506e; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; }
        .card-title { color: #fff; font-size: 1rem; font-weight: 800; letter-spacing: .3px; text-transform: uppercase; }
        .badge-novas { margin-left: auto; background: #0d2a4a; border: 1px solid #12506e; color: #38bdf8; font-size: .75rem; font-weight: 700; padding: 3px 10px; border-radius: 999px; }

        /* ---------- STATUS (CONECTADO) ---------- */
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

        /* ---------- NOTIFICAÇÕES ---------- */
        .notif-lista { background: #070f1d; border: 1px solid #12506e; border-radius: 12px; padding: 4px 12px; }
        .notif-item { display: flex; align-items: flex-start; gap: 12px; padding: 11px 0; border-bottom: 1px solid #12304a; }
        .notif-item:last-child { border-bottom: none; }
        .notif-ico { width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.05rem; flex-shrink: 0; }
        .notif-txt { flex: 1; min-width: 0; }
        .notif-tit { color: #fff; font-weight: 700; font-size: .92rem; }
        .notif-desc { color: #9fb3cc; font-size: .8rem; margin-top: 2px; word-break: break-word; }
        .notif-hora { color: #9fb3cc; font-size: .75rem; white-space: nowrap; }
        .notif-hora i { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-left: 6px; }
        details.notif-mais > summary { cursor: pointer; padding: 12px 4px 2px 4px; color: #38bdf8; font-weight: 600; font-size: .9rem; display: flex; justify-content: space-between; align-items: center; }
        details.notif-mais[open] > summary .chev { transform: rotate(90deg); }

        /* ---------- PÁTIO: KPIs ---------- */
        .kpi-duo { display: flex; align-items: center; background: #070f1d; border: 1.5px solid #12506e; border-radius: 14px; padding: 14px 10px; }
        .kpi-box { flex: 1; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .kpi-ico { font-size: 1.9rem; }
        .kpi-big { color: #fff; font-size: 2.3rem; font-weight: 800; line-height: 1; }
        .kpi-big.verde { color: #00E676; }
        .kpi-big span { font-size: 1.4rem; }
        .kpi-lbl { color: #cfe0f5; font-size: .9rem; margin-top: 3px; }
        .kpi-sub { color: #64748b; font-size: .65rem; margin-top: 1px; }
        .kpi-sep { width: 1px; align-self: stretch; background: #12506e; margin: 0 6px; }

        /* ---------- PÁTIO: CARTÕES DE STATUS ---------- */
        details.st-card, div.st-card {
            --c: #38a9ff;
            background: #0a1424;
            background: color-mix(in srgb, var(--c) 9%, #0a1424);
            border: 1.5px solid var(--c); border-left: 6px solid var(--c);
            border-radius: 14px; margin-bottom: 10px; overflow: hidden;
        }
        details.st-card > summary, div.st-card > .st-sum { display: flex; align-items: center; gap: 14px; padding: 12px 14px; cursor: pointer; -webkit-tap-highlight-color: transparent; }
        div.st-card > .st-sum { cursor: default; }
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
        .dest-aviso { color: #FFD600; font-size: .72rem; padding-top: 6px; }
        .dest-vazio { color: #64748b; font-size: .78rem; padding: 6px 0; }

        /* ---------- BLOCOS MASTER (produção, expedição, estoque, frota...) ---------- */
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

        .css-tabs-view label { display: inline-block; padding: 8px 20px; background-color: #162438; color: #94a3b8; border-radius: 8px; font-size: 0.9rem; font-weight: normal; margin: 0 4px 14px 4px; cursor: pointer; border: 1px solid #1c2b42; transition: 0.2s; }
        .css-tabs-view input[type="radio"]#view_turnos:checked + label.lbl-v-turnos { background-color: #00D672; color: #0a101d; border-color: #00D672; }
        .css-tabs-view input[type="radio"]#view_destinos:checked + label.lbl-v-destinos { background-color: #38bdf8; color: #0a101d; border-color: #38bdf8; }
        .view-content-exp { display: none; animation: fadeIn 0.3s ease; }
        #view_turnos:checked ~ #content_view_turnos { display: block; }
        #view_destinos:checked ~ #content_view_destinos { display: block; }

        .css-tabs-exp label { display: inline-block; padding: 6px 16px; background-color: #162438; color: #94a3b8; border-radius: 6px; font-size: 0.85rem; font-weight: normal; margin: 0 4px; cursor: pointer; border: 1px solid #1c2b42; transition: 0.2s; }
        .css-tabs-exp input[type="radio"]#tab_ontem:checked + label.lbl-ontem { background-color: #38bdf8; color: #0a101d; border-color: #38bdf8; }
        .css-tabs-exp input[type="radio"]#tab_hoje:checked + label.lbl-hoje { background-color: #00D672; color: #0a101d; border-color: #00D672; }
        .tab-content-exp { display: none; animation: fadeIn 0.3s ease; }
        #tab_ontem:checked ~ #content_ontem { display: block; }
        #tab_hoje:checked ~ #content_hoje { display: block; }

        .frota-tabs-main { display: flex; gap: 8px; justify-content: center; margin-bottom: 16px; }
        .frota-tabs-main label { padding: 8px 16px; background-color: #162438; color: #94a3b8; border-radius: 6px; cursor: pointer; border: 1px solid #1c2b42; font-weight: normal; font-size: 0.9rem; transition: 0.2s; }
        .frota-tabs-sub { display: flex; gap: 6px; justify-content: center; margin-bottom: 14px; }
        .frota-tabs-sub label { padding: 6px 12px; background-color: #111c2e; color: #64748b; border-radius: 6px; cursor: pointer; border: 1px solid #1c2b42; font-weight: normal; font-size: 0.8rem; transition: 0.2s; }

        .f-rad-main, .f-rad-sub { display: none; }
        .f-content-dia { display: none; animation: fadeIn 0.3s ease; }

        #frota_dia_ontem:checked ~ .frota-tabs-main .lbl-f-ontem { background-color: #38bdf8; color: #0a101d; border-color: #38bdf8; }
        #frota_dia_hoje:checked ~ .frota-tabs-main .lbl-f-hoje { background-color: #E67E22; color: #0a101d; border-color: #E67E22; }
        #frota_dia_ontem:checked ~ #frota_box_ontem { display: block; }
        #frota_dia_hoje:checked ~ #frota_box_hoje { display: block; }

        .f-content-turno-hoje, .f-content-turno-ontem { display: none; background-color: #05080f; padding: 14px; border-radius: 8px; border: 1px solid #1c2b42; text-align: left; }
        #frota_h_00:checked ~ .frota-tabs-sub .lbl-h-00, #frota_h_08:checked ~ .frota-tabs-sub .lbl-h-08, #frota_h_16:checked ~ .frota-tabs-sub .lbl-h-16, #frota_o_00:checked ~ .frota-tabs-sub .lbl-o-00, #frota_o_08:checked ~ .frota-tabs-sub .lbl-o-08, #frota_o_16:checked ~ .frota-tabs-sub .lbl-o-16 { background-color: #0d2417; color: #00D672; border-color: #00D672; }

        #frota_h_00:checked ~ #frota_h_content_00, #frota_h_08:checked ~ #frota_h_content_08, #frota_h_16:checked ~ #frota_h_content_16, #frota_o_00:checked ~ #frota_o_content_00, #frota_o_08:checked ~ #frota_o_content_08, #frota_o_16:checked ~ #frota_o_content_16 { display: block; }

        .f-tag-ok { background-color: #00D672; color: #0a101d; }
        .f-tag-avaria { background-color: #E74C3C; color: #ffffff; }
        .f-tag-aten { background-color: #FFD600; color: #0a101d; }
        .f-tag-title { font-size: 0.85rem; color: #ffffff; font-weight: normal; margin-bottom: 8px; border-bottom: 1px dashed #1c2b42; padding-bottom: 4px; }
        .f-tag-container { margin-bottom: 16px; }
        .tag-box { display: inline-block; padding: 6px 10px; margin: 3px; border-radius: 6px; font-weight: normal; font-size: 0.8rem; text-align: center; }

        /* ---------- LEGENDA DA FROTA ---------- */
        .f-legenda { margin-top: 14px; background: #05080f; border: 1px solid #1c2b42; border-radius: 8px; padding: 10px 12px; text-align: left; }
        .f-leg-titulo { color: #94a3b8; font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 8px; }
        .f-leg-item { display: flex; align-items: center; gap: 10px; color: #cbd5e1; font-size: .8rem; padding: 3px 0; }
        .f-leg-cor { width: 16px; height: 16px; border-radius: 4px; flex-shrink: 0; }
        .f-leg-nota { color: #64748b; font-size: .7rem; margin-top: 8px; border-top: 1px dashed #1c2b42; padding-top: 6px; }

        /* ---------- TÍTULO DE PÁGINA + RESUMO ---------- */
        .pag-titulo { color: #fff; font-weight: 800; font-size: 1.2rem; padding: 16px 4px 10px 4px; text-transform: uppercase; letter-spacing: .5px; }
        .resumo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; }
        .resumo-card { --c: #38a9ff; background: #0a1424; background: color-mix(in srgb, var(--c) 9%, #0a1424); border: 1.5px solid var(--c); border-radius: 14px; padding: 12px; }
        .resumo-tit { color: var(--c); font-size: .72rem; font-weight: 800; text-transform: uppercase; letter-spacing: .4px; }
        .resumo-val { color: #fff; font-size: 1.7rem; font-weight: 800; line-height: 1.15; margin: 4px 0 2px 0; }
        .resumo-val small { font-size: .85rem; font-weight: 400; color: #9fb3cc; }
        .resumo-sub { color: #9fb3cc; font-size: .75rem; }

        /* ---------- CARTÃO DE STATUS: mantém botão ao lado no celular ---------- */
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; }
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stColumn"], [data-testid="stVerticalBlockBorderWrapper"] [data-testid="column"] { min-width: 0 !important; }

        /* ---------- NAVEGAÇÃO INFERIOR (botões reais; container key=nav_inferior) ---------- */
        .st-key-nav_inferior { position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 100%; max-width: 560px; z-index: 999990; background: #070d18; border-top: 1px solid #12506e; padding: 6px 4px calc(6px + env(safe-area-inset-bottom)) 4px; gap: 0 !important; }
        .st-key-nav_inferior [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 2px !important; }
        .st-key-nav_inferior [data-testid="stColumn"], .st-key-nav_inferior [data-testid="column"] { min-width: 0 !important; flex: 1 1 0 !important; width: auto !important; }
        .st-key-nav_inferior .stButton > button { background: transparent !important; border: none !important; box-shadow: none !important; color: #8fa6c4 !important; min-height: 3.1rem; padding: 2px 0 !important; line-height: 1.15; border-radius: 0 !important; }
        .st-key-nav_inferior .stButton > button p { font-size: .68rem !important; margin: 0 !important; }
        .st-key-nav_inferior .stButton > button[kind="primary"], .st-key-nav_inferior .stButton > button[data-testid="stBaseButton-primary"] { color: #00E676 !important; border-top: 2px solid #00E676 !important; }

        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes pulso { 0% { box-shadow: 0 0 0 0 rgba(0,214,114,.55); } 70% { box-shadow: 0 0 0 9px rgba(0,214,114,0); } 100% { box-shadow: 0 0 0 0 rgba(0,214,114,0); } }
    </style>
""", unsafe_allow_html=True)

SHEET_ID = "10FluiIwlynIlPDA74QI8mpHSIrAc-62H1hZNRBsvfCA"

# ==============================================================================
# 🔧 UTILITÁRIOS
# ==============================================================================
def forcar_par(valor):
    val_int = int(round(float(valor or 0)))
    if val_int % 2 != 0:
        val_int += 1
    return val_int

def fmt(n, casas=0):
    """Formata no padrão brasileiro: 1.968 / 1.968,5"""
    try:
        s = f"{float(n):,.{casas}f}"
    except Exception:
        return "0"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

@st.cache_data(ttl=20)
def carregar_dados_nuvem(worksheet_name: str, cabecalho=0):
    sheet_encoded = urllib.parse.quote(worksheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_encoded}&headers=1"
    try:
        df = pd.read_csv(url, header=cabecalho)
        df = df.dropna(how="all", axis=1).dropna(how="all", axis=0)
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=20)
def carregar_tabela_por_cabecalho(worksheet_name: str, chave: str = "DESTINO"):
    """
    🔧 CORREÇÃO DO TOTAL x DESTINOS:
    As abas Patio_Destino_Status e Balanco_Expedicao_Destino têm 2 linhas de topo
    (ATUALIZADO_EM / linha vazia) antes do cabeçalho real. Antes o código assumia
    'header=2' e, se o Google/pandas deslocasse 1 linha, o primeiro destino virava
    cabeçalho e SUMIA da lista (mas continuava no total). Agora a linha de cabeçalho
    é localizada pelo CONTEÚDO (primeira coluna == 'DESTINO').
    """
    sheet_encoded = urllib.parse.quote(worksheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_encoded}&headers=1"
    try:
        raw = pd.read_csv(url, header=None, dtype=str, keep_default_na=False)
    except Exception:
        return pd.DataFrame()

    for i in range(min(len(raw), 8)):
        if str(raw.iloc[i, 0]).strip().upper() == chave.upper():
            cabecalho = [str(c).strip().upper() for c in raw.iloc[i].tolist()]
            corpo = raw.iloc[i + 1:].copy()
            corpo.columns = cabecalho
            corpo = corpo[~(corpo.astype(str).apply(lambda r: "".join(r).strip() == "", axis=1))]
            return corpo.reset_index(drop=True)
    return pd.DataFrame()

def safe_to_numeric(val):
    if pd.isna(val) or val == "" or val is None: return 0.0
    if isinstance(val, (int, float)): return float(val)
    val_str = str(val).strip()
    try: return float(val_str)
    except:
        try: return float(val_str.replace(".", "").replace(",", "."))
        except: return 0.0

def parse_robusto(texto):
    if not texto or str(texto).strip() in ["", "None"]: return {}
    texto_str = str(texto).strip()
    try: return json.loads(texto_str)
    except:
        try: return ast.literal_eval(texto_str)
        except: return {}

def descobrir_letras_turnos(data_alvo):
    data_referencia = date(2026, 9, 22)
    dias_passados = (data_alvo - data_referencia).days
    turnos = {"08_16": "C", "16_00": "B", "madrugada": "D"}
    for letra, dia in [("C", (0 + dias_passados) % 6), ("B", (2 + dias_passados) % 6), ("A", (4 + dias_passados) % 6)]:
        if dia in [0, 1]: turnos["08_16"] = letra
        elif dia in [2, 3]: turnos["16_00"] = letra
    return turnos

def build_vertical_chart(data, height=150):
    if not data: return ""
    max_v = max([d["value"] for d in data]) if max([d["value"] for d in data]) > 0 else 100
    html = f"<div style='display:flex; justify-content:space-evenly; align-items:flex-end; height:{height}px; border-bottom:1px solid #1c2b42; padding-bottom:0px; margin-top:15px;'>"
    lbl_html = "<div style='display:flex; justify-content:space-evenly; margin-top:8px;'>"
    for d in data:
        h_pct = min(100, (d["value"] / max_v) * 100)
        color = d.get("color", "#38bdf8")
        html += f"<div style='display:flex; flex-direction:column; align-items:center; height:100%; width:100%; justify-content:flex-end;'><span style='font-size:0.85rem; font-weight:normal; color:{color}; margin-bottom:6px;'>{d['text']}</span><div style='width:38px; height:{h_pct}%; background-color:{color}; border-radius:4px 4px 0 0;'></div></div>"
        lbl_html += f"<div style='width:100%; text-align:center; font-size:0.75rem; color:#94a3b8; font-weight:normal;'>{d['label']}</div>"
    html += "</div>"
    lbl_html += "</div>"
    return html + lbl_html

def classificar_kpi_mobile(valor, tipo):
    if valor == 0.0: return "#94a3b8"
    if tipo == "alvura":
        if valor < 88.50: return "#E74C3C"
        elif valor < 88.70: return "#FFD600"
        return "#00D672"
    elif tipo == "sujidade":
        if valor > 2.50: return "#E74C3C"
        elif valor > 2.00: return "#FFD600"
        return "#00D672"
    elif tipo == "viscosidade":
        if valor < 650.0: return "#E74C3C"
        elif valor < 680.0: return "#FFD600"
        return "#00D672"
    elif tipo == "ph":
        if valor > 0 and (valor < 5.50 or valor > 8.50): return "#E74C3C"
        elif valor > 0 and ((5.50 <= valor < 6.00) or (8.00 < valor <= 8.50)): return "#FFD600"
        return "#00D672"
    return "#00D672"

# ==============================================================================
# 🚀 CARREGAMENTO DAS ABAS MOBILE GERADAS PELO CORE
# ==============================================================================
agora_br = datetime.utcnow() - timedelta(hours=4)
hoje_date = agora_br.date()
ontem_date = hoje_date - timedelta(days=1)

df_dash = carregar_dados_nuvem("Mobile_Dashboard", cabecalho=0)
df_qual = carregar_dados_nuvem("Mobile_Qualidade", cabecalho=0)
df_alertas = carregar_dados_nuvem("Mobile_Alertas", cabecalho=0)
df_cache = carregar_dados_nuvem("Cache_Painel", cabecalho=0)
df_patio_dest = carregar_tabela_por_cabecalho("Patio_Destino_Status", "DESTINO")
df_status_virada = carregar_dados_nuvem("Status_Virada_Turnos", cabecalho=0)
df_balanco_dest = carregar_tabela_por_cabecalho("Balanco_Expedicao_Destino", "DESTINO")
df_bafometro = carregar_dados_nuvem("Bafometro_Status", cabecalho=0)
if df_bafometro.empty:
    df_bafometro = carregar_dados_nuvem("Auditoria_Bafometro", cabecalho=0)

cache_dict = {str(row.iloc[0]).strip(): str(row.iloc[1]).strip() for _, row in df_cache.iterrows()} if not df_cache.empty else {}
dados_segregados = parse_robusto(cache_dict.get("dados_segregados", "{}"))

ultima_att = None
vol_hoje = 0
vol_ontem = 0
prev_carr = 0
prod_hoje_calc = 0
prev_prod = 0
estoque_total = 0
status_transbordo = "NORMAL"
ritmo_torre = "NORMAL"

if not df_dash.empty:
    row_d = df_dash.iloc[0]
    ultima_att = str(row_d.get("DATA_HORA", "")).strip() or None
    vol_hoje = forcar_par(safe_to_numeric(row_d.get("EXPEDICAO_HOJE", 0)))
    vol_ontem = forcar_par(safe_to_numeric(row_d.get("EXPEDICAO_ONTEM", 0)))
    prev_carr = forcar_par(safe_to_numeric(row_d.get("PREV_EXPEDICAO", 0)))
    prod_hoje_calc = forcar_par(safe_to_numeric(row_d.get("PRODUCAO_HOJE", 0)))
    prev_prod = forcar_par(safe_to_numeric(row_d.get("PREV_PRODUCAO", 0)))
    estoque_total = forcar_par(safe_to_numeric(row_d.get("ESTOQUE_TOTAL", 0)))
    status_transbordo = str(row_d.get("STATUS_TRANSBORDO", "NORMAL"))

    ritmo_torre_bruto = str(row_d.get("RITMO_TORRE", "NORMAL")).upper()
    if "OPERAÇÃO NO 12" in ritmo_torre_bruto or "ACELERADO" in ritmo_torre_bruto:
        ritmo_torre = "RITMO DE ATUALIZAÇÃO: RÁPIDO"
    else:
        ritmo_torre = ritmo_torre_bruto

# ==============================================================================
# 🎯 PÁTIO: LEITURA POR NOME DE COLUNA (SEM DEPENDER DE POSIÇÃO)
# ==============================================================================
STATUS_COLS = {"PR": ("PR_VEIC", "PR_TON"), "00": ("00_VEIC", "00_TON"), "01": ("01_VEIC", "01_TON"), "FC": ("FC_VEIC", "FC_TON")}

destinos_por_status = {"PR": [], "00": [], "01": [], "FC": [], "TR": []}
dados_patio = {k: {"veiculos": 0, "peso": 0} for k in ["PR", "00", "01", "FC", "TR"]}
total_planilha = {k: {"veiculos": 0, "peso": 0} for k in ["PR", "00", "01", "FC"]}  # linha "TOTAL GERAL" (só p/ auditoria)

if not df_patio_dest.empty:
    for _, linha in df_patio_dest.iterrows():
        dest_nome = str(linha.get("DESTINO", "")).strip()
        if not dest_nome or dest_nome.upper() in ["NAN", "NONE", "DESTINO"]:
            continue

        if "TOTAL" in dest_nome.upper():
            for chv, (c_v, c_t) in STATUS_COLS.items():
                total_planilha[chv]["veiculos"] = int(safe_to_numeric(linha.get(c_v, 0)))
                total_planilha[chv]["peso"] = forcar_par(safe_to_numeric(linha.get(c_t, 0)))
            continue

        for chv, (c_v, c_t) in STATUS_COLS.items():
            v = int(safe_to_numeric(linha.get(c_v, 0)))
            t = forcar_par(safe_to_numeric(linha.get(c_t, 0)))
            if v > 0 or t > 0:
                destinos_por_status[chv].append({"destino": dest_nome, "veic": v, "ton": t})

# 🔧 TOTAL DO CARTÃO = SOMA DOS DESTINOS (sempre bate com o aberto). Se a planilha
# informar outro total, guardamos a diferença para exibir um aviso.
dif_status = {}
for chv in STATUS_COLS:
    lista = destinos_por_status[chv]
    if lista:
        dados_patio[chv]["veiculos"] = sum(i["veic"] for i in lista)
        dados_patio[chv]["peso"] = sum(i["ton"] for i in lista)
        dif_status[chv] = total_planilha[chv]["veiculos"] - dados_patio[chv]["veiculos"]
    else:
        dados_patio[chv]["veiculos"] = total_planilha[chv]["veiculos"]
        dados_patio[chv]["peso"] = total_planilha[chv]["peso"]
        dif_status[chv] = 0

dados_patio["TR"]["veiculos"] = int(safe_to_numeric(df_dash.iloc[0].get("TR_VEIC", 0))) if not df_dash.empty else 0
dados_patio["TR"]["peso"] = forcar_par(safe_to_numeric(df_dash.iloc[0].get("TR_TON", 0))) if not df_dash.empty else 0

total_veiculos_fisicos = dados_patio["00"]["veiculos"] + dados_patio["01"]["veiculos"] + dados_patio["FC"]["veiculos"]
vol_patio_disponivel = forcar_par(dados_patio["00"]["peso"] + dados_patio["01"]["peso"] + dados_patio["FC"]["peso"])

viradas_info = {}
if not df_status_virada.empty:
    for _, row_st in df_status_virada.iterrows():
        linha = str(row_st.get("LINHA", "")).strip().upper()
        viradas_info[linha] = {
            "prox_mat": str(row_st.get("PROXIMO_MATERIAL", "--")),
            "prev_virada": str(row_st.get("PREVISAO_VIRADA", "--")),
            "saldo_rest": forcar_par(safe_to_numeric(row_st.get("SALDO_RESTANTE_T", 0))),
            "status_email": str(row_st.get("STATUS_EMAIL_TROCA", "N/D"))
        }

balanco_destinos = []
total_expedicao_meta = 0.0
total_expedicao_real = 0.0

if not df_balanco_dest.empty:
    for _, r_b in df_balanco_dest.iterrows():
        dest_nome = str(r_b.get("DESTINO", "")).strip()
        if not dest_nome or dest_nome.upper() in ["NAN", "NONE", "DESTINO"]: continue

        meta_val = forcar_par(safe_to_numeric(r_b.get("META_DIA_T", 0)))
        real_val = forcar_par(safe_to_numeric(r_b.get("EXPEDIDO_ZLE_T", 0)))
        saldo_val = forcar_par(safe_to_numeric(r_b.get("SALDO_A_EXPEDIR_T", 0)))

        try: ating_val = float(str(r_b.get("ATINGIMENTO_%", 0)).replace('%', '').replace(',', '.'))
        except: ating_val = 0.0

        if dest_nome.upper() == "TOTAL EXPEDIÇÃO":
            total_expedicao_meta = meta_val
            total_expedicao_real = real_val
        else:
            balanco_destinos.append({
                "destino": dest_nome, "meta": meta_val, "realizado": real_val,
                "saldo": saldo_val, "atingimento": ating_val
            })

dados_maquinas = {"MS1": {}, "MS2": {}}
if not df_qual.empty:
    for _, r_q in df_qual.iterrows():
        m_nome = str(r_q.get("MAQUINA", "")).strip().upper()
        if m_nome in dados_maquinas:
            dados_maquinas[m_nome] = {
                "material": str(r_q.get("MATERIAL", "--")),
                "alvura": safe_to_numeric(r_q.get("ALVURA", 0)),
                "sujidade": safe_to_numeric(r_q.get("SUJIDADE", 0)),
                "viscosidade": safe_to_numeric(r_q.get("VISCOSIDADE", 0)),
                "ph": safe_to_numeric(r_q.get("PH", 0)),
                "producao": forcar_par(safe_to_numeric(r_q.get("PROD_TOTAL", 0))),
                "l1": forcar_par(safe_to_numeric(r_q.get("PROD_LINHA_1", 0))),
                "l2": forcar_par(safe_to_numeric(r_q.get("PROD_LINHA_2", 0))),
                "desclassificando": str(r_q.get("DESCLASSIFICANDO", "NAO")).upper() == "SIM"
            }

# ==============================================================================
# 🩺 DIAGNÓSTICO DE CONEXÃO COM O GOOGLE SHEETS
# ==============================================================================
@st.cache_data(ttl=30)
def diagnosticar_abas():
    """Testa cada aba diretamente e diz POR QUE ela veio vazia (em vez de falhar em silêncio)."""
    abas = [
        "Mobile_Dashboard", "Mobile_Qualidade", "Mobile_Alertas", "Cache_Painel",
        "Patio_Destino_Status", "Balanco_Expedicao_Destino", "Status_Virada_Turnos",
        "Auditoria_Bafometro", "Historico_DKRO", "Abastecimentos_GLP",
    ]
    resultado = []
    for aba in abas:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(aba)}&headers=1"
        try:
            r = requests.get(url, timeout=10)
            txt = r.text or ""
            linhas = [l for l in txt.splitlines() if l.strip()]
            if r.status_code in (401, 403):
                resultado.append((aba, "❌", f"HTTP {r.status_code}: planilha não está compartilhada por link"))
            elif r.status_code == 400:
                resultado.append((aba, "❌", "HTTP 400: a aba não existe com esse nome (confira maiúsculas/acentos)"))
            elif r.status_code != 200:
                resultado.append((aba, "❌", f"HTTP {r.status_code}"))
            elif txt.lstrip().lower().startswith(("<!doctype", "<html")):
                resultado.append((aba, "❌", "O Google devolveu uma página de login: a planilha não está pública (\"qualquer pessoa com o link\")"))
            elif len(linhas) <= 1:
                resultado.append((aba, "⚠️", "A aba existe, mas está vazia (o Core já gravou nela?)"))
            else:
                resultado.append((aba, "✅", f"{len(linhas) - 1} linhas lidas"))
        except Exception as e:
            resultado.append((aba, "❌", f"Sem acesso à internet/Google: {str(e)[:70]}"))
    return resultado

# ==============================================================================
# 🧭 PÁGINAS + NAVEGAÇÃO INFERIOR (clica no ícone e troca a página, sem rolar)
# ==============================================================================
PAGINAS = [
    ("inicio", "🏠", "Início"),
    ("patio", "🚛", "Pátio"),
    ("prod", "🏭", "Produção"),
    ("exp", "🚚", "Expedição"),
    ("estoque", "📦", "Estoque"),
    ("frota", "🚜", "Frota"),
]
CHAVES_PAGINAS = [p[0] for p in PAGINAS]

if "pagina" not in st.session_state:
    p_url = st.query_params.get("p", "inicio")  # permite abrir direto: ?p=patio
    st.session_state.pagina = p_url if p_url in CHAVES_PAGINAS else "inicio"

def ir_para(chave):
    st.session_state.pagina = chave

pagina = st.session_state.pagina

# Barra fixa no rodapé (container com key -> classe CSS .st-key-nav_inferior)
with st.container(key="nav_inferior"):
    cols_nav = st.columns(len(PAGINAS))
    for col_n, (k_n, ico_n, nome_n) in zip(cols_nav, PAGINAS):
        with col_n:
            st.button(
                f"{ico_n}  \n{nome_n}", key=f"nav_{k_n}", on_click=ir_para, args=(k_n,),
                use_container_width=True, type="primary" if pagina == k_n else "secondary"
            )

# ==============================================================================
# 📌 TOPO: BANNER (só no Início) + STATUS DE CONEXÃO
# ==============================================================================
def calcular_conexao(ultima_str, agora):
    """Conectado = o Core gravou dados na planilha nos últimos 15 min."""
    if not ultima_str:
        return "SEM DADOS", "#94a3b8", "—"
    try:
        dt = datetime.strptime(ultima_str[:19], "%d/%m/%Y %H:%M:%S")
    except Exception:
        return "SEM DADOS", "#94a3b8", ultima_str
    minutos = (agora - dt).total_seconds() / 60.0
    txt_hora = dt.strftime("%H:%M:%S") if dt.date() == agora.date() else dt.strftime("%d/%m %H:%M")
    if minutos <= 15: return "CONECTADO", "#00D672", txt_hora
    if minutos <= 45: return "ATRASADO", "#FFD600", txt_hora
    return "DESCONECTADO", "#E74C3C", txt_hora

conn_txt, conn_cor, conn_hora = calcular_conexao(ultima_att, agora_br)

def render_status_card(chave_btn):
    with st.container(border=True):
        col_status, col_btn = st.columns([3, 2], vertical_alignment="center")
        with col_status:
            st.markdown(f"""
                <div style="display:flex; align-items:center;">
                    <span class="conn-dot" style="background:{conn_cor};"></span>
                    <span class="conn-titulo" style="color:{conn_cor};">{conn_txt}</span>
                </div>
                <div class="conn-sub">🕒 Última atualização: {conn_hora}</div>
                <div class="conn-ritmo">🎯 {ritmo_torre}</div>
            """.replace('\n', ''), unsafe_allow_html=True)
        with col_btn:
            if st.button("🔄 Atualizar", key=chave_btn, use_container_width=True):
                st.cache_data.clear()
                st.rerun()

if pagina == "inicio":
    st.markdown(
        f'<div class="topo-banner"><img src="{BANNER_TOPO_URL}" alt="A.L.O.V.E - Eldorado Brasil"></div>',
        unsafe_allow_html=True
    )
else:
    _ico_p, _nome_p = [(p[1], p[2]) for p in PAGINAS if p[0] == pagina][0]
    st.markdown(f'<div class="pag-titulo">{_ico_p} {_nome_p}</div>', unsafe_allow_html=True)

render_status_card(f"btn_atualizar_{pagina}")

# ==============================================================================
# 🏠 PÁGINA INÍCIO: NOTIFICAÇÕES (REAIS: aba Mobile_Alertas) + RESUMO + DIAGNÓSTICO
# ==============================================================================
if pagina == "inicio":
    alertas_lista = []
    if not df_alertas.empty:
        for _, ra in df_alertas.iterrows():
            nivel = str(ra.get("NIVEL", "")).strip().upper()
            texto = str(ra.get("ALERTA", "")).strip()
            if not texto or texto.lower() == "nan":
                continue
            dh = str(ra.get("DATA_HORA", "")).strip()
            hora = dh.split(" ")[1][:5] if " " in dh else "--:--"
            texto_limpo = re.sub(r'^[^\w\[\(]+', '', texto)  # tira o emoji do início (o ícone já indica o nível)
            alertas_lista.append((nivel, texto_limpo, hora))

    ordem_nivel = {"CRITICO": 0, "ATENCAO": 1, "NORMAL": 2}
    alertas_lista.sort(key=lambda a: ordem_nivel.get(a[0], 3))
    n_novas = sum(1 for a in alertas_lista if a[0] in ("CRITICO", "ATENCAO"))

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

    if alertas_lista:
        primeiras = "".join(render_notif(*a) for a in alertas_lista[:3])
        restantes = alertas_lista[3:]
        html_mais = ""
        if restantes:
            html_mais = (
                f'<details class="notif-mais"><summary><span>Ver todas as notificações ({len(alertas_lista)})</span><span class="chev">›</span></summary>'
                f'<div class="notif-lista" style="margin-top:6px;">{"".join(render_notif(*a) for a in restantes)}</div></details>'
            )
        badge = f'<div class="badge-novas">{n_novas} novas</div>' if n_novas else '<div class="badge-novas" style="color:#00D672;">tudo ok</div>'
        html_notif = (
            f'<div class="card-main"><div class="card-head"><div class="icon-sq">🔔</div><div class="card-title">Notificações</div>{badge}</div>'
            f'<div class="notif-lista">{primeiras}</div>{html_mais}</div>'
        )
        st.markdown(html_notif.replace('\n', ''), unsafe_allow_html=True)

    # ---- RESUMO RÁPIDO (os 4 números principais) ----
    html_resumo = f'''
    <div class="resumo-grid">
        <div class="resumo-card" style="--c:#38a9ff;">
            <div class="resumo-tit">🚛 Pátio</div>
            <div class="resumo-val">{total_veiculos_fisicos} <small>veíc.</small></div>
            <div class="resumo-sub">{fmt(vol_patio_disponivel)} t disponíveis</div>
        </div>
        <div class="resumo-card" style="--c:#00D672;">
            <div class="resumo-tit">🚚 Expedição hoje</div>
            <div class="resumo-val">{fmt(vol_hoje)} <small>t</small></div>
            <div class="resumo-sub">Previsão: {fmt(prev_carr)} t</div>
        </div>
        <div class="resumo-card" style="--c:#E5B800;">
            <div class="resumo-tit">🏭 Produção hoje</div>
            <div class="resumo-val">{fmt(prod_hoje_calc)} <small>t</small></div>
            <div class="resumo-sub">Previsão: {fmt(prev_prod)} t</div>
        </div>
        <div class="resumo-card" style="--c:#9b59b6;">
            <div class="resumo-tit">📦 Estoque</div>
            <div class="resumo-val">{fmt(estoque_total)} <small>t</small></div>
            <div class="resumo-sub">Armazém: {status_transbordo}</div>
        </div>
    </div>
    '''
    st.markdown(html_resumo.replace('\n', ''), unsafe_allow_html=True)

    # ---- DIAGNÓSTICO (liga só quando precisar) ----
    if st.toggle("🩺 Diagnóstico da conexão com o Sheets", key="diag_toggle"):
        linhas_diag = diagnosticar_abas()
        html_diag = f'<div class="card-main"><div class="card-title" style="margin-bottom:6px;">Conexão com o Google Sheets</div>'
        html_diag += f'<div class="conn-sub" style="margin-bottom:8px;">Planilha: {SHEET_ID[:6]}…{SHEET_ID[-6:]} · Streamlit {st.__version__}</div>'
        for aba_d, icone_d, msg_d in linhas_diag:
            html_diag += f'<div class="dest-row"><span class="n">{icone_d} {aba_d}</span><span class="v"><small>{html_lib.escape(msg_d)}</small></span></div>'
        html_diag += '</div>'
        st.markdown(html_diag.replace('\n', ''), unsafe_allow_html=True)

if pagina == "patio":
    # ==============================================================================
    # 📦 BLOCO 1: PÁTIO DE VEÍCULOS (CARTÕES EXPANSÍVEIS POR DESTINO)
    # ==============================================================================
    html_patio = f'''
    <div id="sec-patio" class="anc"></div>
    <div class="card-main">
        <div class="card-head"><div class="icon-sq">🏭</div><div class="card-title">Pátio da Fábrica (Tempo Real)</div></div>
        <div class="kpi-duo">
            <div class="kpi-box">
                <div class="kpi-ico">🚚</div>
                <div>
                    <div class="kpi-big">{total_veiculos_fisicos}</div>
                    <div class="kpi-lbl">Veículos Físicos</div>
                    <div class="kpi-sub">Checklist + Apoio + Fila</div>
                </div>
            </div>
            <div class="kpi-sep"></div>
            <div class="kpi-box">
                <div class="kpi-ico">📦</div>
                <div>
                    <div class="kpi-lbl">Carga Disponível</div>
                    <div class="kpi-big verde">{fmt(vol_patio_disponivel)} <span>t</span></div>
                </div>
            </div>
        </div>
    </div>
    '''

    blocos_patio = [
        ("Prog/Chegando", "PR", "#38a9ff", "🚙"),
        ("Checklist", "00", "#FFD600", "📋"),
        ("Apoio", "01", "#E67E22", "🚛"),
        ("Fila de Carregamento", "FC", "#00D672", "✅"),
    ]

    for tit, chv, cor, ico in blocos_patio:
        lista_destinos = destinos_por_status.get(chv, [])
        v_qtd = dados_patio[chv]["veiculos"]
        v_ton = dados_patio[chv]["peso"]

        linhas_dest_html = ""
        if lista_destinos:
            for item in lista_destinos:
                linhas_dest_html += (
                    f'<div class="dest-row"><span class="n">{html_lib.escape(item["destino"])}</span>'
                    f'<span class="v">{item["veic"]} veíc. <small>({fmt(item["ton"])} t)</small></span></div>'
                )
            linhas_dest_html += (
                f'<div class="dest-row total"><span class="n">TOTAL</span>'
                f'<span class="v">{v_qtd} veíc. <small>({fmt(v_ton)} t)</small></span></div>'
            )
            if dif_status.get(chv, 0) != 0:
                linhas_dest_html += (
                    f'<div class="dest-aviso">⚠️ A planilha informa {total_planilha[chv]["veiculos"]} veíc. no total '
                    f'(diferença de {abs(dif_status[chv])} não detalhada por destino).</div>'
                )
        else:
            linhas_dest_html = '<div class="dest-vazio">Nenhum veículo alocado neste status.</div>'

        html_patio += f'''
        <details class="st-card" style="--c:{cor};">
            <summary>
                <div class="st-ico">{ico}</div>
                <div class="st-txt">
                    <div class="st-title">{tit}</div>
                    <div class="st-num">{v_qtd} <span>veíc. / {fmt(v_ton)} t</span></div>
                </div>
                <div class="chev">›</div>
            </summary>
            <div class="st-body">{linhas_dest_html}</div>
        </details>
        '''

    html_patio += f'''
    <div class="st-card" style="--c:#95A5A6;">
        <div class="st-sum">
            <div class="st-ico">📄</div>
            <div class="st-txt">
                <div class="st-title">Termo SAP</div>
                <div class="st-num">{dados_patio["TR"]["veiculos"]} <span>veíc. / {fmt(dados_patio["TR"]["peso"])} t</span></div>
            </div>
            <div style="color:#64748b; font-size:.72rem; text-align:right;">Fila de<br>Faturamento</div>
        </div>
    </div>
    '''
    st.markdown(html_patio.replace('\n', ''), unsafe_allow_html=True)

if pagina == "prod":
    # ==============================================================================
    # 🏭 BLOCO 2: PRODUÇÃO DO DIA (MS1 / MS2)
    # ==============================================================================
    html_prod_content = ""

    for maq in ["MS1", "MS2"]:
        q_dados = dados_maquinas.get(maq, {})
        if q_dados:
            mat_maq = q_dados.get("material", "--")
            p_maq = q_dados.get("producao", 0)
            q_suj = q_dados.get('sujidade', 0.0)
            q_visc = q_dados.get('viscosidade', 0.0)
            q_alvura = q_dados.get('alvura', 0.0)
            q_ph = q_dados.get('ph', 0.0)
            l1 = q_dados.get('l1', 0)
            l2 = q_dados.get('l2', 0)
            desclass = q_dados.get("desclassificando", False)

            c_alv = classificar_kpi_mobile(q_alvura, "alvura")
            c_suj = classificar_kpi_mobile(q_suj, "sujidade")
            c_vis = classificar_kpi_mobile(q_visc, "viscosidade")
            c_ph = classificar_kpi_mobile(q_ph, "ph")

            cor_card_borda = "#E74C3C" if desclass else "#1c2b42"

            lbl_l1 = "Linha A" if maq == "MS1" else "Linha C"
            lbl_l2 = "Linha B" if maq == "MS1" else "Linha D"

            info_v = viradas_info.get(maq, {})
            html_virada = ""
            if info_v:
                p_mat = info_v["prox_mat"]
                p_prev = info_v["prev_virada"]
                s_rest = info_v["saldo_rest"]
                st_em = info_v["status_email"]

                if "🚨" in st_em:
                    cor_alerta = "#E74C3C"
                    txt_alerta = f"⚠️ Falta E-mail ({st_em})"
                elif "✅" in st_em:
                    cor_alerta = "#00D672"
                    txt_alerta = f"📧 E-mail {st_em}"
                else:
                    cor_alerta = "#38bdf8"
                    txt_alerta = f"📧 {st_em}"

                html_virada = f"""
                <div style='background-color: #070d18; border: 1px solid #1c2b42; border-left: 4px solid {cor_alerta}; padding: 10px; margin-top: 14px; border-radius: 6px;'>
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>
                        <span style='font-size:0.75rem; color:#64748b; font-weight:normal; text-transform:uppercase;'>Saldo a Produzir ({mat_maq})</span>
                        <span style='font-size:1.1rem; font-weight:normal; color:#ffffff;'>{fmt(s_rest)} t</span>
                    </div>
                    <div style='display:flex; justify-content:space-between; align-items:center; font-size:0.75rem;'>
                        <span style='color:#cbd5e1; font-weight:normal;'>🔜 Prox: <span style='color:#38bdf8;'>{p_mat}</span> ({p_prev})</span>
                        <span style='color:{cor_alerta}; font-weight:normal;'>{txt_alerta}</span>
                    </div>
                </div>
                """

            html_prod_content += f"""
            <div style='background-color: #0a101d; border: 1.5px solid {cor_card_borda}; border-radius: 8px; padding: 16px; margin-bottom: 12px;'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>
                    <span style='color:#ffffff; font-weight:bold; font-size:1.1rem;'>⚙️ {maq}</span>
                    <span style='color:#FF9F1C; font-weight:normal; font-size:1.1rem;'>📦 MAT: {mat_maq}</span>
                    <span style='color:#38bdf8; font-weight:bold; font-size:1.2rem;'>{fmt(p_maq)} t</span>
                </div>

                <div style='display:flex; justify-content:flex-end; gap: 16px; margin-bottom: 12px; font-size: 0.85rem; color: #64748b; font-weight: normal;'>
                    <span>{lbl_l1}: <span style='color:#ffffff;'>{fmt(l1)} t</span></span>
                    <span>{lbl_l2}: <span style='color:#ffffff;'>{fmt(l2)} t</span></span>
                </div>

                <div style='display: flex; justify-content: space-between; text-align: center; border-top: 1px dashed #1c2b42; padding-top: 14px;'>
                    <div>
                        <div style='font-size:0.7rem; color:#64748b; font-weight:bold; text-transform:uppercase;'>ALVURA</div>
                        <div style='font-size:1.2rem; font-weight:normal; color:{c_alv}; margin: 4px 0;'>{fmt(q_alvura, 2)}%</div>
                        <div style='font-size:0.65rem; color:#475569; font-weight:normal;'>(Mín: 88,5)</div>
                    </div>
                    <div>
                        <div style='font-size:0.7rem; color:#64748b; font-weight:bold; text-transform:uppercase;'>SUJIDADE</div>
                        <div style='font-size:1.2rem; font-weight:normal; color:{c_suj}; margin: 4px 0;'>{fmt(q_suj, 2)}</div>
                        <div style='font-size:0.65rem; color:#475569; font-weight:normal;'>(Máx: 2,5)</div>
                    </div>
                    <div>
                        <div style='font-size:0.7rem; color:#64748b; font-weight:bold; text-transform:uppercase;'>VISCOSID.</div>
                        <div style='font-size:1.2rem; font-weight:normal; color:{c_vis}; margin: 4px 0;'>{fmt(q_visc)}</div>
                        <div style='font-size:0.65rem; color:#475569; font-weight:normal;'>(Mín: 650)</div>
                    </div>
                    <div>
                        <div style='font-size:0.7rem; color:#64748b; font-weight:bold; text-transform:uppercase;'>pH</div>
                        <div style='font-size:1.2rem; font-weight:normal; color:{c_ph}; margin: 4px 0;'>{fmt(q_ph, 1)}</div>
                        <div style='font-size:0.65rem; color:#475569; font-weight:normal;'>(5,5 - 8,5)</div>
                    </div>
                </div>
                {html_virada}
            </div>
            """
        else:
            html_prod_content += f"<div style='color:gray; padding:10px 0;'>Aguardando dados da {maq}...</div>"

    html_prod_completo = f"""
    <div id="sec-prod" class="anc"></div>
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
        </summary>
        <div class="master-content" style="padding-top:16px;">
            {html_prod_content}
        </div>
    </details>
    """
    st.markdown(html_prod_completo.replace('\n', ''), unsafe_allow_html=True)

# ==============================================================================
# 🛠️ FUNÇÃO DE BUSCA HISTÓRICA (COM REGRA DE RESET DIÁRIO E FOLGAS)
# ==============================================================================
@st.cache_data(ttl=60)
def buscar_dados_turnos_historico(data_alvo):
    agora_br_l = datetime.utcnow() - timedelta(hours=4)
    hoje_l = agora_br_l.date()
    is_hoje = (data_alvo == hoje_l)
    letras = descobrir_letras_turnos(data_alvo)

    ativo_key = None
    if is_hoje:
        if agora_br_l.hour < 8: ativo_key = "t1"
        elif agora_br_l.hour < 16: ativo_key = "t2"
        else: ativo_key = "t3"

    try:
        url_csv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
        resp = requests.get(url_csv, timeout=10)
        resp.encoding = 'utf-8'
        linhas = list(csv.reader(StringIO(resp.text)))

        hora_00 = datetime.combine(data_alvo, datetime.min.time())
        hora_08 = hora_00.replace(hour=8)
        hora_16 = hora_00.replace(hour=16)
        hora_fim = hora_00.replace(hour=23, minute=59, second=59)

        corte_00, corte_08, corte_16, corte_fim = 0.0, 0.0, 0.0, 0.0

        for row in linhas[1:]:
            if len(row) > 3:
                try:
                    dt_row = datetime.strptime(row[0].strip(), "%d/%m/%Y %H:%M:%S")
                    vol_linha = safe_to_numeric(row[3])

                    if dt_row <= hora_00: corte_00 = vol_linha
                    if dt_row <= hora_08: corte_08 = vol_linha
                    if dt_row <= hora_16: corte_16 = vol_linha
                    if dt_row <= hora_fim: corte_fim = vol_linha
                except:
                    continue

        vol_t1 = forcar_par(corte_08) if corte_08 < corte_00 else forcar_par(max(0.0, corte_08 - corte_00))
        vol_t2 = forcar_par(corte_16) if corte_16 < corte_08 else forcar_par(max(0.0, corte_16 - corte_08))
        vol_t3 = forcar_par(corte_fim) if corte_fim < corte_16 else forcar_par(max(0.0, corte_fim - corte_16))

        if is_hoje:
            if agora_br_l.hour < 8: vol_t2, vol_t3 = 0, 0
            elif agora_br_l.hour < 16: vol_t3 = 0

        turnos_exibir = []

        if data_alvo.weekday() in [6, 0]:
            str_vol_t1 = "Folga"
            vol_real_t1 = 0
            lbl_sub_t1 = "Somente Armazen."
        else:
            str_vol_t1 = f"{fmt(vol_t1)} t"
            vol_real_t1 = vol_t1
            lbl_sub_t1 = "00h - 08h"

        turnos_exibir.append({"key": "t1", "letra": f"Turno {letras.get('madrugada', 'D')}", "vol": vol_real_t1, "str_vol": str_vol_t1, "horario": lbl_sub_t1})
        turnos_exibir.append({"key": "t2", "letra": f"Turno {letras.get('08_16', 'C')}", "vol": vol_t2, "str_vol": f"{fmt(vol_t2)} t", "horario": "08h - 16h"})
        turnos_exibir.append({"key": "t3", "letra": f"Turno {letras.get('16_00', 'B')}", "vol": vol_t3, "str_vol": f"{fmt(vol_t3)} t", "horario": "16h - 00h"})

        total_dia = vol_real_t1 + vol_t2 + vol_t3
        return {"ativo_key": ativo_key, "turnos": turnos_exibir, "total_dia": total_dia}
    except Exception:
        return None

if pagina == "exp":
    # ==============================================================================
    # 🚚 BLOCO 3: EXPEDIÇÃO DO DIA & TURNOS E DESTINOS
    # ==============================================================================
    dados_exp_hoje = buscar_dados_turnos_historico(hoje_date)
    dados_exp_ontem = buscar_dados_turnos_historico(ontem_date)

    vol_calculado_hoje = forcar_par(dados_exp_hoje.get("total_dia", 0)) if dados_exp_hoje else 0
    vol_exp_hoje = vol_calculado_hoje if vol_hoje == 0 else vol_hoje
    vol_exp_ontem = vol_ontem if vol_ontem > 0 else (forcar_par(dados_exp_ontem.get("total_dia", 0)) if dados_exp_ontem else 0)

    html_hoje = "<div style='font-size:0.75rem; font-weight:normal; color:#00D672; text-transform:uppercase; margin-bottom:10px; text-align:left;'>Turnos em Operação Hoje:</div>"
    if dados_exp_hoje and "turnos" in dados_exp_hoje:
        ativo_key = dados_exp_hoje.get("ativo_key")
        html_hoje += "<div style='display:flex; gap:6px; margin-bottom:8px;'>"
        chart_data_hoje = []
        for t in dados_exp_hoje["turnos"]:
            is_atv = (t["key"] == ativo_key)
            cor_b = "#FF9F1C" if is_atv else "#1c2b42"
            cor_txt = "#FF9F1C" if is_atv else "#ffffff"
            sub_txt = f"{t['horario']} (ATIVO)" if is_atv else t['horario']

            v_str = t.get("str_vol", f"{fmt(t['vol'])} t")
            if v_str == "Folga":
                html_val = "<div style='font-size:0.85rem; font-weight:normal; color:#E74C3C; padding: 5px 0;'>EM FOLGA</div>"
                c_text = "Folga"
            else:
                html_val = f"<div style='font-size:1.1rem; font-weight:normal; color:#ffffff;'>{v_str}</div>"
                c_text = v_str

            html_hoje += f"<div style='flex:1; background-color:#0a101d; border:1px solid {cor_b}; border-radius:8px; padding:8px; text-align:center;'><div style='font-size:0.75rem; font-weight:bold; color:{cor_txt};'>{t['letra']}</div>{html_val}<div style='font-size:0.65rem; color:#64748b;'>{sub_txt}</div></div>"
            chart_data_hoje.append({"label": t['letra'], "value": t['vol'], "text": c_text, "color": "#FF9F1C" if is_atv else "#00D672"})
        html_hoje += "</div>"
        html_hoje += build_vertical_chart(chart_data_hoje)
    else:
        html_hoje += "<div style='color:gray; text-align:left;'>Aguardando dados de hoje...</div>"

    html_ontem = f"<div style='font-size:0.75rem; font-weight:normal; color:#38bdf8; text-transform:uppercase; margin-bottom:10px; text-align:left;'>Fechamento de Ontem ({ontem_date.strftime('%d/%m')}):</div>"
    if dados_exp_ontem and "turnos" in dados_exp_ontem:
        html_ontem += "<div style='display:flex; gap:6px; margin-bottom:8px;'>"
        chart_data_ontem = []
        for t in dados_exp_ontem["turnos"]:
            v_str_o = t.get("str_vol", f"{fmt(t['vol'])} t")
            if v_str_o == "Folga":
                html_val_o = "<div style='font-size:0.85rem; font-weight:normal; color:#E74C3C; padding: 5px 0;'>EM FOLGA</div>"
                c_text_o = "Folga"
            else:
                html_val_o = f"<div style='font-size:1.1rem; font-weight:normal; color:#ffffff;'>{v_str_o}</div>"
                c_text_o = v_str_o

            html_ontem += f"<div style='flex:1; background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:8px; text-align:center;'><div style='font-size:0.75rem; font-weight:bold; color:#38bdf8;'>{t['letra']}</div>{html_val_o}<div style='font-size:0.65rem; color:#64748b;'>{t['horario']}</div></div>"
            chart_data_ontem.append({"label": t['letra'], "value": t['vol'], "text": c_text_o, "color": "#38bdf8"})
        html_ontem += "</div>"
        html_ontem += build_vertical_chart(chart_data_ontem)
    else:
        html_ontem += "<div style='color:gray; text-align:left;'>Sem dados consolidados de ontem.</div>"

    html_destinos = f"""
    <div style="display:flex; justify-content:space-around; background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:12px; margin-bottom:14px; text-align:center;">
        <div>
            <div style="font-size:0.75rem; color:#64748b; font-weight:bold; text-transform:uppercase;">Plano Total Diário</div>
            <div style="font-size:1.4rem; color:#ffffff; font-weight:bold;">{fmt(total_expedicao_meta)} <span style="font-size:0.8rem; color:#64748b; font-weight:normal;">t</span></div>
        </div>
        <div style="border-left:1px solid #1c2b42; padding-left:20px;">
            <div style="font-size:0.75rem; color:#38bdf8; font-weight:bold; text-transform:uppercase;">Total Carregado</div>
            <div style="font-size:1.4rem; color:#38bdf8; font-weight:bold;">{fmt(total_expedicao_real)} <span style="font-size:0.8rem; font-weight:normal;">t</span></div>
        </div>
    </div>
    """

    if balanco_destinos:
        def regra_ordenacao(d):
            nome = str(d.get('destino', '')).upper()
            if "MI" in nome or "LATAM" in nome: return 999999
            try: return int(re.search(r'\d+', nome).group())
            except: return 0

        balanco_destinos_ordenado = sorted(balanco_destinos, key=regra_ordenacao, reverse=True)

        html_destinos += """
        <div style="background-color: #0a101d; border: 1px solid #1c2b42; border-radius: 8px; padding: 10px; overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; font-size: 0.75rem; text-align: center; color: #ffffff; font-weight: normal;">
                <thead>
                    <tr style="border-bottom: 1px solid #1c2b42; color: #64748b; font-weight: normal;">
                        <th style="text-align: left; padding: 8px 4px; font-weight: normal;">Destino</th>
                        <th style="text-align: center; padding: 8px 4px; color: #38bdf8; font-weight: normal;">Plano</th>
                        <th style="text-align: center; padding: 8px 4px; color: #00D672; font-weight: normal;">Carr.</th>
                        <th style="text-align: center; padding: 8px 4px; color: #E5B800; font-weight: normal;">Falta</th>
                        <th style="text-align: center; padding: 8px 4px; font-weight: normal;">%</th>
                    </tr>
                </thead>
                <tbody>
        """
        for d in balanco_destinos_ordenado:
            ating = d['atingimento']
            cor_ating = "#00D672" if ating >= 100 else ("#38bdf8" if ating > 0 else "#64748b")

            if d['saldo'] <= 0 and d['realizado'] > 0:
                saldo_str = "0"
                cor_saldo = "#00D672"
            else:
                saldo_str = fmt(d['saldo'])
                cor_saldo = "#E5B800"

            nome_cru = str(d['destino']).upper()
            if "MI" in nome_cru or "LATAM" in nome_cru:
                dest_nome = "MI / LATAM"
            else:
                parts = nome_cru.split('-')
                if len(parts) >= 2:
                    dest_nome = f"{parts[0].strip()} - {parts[1].strip()}"
                else:
                    dest_nome = nome_cru

            html_destinos += f"""
                <tr style="border-bottom: 1px dashed #1c2b42; font-weight: normal;">
                    <td style="text-align: left; padding: 10px 4px; font-weight: normal;">{dest_nome}</td>
                    <td style="text-align: center; padding: 10px 4px; color: #38bdf8; font-weight: normal;">{fmt(d['meta'])}</td>
                    <td style="text-align: center; padding: 10px 4px; color: #00D672; font-weight: normal;">{fmt(d['realizado'])}</td>
                    <td style="text-align: center; padding: 10px 4px; color: {cor_saldo}; font-weight: normal;">{saldo_str}</td>
                    <td style="text-align: center; padding: 10px 4px; color: {cor_ating}; font-weight: normal;">{ating:.0f}%</td>
                </tr>
            """
        html_destinos += """
                </tbody>
            </table>
        </div>
        """
    else:
        html_destinos += '<div style="color:#64748b; font-size:0.8rem; text-align:center;">Nenhum destino ativo reportado.</div>'

    html_exp_completo = f"""
    <div id="sec-exp" class="anc"></div>
    <details class="master-box" style="border-left-color: #00D672;" open>
        <summary>
            <div class="header-layout">
                <div class="icon-box" style="background-color: rgba(0, 214, 114, 0.15); color: #00D672;">🚚</div>
                <div class="master-metric-title">Expedição Realizada</div>
            </div>
            <div class="value-layout">
                <div class="master-metric-val">{fmt(vol_exp_hoje)}</div>
                <div class="master-metric-unit">TON</div>
            </div>
            <div class="master-metric-sub" style="color: #00D672;">Consolidado Ontem (D-1): {fmt(vol_exp_ontem)} t</div>
        </summary>
        <div class="master-content css-tabs-view" style="padding-top:16px;">
            <div style="text-align: center; margin-bottom: 16px;">
                <input type="radio" name="exp_main_view" id="view_turnos" checked>
                <label for="view_turnos" class="lbl-v-turnos">⏰ Turnos</label>

                <input type="radio" name="exp_main_view" id="view_destinos">
                <label for="view_destinos" class="lbl-v-destinos">📍 Destinos</label>

                <div class="view-content-exp" id="content_view_turnos" style="margin-top: 14px;">
                    <div class="css-tabs-exp">
                        <div style="text-align: center;">
                            <input type="radio" name="exp_tabs" id="tab_ontem">
                            <label for="tab_ontem" class="lbl-ontem">⏮️ Ontem (D-1)</label>

                            <input type="radio" name="exp_tabs" id="tab_hoje" checked>
                            <label for="tab_hoje" class="lbl-hoje">📅 Hoje</label>

                            <div class="tab-content-exp" id="content_ontem" style="margin-top: 14px;">
                                {html_ontem}
                            </div>

                            <div class="tab-content-exp" id="content_hoje" style="margin-top: 14px;">
                                {html_hoje}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="view-content-exp" id="content_view_destinos" style="margin-top: 14px; text-align: left;">
                    {html_destinos}
                </div>
            </div>
        </div>
    </details>
    """
    st.markdown(html_exp_completo.replace('\n', ''), unsafe_allow_html=True)

if pagina == "estoque":
    # ==============================================================================
    # 📦 BLOCO 4: ESTOQUE TOTAL E MATERIAIS
    # ==============================================================================
    html_est = '<div id="sec-estoque" class="anc"></div><details class="master-box" style="border-left-color: #9b59b6;">'
    html_est += f'''
    <summary>
        <div class="header-layout">
            <div class="icon-box" style="background-color: rgba(155, 89, 182, 0.15); color: #9b59b6;">📦</div>
            <div class="master-metric-title">Estoque Físico no Armazém</div>
        </div>
        <div class="value-layout">
            <div class="master-metric-val">{fmt(estoque_total)}</div>
            <div class="master-metric-unit">TON</div>
        </div>
        <div class="master-metric-sub" style="color: #9b59b6;">Status do Armazém: {status_transbordo}</div>
    </summary>
    <div class="master-content" style="padding-top:16px;">
    '''

    if dados_segregados:
        df_seg = pd.DataFrame(list(dados_segregados.items()), columns=["Material", "Toneladas"]).sort_values(by="Toneladas", ascending=False)
        chart_data_est = []
        for _, row in df_seg.iterrows():
            t_par = forcar_par(row["Toneladas"])
            mat_nome = str(row["Material"]).upper()

            if "SQ" in mat_nome:
                cor_barra = "#FF7700"
            elif "EQ" in mat_nome:
                cor_barra = "#00D672"
            else:
                cor_barra = "#38bdf8"

            chart_data_est.append({
                "label": row["Material"],
                "value": t_par,
                "text": f"{fmt(t_par)} t",
                "color": cor_barra
            })
        html_est += build_vertical_chart(chart_data_est)
    else:
        html_est += '<div style="color:gray;">Aguardando detalhamento de material...</div>'

    html_est += "</div></details>"
    st.markdown(html_est.replace('\n', ''), unsafe_allow_html=True)

if pagina == "frota":
    # ==============================================================================
    # 🚜 BLOCO 5: FROTA E EQUIPAMENTOS (VIA HISTÓRICO DKRO) + LEGENDA DE CORES
    # ==============================================================================
    df_frota = carregar_dados_nuvem("Historico_DKRO", cabecalho=0)

    frota_agrupada = {
        "hoje": {"00h - 08h": {"EMP": {}, "TALHA": {}}, "08h - 16h": {"EMP": {}, "TALHA": {}}, "16h - 00h": {"EMP": {}, "TALHA": {}}},
        "ontem": {"00h - 08h": {"EMP": {}, "TALHA": {}}, "08h - 16h": {"EMP": {}, "TALHA": {}}, "16h - 00h": {"EMP": {}, "TALHA": {}}}
    }

    equip_em_uso_hoje = 0

    if not df_frota.empty and len(df_frota.columns) >= 7:
        for _, row in df_frota.iterrows():
            try:
                dt_str = str(row.iloc[1]).strip()
                tipo = str(row.iloc[5]).strip().upper()
                equip = str(row.iloc[6]).strip().upper()
                cond = str(row.iloc[8]).strip().upper() if len(row) > 8 else "100% OK"

                if not equip or equip in ["NAN", "NONE", ""]: continue

                dt_obj = pd.to_datetime(dt_str, format="%d/%m/%Y %H:%M:%S", errors="coerce")
                if pd.isna(dt_obj):
                    dt_obj = pd.to_datetime(dt_str, errors="coerce", dayfirst=True)
                if pd.isna(dt_obj): continue

                d_date = dt_obj.date()
                d_hour = dt_obj.hour

                if d_date == hoje_date: day_key = "hoje"
                elif d_date == ontem_date: day_key = "ontem"
                else: continue

                if d_hour < 8: shift_key = "00h - 08h"
                elif d_hour < 16: shift_key = "08h - 16h"
                else: shift_key = "16h - 00h"

                cat_key = "TALHA" if "TALHA" in tipo or "PONTE" in tipo or "TALHA" in equip else "EMP"

                # Vale a PIOR condição registrada para o equipamento dentro do turno
                current_cond = frota_agrupada[day_key][shift_key][cat_key].get(equip, "100% OK")
                if "AVARIA" in cond:
                    frota_agrupada[day_key][shift_key][cat_key][equip] = "AVARIA"
                elif "ATEN" in cond and current_cond != "AVARIA":
                    frota_agrupada[day_key][shift_key][cat_key][equip] = "ATENÇÃO"
                else:
                    frota_agrupada[day_key][shift_key][cat_key][equip] = current_cond
            except: pass

        hoje_set = set()
        for s in ["00h - 08h", "08h - 16h", "16h - 00h"]:
            hoje_set.update(frota_agrupada["hoje"][s]["EMP"].keys())
            hoje_set.update(frota_agrupada["hoje"][s]["TALHA"].keys())
        equip_em_uso_hoje = len(hoje_set)

    agora_h = agora_br.hour
    ch_h_00 = "checked" if agora_h < 8 else ""
    ch_h_08 = "checked" if 8 <= agora_h < 16 else ""
    ch_h_16 = "checked" if 16 <= agora_h else ""

    def render_tags(dict_equip):
        if not dict_equip: return "<span style='color:#64748b; font-size:0.8rem; font-weight:normal;'>Nenhum registro neste turno.</span>"
        html_t = ""
        for eq, cond in sorted(dict_equip.items()):
            cls = "f-tag-avaria" if cond == "AVARIA" else ("f-tag-aten" if cond == "ATENÇÃO" else "f-tag-ok")
            html_t += f"<span class='tag-box {cls}'>{eq}</span> "
        return html_t

    html_legenda_frota = """
    <div class="f-legenda">
        <div class="f-leg-titulo">🎨 Legenda das cores</div>
        <div class="f-leg-item"><span class="f-leg-cor f-tag-ok"></span><span><b>Verde</b> — OK: nenhum problema apontado no checklist</span></div>
        <div class="f-leg-item"><span class="f-leg-cor f-tag-aten"></span><span><b>Amarelo</b> — Atenção: item de atenção apontado no checklist</span></div>
        <div class="f-leg-item"><span class="f-leg-cor f-tag-avaria"></span><span><b>Vermelho</b> — Avaria: equipamento com avaria apontada</span></div>
        <div class="f-leg-nota">Se houver mais de um apontamento no mesmo turno, vale a pior condição (avaria &gt; atenção &gt; OK).</div>
    </div>
    """

    html_frota = f"""
    <div id="sec-frota" class="anc"></div>
    <details class="master-box" style="border-left-color: #E67E22;">
        <summary>
            <div class="header-layout">
                <div class="icon-box" style="background-color: rgba(230, 126, 34, 0.15); color: #E67E22;">🚜</div>
                <div class="master-metric-title">Frota / Equipamentos</div>
            </div>
            <div class="value-layout">
                <div class="master-metric-val">{equip_em_uso_hoje}</div>
                <div class="master-metric-unit">Veículos Logados Hoje</div>
            </div>
            <div class="master-metric-sub" style="color: #E67E22;">Empilhadeiras e Talhas Elétricas</div>
        </summary>
        <div class="master-content" style="text-align: center; padding-top:16px;">
            <input type="radio" name="frota_day" id="frota_dia_ontem" class="f-rad-main">
            <input type="radio" name="frota_day" id="frota_dia_hoje" class="f-rad-main" checked>

            <div class="frota-tabs-main">
                <label for="frota_dia_ontem" class="lbl-f-ontem">⏮️ Ontem (D-1)</label>
                <label for="frota_dia_hoje" class="lbl-f-hoje">📅 Hoje</label>
            </div>

            <div id="frota_box_hoje" class="f-content-dia">
                <input type="radio" name="frota_h_shift" id="frota_h_00" class="f-rad-sub" {ch_h_00}>
                <input type="radio" name="frota_h_shift" id="frota_h_08" class="f-rad-sub" {ch_h_08}>
                <input type="radio" name="frota_h_shift" id="frota_h_16" class="f-rad-sub" {ch_h_16}>

                <div class="frota-tabs-sub">
                    <label for="frota_h_00" class="lbl-h-00">00h - 08h</label>
                    <label for="frota_h_08" class="lbl-h-08">08h - 16h</label>
                    <label for="frota_h_16" class="lbl-h-16">16h - 00h</label>
                </div>

                <div id="frota_h_content_00" class="f-content-turno-hoje">
                    <div class="f-tag-container"><div class="f-tag-title">🟢 Empilhadeiras Logadas</div><div>{render_tags(frota_agrupada['hoje']['00h - 08h']['EMP'])}</div></div>
                    <div class="f-tag-container" style="margin-bottom:0;"><div class="f-tag-title">🏗️ Talhas / Pontes Rolantes</div><div>{render_tags(frota_agrupada['hoje']['00h - 08h']['TALHA'])}</div></div>
                </div>
                <div id="frota_h_content_08" class="f-content-turno-hoje">
                    <div class="f-tag-container"><div class="f-tag-title">🟢 Empilhadeiras Logadas</div><div>{render_tags(frota_agrupada['hoje']['08h - 16h']['EMP'])}</div></div>
                    <div class="f-tag-container" style="margin-bottom:0;"><div class="f-tag-title">🏗️ Talhas / Pontes Rolantes</div><div>{render_tags(frota_agrupada['hoje']['08h - 16h']['TALHA'])}</div></div>
                </div>
                <div id="frota_h_content_16" class="f-content-turno-hoje">
                    <div class="f-tag-container"><div class="f-tag-title">🟢 Empilhadeiras Logadas</div><div>{render_tags(frota_agrupada['hoje']['16h - 00h']['EMP'])}</div></div>
                    <div class="f-tag-container" style="margin-bottom:0;"><div class="f-tag-title">🏗️ Talhas / Pontes Rolantes</div><div>{render_tags(frota_agrupada['hoje']['16h - 00h']['TALHA'])}</div></div>
                </div>
            </div>

            <div id="frota_box_ontem" class="f-content-dia">
                <input type="radio" name="frota_o_shift" id="frota_o_00" class="f-rad-sub">
                <input type="radio" name="frota_o_shift" id="frota_o_08" class="f-rad-sub" checked>
                <input type="radio" name="frota_o_shift" id="frota_o_16" class="f-rad-sub">

                <div class="frota-tabs-sub">
                    <label for="frota_o_00" class="lbl-o-00">00h - 08h</label>
                    <label for="frota_o_08" class="lbl-o-08">08h - 16h</label>
                    <label for="frota_o_16" class="lbl-o-16">16h - 00h</label>
                </div>

                <div id="frota_o_content_00" class="f-content-turno-ontem">
                    <div class="f-tag-container"><div class="f-tag-title">🟢 Empilhadeiras Logadas</div><div>{render_tags(frota_agrupada['ontem']['00h - 08h']['EMP'])}</div></div>
                    <div class="f-tag-container" style="margin-bottom:0;"><div class="f-tag-title">🏗️ Talhas / Pontes Rolantes</div><div>{render_tags(frota_agrupada['ontem']['00h - 08h']['TALHA'])}</div></div>
                </div>
                <div id="frota_o_content_08" class="f-content-turno-ontem">
                    <div class="f-tag-container"><div class="f-tag-title">🟢 Empilhadeiras Logadas</div><div>{render_tags(frota_agrupada['ontem']['08h - 16h']['EMP'])}</div></div>
                    <div class="f-tag-container" style="margin-bottom:0;"><div class="f-tag-title">🏗️ Talhas / Pontes Rolantes</div><div>{render_tags(frota_agrupada['ontem']['08h - 16h']['TALHA'])}</div></div>
                </div>
                <div id="frota_o_content_16" class="f-content-turno-ontem">
                    <div class="f-tag-container"><div class="f-tag-title">🟢 Empilhadeiras Logadas</div><div>{render_tags(frota_agrupada['ontem']['16h - 00h']['EMP'])}</div></div>
                    <div class="f-tag-container" style="margin-bottom:0;"><div class="f-tag-title">🏗️ Talhas / Pontes Rolantes</div><div>{render_tags(frota_agrupada['ontem']['16h - 00h']['TALHA'])}</div></div>
                </div>
            </div>

            {html_legenda_frota}
        </div>
    </details>
    """
    st.markdown(html_frota.replace('\n', ''), unsafe_allow_html=True)

if pagina == "frota":
    # ==============================================================================
    # ⛽ BLOCO 6: CONSUMO GLP MENSAL
    # ==============================================================================
    df_glp = carregar_dados_nuvem("Abastecimentos_GLP", cabecalho=None)
    html_glp = '<details class="master-box" style="border-left-color: #fd7e14;">'

    if not df_glp.empty and len(df_glp.columns) >= 8:
        df_g = pd.DataFrame()
        df_g["DATA_DT"] = pd.to_datetime(df_glp.iloc[:, 2].astype(str).str.strip(), format="%d/%m/%Y", errors="coerce")
        df_g = df_g.dropna(subset=["DATA_DT"])

        if not df_g.empty:
            df_g["MES_ANO"] = df_g["DATA_DT"].dt.strftime("%m/%Y")
            df_g["MAQUINA"] = df_glp.iloc[:, 5].astype(str).str.strip()
            df_g["KG_NUM"] = df_glp.iloc[:, 7].apply(safe_to_numeric)

            meses_disp = df_g["MES_ANO"].dropna().unique().tolist()
            if meses_disp:
                meses_disp.sort(key=lambda x: datetime.strptime(x, "%m/%Y"))
                mes_recente = meses_disp[-1]
                df_mes_recente = df_g[df_g["MES_ANO"] == mes_recente]
                total_glp_recente = forcar_par(df_mes_recente["KG_NUM"].sum())

                html_glp += f'''
                <summary>
                    <div class="header-layout">
                        <div class="icon-box" style="background-color: rgba(253, 126, 20, 0.15); color: #fd7e14;">⛽</div>
                        <div class="master-metric-title">Consumo de GLP da Frota</div>
                    </div>
                    <div class="value-layout">
                        <div class="master-metric-val">{fmt(total_glp_recente)}</div>
                        <div class="master-metric-unit">KG</div>
                    </div>
                    <div class="master-metric-sub" style="color: #fd7e14;">Acumulado do Mês Atual ({mes_recente})</div>
                </summary>
                '''
                html_glp += '<div class="master-content" style="padding-top:16px;">'

                df_maq = df_mes_recente.groupby("MAQUINA")["KG_NUM"].sum().reset_index().sort_values(by="KG_NUM", ascending=False)

                if not df_maq.empty:
                    chart_data_glp = []
                    for _, row in df_maq.iterrows():
                        val_kg_par = forcar_par(row["KG_NUM"])
                        chart_data_glp.append({
                            "label": row["MAQUINA"],
                            "value": val_kg_par,
                            "text": f"{fmt(val_kg_par)} kg",
                            "color": "#fd7e14"
                        })
                    html_glp += build_vertical_chart(chart_data_glp)
                else:
                    html_glp += '<div style="color:gray; text-align:center;">Sem consumo registrado.</div>'
                html_glp += '</div>'
    else:
        html_glp += '''
        <summary>
            <div class="header-layout">
                <div class="icon-box" style="background-color: rgba(253, 126, 20, 0.15); color: #fd7e14;">⛽</div>
                <div class="master-metric-title">Consumo de GLP</div>
            </div>
        </summary>
        <div class="master-content"><div style="color:gray; padding-top:16px;">Planilha indisponível.</div></div>
        '''

    html_glp += '</details>'
    st.markdown(html_glp.replace('\n', ''), unsafe_allow_html=True)

if pagina == "frota":
    # ==============================================================================
    # 🩺 BLOCO 7: AUDITORIA BAFÔMETRO (PROTEGIDO COM BOTÃO E SENHA)
    # ==============================================================================
    col_baf_btn, col_baf_lock = st.columns([3, 1], vertical_alignment="center")

    with col_baf_btn:
        if not st.session_state.bafometro_autenticado:
            btn_abrir_modal = st.button("🔒 Acessar Auditoria de Bafômetro", use_container_width=True)
        else:
            st.markdown("<div style='color:#00D672; font-size:0.85rem; font-weight:bold; text-align:left;'>🔓 Acesso ao Bafômetro Liberado</div>", unsafe_allow_html=True)

    with col_baf_lock:
        if st.session_state.bafometro_autenticado:
            if st.button("Bloquear", use_container_width=True):
                st.session_state.bafometro_autenticado = False
                st.rerun()

    @st.dialog("Segurança Operacional - Acesso Restrito")
    def modal_senha_bafometro():
        st.markdown("<p style='font-size:0.85rem; color:#94a3b8;'>Digite a senha de gestor para visualizar os dados de bafômetro dos motoristas:</p>", unsafe_allow_html=True)
        senha_digitada = st.text_input("Senha", type="password", key="input_senha_baf")

        col_confirmar, col_fechar = st.columns(2)
        with col_confirmar:
            if st.button("Confirmar", use_container_width=True, type="primary"):
                if senha_digitada == SENHA_BAFOMETRO:
                    st.session_state.bafometro_autenticado = True
                    st.success("Acesso autorizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Senha incorreta. Tente novamente.")
        with col_fechar:
            if st.button("Cancelar", use_container_width=True):
                st.rerun()

    if not st.session_state.bafometro_autenticado and 'btn_abrir_modal' in locals() and btn_abrir_modal:
        modal_senha_bafometro()

    if st.session_state.bafometro_autenticado:
        total_testes = len(df_bafometro) if not df_bafometro.empty else 0

        col_res = None
        for c in df_bafometro.columns:
            if any(termo in str(c).upper() for termo in ["RESULTADO", "STATUS", "PARECER"]):
                col_res = c
                break

        aprovados = 0
        pendentes_reprovados = 0
        if not df_bafometro.empty and col_res:
            aprovados = int((df_bafometro[col_res].astype(str).str.upper().str.contains("APROV|0.00|0,00|OK|NEGATIVO")).sum())
            pendentes_reprovados = max(0, total_testes - aprovados)

        cor_baf_borda = "#00D672" if pendentes_reprovados == 0 else "#E74C3C"

        html_baf = f"""
        <details class="master-box" style="border-left-color: {cor_baf_borda};" open>
            <summary>
                <div class="header-layout">
                    <div class="icon-box" style="background-color: rgba(0, 214, 114, 0.15); color: {cor_baf_borda};">🩺</div>
                    <div class="master-metric-title">Auditoria de Bafômetro (H&S)</div>
                </div>
                <div class="value-layout">
                    <div class="master-metric-val">{total_testes}</div>
                    <div class="master-metric-unit">Testes Registrados Hoje</div>
                </div>
                <div class="master-metric-sub" style="color: {cor_baf_borda};">
                    Aprovados: {aprovados} | Pendentes / Reprovados: {pendentes_reprovados}
                </div>
            </summary>
            <div class="master-content" style="padding-top:16px;">
        """

        if not df_bafometro.empty:
            html_baf += """
                <div style="overflow-x:auto;">
                    <table style="width:100%; border-collapse:collapse; font-size:0.75rem; text-align:left; color:#ffffff;">
                        <thead>
                            <tr style="border-bottom:1px solid #1c2b42; color:#94a3b8;">
            """
            cols_para_exibir = list(df_bafometro.columns[:5])
            for c in cols_para_exibir:
                html_baf += f"<th style='padding:6px;'>{str(c).upper()}</th>"
            html_baf += "</tr></thead><tbody>"

            for _, row_b in df_bafometro.head(15).iterrows():
                html_baf += "<tr style='border-bottom:1px dashed #1c2b42;'>"
                for c in cols_para_exibir:
                    val_cel = str(row_b.get(c, ""))
                    cor_cel = "#ffffff"
                    if any(x in val_cel.upper() for x in ["APROV", "OK", "0,00", "0.00"]):
                        cor_cel = "#00D672"
                    elif any(x in val_cel.upper() for x in ["REPROV", "POSITIV", "RECUS"]):
                        cor_cel = "#E74C3C"
                    elif any(x in val_cel.upper() for x in ["PEND", "AGUARD"]):
                        cor_cel = "#FF9F1C"
                    html_baf += f"<td style='padding:6px; color:{cor_cel};'>{val_cel}</td>"
                html_baf += "</tr>"
            html_baf += "</tbody></table></div>"
        else:
            html_baf += "<div style='color:gray; text-align:center;'>Nenhum registro de teste encontrado na aba Bafometro_Status.</div>"

        html_baf += "</div></details>"
        st.markdown(html_baf.replace('\n', ''), unsafe_allow_html=True)

if pagina == "exp":
    # ==============================================================================
    # 📊 BLOCO 8: COMPARATIVO PRODUÇÃO vs EXPEDIÇÃO (NO FINAL)
    # ==============================================================================
    hoje_dt = hoje_date
    fim_ano = date(hoje_dt.year, 12, 31)
    dias_restantes = max(1, (fim_ano - hoje_dt).days)
    meta_teto_estoque = 3468.0

    carr_base_ano = 1362558.0
    prod_base_ano = 1362676.0
    ritmo_esperado_dia = 5200.0

    carr_ano_atual = forcar_par(carr_base_ano + vol_hoje)
    prod_ano_atual = forcar_par(prod_base_ano + prod_hoje_calc)

    diff_prod_carr = forcar_par(abs(prod_ano_atual - carr_ano_atual))

    if carr_ano_atual >= prod_ano_atual:
        txt_variacao = f"+{fmt(diff_prod_carr)} t (Expedição Superando)"
        cor_variacao = "#00D672"
    else:
        txt_variacao = f"+{fmt(diff_prod_carr)} t (Produção Superando)"
        cor_variacao = "#FF9F1C"

    excesso_estoque = max(0.0, estoque_total - meta_teto_estoque)
    ritmo_extra_dia = excesso_estoque / dias_restantes
    meta_diaria_carr = forcar_par(ritmo_esperado_dia + ritmo_extra_dia)

    proj_prod_fechamento = forcar_par(prod_ano_atual + (dias_restantes * ritmo_esperado_dia))
    carr_futuro_nec = (estoque_total + (dias_restantes * ritmo_esperado_dia)) - meta_teto_estoque
    proj_carr_fechamento = forcar_par(carr_ano_atual + carr_futuro_nec)

    html_meta_anual = f"""
    <details class="master-box" style="border-left-color: #007BFF;" open>
        <summary>
            <div class="header-layout">
                <div class="icon-box" style="background-color: rgba(0, 123, 255, 0.15); color: #007BFF;">📊</div>
                <div class="master-metric-title">Comparativo Produção vs Expedição</div>
            </div>
            <div class="value-layout">
                <div class="master-metric-val">{fmt(carr_ano_atual)}</div>
                <div class="master-metric-unit">t Expedidas</div>
            </div>
            <div class="master-metric-sub" style="color: #007BFF;">Meta Diária Necessária: {fmt(meta_diaria_carr)} t/dia</div>
        </summary>
        <div class="master-content" style="padding-top:16px;">
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
                <div style="background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:10px;">
                    <div style="font-size:0.75rem; color:#007BFF; font-weight:bold; text-transform:uppercase;">EXPEDIÇÃO ANUAL</div>
                    <div style="font-size:1.4rem; font-weight:bold; color:#fff; margin:4px 0;">{fmt(carr_ano_atual)} <span style="font-size:0.8rem; color:#64748b; font-weight:normal;">t</span></div>
                    <div style="font-size:0.7rem; color:#64748b;">Proj. 31/12: <span style="color:#007BFF;">{fmt(proj_carr_fechamento)} t</span></div>
                </div>
                <div style="background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:10px;">
                    <div style="font-size:0.75rem; color:#00D672; font-weight:bold; text-transform:uppercase;">PRODUÇÃO ANUAL</div>
                    <div style="font-size:1.4rem; font-weight:bold; color:#fff; margin:4px 0;">{fmt(prod_ano_atual)} <span style="font-size:0.8rem; color:#64748b; font-weight:normal;">t</span></div>
                    <div style="font-size:0.7rem; color:#64748b;">Proj. 31/12: <span style="color:#00D672;">{fmt(proj_prod_fechamento)} t</span></div>
                </div>
            </div>
            <div style="background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:12px; font-size:0.82rem; color:#cbd5e1; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;">
                <span>Variação Produção vs Expedição: <span style="color:{cor_variacao}; font-size:0.9rem; font-weight:bold;">{txt_variacao}</span></span>
                <span>Estoque de Virada 25/26: <span style="color:#38bdf8; font-size:0.9rem; font-weight:bold;">3.468 t</span></span>
            </div>
        </div>
    </details>
    """
    st.markdown(html_meta_anual.replace('\n', ''), unsafe_allow_html=True)

st.markdown("<br><center><span style='color:#64748b; font-size: 0.75rem; font-weight: normal; letter-spacing: 0.5px;'>A.L.O.V.E - Mobile / Developed by Crist Ciriaco</span></center>", unsafe_allow_html=True)
