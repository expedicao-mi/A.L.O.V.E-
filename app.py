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

st_autorefresh(interval=60000, limit=None, key="refresh_mobile")

if "bafometro_autenticado" not in st.session_state:
    st.session_state.bafometro_autenticado = False

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
        /* 🚀 1. TRAVA O FUNDO E GARANTE SCROLL NATIVO LISO NO IPHONE */
        html, body, [data-testid="stAppViewContainer"], .stApp {
            background: radial-gradient(ellipse at top, #0c1a33 0%, #070d18 55%, #050911 100%) !important;
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

        /* 🚀 3. ESCONDE CABEÇALHO, RODAPÉ E BOTÕES DO STREAMLIT */
        #MainMenu, footer, header,
        [data-testid="stHeader"],
        [data-testid="stFooter"],
        [data-testid="manage-app-button"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        .stStatusWidget,
        .stAppDeployButton,
        div[class^="viewerBadge"],
        div[class*="_profileContainer"],
        div[class*="_container_"],
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

        /* COLUNA CENTRAL ESTILO APP */
        .block-container {
            padding-top: 0rem !important; 
            padding-bottom: 6rem !important;
            padding-left: 0.8rem !important; 
            padding-right: 0.8rem !important;
            max-width: 560px !important; 
            margin: 0 auto !important;
        }

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
    identificando a linha do cabeçalho e extraindo o carimbo da Linha 1.
    """
    try:
        if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
            dados_secret = dict(st.secrets["gcp_service_account"])
            cliente = gspread.service_account_from_dict(dados_secret)
        elif os.path.exists("credentials.json"):
            cliente = gspread.service_account(filename="credentials.json")
        else:
            return pd.DataFrame(), None

        planilha = cliente.open_by_key(SHEET_ID)
        aba = planilha.worksheet(worksheet_name)
        linhas = aba.get_all_values()

        if not linhas:
            return pd.DataFrame(), None

        # 1. Resgata carimbo de atualização se estiver na Linha 1
        carimbo_att = None
        if len(linhas) > 0 and len(linhas[0]) >= 2:
            if "ATUALIZADO" in str(linhas[0][0]).upper():
                carimbo_att = str(linhas[0][1]).strip()

        # 2. Localiza a linha do cabeçalho que contém a coluna_chave
        header_idx = -1
        for i, row in enumerate(linhas[:10]):
            row_vals = [str(x).strip().upper() for x in row]
            if coluna_chave.upper() in row_vals:
                header_idx = i
                break

        if header_idx != -1:
            cabecalho = [str(c).strip().upper() for c in linhas[header_idx]]
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
            return df, carimbo_att

    except Exception as e:
        st.warning(f"⚠️ Erro ao ler aba {worksheet_name}: {e}")

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
    if d_baf.empty: d_baf = carregar_dados_nuvem("Auditoria_Bafometro", cabecalho=0)
    d_frot = carregar_dados_nuvem("Historico_DKRO", cabecalho=0)
    
    d_bal, _ = carregar_tabela_cega("Balanco_Expedicao_Destino", "DESTINO")
    d_pat, h_pat = carregar_tabela_cega("Patio_Destino_Status", "DESTINO")
    d_tr, _ = carregar_tabela_cega("Status_TR", "PLACA")
    d_pran = carregar_prancheta_direto()
    
    return d_dash, d_qual, d_alert, d_cache, d_virada, d_bal, d_baf, d_frot, d_pran, d_pat, h_pat, d_tr

df_dash, df_qual, df_alertas, df_cache, df_status_virada, df_balanco_dest, df_bafometro, df_frota, df_prancheta, df_patio_dest, hora_att_patio, df_status_tr = carregar_dados_mobile_otimizados()

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

# ==============================================================================
# 🖨️ RECARGA NATIVA & SPLASH SCREEN (A.L.O.V.E TYPING EFFECT)
# ==============================================================================
if st.query_params.get("refresh") == "1":
    st.cache_data.clear()
    st.query_params.clear()
    st.session_state.pop("splash_exibida", None) # Força a animação a rodar ao atualizar
    st.rerun()

# A animação só é desenhada na tela se for o primeiro carregamento
if "splash_exibida" not in st.session_state:
    st.session_state.splash_exibida = True
    st.markdown("""
        <style>
            [data-testid="stStatusWidget"] { display: none !important; visibility: hidden !important; }
            .alove-loader-bg {
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background: #050911; z-index: 99999999;
                display: flex; justify-content: center; align-items: center;
                animation: loaderFadeOut 0.4s 1.2s forwards; pointer-events: none;
            }
            .alove-loader-text {
                font-size: 2.8rem; font-weight: 900; color: #00D672;
                letter-spacing: 6px; text-shadow: 0 0 20px rgba(0,214,114,0.6);
                overflow: hidden; white-space: nowrap; border-right: 4px solid #00D672;
                width: 0;
                animation: loaderTyping 1s steps(7, end) forwards, loaderBlink 0.5s step-end infinite alternate;
            }
            @keyframes loaderTyping { from { width: 0 } to { width: 5.5em } }
            @keyframes loaderBlink { 50% { border-color: transparent } }
            @keyframes loaderFadeOut { to { opacity: 0; visibility: hidden; display: none; } }
        </style>
        <div class="alove-loader-bg"><div class="alove-loader-text">A.L.O.V.E</div></div>
    """, unsafe_allow_html=True)

st.markdown(f'<div id="sec-topo"></div><div class="topo-banner"><img src="{BANNER_TOPO_URL}"></div>', unsafe_allow_html=True)

# ==============================================================================
# 🖨️ RENDERIZAÇÃO 1: STATUS DO SISTEMA + SEMÁFORO (CONFORME IMAGEM 3)
# ==============================================================================
led_core = "#00D672"
borda_core = "#00D672"
led_off = "#E74C3C"
borda_off = "#142842"

html_status_sistema = f"""
<div class="card-main" style="margin-bottom: 14px; padding: 14px 16px; border: 1.5px solid #142842; border-radius: 14px; background: #070d18;">
    <details open style="border: none; background: transparent;">
        <summary style="list-style: none; cursor: pointer; outline: none;">
            <!-- LINHA 1: TÍTULO COM BARRA VERDE -->
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <div style="width: 4px; height: 18px; background: #00D672; border-radius: 2px;"></div>
                <div style="color: #ffffff; font-size: 1.05rem; font-weight: 800; letter-spacing: 0.5px;">STATUS DO SISTEMA</div>
            </div>

            <!-- LINHA 2: STATUS, HORA E BOTÃO ATUALIZAR QUADRADO À DIREITA -->
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                    <div style="color: #00D672; font-weight: 800; font-size: 0.95rem; display: flex; align-items: center; gap: 6px;">
                        <span style="width: 10px; height: 10px; border-radius: 50%; background: #00D672; display: inline-block; box-shadow: 0 0 6px #00D672;"></span>
                        ATUALIZADO
                    </div>
                    <div style="color: #94a3b8; font-size: 0.78rem; font-weight: 500;">
                        🕒 Última atualização: <span style="color: #cbd5e1;">{conn_hora}</span>
                    </div>
                </div>
                <!-- BOTÃO COMPACTO QUADRADO COM BORDA CIANO -->
                <a href="?refresh=1" target="_self" onclick="event.stopPropagation();" 
                   style="width: 38px; height: 38px; border: 1.5px solid #00b4ff; border-radius: 8px; background: #070d18; display: flex; align-items: center; justify-content: center; font-size: 1.15rem; color: #ffffff; text-decoration: none; box-shadow: 0 0 10px rgba(0, 180, 255, 0.25); flex-shrink: 0; margin-left: 8px;">
                   🔄
                </a>
            </div>
        </summary>

        <!-- LINHA 3: OS 4 CARDS DO SEMÁFORO (CORE, TORRE, TOTEM, TV) -->
        <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-top: 14px; padding-top: 12px; border-top: 1px solid #14243b;">
            <!-- CORE (ONLINE 🟢) -->
            <div style="flex: 1; background: #070d18; border: 1.5px solid {borda_core}; border-radius: 12px; padding: 12px 2px; text-align: center; position: relative; box-shadow: 0 0 12px rgba(0, 214, 114, 0.2);">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: {led_core}; box-shadow: 0 0 8px {led_core}; position: absolute; top: 8px; right: 8px;"></span>
                <div style="font-size: 1.45rem; margin-top: 4px; margin-bottom: 4px;">🤖</div>
                <div style="color: #ffffff; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.5px;">CORE</div>
            </div>

            <!-- TORRE (OFFLINE 🔴) -->
            <div style="flex: 1; background: #070d18; border: 1.5px solid {borda_off}; border-radius: 12px; padding: 12px 2px; text-align: center; position: relative;">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: {led_off}; box-shadow: 0 0 8px {led_off}; position: absolute; top: 8px; right: 8px;"></span>
                <div style="font-size: 1.45rem; margin-top: 4px; margin-bottom: 4px;">📡</div>
                <div style="color: #64748b; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.5px;">TORRE</div>
            </div>

            <!-- TOTEM (OFFLINE 🔴) -->
            <div style="flex: 1; background: #070d18; border: 1.5px solid {borda_off}; border-radius: 12px; padding: 12px 2px; text-align: center; position: relative;">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: {led_off}; box-shadow: 0 0 8px {led_off}; position: absolute; top: 8px; right: 8px;"></span>
                <div style="font-size: 1.45rem; margin-top: 4px; margin-bottom: 4px;">📱</div>
                <div style="color: #64748b; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.5px;">TOTEM</div>
            </div>

            <!-- TV (OFFLINE 🔴) -->
            <div style="flex: 1; background: #070d18; border: 1.5px solid {borda_off}; border-radius: 12px; padding: 12px 2px; text-align: center; position: relative;">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: {led_off}; box-shadow: 0 0 8px {led_off}; position: absolute; top: 8px; right: 8px;"></span>
                <div style="font-size: 1.45rem; margin-top: 4px; margin-bottom: 4px;">📺</div>
                <div style="color: #64748b; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.5px;">TV</div>
            </div>
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
# 🖨️ RENDERIZAÇÃO 4: PÁTIO DA FÁBRICA (COM DESTINOS DETALHADOS FUNCIONANDO)
# ==============================================================================
txt_att_patio = f" | 🕒 Base: {hora_att_patio.split(' ')[1][:5]}" if hora_att_patio and " " in hora_att_patio else ""

html_patio = f"""
<div id="sec-patio"></div>
<details class="master-box" style="border-left-color: #38a9ff;" open>
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
            <div class="st-ico">{ico}</div>
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
# 🖨️ RENDERIZAÇÃO 5: PRODUÇÃO DE CELULOSE (LAYOUT MODERNO COM LEDS E BARRAS)
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

        # Cor de destaque e LED da máquina (Verde se OK / Vermelho se Desclassificando)
        cor_status_maq = "#E74C3C" if desclass else "#00D672"
        led_status = "🔴" if desclass else "🟢"

        lbl_l1 = "Linha A" if maq == "MS1" else "Linha C"
        lbl_l2 = "Linha B" if maq == "MS1" else "Linha D"

        info_v = viradas_info.get(maq, {})
        p_mat = info_v.get("prox_mat", "--") if info_v else "--"
        p_prev = info_v.get("prev_virada", "--") if info_v else "--"

        html_prod_content += f"""
        <div style="background-color: #0c1524; border: 1.5px solid #1c2b42; border-left: 5px solid {cor_status_maq}; border-radius: 14px; padding: 14px 16px; margin-bottom: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.25);">
            <!-- TOPO: IDENTIFICAÇÃO E LINHAS -->
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <!-- LADO ESQUERDO: MÁQUINA + MAT -->
                <div style="display:flex; flex-direction:column; gap:4px;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="color:#ffffff; font-weight:800; font-size:1.15rem; letter-spacing:0.3px;">⚙️ {maq}</span>
                        <span style="font-size:0.95rem;">{led_status}</span>
                    </div>
                    <div style="color:#FF9F1C; font-weight:800; font-size:1.02rem;">
                        📦 MAT: {mat_maq}
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
render_html(html_prod_completo)


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
        <div style="font-size:1.25rem; color:#38bdf8; font-weight:bold; margin-top:2px;">{fmt(total_expedicao_real)} <span style="font-size:0.75rem; font-weight:normal;">t</span></div>
    </div>

    <!-- CARD 3: TOTAL PENDENTE (LARANJA) -->
    <div style="flex: 1;">
        <div style="font-size:0.68rem; color:#FF9F1C; font-weight:bold; text-transform:uppercase;">Pendente</div>
        <div style="font-size:1.25rem; color:#FF9F1C; font-weight:bold; margin-top:2px;">{fmt(total_expedicao_falta)} <span style="font-size:0.75rem; font-weight:normal;">t</span></div>
    </div>
</div>
"""

# ⚠️ AQUI ESTAVA O BUG: Essa linha tinha sido apagada!
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

        /* 🍏 SWITCH DESLIZANTE IOS NATIVO */
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
        padding: 2px !important;
        margin-right: 22px !important;
        width: 154px !important;
        height: 28px !important;
        box-sizing: border-box !important;
        flex-shrink: 0 !important;
        user-select: none !important;
        -webkit-user-select: none !important;
        transition: all 0.3s ease;
    }}

    .ios-slider-thumb {{
        position: absolute;
        top: 2px;
        left: 2px;
        width: 73px;
        height: 20px;
        background: #00D672;
        border-radius: 999px;
        box-shadow: 0 0 10px rgba(0, 214, 114, 0.45);
        transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
        z-index: 1;
        pointer-events: none;
    }}

    #day_ontem:checked ~ details .ios-slider-thumb {{
        transform: translateX(75px);
    }}

    /* Textos dos botões sobrepostos */
    .ios-slider-btn {{
        position: relative;
        flex: 1;
        text-align: center;
        font-size: 0.68rem;
        font-weight: 800;
        line-height: 20px;
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

    <details class="master-box" style="border-left-color: #00D672;" open>
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
# 🖨️ RENDERIZAÇÃO 6.5: ANÁLISE DE PEDIDOS (ZLE087 - CORRIGIDO E BLINDADO)
# ==============================================================================
@st.cache_data(ttl=30)
def carregar_pedidos_zle087():
    try:
        # Tenta carregar via gspread primeiro (blindado)
        df, carimbo = carregar_tabela_cega("Status_Pedidos_ZLE087", coluna_chave="FLUXO")
        
        if df.empty:
            # Fallback via URL CSV direta
            url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Status_Pedidos_ZLE087"
            df_raw = pd.read_csv(url, header=None, dtype=str)
            if df_raw.empty:
                return pd.DataFrame(), "--:--"
            
            # Localiza a linha do cabeçalho
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
    except Exception as e:
        return pd.DataFrame(), "--:--"

df_pedidos, hora_att_ped = carregar_pedidos_zle087()

pedidos_transf = []
pedidos_mi = []
tot_saldo_transf = 0.0
tot_saldo_mi = 0.0

if not df_pedidos.empty:
    # Função flexível para encontrar colunas mesmo com cortes ou variações de nomes
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
        # Busca qualquer coluna com "SALDO" que NÃO tenha "PROX" (pega SALDO_RESTA, SALDO_RESTANTE, etc.)
        saldo = safe_to_numeric(obter_val(r, ["SALDO"], ["PROX"]) or 0)
        
        prox_ped = str(obter_val(r, ["PROX", "PED"]) or "--").strip()
        prox_mat = str(obter_val(r, ["PROX", "MAT"]) or "--").strip()
        # Busca a coluna com "SALDO" e "PROX" (pega SALDO_PROXII, SALDO_PROXIMO, etc.)
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

tot_saldo_geral = tot_saldo_transf + tot_saldo_mi

def gerar_cards_pedidos(lista_itens, cor_primaria):
    if not lista_itens:
        return '<div style="color:#64748b; font-size:0.82rem; text-align:center; padding:16px;">Nenhum pedido ativo encontrado.</div>'
    
    html = ""
    for item in lista_itens:
        # Tag de alerta se estiver em fim de pedido (< 100t)
        if item["is_fim"]:
            tag_status = f'<span style="background:rgba(231,76,60,0.18); border:1px solid #e74c3c; color:#ff7675; font-size:0.68rem; font-weight:800; padding:2px 8px; border-radius:6px; white-space:nowrap;">⚠️ FIM: {fmt(item["saldo"])} t</span>'
        else:
            tag_status = f'<span style="background:rgba(56,189,248,0.15); border:1px solid #38bdf8; color:#38bdf8; font-size:0.68rem; font-weight:800; padding:2px 8px; border-radius:6px; white-space:nowrap;">SALDO: {fmt(item["saldo"])} t</span>'

        # Barra de atendimento do pedido atual
        pct_atend = 0.0
        if item["qtd_ini"] > 0:
            carr = max(0.0, item["qtd_ini"] - item["saldo"])
            pct_atend = min(100.0, max(0.0, (carr / item["qtd_ini"]) * 100.0))

        # Informação do próximo pedido
        info_prox = ""
        if item["prox_ped"] not in ("--", "", "nan") and not "SEM PR" in item["prox_mat"].upper():
            info_prox = f"""
            <div style="background:#050911; border:1px dashed #1c2b42; border-radius:8px; padding:6px 10px; margin-top:8px; font-size:0.72rem; color:#94a3b8;">
                🔜 <b>Próximo:</b> <span style="color:#ffffff; font-weight:bold;">{item['prox_ped']}</span> ({item['prox_mat']}) &bull; Saldo: <span style="color:#38bdf8; font-weight:bold;">{item['saldo_prox']}</span>
            </div>
            """

        cor_mat = "#00D672" if "EQ" in item["material"].upper() else ("#00D6FF" if "SQ" in item["material"].upper() else "#FF9F1C")

        html += f"""
        <div style="background:#070d18; border:1.5px solid #142842; border-left:4px solid {cor_primaria}; border-radius:12px; padding:12px 14px; margin-bottom:10px; box-shadow:0 3px 10px rgba(0,0,0,0.25);">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
                <div style="color:#ffffff; font-weight:800; font-size:0.88rem; line-height:1.2;">{item['destino']}</div>
                {tag_status}
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem; color:#94a3b8; margin-top:6px;">
                <div>📦 Pedido: <b style="color:#ffffff;">{item['pedido']}</b></div>
                <div>Mat: <b style="color:{cor_mat};">{item['material']}</b></div>
            </div>

            <!-- Progresso do pedido atual -->
            <div style="margin-top:8px;">
                <div style="display:flex; justify-content:space-between; font-size:0.68rem; color:#64748b; margin-bottom:3px;">
                    <span>Atendido: {pct_atend:.0f}%</span>
                    <span>Meta: {fmt(item['qtd_ini'])} t</span>
                </div>
                <div style="width:100%; height:5px; background:#14243b; border-radius:999px; overflow:hidden;">
                    <div style="width:{pct_atend:.1f}%; height:100%; background:linear-gradient(90deg, #38bdf8, {cor_primaria}); border-radius:999px;"></div>
                </div>
            </div>

            {info_prox}
        </div>
        """
    return html

html_cards_transf = gerar_cards_pedidos(pedidos_transf, "#0084FF")
html_cards_mi = gerar_cards_pedidos(pedidos_mi, "#00D672")

html_bloco_pedidos = f"""
<style>
    .ped-wrapper input[type="radio"] {{ display: none !important; }}

    .ped-tab-bar {{
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 14px;
        padding: 0 4px;
    }}
    .ped-tab-bar label {{
        flex: 1;
        max-width: 190px;
        text-align: center;
        padding: 9px 8px;
        font-size: 0.80rem;
        font-weight: 800;
        color: #94a3b8;
        background: #070d18;
        border: 1.5px solid #1c2b42;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
        white-space: nowrap;
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

<div class="ped-wrapper">
    <input type="radio" name="ped_view" id="tab_transf" checked>
    <input type="radio" name="ped_view" id="tab_mi">

    <details class="master-box" style="border-left-color: #0084FF; margin-bottom: 14px;" open>
       <summary>
            <!-- CABEÇALHO COM TÍTULO E ÍCONE -->
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                <div class="header-layout" style="margin-bottom:0;">
                    <div class="icon-box" style="background-color: rgba(0, 132, 255, 0.15); color: #0084FF;">📑</div>
                    <div class="master-metric-title">Análise de Pedidos (ZLE087)</div>
                </div>
                <div style="font-size:0.75rem; color:#64748b; font-weight:700;">
                    Total: <b style="color:#ffffff;">{len(pedidos_transf) + len(pedidos_mi)} ordens ativas</b>
                </div>
            </div>

            <!-- VALOR PRINCIPAL: SALDO TOTAL PENDENTE -->
            <div class="value-layout" style="margin-bottom:6px;">
                <div class="master-metric-val">{fmt(tot_saldo_geral)}</div>
                <div class="master-metric-unit">TON PENDENTES</div>
            </div>

            <!-- SUB-RESUMO: QUANTIDADE DE PEDIDOS EM ABERTO POR DESTINO/FLUXO -->
            <div style="display: flex; gap: 8px; margin-top: 6px;">
                <!-- Pílula Transferência -->
                <div style="flex: 1; background: #070d18; border: 1.5px solid #142842; border-left: 3px solid #0084FF; border-radius: 10px; padding: 8px 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.72rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">🚛 Transferência</span>
                        <span style="background: rgba(0, 132, 255, 0.15); color: #38bdf8; font-size: 0.68rem; font-weight: 800; padding: 2px 6px; border-radius: 4px;">{len(pedidos_transf)} pedidos</span>
                    </div>
                    <div style="font-size: 0.95rem; font-weight: 800; color: #ffffff; margin-top: 4px;">
                        {fmt(tot_saldo_transf)} <span style="font-size: 0.72rem; color: #64748b; font-weight: normal;">t pendentes</span>
                    </div>
                </div>

                <!-- Pílula Mercado Interno -->
                <div style="flex: 1; background: #070d18; border: 1.5px solid #142842; border-left: 3px solid #00D672; border-radius: 10px; padding: 8px 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.72rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">🏢 MI / LATAM</span>
                        <span style="background: rgba(0, 214, 114, 0.15); color: #00D672; font-size: 0.68rem; font-weight: 800; padding: 2px 6px; border-radius: 4px;">{len(pedidos_mi)} pedidos</span>
                    </div>
                    <div style="font-size: 0.95rem; font-weight: 800; color: #ffffff; margin-top: 4px;">
                        {fmt(tot_saldo_mi)} <span style="font-size: 0.72rem; color: #64748b; font-weight: normal;">t pendentes</span>
                    </div>
                </div>
            </div>
        </summary>

        <div class="master-content" style="padding-top: 14px;">
            <!-- SELETORES EM ABAS LADO A LADO -->
            <div class="ped-tab-bar">
                <label for="tab_transf" class="lbl-transf">🚛 Transferência ({len(pedidos_transf)})</label>
                <label for="tab_mi" class="lbl-mi">🏢 MI / LATAM ({len(pedidos_mi)})</label>
            </div>

            <!-- PAINEL 1: TRANSFERÊNCIA -->
            <div class="ped-view-transf">
                {html_cards_transf}
            </div>

            <!-- PAINEL 2: MERCADO INTERNO / LATAM -->
            <div class="ped-view-mi">
                {html_cards_mi}
            </div>
        </div>
    </details>
</div>
"""
render_html(html_bloco_pedidos)


# ==============================================================================
# 🖨️ RENDERIZAÇÃO 7: ESTOQUE FÍSICO (COM BARRA DE OCUPAÇÃO 25K + BARRAS + ROSCA)
# ==============================================================================
CAPACIDADE_MAX_ARMAZEM = 25000.0
pct_ocupacao_est = min(100.0, max(0.0, (estoque_total / CAPACIDADE_MAX_ARMAZEM * 100.0)))
espaco_livre_est = max(0.0, CAPACIDADE_MAX_ARMAZEM - estoque_total)

# 1. Processamento e segregação dos materiais
itens_barras = []
tot_eq = 0.0
tot_sq = 0.0

if dados_segregados:
    for m_raw, v_raw in dados_segregados.items():
        t_val = forcar_par(safe_to_numeric(v_raw))
        if t_val <= 0:
            continue
        m_str = str(m_raw).strip().upper()
        is_sq = "SQ" in m_str
        
        # Separa o código do material e o tipo (EQ ou SQ)
        cod_mat = re.sub(r'[^0-9]', '', m_str) or m_str.split()[0]
        tipo_mat = "SQ" if is_sq else "EQ"
        
        if is_sq:
            tot_sq += t_val
        else:
            tot_eq += t_val
            
        itens_barras.append({
            "cod": cod_mat,
            "tipo": tipo_mat,
            "ton": t_val,
            "is_sq": is_sq
        })

itens_barras.sort(key=lambda x: x["ton"], reverse=True)
max_ton_est = max([x["ton"] for x in itens_barras], default=1.0)
tot_geral_calc = (tot_eq + tot_sq) if (tot_eq + tot_sq) > 0 else (estoque_total if estoque_total > 0 else 1.0)
pct_sq = min(100.0, max(0.0, (tot_sq / tot_geral_calc) * 100.0))
pct_eq = 100.0 - pct_sq

# 2. Montagem das Barras Verticais com escala rebaixada (folga no teto)
barras_html = ""
for item in itens_barras[:8]:
    cor_b = "#FFD600" if item["is_sq"] else "#00E676"
    h_px = max(6, int((item["ton"] / max_ton_est) * 68))
    
    barras_html += f"""
    <div style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; min-width: 38px;">
        <div style="color: {cor_b}; font-size: 0.68rem; font-weight: 800; margin-bottom: 6px; white-space: nowrap;">
            {fmt(item['ton'])} t
        </div>
        <div style="width: 24px; height: {h_px}px; background: {cor_b}; border-radius: 4px 4px 0 0; box-shadow: 0 0 10px {cor_b}44;"></div>
        <div style="width: 100%; border-top: 1.5px solid #1c2b42; padding-top: 5px; text-align: center;">
            <div style="color: #cbd5e1; font-size: 0.75rem; font-weight: 800;">{item['cod']}</div>
            <div style="color: #64748b; font-size: 0.65rem; font-weight: 700;">({item['tipo']})</div>
        </div>
    </div>
    """

# 3. Montagem do Gráfico Donut (SVG Vetorial)
svg_donut = f"""
<svg width="115" height="115" viewBox="0 0 42 42" style="transform: rotate(-90deg); display: block;">
    <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#00E676" stroke-width="5.5"></circle>
    <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#FFD600" stroke-width="5.6"
            stroke-dasharray="{pct_sq:.1f} {100.0 - pct_sq:.1f}" stroke-dashoffset="0"
            stroke-linecap="round"></circle>
</svg>
"""

html_est = f"""
<div id="sec-est"></div>
<details class="master-box" style="border-left-color: #00E676;" open>
    <summary>
        <!-- TOPO DO CARD -->
        <div class="header-layout">
            <div class="icon-box" style="background-color: rgba(0, 230, 118, 0.15); color: #00E676;">📦</div>
            <div class="master-metric-title">Estoque Físico no Armazém</div>
        </div>

        <!-- VALOR PRINCIPAL -->
        <div class="value-layout" style="margin-bottom: 2px;">
            <div class="master-metric-val">{fmt(estoque_total)}</div>
            <div class="master-metric-unit">TON</div>
        </div>

        <!-- BARRA DE OCUPAÇÃO (MÉTRICA 25.000 t) -->
        <div style="margin-top: 6px; margin-bottom: 2px;">
            <div style="font-size: 0.75rem; color: #cbd5e1; margin-bottom: 5px;">
                Ocupação: <b style="color: #ffffff;">{fmt(estoque_total)} t</b> de <b style="color: #ffffff;">{fmt(CAPACIDADE_MAX_ARMAZEM)} t</b> ({pct_ocupacao_est:.0f}%) 📦
            </div>
            <div style="width: 100%; height: 7px; background: #14243b; border-radius: 999px; overflow: hidden;">
                <div style="width: {pct_ocupacao_est:.1f}%; height: 100%; background: linear-gradient(90deg, #38bdf8 0%, #00E676 100%); border-radius: 999px; box-shadow: 0 0 10px rgba(0,230,118,0.45);"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #64748b; margin-top: 4px;">
                <span>Espaço Livre: <b style="color: #38bdf8;">{fmt(espaco_livre_est)} t</b></span>
                <span>Capacidade: 25.000 t</span>
            </div>
        </div>
    </summary>

    <div class="master-content" style="padding-top: 14px;">
        <!-- 1. CARD SUPERIOR: BARRAS POR MATERIAL COM BORDA DISCRETA -->
        <div style="background: #070d18; border: 1.5px solid #142842; border-radius: 14px; padding: 18px 8px 10px 8px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.25);">
            <div style="display: flex; justify-content: space-around; align-items: flex-end; height: 135px; gap: 4px; padding: 0 4px;">
                {barras_html if itens_barras else '<div style="color:#64748b; font-size:0.8rem; margin:auto;">Aguardando dados segregados...</div>'}
            </div>
        </div>

        <!-- 2. CARD INFERIOR: DONUT ROSCA (MATERIAL EQ vs SQ) -->
        <div style="background: #070d18; border: 1.5px solid #142842; border-radius: 14px; padding: 14px 18px; display: flex; align-items: center; justify-content: space-around; gap: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.25);">
            <div style="position: relative; width: 115px; height: 115px; flex-shrink: 0;">
                {svg_donut}
            </div>

            <div style="display: flex; flex-direction: column; gap: 12px; min-width: 130px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px; font-size: 0.82rem; color: #cbd5e1; font-weight: 700;">
                        <span style="width: 10px; height: 10px; border-radius: 50%; background: #00E676; display: inline-block;"></span>
                        Material EQ
                    </div>
                    <div style="color: #ffffff; font-size: 1.25rem; font-weight: 800; margin-left: 18px; line-height: 1.15;">
                        {fmt(tot_eq)} <span style="font-size: 0.8rem; font-weight: normal; color: #94a3b8;">t</span>
                    </div>
                </div>

                <div>
                    <div style="display: flex; align-items: center; gap: 8px; font-size: 0.82rem; color: #cbd5e1; font-weight: 700;">
                        <span style="width: 10px; height: 10px; border-radius: 50%; background: #FFD600; display: inline-block;"></span>
                        Material SQ
                    </div>
                    <div style="color: #ffffff; font-size: 1.25rem; font-weight: 800; margin-left: 18px; line-height: 1.15;">
                        {fmt(tot_sq)} <span style="font-size: 0.8rem; font-weight: normal; color: #94a3b8;">t</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</details>
"""
render_html(html_est)




# ==============================================================================
# 🖨️ RENDERIZAÇÃO 8: FROTA E EQUIPAMENTOS (DKRO)
# ==============================================================================
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

html_frota = f"""
<details class="master-box" style="border-left-color:#E67E22;">
    <summary>
        <div class="header-layout"><div class="icon-box" style="background-color:rgba(230,126,34,.15); color:#E67E22;">🚜</div><div class="master-metric-title">Frota e Equipamentos</div></div>
        <div class="value-layout"><div class="master-metric-val">{v_hoje}</div><div class="master-metric-unit">Veículos Logados Hoje</div></div>
        <div class="master-metric-sub" style="color:#E67E22;">Empilhadeiras e Talhas Elétricas</div>
    </summary>
    <div class="master-content" style="padding-top:16px;">
        <div style="font-size:0.75rem; font-weight:bold; color:#00D672; text-transform:uppercase; margin-bottom:8px;">📅 LOGADOS HOJE ({hoje_date.strftime('%d/%m')})</div>
        <div style="background-color:#05080f; padding:12px; border-radius:8px; border:1px solid #1c2b42; margin-bottom:16px;">
            <div class="f-tag-title">🟢 Empilhadeiras ({len(frota_agr['h']['e'])})</div>
            <div style="margin-bottom:12px;">{rnd_tg(frota_agr['h']['e'])}</div>
            <div class="f-tag-title">🏗️ Talhas / Pontes ({len(frota_agr['h']['t'])})</div>
            <div>{rnd_tg(frota_agr['h']['t'])}</div>
        </div>
        <div style="font-size:0.75rem; font-weight:bold; color:#38bdf8; text-transform:uppercase; margin-bottom:8px;">⏮️ LOGADOS ONTEM ({ontem_date.strftime('%d/%m')})</div>
        <div style="background-color:#05080f; padding:12px; border-radius:8px; border:1px solid #1c2b42; margin-bottom:16px;">
            <div class="f-tag-title">🟢 Empilhadeiras ({len(frota_agr['o']['e'])})</div>
            <div style="margin-bottom:12px;">{rnd_tg(frota_agr['o']['e'])}</div>
            <div class="f-tag-title">🏗️ Talhas / Pontes ({len(frota_agr['o']['t'])})</div>
            <div>{rnd_tg(frota_agr['o']['t'])}</div>
        </div>
        <div class="f-legenda">
            <div class="f-leg-titulo">🎨 Legenda das cores</div>
            <div class="f-leg-item"><span class="f-leg-cor f-tag-ok"></span><span><b>Verde</b> — OK: sem avarias apontadas</span></div>
            <div class="f-leg-item"><span class="f-leg-cor f-tag-aten"></span><span><b>Amarelo</b> — Atenção: item apontado no checklist</span></div>
            <div class="f-leg-item"><span class="f-leg-cor f-tag-avaria"></span><span><b>Vermelho</b> — Avaria: equipamento bloqueado/quebrado</span></div>
        </div>
    </div>
</details>
"""
render_html(html_frota)



# ==============================================================================
# 🖨️ RENDERIZAÇÃO 9: AUDITORIA BAFÔMETRO (H&S - SIMPLES E SEM SENHA)
# ==============================================================================

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

# 2. Separação dos Colaboradores
lista_aprovados = []
lista_trocas = []
lista_pendentes = []

if not df_bafometro.empty:
    df_bafometro.columns = [str(c).strip().upper() for c in df_bafometro.columns]
    
    c_turno = next((c for c in df_bafometro.columns if "TURNO" in c), None)
    if c_turno:
        v_turnos = [str(x).strip() for x in df_bafometro[c_turno].dropna().tolist() if str(x).strip() not in ["", "nan", "None"]]
        if v_turnos:
            periodo_rotulo = v_turnos[0].capitalize()

    for _, r_baf in df_bafometro.iterrows():
        colab = str(r_baf.get("COLABORADOR", "")).strip()
        if not colab or colab.upper() in ["NAN", "NONE", ""]: continue
        
        funcao = str(r_baf.get("FUNCAO", r_baf.get("FUNÇÃO", "--"))).strip()
        status = str(r_baf.get("STATUS", "")).strip().upper()
        resultado = str(r_baf.get("RESULTADO", "")).strip().upper()
        
        dado_colab = {"nome": colab, "funcao": funcao, "status": status, "res": resultado}
        
        if "TROCA" in status or "TROCA" in resultado or "NÃO CADAST" in status or "NAO CADAST" in status:
            lista_trocas.append(dado_colab)
        elif any(x in resultado for x in ["APROV", "OK", "0.00", "0,00", "NEGATIVO"]):
            lista_aprovados.append(dado_colab)
        else:
            lista_pendentes.append(dado_colab)

total_registrados_baf = len(lista_aprovados) + len(lista_trocas) + len(lista_pendentes)
nome_turno_completo = f"Turno {letra_vigente} ({periodo_rotulo})"

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
    if not colaboradores: return "<div style='color:#64748b; font-size:0.75rem; padding:6px 8px;'>Nenhum colaborador nesta seção.</div>"
    colaboradores_ordenados = sorted(colaboradores, key=lambda x: (obter_ordem_funcao(x["funcao"]), x["nome"]))
    grupos = {1: ("LÍDER", []), 2: ("ASSISTENTE", []), 3: ("OPERADOR DE EMPILHADEIRA", []), 4: ("AUXILIAR DE EXPEDIÇÃO", []), 5: ("MECÂNICO", []), 6: ("OUTRAS FUNÇÕES", [])}
    for c in colaboradores_ordenados: grupos[obter_ordem_funcao(c["funcao"])][1].append(c)
    html_out = ""
    for _, (rotulo, membros) in grupos.items():
        if not membros: continue
        html_out += f'<div style="font-size:0.70rem; font-weight:800; color:#94a3b8; letter-spacing:0.4px; margin-top:8px; margin-bottom:4px; padding-left:4px; border-left:2px solid #00D672;">{rotulo} ({len(membros)})</div>'
        for item in membros:
            html_out += f'<div style="display:flex; justify-content:space-between; align-items:center; padding:5px 8px; border-bottom:1px dashed #1c2b42; font-size:0.78rem;"><div><b style="color:#ffffff;">{html_lib.escape(item["nome"])}</b><div style="color:#64748b; font-size:0.67rem;">{html_lib.escape(item["funcao"])}</div></div><span style="color:#00D672; font-weight:800; font-size:0.72rem;">{item["res"] or item["status"]}</span></div>'
    return html_out

def renderizar_itens_simples(lista_dados, cor_texto):
    if not lista_dados: return "<div style='color:#64748b; font-size:0.75rem; padding:6px 8px;'>Nenhum colaborador nesta seção.</div>"
    h = ""
    for item in sorted(lista_dados, key=lambda x: x["nome"]):
        h += f'<div style="display:flex; justify-content:space-between; align-items:center; padding:6px 8px; border-bottom:1px dashed #1c2b42; font-size:0.78rem;"><div><b style="color:#ffffff;">{html_lib.escape(item["nome"])}</b><div style="color:#64748b; font-size:0.67rem;">{html_lib.escape(item["funcao"])}</div></div><span style="color:{cor_texto}; font-weight:800; font-size:0.72rem;">{item["res"] or item["status"]}</span></div>'
    return h

# 4. Renderização do Card Bafômetro (Sem atributo 'open' para nascer fechado)
html_baf_final = f"""
<div id="sec-baf"></div>
<details class="master-box" style="border-left-color: #FFFFFF; margin-bottom: 14px;">
    <summary>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div class="header-layout" style="margin-bottom: 0;">
                <div class="icon-box" style="background-color: rgba(255, 255, 255, 0.15); color: #FFFFFF;">🩺</div>
                <div class="master-metric-title">Auditoria Bafômetro (H&S)</div>
            </div>
        </div>
        <div class="value-layout" style="margin-bottom: 2px;">
            <div class="master-metric-val">{total_registrados_baf}</div>
            <div class="master-metric-unit">Testes Registrados</div>
        </div>
        <div class="master-metric-sub" style="color: #cbd5e1; font-weight: bold;">
            {nome_turno_completo} &nbsp;|&nbsp; 🟢 {len(lista_aprovados)} Aprovados &bull; <span style="color:#38bdf8;">🔄 {len(lista_trocas)} Trocas</span> &bull; 🔴 {len(lista_pendentes)} Pendentes
        </div>
    </summary>

    <div class="master-content" style="padding-top: 14px;">
        <!-- SEÇÃO 1: APROVADOS -->
        <div style="background:#070d18; border:1px solid #142842; border-left:3px solid #00D672; border-radius:10px; padding:10px; margin-bottom:10px;">
            <div style="font-size:0.75rem; font-weight:800; color:#00D672; text-transform:uppercase; margin-bottom:4px;">
                APROVADOS ({len(lista_aprovados)})
            </div>
            {agrupar_e_renderizar_aprovados(lista_aprovados)}
        </div>

        <!-- SEÇÃO 2: TROCAS -->
        <div style="background:#070d18; border:1px solid #142842; border-left:3px solid #38bdf8; border-radius:10px; padding:10px; margin-bottom:10px;">
            <div style="font-size:0.75rem; font-weight:800; color:#38bdf8; text-transform:uppercase; margin-bottom:6px;">
                TROCAS / NÃO CADASTRADOS ({len(lista_trocas)})
            </div>
            {renderizar_itens_simples(lista_trocas, '#38bdf8')}
        </div>

        <!-- SEÇÃO 3: PENDENTES -->
        <div style="background:#070d18; border:1px solid #142842; border-left:3px solid #E74C3C; border-radius:10px; padding:10px; margin-bottom: 12px;">
            <div style="font-size:0.75rem; font-weight:800; color:#E74C3C; text-transform:uppercase; margin-bottom:6px;">
                NÃO REALIZADOS / PENDENTES ({len(lista_pendentes)})
            </div>
            {renderizar_itens_simples(lista_pendentes, '#E74C3C')}
        </div>
    </div>
</details>
"""
render_html(html_baf_final)





# ==============================================================================
# 🖨️ RENDERIZAÇÃO 10: COMPARATIVO ANUAL (PRODUÇÃO VS EXPEDIÇÃO)
# ==============================================================================
d_res = max(1, (date(hoje_date.year, 12, 31) - hoje_date).days)
ca_at = forcar_par(1362558.0 + vol_hoje)
pa_at = forcar_par(1362676.0 + prod_hoje_calc)
df_pc = forcar_par(abs(pa_at - ca_at))

tv, cv = (f"+{fmt(df_pc)} t (Expedição Superando)", "#00D672") if ca_at >= pa_at else (f"+{fmt(df_pc)} t (Produção Superando)", "#FF9F1C")
mdc = forcar_par(5200.0 + (max(0.0, estoque_total - 3468.0) / d_res))
ppf = forcar_par(pa_at + (d_res * 5200.0))
pcf = forcar_par(ca_at + ((estoque_total + (d_res * 5200.0)) - 3468.0))

h_an = f'<details class="master-box" style="border-left-color:#007BFF;" open><summary><div class="header-layout"><div class="icon-box" style="background-color:rgba(0,123,255,.15); color:#007BFF;">📊</div><div class="master-metric-title">Comparativo Produção vs Expedição</div></div><div class="value-layout"><div class="master-metric-val">{fmt(ca_at)}</div><div class="master-metric-unit">t Expedidas</div></div><div class="master-metric-sub" style="color:#007BFF;">Meta Diária Necessária: {fmt(mdc)} t/dia</div></summary><div class="master-content" style="padding-top:16px;"><div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px;"><div style="background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:10px;"><div style="font-size:0.75rem; color:#007BFF; font-weight:bold;">EXPEDIÇÃO ANUAL</div><div style="font-size:1.4rem; font-weight:bold; color:#fff; margin:4px 0;">{fmt(ca_at)} <span style="font-size:0.8rem; color:#64748b; font-weight:normal;">t</span></div><div style="font-size:0.7rem; color:#64748b;">Proj. 31/12: <span style="color:#007BFF;">{fmt(pcf)} t</span></div></div><div style="background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:10px;"><div style="font-size:0.75rem; color:#00D672; font-weight:bold;">PRODUÇÃO ANUAL</div><div style="font-size:1.4rem; font-weight:bold; color:#fff; margin:4px 0;">{fmt(pa_at)} <span style="font-size:0.8rem; color:#64748b; font-weight:normal;">t</span></div><div style="font-size:0.7rem; color:#64748b;">Proj. 31/12: <span style="color:#00D672;">{fmt(ppf)} t</span></div></div></div><div style="background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:12px; font-size:0.82rem; color:#cbd5e1; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;"><span>Variação: <span style="color:{cv}; font-weight:bold;">{tv}</span></span><span>Estoque Meta: <span style="color:#38bdf8; font-weight:bold;">3.468 t</span></span></div></div></details>'
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


st.markdown("<br><center><span style='color:#64748b; font-size:0.75rem; letter-spacing:0.5px;'>A.L.O.V.E - Mobile / Developed by Cristiano Ciriaco</span></center>", unsafe_allow_html=True)
