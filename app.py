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

# 1. URLs OFICIAIS DE IDENTIDADE VISUAL
LOGO_ALOVE_URL = "https://raw.githubusercontent.com/expedicao-mi/A.L.O.V.E-/main/app_icon.png"
BANNER_TOPO_URL = "https://raw.githubusercontent.com/expedicao-mi/A.L.O.V.E-/main/logo_alove.jpg?v=99"

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
# 🎨 CSS (LAYOUT VERTICAL APERFEIÇOADO)
# ==============================================================================
st.markdown("""
    <style>
        /* MATA AS MARCAS DO STREAMLIT */
        #MainMenu, footer, header, [data-testid="manage-app-button"], [data-testid="stToolbar"], [data-testid="stDecoration"], .viewerBadge_container__1QSob, .viewerBadge_link__1S137 {
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
        .topo-banner img { width: 100%; max-height: 130px; object-fit: contain; display: block; margin: 0 auto; }

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

        /* STATUS SUPERIOR */
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

        /* BLOCOS MASTER (ACCORDIONS DE PRODUÇÃO E EXPEDIÇÃO) */
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

        /* TAGS DE FROTA E LEGENDAS */
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
        .f-leg-nota { color: #64748b; font-size: .7rem; margin-top: 8px; border-top: 1px dashed #1c2b42; padding-top: 6px; }

        /* NAVEGAÇÃO INFERIOR */
        .bottom-nav { position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 100%; max-width: 560px; z-index: 999990; display: flex; justify-content: space-around; background: #070d18; border-top: 1px solid #12506e; padding: 8px 0 calc(8px + env(safe-area-inset-bottom)); }
        .bottom-nav a { color: #8fa6c4; text-decoration: none; font-size: .7rem; display: flex; flex-direction: column; align-items: center; gap: 2px; min-width: 56px; }
        .bottom-nav a span { font-size: 1.25rem; }
        .bottom-nav a:active { color: #00D672; }

        @keyframes pulso { 0% { box-shadow: 0 0 0 0 rgba(0,214,114,.55); } 70% { box-shadow: 0 0 0 9px rgba(0,214,114,0); } 100% { box-shadow: 0 0 0 0 rgba(0,214,114,0); } }
    </style>
""", unsafe_allow_html=True)

SHEET_ID = "10FluiIwlynIlPDA74QI8mpHSIrAc-62H1hZNRBsvfCA"

# ==============================================================================
# 🔧 UTILITÁRIOS
# ==============================================================================
def forcar_par(valor):
    val_int = int(round(float(valor or 0)))
    return val_int + 1 if val_int % 2 != 0 else val_int

def fmt(n, casas=0):
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
        return df.dropna(how="all", axis=1).dropna(how="all", axis=0)
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=20)
def carregar_tabela_por_cabecalho(worksheet_name: str, chave: str = "DESTINO"):
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
            return corpo[~(corpo.astype(str).apply(lambda r: "".join(r).strip() == "", axis=1))].reset_index(drop=True)
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
# 🚀 EXTRAÇÃO DA NUVEM (SHEETS)
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
if df_bafometro.empty: df_bafometro = carregar_dados_nuvem("Auditoria_Bafometro", cabecalho=0)
df_frota = carregar_dados_nuvem("Historico_DKRO", cabecalho=0)

cache_dict = {str(row.iloc[0]).strip(): str(row.iloc[1]).strip() for _, row in df_cache.iterrows()} if not df_cache.empty else {}
dados_segregados = parse_robusto(cache_dict.get("dados_segregados", "{}"))

ultima_att = None
vol_hoje = vol_ontem = prev_carr = prod_hoje_calc = prev_prod = estoque_total = 0
status_transbordo = ritmo_torre = "NORMAL"

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

    rt_bruto = str(row_d.get("RITMO_TORRE", "NORMAL")).upper()
    ritmo_torre = "RITMO DE ATUALIZAÇÃO: RÁPIDO" if "12" in rt_bruto or "ACELERADO" in rt_bruto else rt_bruto

# ==============================================================================
# 🎯 TOPO: BANNER + CONEXÃO
# ==============================================================================
st.markdown(f'<div id="sec-inicio" class="anc"></div><div class="topo-banner"><img src="{BANNER_TOPO_URL}"></div>', unsafe_allow_html=True)

