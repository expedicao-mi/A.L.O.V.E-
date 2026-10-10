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
from streamlit_autorefresh import st_autorefresh

# ==============================================================================
# ⚙️ CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
LOGO_ALOVE_URL = "https://raw.githubusercontent.com/expedicao-mi/A.L.O.V.E-/main/app_icon.png"
BANNER_TOPO_URL = "https://raw.githubusercontent.com/expedicao-mi/A.L.O.V.E-/main/logo_alove.jpg?v=99"

st.set_page_config(
    page_title="A.L.O.V.E. Mobile",
    page_icon="🚛",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st_autorefresh(interval=60000, limit=None, key="refresh_mobile")

if "bafometro_autenticado" not in st.session_state:
    st.session_state.bafometro_autenticado = False

# ==============================================================================
# 🎨 CSS (LAYOUT VERTICAL COM DESIGN DE APP E BARRA FIXA)
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

st.markdown("""
    <style>
        /* MATA AS MARCAS DO STREAMLIT */
        #MainMenu, footer, header, [data-testid="manage-app-button"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
            display: none !important; visibility: hidden !important;
        }

        /* FUNDO E SCROLL */
        html, body, [data-testid="stAppViewContainer"], .stApp, .main {
            background: radial-gradient(ellipse at top, #0c1a33 0%, #070d18 55%, #050911 100%) !important;
            border: none !important; outline: none !important; box-shadow: none !important;
        }
        [data-testid="stMain"], section.main { scroll-behavior: smooth; }

        /* COLUNA CENTRAL ESTILO APP */
        .block-container {
            padding-top: 0rem !important; padding-bottom: 5.5rem !important;
            padding-left: 0.8rem !important; padding-right: 0.8rem !important;
            max-width: 560px !important; margin: 0 auto !important;
        }

        .anc { scroll-margin-top: 8px; height: 0; }
        
        /* BANNER */
        .topo-banner { margin: 0 -0.8rem 14px -0.8rem; background: #050d1a; border-bottom: 1px solid #12506e; text-align: center; }
        .topo-banner img { width: 100%; max-height: 130px; object-fit: cover; display: block; margin: 0 auto; }

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

        /* STATUS (CONECTADO) */
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
        details.notif-mais > summary { cursor: pointer; padding: 12px 4px 2px 4px; color: #38bdf8; font-weight: 600; font-size: .9rem; display: flex; justify-content: space-between; align-items: center; }
        details.notif-mais[open] > summary .chev { transform: rotate(90deg); }

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
        details.st-card, div.st-card {
            --c: #38a9ff; background: #0a1424; background: color-mix(in srgb, var(--c) 9%, #0a1424);
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

        /* TABS CSS NATIVO (PARA PRODUÇÃO/EXPEDIÇÃO/FROTA) */
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

        /* TABS FROTA */
        .frota-tabs-main { display: flex; gap: 8px; justify-content: center; margin-bottom: 16px; }
        .frota-tabs-main label { padding: 8px 16px; background-color: #162438; color: #94a3b8; border-radius: 6px; cursor: pointer; border: 1px solid #1c2b42; font-weight: normal; font-size: 0.9rem; transition: 0.2s; }
        .frota-tabs-sub { display: flex; gap: 6px; justify-content: center; margin-bottom: 14px; }
        .frota-tabs-sub label { padding: 6px 12px; background-color: #111c2e; color: #64748b; border-radius: 6px; cursor: pointer; border: 1px solid #1c2b42; font-weight: normal; font-size: 0.8rem; transition: 0.2s; }

        .f-rad-main, .f-rad-sub, input[type="radio"] { display: none; }
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
        .f-tag-container { margin-bottom: 16px; text-align: left; }
        .tag-box { display: inline-block; padding: 6px 10px; margin: 3px; border-radius: 6px; font-weight: normal; font-size: 0.8rem; text-align: center; }
        .f-legenda { margin-top: 14px; background: #05080f; border: 1px solid #1c2b42; border-radius: 8px; padding: 10px 12px; text-align: left; }
        .f-leg-titulo { color: #94a3b8; font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 8px; }
        .f-leg-item { display: flex; align-items: center; gap: 10px; color: #cbd5e1; font-size: .8rem; padding: 3px 0; }
        .f-leg-cor { width: 16px; height: 16px; border-radius: 4px; flex-shrink: 0; }

        /* ---------- BARRA DE NAVEGAÇÃO INFERIOR CSS (FIXA, SEM BOTÕES FEIOS) ---------- */
        .bottom-nav { position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 100%; max-width: 560px; z-index: 999990; display: flex; justify-content: space-around; background: #070d18; border-top: 1px solid #12506e; padding: 10px 0 calc(10px + env(safe-area-inset-bottom)); }
        .bottom-nav a { color: #8fa6c4; text-decoration: none; font-size: .7rem; display: flex; flex-direction: column; align-items: center; gap: 4px; min-width: 56px; }
        .bottom-nav a span { font-size: 1.4rem; }
        .bottom-nav a:active { color: #00D672; }

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

@st.cache_data(ttl=20)
def carregar_dados_nuvem(worksheet_name: str, cabecalho=0):
    sheet_encoded = urllib.parse.quote(worksheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_encoded}&headers=1"
    try:
        df = pd.read_csv(url, header=cabecalho)
        return df.dropna(how="all", axis=1).dropna(how="all", axis=0)
    except: return pd.DataFrame()

@st.cache_data(ttl=20)
def carregar_tabela_cega(worksheet_name: str, chave: str = "DESTINO"):
    """Procura a palavra-chave em qualquer lugar do topo e define ali como cabeçalho."""
    sheet_encoded = urllib.parse.quote(worksheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_encoded}"
    try:
        raw = pd.read_csv(url, header=None, dtype=str, keep_default_na=False)
    except: return pd.DataFrame()

    for idx_linha in range(min(len(raw), 10)):
        for idx_col in range(min(len(raw.columns), 10)):
            if str(raw.iloc[idx_linha, idx_col]).strip().upper() == chave.upper():
                cabecalho = [str(c).strip().upper() for c in raw.iloc[idx_linha].tolist()]
                corpo = raw.iloc[idx_linha + 1:].copy()
                corpo.columns = cabecalho
                corpo = corpo.loc[:, ~corpo.columns.str.contains('^UNNAMED', na=False, case=False)]
                corpo = corpo[~(corpo.astype(str).apply(lambda r: "".join(r).strip() == "", axis=1))]
                return corpo.reset_index(drop=True)
    return pd.DataFrame()

def safe_to_numeric(val):
    if pd.isna(val) or val == "" or val is None: return 0.0
    if isinstance(val, (int, float)): return float(val)
    try: return float(str(val).strip().replace(".", "").replace(",", "."))
    except: return 0.0

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

df_dash = carregar_dados_nuvem("Mobile_Dashboard", cabecalho=0)
df_qual = carregar_dados_nuvem("Mobile_Qualidade", cabecalho=0)
df_alertas = carregar_dados_nuvem("Mobile_Alertas", cabecalho=0)
df_cache = carregar_dados_nuvem("Cache_Painel", cabecalho=0)
df_patio_dest = carregar_tabela_cega("Patio_Destino_Status", "DESTINO")
df_status_virada = carregar_dados_nuvem("Status_Virada_Turnos", cabecalho=0)
df_balanco_dest = carregar_tabela_cega("Balanco_Expedicao_Destino", "DESTINO")
df_bafometro = carregar_dados_nuvem("Bafometro_Status", cabecalho=0)
if df_bafometro.empty: df_bafometro = carregar_dados_nuvem("Auditoria_Bafometro", cabecalho=0)
df_frota = carregar_dados_nuvem("Historico_DKRO", cabecalho=0)

cache_dict = {str(row.iloc[0]).strip(): str(row.iloc[1]).strip() for _, row in df_cache.iterrows()} if not df_cache.empty else {}
dados_segregados = parse_robusto(cache_dict.get("dados_segregados", "{}"))

ultima_att = None
vol_hoje = vol_ontem = prev_carr = prod_hoje_calc = prev_prod = estoque_total = 0
status_transbordo = ritmo_torre = "NORMAL"

# 🟢 NORMALIZAÇÃO TOTAL DE COLUNAS (Ignora maiúsculas, minúsculas e espaços em branco)
if not df_dash.empty:
    df_dash.columns = [str(c).strip().upper() for c in df_dash.columns]
    row_d = df_dash.iloc[0]
    
    # Função auxiliar interna para buscar independente de pequenas variações de nome
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

# 🟢 FALLBACK DE PREVISÃO CASO VENHA ZERADO DO DASHBOARD:
# Se prev_prod ou prev_carr vierem zerados por delay de sincronização, calcula no próprio app:
if prev_prod == 0 and prod_hoje_calc > 0:
    horas_corridas = max(0.1, agora_br.hour + (agora_br.minute / 60.0))
    prev_prod = forcar_par((prod_hoje_calc / horas_corridas) * 24.0)

if prev_carr == 0 and vol_hoje > 0:
    horas_corridas = max(0.1, agora_br.hour + (agora_br.minute / 60.0))
    prev_carr = forcar_par((vol_hoje / horas_corridas) * 24.0)

    ritmo_torre_bruto = str(row_d.get("RITMO_TORRE", "NORMAL")).upper()
    ritmo_torre = "RITMO DE ATUALIZAÇÃO: RÁPIDO" if "12" in ritmo_torre_bruto or "ACELERADO" in ritmo_torre_bruto else ritmo_torre_bruto

    ritmo_torre_bruto = str(row_d.get("RITMO_TORRE", "NORMAL")).upper()
    ritmo_torre = "RITMO DE ATUALIZAÇÃO: RÁPIDO" if "12" in ritmo_torre_bruto or "ACELERADO" in ritmo_torre_bruto else ritmo_torre_bruto

try: dt_att = datetime.strptime(ultima_att[:19], "%d/%m/%Y %H:%M:%S")
except: dt_att = agora_br

minutos_inativos = (agora_br - dt_att).total_seconds() / 60.0
conn_txt, conn_cor = ("CONECTADO", "#00D672") if minutos_inativos <= 15 else ("ATRASADO", "#FFD600") if minutos_inativos <= 45 else ("DESCONECTADO", "#E74C3C")
conn_hora = dt_att.strftime("%H:%M:%S") if dt_att.date() == hoje_date else dt_att.strftime("%d/%m %H:%M")

# ==============================================================================
# 🎯 PROCESSAMENTO DO PÁTIO (DESTINOS E STATUS)
# ==============================================================================
STATUS_COLS = {"PR": ("PR_VEIC", "PR_TON"), "00": ("00_VEIC", "00_TON"), "01": ("01_VEIC", "01_TON"), "FC": ("FC_VEIC", "FC_TON")}
destinos_por_status = {"PR": [], "00": [], "01": [], "FC": [], "TR": []}
dados_patio = {k: {"veiculos": 0, "peso": 0} for k in ["PR", "00", "01", "FC", "TR"]}
total_planilha = {k: {"veiculos": 0, "peso": 0} for k in ["PR", "00", "01", "FC"]}

if not df_patio_dest.empty:
    for _, linha in df_patio_dest.iterrows():
        dest_nome = str(linha.get("DESTINO", "")).strip()
        if not dest_nome or dest_nome.upper() in ["NAN", "NONE", "DESTINO"]: continue

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

dif_status = {}
for chv in STATUS_COLS:
    lista = destinos_por_status[chv]
    if lista:
        dados_patio[chv]["veiculos"] = sum(i["veic"] for i in lista)
        dados_patio[chv]["peso"] = sum(i["ton"] for i in lista)
        dif_status[chv] = total_planilha[chv]["veiculos"] - dados_patio[chv]["veiculos"]
    else:
        dados_patio[chv]["veiculos"], dados_patio[chv]["peso"], dif_status[chv] = total_planilha[chv]["veiculos"], total_planilha[chv]["peso"], 0

dados_patio["TR"]["veiculos"] = int(safe_to_numeric(df_dash.iloc[0].get("TR_VEIC", 0))) if not df_dash.empty else 0
dados_patio["TR"]["peso"] = forcar_par(safe_to_numeric(df_dash.iloc[0].get("TR_TON", 0))) if not df_dash.empty else 0

total_veiculos_fisicos = dados_patio["00"]["veiculos"] + dados_patio["01"]["veiculos"] + dados_patio["FC"]["veiculos"]
vol_patio_disponivel = forcar_par(dados_patio["00"]["peso"] + dados_patio["01"]["peso"] + dados_patio["FC"]["peso"])

# ==============================================================================
# 🎯 PROCESSAMENTO PRODUÇÃO E VIRADA DE LINHA
# ==============================================================================
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
# 🎯 PROCESSAMENTO EXPEDIÇÃO (BALANÇO DESTINOS)
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

# ==============================================================================
# 🎯 TOPO HTML: BANNER E STATUS (Sempre Visível)
# ==============================================================================
st.markdown(f'<div id="sec-inicio" class="anc"></div><div class="topo-banner"><img src="{BANNER_TOPO_URL}"></div>', unsafe_allow_html=True)

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
        if st.button("🔄 Atualizar", use_container_width=True):
            st.cache_data.clear(); st.rerun()

# ==============================================================================
# 🔔 ALERTAS GERAIS E NOTIFICAÇÕES (Sempre Visível)
# ==============================================================================
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

# ==============================================================================
# 📦 CONSTRUÇÃO DOS MÓDULOS DE RENDERIZAÇÃO (Rolagem Vertical)
# ==============================================================================

# --- MÓDULO PÁTIO ---
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

# --- MÓDULO PRODUÇÃO ---
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

            if "🚨" in st_em: cor_alerta = "#E74C3C"; txt_alerta = f"⚠️ Falta E-mail ({st_em})"
            elif "✅" in st_em: cor_alerta = "#00D672"; txt_alerta = f"📧 E-mail {st_em}"
            else: cor_alerta = "#38bdf8"; txt_alerta = f"📧 {st_em}"

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
                <div><div style='font-size:0.7rem; color:#64748b; font-weight:bold;'>ALVURA</div><div style='font-size:1.2rem; font-weight:normal; color:{c_alv}; margin:4px 0;'>{fmt(q_alvura, 2)}%</div><div style='font-size:0.65rem; color:#475569;'>(Mín: 88,5)</div></div>
                <div><div style='font-size:0.7rem; color:#64748b; font-weight:bold;'>SUJIDADE</div><div style='font-size:1.2rem; font-weight:normal; color:{c_suj}; margin:4px 0;'>{fmt(q_suj, 2)}</div><div style='font-size:0.65rem; color:#475569;'>(Máx: 2,5)</div></div>
                <div><div style='font-size:0.7rem; color:#64748b; font-weight:bold;'>VISCOSID.</div><div style='font-size:1.2rem; font-weight:normal; color:{c_vis}; margin:4px 0;'>{fmt(q_visc)}</div><div style='font-size:0.65rem; color:#475569;'>(Mín: 650)</div></div>
                <div><div style='font-size:0.7rem; color:#64748b; font-weight:bold;'>pH</div><div style='font-size:1.2rem; font-weight:normal; color:{c_ph}; margin:4px 0;'>{fmt(q_ph, 1)}</div><div style='font-size:0.65rem; color:#475569;'>(5,5 - 8,5)</div></div>
            </div>
            {html_virada}
        </div>
        """
    else:
        html_prod_content += f"<div style='color:gray; padding:10px 0;'>Aguardando dados da {maq}...</div>"

html_prod_completo = f"""
<div id="sec-prod" class="anc"></div>
<details class="master-box" style="border-left-color: #E5B800;" open>
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

# --- MÓDULO EXPEDIÇÃO ---
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
        if dt_a.weekday() in [6, 0]: tns.append({"letra": f"Turno {ls.get('madrugada','D')}", "v": 0, "str_vol": "EM FOLGA", "horario": "Somente Armazen."})
        else: tns.append({"letra": f"Turno {ls.get('madrugada','D')}", "v": v1, "str_vol": f"{fmt(v1)} t", "horario": "00h - 08h"})
        tns.append({"letra": f"Turno {ls.get('08_16','C')}", "v": v2, "str_vol": f"{fmt(v2)} t", "horario": "08h - 16h"})
        tns.append({"letra": f"Turno {ls.get('16_00','B')}", "v": v3, "str_vol": f"{fmt(v3)} t", "horario": "16h - 00h"})
        return tns
    except: return []

tns_hoje = func_exp_dados(hoje_date)
tns_ontem = func_exp_dados(ontem_date)

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
    html_destinos += "</tbody></table></div>"
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
            <div class="master-metric-val">{fmt(vol_hoje)}</div>
            <div class="master-metric-unit">TON</div>
        </div>
        <div class="master-metric-sub" style="color: #00D672;">Consolidado Ontem (D-1): {fmt(vol_ontem)} t</div>
        <div class="master-metric-sub" style="color: #64748b;">Prev. Fechamento: {fmt(prev_carr)} t</div>
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
                            <div style='font-size:0.75rem; font-weight:normal; color:#38bdf8; text-transform:uppercase; margin-bottom:10px; text-align:left;'>Fechamento de Ontem ({ontem_date.strftime('%d/%m')}):</div>
                            <div style='display:flex; gap:6px; margin-bottom:8px;'>
"""
for t in tns_ontem:
    v_str_o = t.get("str_vol", f"{fmt(t['v'])} t")
    html_val_o = f"<div style='font-size:0.85rem; font-weight:normal; color:#E74C3C; padding: 5px 0;'>EM FOLGA</div>" if v_str_o == "EM FOLGA" else f"<div style='font-size:1.1rem; font-weight:normal; color:#ffffff;'>{v_str_o}</div>"
    html_exp_completo += f"<div style='flex:1; background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:8px; text-align:center;'><div style='font-size:0.75rem; font-weight:bold; color:#38bdf8;'>{t['letra']}</div>{html_val_o}<div style='font-size:0.65rem; color:#64748b;'>{t['horario']}</div></div>"
html_exp_completo += """
                            </div>
                        </div>

                        <div class="tab-content-exp" id="content_hoje" style="margin-top: 14px;">
                            <div style='font-size:0.75rem; font-weight:normal; color:#00D672; text-transform:uppercase; margin-bottom:10px; text-align:left;'>Turnos em Operação Hoje:</div>
                            <div style='display:flex; gap:6px; margin-bottom:8px;'>
"""
for i, t in enumerate(tns_hoje):
    is_atv = False
    if hoje_date == agora_br.date():
        if agora_br.hour < 8 and i == 0: is_atv = True
        elif 8 <= agora_br.hour < 16 and i == 1: is_atv = True
        elif agora_br.hour >= 16 and i == 2: is_atv = True
    c_b, c_t = ("#FF9F1C", "#FF9F1C") if is_atv else ("#1c2b42", "#ffffff")
    v_str = t.get("str_vol", f"{fmt(t['v'])} t")
    html_val = f"<div style='font-size:0.85rem; font-weight:normal; color:#E74C3C; padding: 5px 0;'>EM FOLGA</div>" if v_str == "EM FOLGA" else f"<div style='font-size:1.1rem; font-weight:normal; color:#ffffff;'>{v_str}</div>"
    html_exp_completo += f"<div style='flex:1; background-color:#0a101d; border:1px solid {c_b}; border-radius:8px; padding:8px; text-align:center;'><div style='font-size:0.75rem; font-weight:bold; color:{c_t};'>{t['letra']}</div>{html_val}<div style='font-size:0.65rem; color:#64748b;'>{t['horario']}{' (ATIVO)' if is_atv else ''}</div></div>"
html_exp_completo += f"""
                            </div>
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

# --- MÓDULO ESTOQUE FÍSICO ---
html_est = f'<div id="sec-estoque" class="anc"></div><details class="master-box" style="border-left-color: #9b59b6;" open>'
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
    html_est += "<div style='display:flex; flex-wrap:wrap; gap:8px; justify-content:center;'>"
    for _, r in df_seg.iterrows():
        t = forcar_par(r["Toneladas"])
        m = str(r["Material"]).upper()
        cb = "#00D672" if "EQ" in m else "#38bdf8"
        html_est += f"<div style='flex:1; min-width:30%; background-color:#0a101d; border:1px solid #1c2b42; border-radius:6px; padding:10px; text-align:center;'><div style='font-size:0.75rem; color:#94a3b8; font-weight:bold;'>{m}</div><div style='font-size:1.1rem; font-weight:bold; color:{cb}; margin-top:2px;'>{fmt(t)} t</div></div>"
    html_est += "</div>"
else:
    html_est += '<div style="color:gray;">Aguardando detalhamento de material...</div>'

html_est += "</div></details>"

# --- MÓDULO FROTA E EQUIPAMENTOS ---
frota_agr = {"h": {"e": [], "t": []}, "o": {"e": [], "t": []}}
if not df_frota.empty and len(df_frota.columns) >= 7:
    for _, r in df_frota.iterrows():
        try:
            dt, tp, eq, cd = str(r.iloc[1]).strip(), str(r.iloc[5]).strip().upper(), str(r.iloc[6]).strip().upper(), str(r.iloc[8]).strip().upper() if len(r)>8 else "OK"
            if not eq or eq in ["NAN", "NONE", ""]: continue
            dto = pd.to_datetime(dt, format="%d/%m/%Y %H:%M:%S", errors="coerce")
            if pd.isna(dto): dto = pd.to_datetime(dt, errors="coerce", dayfirst=True)
            if pd.isna(dto): continue
            
            dk = "h" if dto.date() == hoje_date else ("o" if dto.date() == ontem_date else None)
            if not dk: continue
            
            ck = "t" if "TALHA" in tp or "PONTE" in tp or "TALHA" in eq else "e"
            cnd = "AVARIA" if "AVARIA" in cd else ("ATENÇÃO" if "ATEN" in cd else "OK")
            
            exist = next((i for i in frota_agr[dk][ck] if i['eq'] == eq), None)
            if exist:
                if cnd == "AVARIA": exist['c'] = "AVARIA"
                elif cnd == "ATENÇÃO" and exist['c'] != "AVARIA": exist['c'] = "ATENÇÃO"
            else:
                frota_agr[dk][ck].append({"eq": eq, "c": cnd})
        except: pass

v_hoje = len(frota_agr['h']['e']) + len(frota_agr['h']['t'])

def rnd_tg(lst):
    if not lst: return "<span style='color:#64748b; font-size:0.8rem;'>Nenhum registro.</span>"
    lst.sort(key=lambda x: x['eq'])
    r = ""
    for i in lst:
        cl = "f-tag-avaria" if i['c'] == "AVARIA" else ("f-tag-aten" if i['c'] == "ATENÇÃO" else "f-tag-ok")
        r += f"<span class='tag-box {cl}'>{i['eq']}</span> "
    return r

html_frota = f'<div id="sec-frota" class="anc"></div><details class="master-box" style="border-left-color:#E67E22;"><summary><div class="header-layout"><div class="icon-box" style="background-color:rgba(230,126,34,.15); color:#E67E22;">🚜</div><div class="master-metric-title">Frota e Equipamentos</div></div><div class="value-layout"><div class="master-metric-val">{v_hoje}</div><div class="master-metric-unit">Veículos Logados Hoje</div></div><div class="master-metric-sub" style="color:#E67E22;">Empilhadeiras e Talhas Elétricas</div></summary><div class="master-content" style="padding-top:16px;">'
html_frota += f"<div style='font-size:0.75rem; font-weight:bold; color:#00D672; text-transform:uppercase; margin-bottom:8px;'>📅 LOGADOS HOJE ({hoje_date.strftime('%d/%m')})</div><div style='background-color:#05080f; padding:12px; border-radius:8px; border:1px solid #1c2b42; margin-bottom:16px;'><div class='f-tag-title'>🟢 Empilhadeiras ({len(frota_agr['h']['e'])})</div><div style='margin-bottom:12px;'>{rnd_tg(frota_agr['h']['e'])}</div><div class='f-tag-title'>🏗️ Talhas / Pontes ({len(frota_agr['h']['t'])})</div><div>{rnd_tg(frota_agr['h']['t'])}</div></div>"
html_frota += f"<div style='font-size:0.75rem; font-weight:bold; color:#38bdf8; text-transform:uppercase; margin-bottom:8px;'>⏮️ LOGADOS ONTEM ({ontem_date.strftime('%d/%m')})</div><div style='background-color:#05080f; padding:12px; border-radius:8px; border:1px solid #1c2b42; margin-bottom:16px;'><div class='f-tag-title'>🟢 Empilhadeiras ({len(frota_agr['o']['e'])})</div><div style='margin-bottom:12px;'>{rnd_tg(frota_agr['o']['e'])}</div><div class='f-tag-title'>🏗️ Talhas / Pontes ({len(frota_agr['o']['t'])})</div><div>{rnd_tg(frota_agr['o']['t'])}</div></div>"
html_frota += '<div class="f-legenda"><div class="f-leg-titulo">🎨 Legenda das cores</div><div class="f-leg-item"><span class="f-leg-cor f-tag-ok"></span><span><b>Verde</b> — OK: sem avarias apontadas</span></div><div class="f-leg-item"><span class="f-leg-cor f-tag-aten"></span><span><b>Amarelo</b> — Atenção: item apontado no checklist</span></div><div class="f-leg-item"><span class="f-leg-cor f-tag-avaria"></span><span><b>Vermelho</b> — Avaria: equipamento bloqueado/quebrado</span></div></div></div></details>'

# --- MÓDULO COMPARATIVO ANUAL ---
d_res = max(1, (date(hoje_date.year, 12, 31) - hoje_date).days)
ca_at = forcar_par(1362558.0 + vol_hoje)
pa_at = forcar_par(1362676.0 + prod_hoje_calc)
df_pc = forcar_par(abs(pa_at - ca_at))

tv, cv = (f"+{fmt(df_pc)} t (Expedição Superando)", "#00D672") if ca_at >= pa_at else (f"+{fmt(df_pc)} t (Produção Superando)", "#FF9F1C")
mdc = forcar_par(5200.0 + (max(0.0, estoque_total - 3468.0) / d_res))
ppf = forcar_par(pa_at + (d_res * 5200.0))
pcf = forcar_par(ca_at + ((estoque_total + (d_res * 5200.0)) - 3468.0))

h_an = f'<details class="master-box" style="border-left-color:#007BFF;" open><summary><div class="header-layout"><div class="icon-box" style="background-color:rgba(0,123,255,.15); color:#007BFF;">📊</div><div class="master-metric-title">Comparativo Produção vs Expedição</div></div><div class="value-layout"><div class="master-metric-val">{fmt(ca_at)}</div><div class="master-metric-unit">t Expedidas</div></div><div class="master-metric-sub" style="color:#007BFF;">Meta Diária Necessária: {fmt(mdc)} t/dia</div></summary><div class="master-content" style="padding-top:16px;"><div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px;"><div style="background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:10px;"><div style="font-size:0.75rem; color:#007BFF; font-weight:bold;">EXPEDIÇÃO ANUAL</div><div style="font-size:1.4rem; font-weight:bold; color:#fff; margin:4px 0;">{fmt(ca_at)} <span style="font-size:0.8rem; color:#64748b; font-weight:normal;">t</span></div><div style="font-size:0.7rem; color:#64748b;">Proj. 31/12: <span style="color:#007BFF;">{fmt(pcf)} t</span></div></div><div style="background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:10px;"><div style="font-size:0.75rem; color:#00D672; font-weight:bold;">PRODUÇÃO ANUAL</div><div style="font-size:1.4rem; font-weight:bold; color:#fff; margin:4px 0;">{fmt(pa_at)} <span style="font-size:0.8rem; color:#64748b; font-weight:normal;">t</span></div><div style="font-size:0.7rem; color:#64748b;">Proj. 31/12: <span style="color:#00D672;">{fmt(ppf)} t</span></div></div></div><div style="background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:12px; font-size:0.82rem; color:#cbd5e1; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;"><span>Variação: <span style="color:{cv}; font-weight:bold;">{tv}</span></span><span>Estoque Meta: <span style="color:#38bdf8; font-weight:bold;">3.468 t</span></span></div></div></details>'


# ==============================================================================
# 🖨️ RENDERIZANDO TODOS OS BLOCOS (ROLAGEM VERTICAL)
# ==============================================================================
st.markdown(html_patio, unsafe_allow_html=True)
st.markdown(html_prod_completo, unsafe_allow_html=True)
st.markdown(html_exp_completo, unsafe_allow_html=True)
st.markdown(html_est, unsafe_allow_html=True)
st.markdown(html_frota, unsafe_allow_html=True)

# Bloco Bafômetro
c1, c2 = st.columns([3, 1], vertical_alignment="center")
with c1:
    if not st.session_state.bafometro_autenticado:
        btn_abrir_modal = st.button("🔒 Acessar Bafômetro", use_container_width=True)
    else: st.markdown("<div style='color:#00D672; font-size:0.85rem; font-weight:bold;'>🔓 Acesso ao Bafômetro Liberado</div>", unsafe_allow_html=True)
with c2:
    if st.session_state.bafometro_autenticado:
        if st.button("Bloquear", use_container_width=True): st.session_state.bafometro_autenticado = False; st.rerun()

@st.dialog("Segurança Operacional")
def modal_senha_bafometro():
    st.markdown("<p style='font-size:0.85rem; color:#94a3b8;'>Digite a senha de gestor:</p>", unsafe_allow_html=True)
    senha = st.text_input("Senha", type="password")
    cc, cf = st.columns(2)
    with cc:
        if st.button("Confirmar", use_container_width=True, type="primary"):
            if senha == SENHA_BAFOMETRO: st.session_state.bafometro_autenticado = True; st.rerun()
            else: st.error("Senha incorreta.")
    with cf:
        if st.button("Cancelar", use_container_width=True): st.rerun()

if not st.session_state.bafometro_autenticado and 'btn_abrir_modal' in locals() and btn_abrir_modal: modal_senha_bafometro()

if st.session_state.bafometro_autenticado:
    tt = len(df_bafometro) if not df_bafometro.empty else 0
    cr = next((c for c in df_bafometro.columns if any(t in str(c).upper() for t in ["RESULTADO", "STATUS", "PARECER"])), None)
    ap = int((df_bafometro[cr].astype(str).str.upper().str.contains("APROV|0.00|0,00|OK|NEGATIVO")).sum()) if not df_bafometro.empty and cr else 0
    pd_rep = max(0, tt - ap)
    cb = "#00D672" if pd_rep == 0 else "#E74C3C"

    hb = f'<details class="master-box" style="border-left-color:{cb};" open><summary><div class="header-layout"><div class="icon-box" style="background-color:rgba(0,214,114,.15); color:{cb};">🩺</div><div class="master-metric-title">Auditoria Bafômetro (H&S)</div></div><div class="value-layout"><div class="master-metric-val">{tt}</div><div class="master-metric-unit">Testes Registrados Hoje</div></div><div class="master-metric-sub" style="color:{cb};">Aprovados: {ap} | Pendentes / Reprovados: {pd_rep}</div></summary><div class="master-content" style="padding-top:16px;">'

    if not df_bafometro.empty:
        cpe = list(df_bafometro.columns[:5])
        hb += f"<div style='overflow-x:auto;'><table style='width:100%; border-collapse:collapse; font-size:0.75rem; text-align:left; color:#ffffff;'><thead><tr style='border-bottom:1px solid #1c2b42; color:#94a3b8;'>{''.join(f'<th style=\"padding:6px;\">{str(c).upper()}</th>' for c in cpe)}</tr></thead><tbody>"
        for _, rb in df_bafometro.head(15).iterrows():
            hb += "<tr style='border-bottom:1px dashed #1c2b42;'>"
            for c in cpe:
                vc = str(rb.get(c, ""))
                vcu = vc.upper()
                cc = "#00D672" if any(x in vcu for x in ["APROV","OK","0,00","0.00"]) else ("#E74C3C" if any(x in vcu for x in ["REPROV","POSITIV","RECUS"]) else ("#FF9F1C" if any(x in vcu for x in ["PEND","AGUARD"]) else "#ffffff"))
                hb += f"<td style='padding:6px; color:{cc};'>{vc}</td>"
            hb += "</tr>"
        hb += "</tbody></table></div>"
    else: hb += "<div style='color:gray; text-align:center;'>Nenhum registro encontrado.</div>"
    hb += "</div></details>"
    st.markdown(hb.replace('\n', ''), unsafe_allow_html=True)

st.markdown(h_an, unsafe_allow_html=True)
st.markdown("<br><center><span style='color:#64748b; font-size:0.75rem; letter-spacing:0.5px;'>A.L.O.V.E - Mobile / Developed by Crist Ciriaco</span></center>", unsafe_allow_html=True)

# ==============================================================================
# 🧭 NAVEGAÇÃO INFERIOR ESTRITA (FIXA VIA CSS PURO)
# ==============================================================================
st.markdown("""
<div class="bottom-nav">
    <a href="#sec-inicio" target="_self"><span>🏠</span>Início</a>
    <a href="#sec-patio" target="_self"><span>🚛</span>Pátio</a>
    <a href="#sec-prod" target="_self"><span>🏭</span>Produção</a>
    <a href="#sec-exp" target="_self"><span>🚚</span>Exped</a>
    <a href="#sec-estoque" target="_self"><span>📦</span>Estoque</a>
    <a href="#sec-frota" target="_self"><span>🚜</span>Frota</a>
</div>
""", unsafe_allow_html=True)