def calc_conn(ultima_str, agora):
    if not ultima_str: return "SEM DADOS", "#94a3b8", "—"
    try: dt = datetime.strptime(ultima_str[:19], "%d/%m/%Y %H:%M:%S")
    except: return "SEM DADOS", "#94a3b8", ultima_str
    m = (agora - dt).total_seconds() / 60.0
    th = dt.strftime("%H:%M:%S") if dt.date() == agora.date() else dt.strftime("%d/%m %H:%M")
    if m <= 15: return "CONECTADO", "#00D672", th
    if m <= 45: return "ATRASADO", "#FFD600", th
    return "DESCONECTADO", "#E74C3C", th

conn_txt, conn_cor, conn_hora = calc_conn(ultima_att, agora_br)

with st.container(border=True):
    c1, c2 = st.columns([3, 2], vertical_alignment="center")
    with c1:
        st.markdown(f'<div style="display:flex; align-items:center;"><span class="conn-dot" style="background:{conn_cor};"></span><span class="conn-titulo" style="color:{conn_cor};">{conn_txt}</span></div><div class="conn-sub">🕒 Última att: {conn_hora}</div><div class="conn-ritmo">🎯 {ritmo_torre}</div>', unsafe_allow_html=True)
    with c2:
        if st.button("🔄 Atualizar", use_container_width=True):
            st.cache_data.clear(); st.rerun()

# ==============================================================================
# 🔔 NOTIFICAÇÕES (MOBILE ALERTAS)
# ==============================================================================
alertas_list = []
if not df_alertas.empty:
    for _, ra in df_alertas.iterrows():
        n = str(ra.get("NIVEL", "")).strip().upper()
        t = str(ra.get("ALERTA", "")).strip()
        if not t or t.lower() == "nan": continue
        dh = str(ra.get("DATA_HORA", "")).strip()
        alertas_list.append((n, re.sub(r'^[^\w\[\(]+', '', t), dh.split(" ")[1][:5] if " " in dh else "--:--"))

ord_n = {"CRITICO": 0, "ATENCAO": 1, "NORMAL": 2}
alertas_list.sort(key=lambda a: ord_n.get(a[0], 3))
n_nov = sum(1 for a in alertas_list if a[0] in ("CRITICO", "ATENCAO"))
ESTILO_NIVEL = {"CRITICO": ("#E74C3C", "rgba(231,76,60,.18)", "🚨", "Alerta crítico"), "ATENCAO": ("#FFD600", "rgba(255,214,0,.16)", "⚠️️", "Atenção")}

def render_not(nivel, texto, hora):
    cor, bg, ico, tit = ESTILO_NIVEL.get(nivel, ("#00D672", "rgba(0,214,114,.16)", "✅", "Operação normal"))
    return f'<div class="notif-item"><div class="notif-ico" style="background:{bg}; color:{cor};">{ico}</div><div class="notif-txt"><div class="notif-tit">{tit}</div><div class="notif-desc">{html_lib.escape(texto)}</div></div><div class="notif-hora">{hora}<i style="background:{cor};"></i></div></div>'

if alertas_list:
    pr = "".join(render_not(*a) for a in alertas_list[:3])
    rs = alertas_list[3:]
    htm_m = f'<details class="notif-mais"><summary><span>Ver todas as notificações ({len(alertas_list)})</span><span class="chev">›</span></summary><div class="notif-lista" style="margin-top:6px;">{"".join(render_not(*a) for a in rs)}</div></details>' if rs else ""
    st.markdown(f'<div class="card-main"><div class="card-head"><div class="icon-sq">🔔</div><div class="card-title">Notificações</div><div class="badge-novas" style="color:{"#38bdf8" if n_nov else "#00D672"};">{n_nov} novas</div></div><div class="notif-lista">{pr}</div>{htm_m}</div>', unsafe_allow_html=True)

# ==============================================================================
# 📦 BLOCO 1: PÁTIO DE VEÍCULOS
# ==============================================================================
STATUS_COLS = {"PR": ("PR_VEIC", "PR_TON"), "00": ("00_VEIC", "00_TON"), "01": ("01_VEIC", "01_TON"), "FC": ("FC_VEIC", "FC_TON")}
dest_status = {"PR": [], "00": [], "01": [], "FC": [], "TR": []}
dados_p = {k: {"v": 0, "p": 0} for k in dest_status}
tot_plan = {k: {"v": 0, "p": 0} for k in STATUS_COLS}

if not df_patio_dest.empty:
    for _, l in df_patio_dest.iterrows():
        dn = str(l.get("DESTINO", "")).strip()
        if not dn or dn.upper() in ["NAN", "NONE", "DESTINO"]: continue
        if "TOTAL" in dn.upper():
            for ch, (cv, ct) in STATUS_COLS.items():
                tot_plan[ch]["v"], tot_plan[ch]["p"] = int(safe_to_numeric(l.get(cv, 0))), forcar_par(safe_to_numeric(l.get(ct, 0)))
            continue
        for ch, (cv, ct) in STATUS_COLS.items():
            v, t = int(safe_to_numeric(l.get(cv, 0))), forcar_par(safe_to_numeric(l.get(ct, 0)))
            if v > 0 or t > 0: dest_status[ch].append({"d": dn, "v": v, "t": t})

dif_st = {}
for ch in STATUS_COLS:
    if dest_status[ch]:
        dados_p[ch]["v"], dados_p[ch]["p"] = sum(i["v"] for i in dest_status[ch]), sum(i["t"] for i in dest_status[ch])
        dif_st[ch] = tot_plan[ch]["v"] - dados_p[ch]["v"]
    else:
        dados_p[ch]["v"], dados_p[ch]["p"], dif_st[ch] = tot_plan[ch]["v"], tot_plan[ch]["p"], 0

dados_p["TR"]["v"] = int(safe_to_numeric(df_dash.iloc[0].get("TR_VEIC", 0))) if not df_dash.empty else 0
dados_p["TR"]["p"] = forcar_par(safe_to_numeric(df_dash.iloc[0].get("TR_TON", 0))) if not df_dash.empty else 0

tvf = dados_p["00"]["v"] + dados_p["01"]["v"] + dados_p["FC"]["v"]
vpd = forcar_par(dados_p["00"]["p"] + dados_p["01"]["p"] + dados_p["FC"]["p"])

h_patio = f'<div id="sec-patio" class="anc"></div><div class="card-main"><div class="card-head"><div class="icon-sq">🏭</div><div class="card-title">Pátio (Tempo Real)</div></div><div class="kpi-duo"><div class="kpi-box"><div class="kpi-ico">🚚</div><div><div class="kpi-big">{tvf}</div><div class="kpi-lbl">Veículos Físicos</div><div class="kpi-sub">Checklist + Apoio + Fila</div></div></div><div class="kpi-sep"></div><div class="kpi-box"><div class="kpi-ico">📦</div><div><div class="kpi-lbl">Carga Disponível</div><div class="kpi-big verde">{fmt(vpd)} <span>t</span></div></div></div></div></div>'

for tit, chv, cor, ico in [("Prog/Chegando", "PR", "#38a9ff", "🚙"), ("Checklist", "00", "#FFD600", "📋"), ("Apoio", "01", "#E67E22", "🚛"), ("Fila de Carregamento", "FC", "#00D672", "✅")]:
    ld = dest_status[chv]
    h_linhas = "".join(f'<div class="dest-row"><span class="n">{html_lib.escape(i["d"])}</span><span class="v">{i["v"]} veíc. <small>({fmt(i["t"])} t)</small></span></div>' for i in ld) + f'<div class="dest-row total"><span class="n">TOTAL</span><span class="v">{dados_p[chv]["v"]} veíc. <small>({fmt(dados_p[chv]["p"])} t)</small></span></div>' if ld else '<div class="dest-vazio">Nenhum veículo alocado neste status.</div>'
    if dif_st.get(chv, 0) != 0 and ld: h_linhas += f'<div class="dest-aviso">⚠️ A planilha informa {tot_plan[chv]["v"]} veíc. no total (diferença de {abs(dif_st[chv])} não detalhada por destino).</div>'
    h_patio += f'<details class="st-card" style="--c:{cor};"><summary><div class="st-ico">{ico}</div><div class="st-txt"><div class="st-title">{tit}</div><div class="st-num">{dados_p[chv]["v"]} <span>veíc. / {fmt(dados_p[chv]["p"])} t</span></div></div><div class="chev">›</div></summary><div class="st-body">{h_linhas}</div></details>'

h_patio += f'<div class="st-card" style="--c:#95A5A6;"><div class="st-sum"><div class="st-ico">📄</div><div class="st-txt"><div class="st-title">Termo SAP</div><div class="st-num">{dados_p["TR"]["v"]} <span>veíc. / {fmt(dados_p["TR"]["p"])} t</span></div></div><div style="color:#64748b; font-size:.72rem; text-align:right;">Fila de<br>Faturamento</div></div></div>'
st.markdown(h_patio.replace('\n', ''), unsafe_allow_html=True)

# ==============================================================================
# 🏭 BLOCO 2: PRODUÇÃO
# ==============================================================================
viradas_info = {}
if not df_status_virada.empty:
    for _, rs in df_status_virada.iterrows():
        viradas_info[str(rs.get("LINHA", "")).strip().upper()] = {"p_mat": str(rs.get("PROXIMO_MATERIAL", "--")), "p_vir": str(rs.get("PREVISAO_VIRADA", "--")), "s_rest": forcar_par(safe_to_numeric(rs.get("SALDO_RESTANTE_T", 0))), "s_em": str(rs.get("STATUS_EMAIL_TROCA", "N/D"))}

h_prod_c = ""
for maq in ["MS1", "MS2"]:
    qd = {}
    if not df_qual.empty:
        for _, rq in df_qual.iterrows():
            if str(rq.get("MAQUINA", "")).strip().upper() == maq:
                qd = {"mat": str(rq.get("MATERIAL", "--")), "alv": safe_to_numeric(rq.get("ALVURA", 0)), "suj": safe_to_numeric(rq.get("SUJIDADE", 0)), "vis": safe_to_numeric(rq.get("VISCOSIDADE", 0)), "ph": safe_to_numeric(rq.get("PH", 0)), "prod": forcar_par(safe_to_numeric(rq.get("PROD_TOTAL", 0))), "l1": forcar_par(safe_to_numeric(rq.get("PROD_LINHA_1", 0))), "l2": forcar_par(safe_to_numeric(rq.get("PROD_LINHA_2", 0))), "desc": str(rq.get("DESCLASSIFICANDO", "NAO")).upper() == "SIM"}
                break
    if qd:
        ca, cs, cv, cp = classificar_kpi_mobile(qd['alv'], "alvura"), classificar_kpi_mobile(qd['suj'], "sujidade"), classificar_kpi_mobile(qd['vis'], "viscosidade"), classificar_kpi_mobile(qd['ph'], "ph")
        cb = "#E74C3C" if qd['desc'] else "#1c2b42"
        vi = viradas_info.get(maq, {})
        hv = ""
        if vi:
            ca_txt = "#E74C3C" if "🚨" in vi['s_em'] else ("#00D672" if "✅" in vi['s_em'] else "#38bdf8")
            hv = f"<div style='background-color:#070d18; border:1px solid #1c2b42; border-left:4px solid {ca_txt}; padding:10px; margin-top:14px; border-radius:6px;'><div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'><span style='font-size:0.75rem; color:#64748b; text-transform:uppercase;'>Saldo a Produzir ({qd['mat']})</span><span style='font-size:1.1rem; color:#ffffff;'>{fmt(vi['s_rest'])} t</span></div><div style='display:flex; justify-content:space-between; align-items:center; font-size:0.75rem;'><span style='color:#cbd5e1;'>🔜 Prox: <span style='color:#38bdf8;'>{vi['p_mat']}</span> ({vi['p_vir']})</span><span style='color:{ca_txt};'>📧 {vi['s_em'].replace('📧 ', '').replace('⚠️ ', '')}</span></div></div>"
        
        h_prod_c += f"<div style='background-color:#0a101d; border:1.5px solid {cb}; border-radius:8px; padding:16px; margin-bottom:12px;'><div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'><span style='color:#ffffff; font-weight:bold; font-size:1.1rem;'>⚙️ {maq}</span><span style='color:#FF9F1C; font-size:1.1rem;'>📦 MAT: {qd['mat']}</span><span style='color:#38bdf8; font-weight:bold; font-size:1.2rem;'>{fmt(qd['prod'])} t</span></div><div style='display:flex; justify-content:flex-end; gap:16px; margin-bottom:12px; font-size:0.85rem; color:#64748b;'><span>{'Linha A' if maq=='MS1' else 'Linha C'}: <span style='color:#ffffff;'>{fmt(qd['l1'])} t</span></span><span>{'Linha B' if maq=='MS1' else 'Linha D'}: <span style='color:#ffffff;'>{fmt(qd['l2'])} t</span></span></div><div style='display:flex; justify-content:space-between; text-align:center; border-top:1px dashed #1c2b42; padding-top:14px;'><div><div style='font-size:0.7rem; color:#64748b; font-weight:bold;'>ALVURA</div><div style='font-size:1.2rem; color:{ca}; margin:4px 0;'>{fmt(qd['alv'], 2)}%</div><div style='font-size:0.65rem; color:#475569;'>(Mín: 88,5)</div></div><div><div style='font-size:0.7rem; color:#64748b; font-weight:bold;'>SUJIDADE</div><div style='font-size:1.2rem; color:{cs}; margin:4px 0;'>{fmt(qd['suj'], 2)}</div><div style='font-size:0.65rem; color:#475569;'>(Máx: 2,5)</div></div><div><div style='font-size:0.7rem; color:#64748b; font-weight:bold;'>VISCOSID.</div><div style='font-size:1.2rem; color:{cv}; margin:4px 0;'>{fmt(qd['vis'])}</div><div style='font-size:0.65rem; color:#475569;'>(Mín: 650)</div></div><div><div style='font-size:0.7rem; color:#64748b; font-weight:bold;'>pH</div><div style='font-size:1.2rem; color:{cp}; margin:4px 0;'>{fmt(qd['ph'], 1)}</div><div style='font-size:0.65rem; color:#475569;'>(5,5 - 8,5)</div></div></div>{hv}</div>"
    else:
        h_prod_c += f"<div style='color:gray; padding:10px 0;'>Aguardando dados da {maq}...</div>"

pms1 = next((forcar_par(safe_to_numeric(r.get("PROD_TOTAL",0))) for _, r in df_qual.iterrows() if str(r.get("MAQUINA","")).strip().upper()=="MS1"), 0) if not df_qual.empty else 0
pms2 = next((forcar_par(safe_to_numeric(r.get("PROD_TOTAL",0))) for _, r in df_qual.iterrows() if str(r.get("MAQUINA","")).strip().upper()=="MS2"), 0) if not df_qual.empty else 0

st.markdown(f'<div id="sec-prod" class="anc"></div><details class="master-box" style="border-left-color:#E5B800;"><summary><div class="header-layout"><div class="icon-box" style="background-color:rgba(229,184,0,.15); color:#E5B800;">🏭</div><div class="master-metric-title">Produção de Celulose</div></div><div class="value-layout"><div class="master-metric-val">{fmt(prod_hoje_calc)}</div><div class="master-metric-unit">TON</div></div><div class="master-metric-sub" style="color:#E5B800;">MS1: {fmt(pms1)} t | MS2: {fmt(pms2)} t</div></summary><div class="master-content" style="padding-top:16px;">{h_prod_c}</div></details>'.replace('\n', ''), unsafe_allow_html=True)

# ==============================================================================
# 🚚 BLOCO 3: EXPEDIÇÃO (LISTA DIRETA SEM TABS)
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
        if dt_a.weekday() in [6, 0]: tns.append({"l": f"Turno {ls.get('madrugada','D')}", "v": 0, "sv": "EM FOLGA", "h": "Somente Armazen."})
        else: tns.append({"l": f"Turno {ls.get('madrugada','D')}", "v": v1, "sv": f"{fmt(v1)} t", "h": "00h - 08h"})
        tns.append({"l": f"Turno {ls.get('08_16','C')}", "v": v2, "sv": f"{fmt(v2)} t", "h": "08h - 16h"})
        tns.append({"l": f"Turno {ls.get('16_00','B')}", "v": v3, "sv": f"{fmt(v3)} t", "h": "16h - 00h"})
        return tns
    except: return []

tns_hoje = func_exp_dados(hoje_date)
tns_ontem = func_exp_dados(ontem_date)

bd_list = []
tm_exp, tr_exp = 0.0, 0.0
if not df_balanco_dest.empty:
    for _, r in df_balanco_dest.iterrows():
        dn = str(r.get("DESTINO", "")).strip()
        if not dn or dn.upper() in ["NAN", "NONE", "DESTINO"]: continue
        mv, rv, sv = forcar_par(safe_to_numeric(r.get("META_DIA_T",0))), forcar_par(safe_to_numeric(r.get("EXPEDIDO_ZLE_T",0))), forcar_par(safe_to_numeric(r.get("SALDO_A_EXPEDIR_T",0)))
        try: av = float(str(r.get("ATINGIMENTO_%",0)).replace('%','').replace(',','.'))
        except: av = 0.0
        if "TOTAL" in dn.upper(): tm_exp, tr_exp = mv, rv
        else:
            nm = "MI / LATAM" if "MI" in dn.upper() or "LATAM" in dn.upper() else (f"{dn.split('-')[0].strip()} - {dn.split('-')[1].strip()}" if "-" in dn else dn)
            bd_list.append({"d": nm, "m": mv, "r": rv, "s": sv, "a": av})

def rule_ord(x):
    if "MI" in x['d'] or "LATAM" in x['d']: return 999999
    try: return int(re.search(r'\d+', x['d']).group())
    except: return 0

bd_list.sort(key=rule_ord, reverse=True)

h_exp = f'<div id="sec-exp" class="anc"></div><details class="master-box" style="border-left-color:#00D672;" open><summary><div class="header-layout"><div class="icon-box" style="background-color:rgba(0,214,114,.15); color:#00D672;">🚚</div><div class="master-metric-title">Expedição Realizada</div></div><div class="value-layout"><div class="master-metric-val">{fmt(vol_hoje)}</div><div class="master-metric-unit">TON</div></div><div class="master-metric-sub" style="color:#00D672;">Consolidado Ontem (D-1): {fmt(vol_ontem)} t</div></summary><div class="master-content" style="padding-top:16px;">'

h_exp += "<div style='font-size:0.75rem; font-weight:bold; color:#00D672; text-transform:uppercase; margin-bottom:8px;'>🗓️ TURNOS EM OPERAÇÃO (HOJE)</div><div style='display:flex; gap:6px; margin-bottom:16px;'>"
for i, t in enumerate(tns_hoje):
    is_atv = False
    if hoje_date == agora_br.date():
        if agora_br.hour < 8 and i == 0: is_atv = True
        elif 8 <= agora_br.hour < 16 and i == 1: is_atv = True
        elif agora_br.hour >= 16 and i == 2: is_atv = True
    c_b, c_t = ("#FF9F1C", "#FF9F1C") if is_atv else ("#1c2b42", "#ffffff")
    h_exp += f"<div style='flex:1; background-color:#0a101d; border:1px solid {c_b}; border-radius:8px; padding:8px; text-align:center;'><div style='font-size:0.75rem; font-weight:bold; color:{c_t};'>{t['l']}</div><div style='font-size:1.1rem; font-weight:normal; color:{'#E74C3C' if t['sv']=='EM FOLGA' else '#ffffff'};'>{t['sv']}</div><div style='font-size:0.65rem; color:#64748b;'>{t['h']}{' (ATIVO)' if is_atv else ''}</div></div>"
h_exp += "</div>"

h_exp += f"<div style='font-size:0.75rem; font-weight:bold; color:#38bdf8; text-transform:uppercase; margin-bottom:8px;'>⏮️ FECHAMENTO D-1 ({ontem_date.strftime('%d/%m')})</div><div style='display:flex; gap:6px; margin-bottom:20px;'>"
for t in tns_ontem:
    h_exp += f"<div style='flex:1; background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:8px; text-align:center;'><div style='font-size:0.75rem; font-weight:bold; color:#38bdf8;'>{t['l']}</div><div style='font-size:1.1rem; font-weight:normal; color:{'#E74C3C' if t['sv']=='EM FOLGA' else '#ffffff'};'>{t['sv']}</div><div style='font-size:0.65rem; color:#64748b;'>{t['h']}</div></div>"
h_exp += "</div>"

h_exp += f"<div style='font-size:0.75rem; font-weight:bold; color:#ffffff; text-transform:uppercase; margin-bottom:8px;'>📍 BALANÇO POR DESTINO</div><div style='display:flex; justify-content:space-around; background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:12px; margin-bottom:14px; text-align:center;'><div><div style='font-size:0.75rem; color:#64748b; font-weight:bold; text-transform:uppercase;'>Plano Total Diário</div><div style='font-size:1.4rem; color:#ffffff; font-weight:bold;'>{fmt(tm_exp)} <span style='font-size:0.8rem; color:#64748b; font-weight:normal;'>t</span></div></div><div style='border-left:1px solid #1c2b42; padding-left:20px;'><div style='font-size:0.75rem; color:#38bdf8; font-weight:bold; text-transform:uppercase;'>Total Carregado</div><div style='font-size:1.4rem; color:#38bdf8; font-weight:bold;'>{fmt(tr_exp)} <span style='font-size:0.8rem; font-weight:normal;'>t</span></div></div></div>"

if bd_list:
    h_exp += "<div style='background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:10px; overflow-x:auto;'><table style='width:100%; border-collapse:collapse; font-size:0.75rem; text-align:center; color:#ffffff; font-weight:normal;'><thead><tr style='border-bottom:1px solid #1c2b42; color:#64748b; font-weight:normal;'><th style='text-align:left; padding:8px 4px; font-weight:normal;'>Destino</th><th style='text-align:center; padding:8px 4px; color:#38bdf8; font-weight:normal;'>Plano</th><th style='text-align:center; padding:8px 4px; color:#00D672; font-weight:normal;'>Carr.</th><th style='text-align:center; padding:8px 4px; color:#E5B800; font-weight:normal;'>Falta</th><th style='text-align:center; padding:8px 4px; font-weight:normal;'>%</th></tr></thead><tbody>"
    for d in bd_list:
        ca = "#00D672" if d['a'] >= 100 else ("#38bdf8" if d['a'] > 0 else "#64748b")
        cs, ss = ("#00D672", "0") if d['s'] <= 0 and d['r'] > 0 else ("#E5B800", fmt(d['s']))
        h_exp += f"<tr style='border-bottom:1px dashed #1c2b42;'><td style='text-align:left; padding:10px 4px;'>{d['d']}</td><td style='color:#38bdf8; padding:10px 4px;'>{fmt(d['m'])}</td><td style='color:#00D672; padding:10px 4px;'>{fmt(d['r'])}</td><td style='color:{cs}; padding:10px 4px;'>{ss}</td><td style='color:{ca}; padding:10px 4px;'>{d['a']:.0f}%</td></tr>"
    h_exp += "</tbody></table></div>"
else: h_exp += '<div style="color:#64748b; font-size:0.8rem; text-align:center;">Nenhum destino ativo reportado.</div>'

h_exp += "</div></details>"
st.markdown(h_exp.replace('\n', ''), unsafe_allow_html=True)

# ==============================================================================
# 📦 BLOCO 4: ESTOQUE SEGREGADO (CAIXAS AZUIS E VERDES IDÊNTICAS À TV)
# ==============================================================================
h_est = f'<div id="sec-estoque" class="anc"></div><details class="master-box" style="border-left-color:#9b59b6;"><summary><div class="header-layout"><div class="icon-box" style="background-color:rgba(155,89,182,.15); color:#9b59b6;">📦</div><div class="master-metric-title">Estoque Físico no Armazém</div></div><div class="value-layout"><div class="master-metric-val">{fmt(estoque_total)}</div><div class="master-metric-unit">TON</div></div><div class="master-metric-sub" style="color:#9b59b6;">Status do Armazém: {status_transbordo}</div></summary><div class="master-content" style="padding-top:16px;">'

if dados_segregados:
    df_seg = pd.DataFrame(list(dados_segregados.items()), columns=["Material", "Toneladas"]).sort_values(by="Toneladas", ascending=False)
    h_est += "<div style='display:flex; flex-wrap:wrap; gap:8px; justify-content:center;'>"
    for _, r in df_seg.iterrows():
        t = forcar_par(r["Toneladas"])
        m = str(r["Material"]).upper()
        # Se contiver "EQ", usa a cor verde, senão o azul padrão
        cb = "#00D672" if "EQ" in m else "#38bdf8"
        h_est += f"<div style='flex:1; min-width:30%; background-color:#0a101d; border:1px solid #1c2b42; border-radius:6px; padding:10px; text-align:center;'><div style='font-size:0.75rem; color:#94a3b8; font-weight:bold;'>{m}</div><div style='font-size:1.1rem; font-weight:bold; color:{cb}; margin-top:2px;'>{fmt(t)} t</div></div>"
    h_est += "</div>"
else:
    h_est += '<div style="color:gray;">Aguardando detalhamento de material...</div>'

h_est += "</div></details>"
st.markdown(h_est.replace('\n', ''), unsafe_allow_html=True)

# ==============================================================================
# 🚜 BLOCO 5: FROTA (LISTA DIRETA)
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
            
            # Atualiza mantendo a pior condição
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

h_fr = f'<div id="sec-frota" class="anc"></div><details class="master-box" style="border-left-color:#E67E22;"><summary><div class="header-layout"><div class="icon-box" style="background-color:rgba(230,126,34,.15); color:#E67E22;">🚜</div><div class="master-metric-title">Frota e Equipamentos</div></div><div class="value-layout"><div class="master-metric-val">{v_hoje}</div><div class="master-metric-unit">Veículos Logados Hoje</div></div><div class="master-metric-sub" style="color:#E67E22;">Empilhadeiras e Talhas Elétricas</div></summary><div class="master-content" style="padding-top:16px;">'

h_fr += f"<div style='font-size:0.75rem; font-weight:bold; color:#00D672; text-transform:uppercase; margin-bottom:8px;'>📅 LOGADOS HOJE ({hoje_date.strftime('%d/%m')})</div><div style='background-color:#05080f; padding:12px; border-radius:8px; border:1px solid #1c2b42; margin-bottom:16px;'><div class='f-tag-title'>🟢 Empilhadeiras ({len(frota_agr['h']['e'])})</div><div style='margin-bottom:12px;'>{rnd_tg(frota_agr['h']['e'])}</div><div class='f-tag-title'>🏗️ Talhas / Pontes ({len(frota_agr['h']['t'])})</div><div>{rnd_tg(frota_agr['h']['t'])}</div></div>"

h_fr += f"<div style='font-size:0.75rem; font-weight:bold; color:#38bdf8; text-transform:uppercase; margin-bottom:8px;'>⏮️ LOGADOS ONTEM ({ontem_date.strftime('%d/%m')})</div><div style='background-color:#05080f; padding:12px; border-radius:8px; border:1px solid #1c2b42; margin-bottom:16px;'><div class='f-tag-title'>🟢 Empilhadeiras ({len(frota_agr['o']['e'])})</div><div style='margin-bottom:12px;'>{rnd_tg(frota_agr['o']['e'])}</div><div class='f-tag-title'>🏗️ Talhas / Pontes ({len(frota_agr['o']['t'])})</div><div>{rnd_tg(frota_agr['o']['t'])}</div></div>"

h_fr += '<div class="f-legenda"><div class="f-leg-titulo">🎨 Legenda das cores</div><div class="f-leg-item"><span class="f-leg-cor f-tag-ok"></span><span><b>Verde</b> — OK: sem avarias apontadas</span></div><div class="f-leg-item"><span class="f-leg-cor f-tag-aten"></span><span><b>Amarelo</b> — Atenção: item apontado no checklist</span></div><div class="f-leg-item"><span class="f-leg-cor f-tag-avaria"></span><span><b>Vermelho</b> — Avaria: equipamento bloqueado/quebrado</span></div></div></div></details>'
st.markdown(h_fr.replace('\n', ''), unsafe_allow_html=True)

# ==============================================================================
# 🩺 BLOCO 6: AUDITORIA BAFÔMETRO (PROTEGIDO)
# ==============================================================================
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

# ==============================================================================
# 📊 BLOCO 7: COMPARATIVO ANUAL E RODAPÉ
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
st.markdown(h_an.replace('\n', ''), unsafe_allow_html=True)
st.markdown("<br><center><span style='color:#64748b; font-size:0.75rem; letter-spacing:0.5px;'>A.L.O.V.E - Mobile / Developed by Crist Ciriaco</span></center>", unsafe_allow_html=True)

# ==============================================================================
# 🧭 NAVEGAÇÃO INFERIOR ESTRITA
# ==============================================================================
st.markdown("""
<div class="bottom-nav">
    <a href="#sec-inicio" target="_self"><span>🏠</span>Início</a>
    <a href="#sec-patio" target="_self"><span>🚛</span>Pátio</a>
    <a href="#sec-prod" target="_self"><span>🏭</span>Produção</a>
    <a href="#sec-exp" target="_self"><span>🚚</span>Expedição</a>
    <a href="#sec-estoque" target="_self"><span>📦</span>Estoque</a>
    <a href="#sec-frota" target="_self"><span>🚜</span>Frota</a>
</div>
""".replace('\n', ''), unsafe_allow_html=True)
