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

# ==============================================================================
# 🔑 ESTADO DA SESSÃO E NAVEGAÇÃO
# ==============================================================================
if "bafometro_autenticado" not in st.session_state:
    st.session_state.bafometro_autenticado = False

# Gerenciamento da Aba Ativa (SPA - Single Page Application)
if "aba_ativa" not in st.session_state:
    st.session_state.aba_ativa = "inicio"

# Função para mudar de aba chamada pelos botões
def mudar_aba(nova_aba):
    st.session_state.aba_ativa = nova_aba

# ==============================================================================
# 🎨 CSS (TEMA E BOTÕES DA BARRA INFERIOR)
# ==============================================================================
st.markdown(f"""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        #MainMenu, footer, header, [data-testid="stToolbar"] {{ display: none !important; }}
        html, body, [data-testid="stAppViewContainer"], .stApp, .main {{
            background: radial-gradient(ellipse at top, #0c1a33 0%, #070d18 55%, #050911 100%) !important;
        }}
        .block-container {{
            padding-top: 0rem !important; padding-bottom: 5.5rem !important;
            padding-left: 0.8rem !important; padding-right: 0.8rem !important;
            max-width: 560px !important; margin: 0 auto !important;
        }}
        .topo-banner {{ margin: 0 -0.8rem 14px -0.8rem; background: #050d1a; border-bottom: 1px solid #12506e; text-align: center; }}
        .topo-banner img {{ width: 100%; max-height: 130px; object-fit: contain; display: block; margin: 0 auto; }}

        .card-main {{
            background: linear-gradient(180deg, #0b1830 0%, #08111f 100%);
            border: 1.5px solid #12506e; border-radius: 16px; padding: 14px;
            margin-bottom: 14px; box-shadow: 0 0 14px rgba(0, 180, 255, 0.10);
        }}
        .card-head {{ display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }}
        .icon-sq {{ width: 38px; height: 38px; border-radius: 10px; background: #0d2340; border: 1px solid #12506e; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; }}
        .card-title {{ color: #fff; font-size: 1rem; font-weight: 800; text-transform: uppercase; }}
        
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background: linear-gradient(180deg, #0b1830 0%, #08111f 100%) !important;
            border: 1.5px solid #12506e !important; border-radius: 16px !important; margin-bottom: 14px;
        }}
        .conn-dot {{ display: inline-block; width: 14px; height: 14px; border-radius: 50%; margin-right: 10px; }}
        .conn-titulo {{ font-size: 1.15rem; font-weight: 800; }}
        
        details.st-card, div.st-card {{
            --c: #38a9ff; background: #0a1424; background: color-mix(in srgb, var(--c) 9%, #0a1424);
            border: 1.5px solid var(--c); border-left: 6px solid var(--c);
            border-radius: 14px; margin-bottom: 10px; overflow: hidden;
        }}
        details.st-card > summary, div.st-card > .st-sum {{ display: flex; align-items: center; gap: 14px; padding: 12px 14px; cursor: pointer; list-style:none; }}
        details.st-card > summary::-webkit-details-marker {{ display: none; }}
        
        .st-ico {{ width: 52px; height: 52px; border-radius: 50%; border: 2px solid var(--c); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; flex-shrink: 0; background: rgba(255,255,255,0.03); }}
        .st-txt {{ flex: 1; min-width: 0; }}
        .st-title {{ color: #fff; font-weight: 800; font-size: 1.02rem; text-transform: uppercase; }}
        .st-num {{ color: #fff; font-size: 1.9rem; font-weight: 800; line-height: 1.15; }}
        .st-num span {{ font-size: .95rem; font-weight: 400; color: #9fb3cc; }}
        .st-body {{ background: #070d18; padding: 8px 14px 10px 14px; border-top: 1px solid #12304a; }}
        
        .dest-row {{ display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px dashed #1c2b42; font-size: .82rem; }}
        .dest-row .n {{ color: #fff; }}
        .dest-row .v {{ color: #38bdf8; }}
        .dest-row.total {{ border-bottom: none; border-top: 1px solid #12506e; margin-top: 4px; padding-top: 8px; font-weight: 700; }}
        
        .kpi-duo {{ display: flex; align-items: center; background: #070f1d; border: 1.5px solid #12506e; border-radius: 14px; padding: 14px 10px; }}
        .kpi-box {{ flex: 1; display: flex; align-items: center; justify-content: center; gap: 10px; }}
        .kpi-ico {{ font-size: 1.9rem; }}
        .kpi-big {{ color: #fff; font-size: 2.3rem; font-weight: 800; line-height: 1; }}
        .kpi-big.verde {{ color: #00E676; }}
        .kpi-lbl {{ color: #cfe0f5; font-size: .9rem; margin-top: 3px; }}
        .kpi-sep {{ width: 1px; align-self: stretch; background: #12506e; margin: 0 6px; }}
        
        /* BOTTOM NAV FEITO COM STREAMLIT COLUMNS */
        .bottom-nav-container {{
            position: fixed; bottom: 0; left: 50%; transform: translateX(-50%);
            width: 100%; max-width: 560px; z-index: 999990;
            background: #070d18; border-top: 1px solid #12506e;
            padding: 8px 0 calc(8px + env(safe-area-inset-bottom));
        }}
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
    try: s = f"{float(n):,.{casas}f}"
    except: return "0"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

@st.cache_data(ttl=20)
def carregar_dados_nuvem(worksheet_name: str, cabecalho=0):
    sheet_encoded = urllib.parse.quote(worksheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_encoded}&headers=1"
    try:
        df = pd.read_csv(url, header=cabecalho)
        return df.dropna(how="all", axis=1).dropna(how="all", axis=0)
    except: return pd.DataFrame()

def safe_to_numeric(val):
    if pd.isna(val) or val == "" or val is None: return 0.0
    if isinstance(val, (int, float)): return float(val)
    try: return float(str(val).strip().replace(".", "").replace(",", "."))
    except: return 0.0

def classificar_kpi(valor, tipo):
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
df_patio = carregar_dados_nuvem("Patio_Destino_Status", cabecalho=None) # Busca crua para não perder o cabeçalho
df_balanco = carregar_dados_nuvem("Balanco_Expedicao_Destino", cabecalho=None)
df_virada = carregar_dados_nuvem("Status_Virada_Turnos", cabecalho=0)
df_cache = carregar_dados_nuvem("Cache_Painel", cabecalho=0)

cache_dict = {str(row.iloc[0]).strip(): str(row.iloc[1]).strip() for _, row in df_cache.iterrows()} if not df_cache.empty else {}
dados_segregados = ast.literal_eval(cache_dict.get("dados_segregados", "{}")) if cache_dict.get("dados_segregados") else {}

vol_hoje = vol_ontem = prev_carr = prod_hoje = prev_prod = estoque_total = 0
status_transbordo = ritmo_torre = "NORMAL"

if not df_dash.empty:
    row_d = df_dash.iloc[0]
    ultima_att = str(row_d.get("DATA_HORA", ""))
    vol_hoje = forcar_par(safe_to_numeric(row_d.get("EXPEDICAO_HOJE", 0)))
    vol_ontem = forcar_par(safe_to_numeric(row_d.get("EXPEDICAO_ONTEM", 0)))
    prod_hoje = forcar_par(safe_to_numeric(row_d.get("PRODUCAO_HOJE", 0)))
    prev_prod = forcar_par(safe_to_numeric(row_d.get("PREV_PRODUCAO", 0)))
    estoque_total = forcar_par(safe_to_numeric(row_d.get("ESTOQUE_TOTAL", 0)))
    status_transbordo = str(row_d.get("STATUS_TRANSBORDO", "NORMAL"))
    ritmo_torre = str(row_d.get("RITMO_TORRE", "NORMAL"))

# Lógica de conexão
try: dt_att = datetime.strptime(ultima_att[:19], "%d/%m/%Y %H:%M:%S")
except: dt_att = agora_br

minutos_inativos = (agora_br - dt_att).total_seconds() / 60.0
conn_txt, conn_cor = ("CONECTADO", "#00D672") if minutos_inativos <= 15 else ("DESCONECTADO", "#E74C3C")
conn_hora = dt_att.strftime("%H:%M:%S") if dt_att.date() == hoje_date else dt_att.strftime("%d/%m %H:%M")

# ==============================================================================
# 🎨 TOPO: BANNER
# ==============================================================================
st.markdown(f'<div class="topo-banner"><img src="{BANNER_TOPO_URL}"></div>', unsafe_allow_html=True)

# ==============================================================================
# 📱 GERENCIADOR DE TELAS (ABAS)
# ==============================================================================

# ------------------------------------------------------------------------------
# TELA 1: INÍCIO (DASHBOARD & ALERTAS)
# ------------------------------------------------------------------------------
if st.session_state.aba_ativa == "inicio":
    with st.container(border=True):
        c1, c2 = st.columns([3, 2], vertical_alignment="center")
        with c1:
            st.markdown(f'<div style="display:flex; align-items:center;"><span class="conn-dot" style="background:{conn_cor};"></span><span class="conn-titulo" style="color:{conn_cor};">{conn_txt}</span></div><div class="conn-sub" style="color:#94a3b8; font-size:12px;">🕒 Última att: {conn_hora}</div><div class="conn-ritmo" style="color:#38bdf8; font-size:12px; font-weight:bold;">🎯 {ritmo_torre}</div>', unsafe_allow_html=True)
        with c2:
            if st.button("🔄 Atualizar", use_container_width=True):
                st.cache_data.clear(); st.rerun()

    # Tratamento da Aba Mobile_Alertas
    if not df_alertas.empty:
        html_al = f'<div class="card-main"><div class="card-head"><div class="icon-sq">🔔</div><div class="card-title">Notificações</div></div><div class="notif-lista">'
        for _, ra in df_alertas.head(5).iterrows():
            n = str(ra.get("NIVEL", "NORMAL")).upper()
            t = str(ra.get("ALERTA", "")).strip()
            dh = str(ra.get("DATA_HORA", "")).strip()
            hora = dh.split(" ")[1][:5] if " " in dh else "--:--"
            cor, bg, ico = ("#E74C3C", "rgba(231,76,60,.18)", "🚨") if n == "CRITICO" else ("#FFD600", "rgba(255,214,0,.16)", "⚠") if n == "ATENCAO" else ("#00D672", "rgba(0,214,114,.16)", "✅")
            t_limpo = re.sub(r'^[^\w\[\(]+', '', t)
            html_al += f'<div class="notif-item"><div class="notif-ico" style="background:{bg}; color:{cor};">{ico}</div><div class="notif-txt"><div class="notif-tit" style="color:{cor}">{n}</div><div class="notif-desc" style="color:#cbd5e1; font-size:12px;">{html_lib.escape(t_limpo)}</div></div><div class="notif-hora" style="color:#94a3b8; font-size:11px;">{hora}</div></div>'
        html_al += "</div></div>"
        st.markdown(html_al, unsafe_allow_html=True)
    else:
        st.info("Nenhuma notificação recente.")

# ------------------------------------------------------------------------------
# TELA 2: PÁTIO DE VEÍCULOS
# ------------------------------------------------------------------------------
elif st.session_state.aba_ativa == "patio":
    STATUS_COLS = {"PR": ["PR_VEIC", "PR_TON"], "00": ["00_VEIC", "00_TON"], "01": ["01_VEIC", "01_TON"], "FC": ["FC_VEIC", "FC_TON"]}
    dados_p = {k: {"v": 0, "p": 0, "lista": []} for k in STATUS_COLS}
    
    # TR vem do dashboard
    tr_v = int(safe_to_numeric(df_dash.iloc[0].get("TR_VEIC", 0))) if not df_dash.empty else 0
    tr_p = forcar_par(safe_to_numeric(df_dash.iloc[0].get("TR_TON", 0))) if not df_dash.empty else 0

    # Busca no array crú do DataFrame de Patio (ignora as linhas iniciais)
    cabecalho_idx = -1
    for i in range(min(10, len(df_patio))):
        if str(df_patio.iloc[i, 0]).strip().upper() == "DESTINO":
            cabecalho_idx = i
            break
            
    if cabecalho_idx != -1:
        cols_nome = [str(c).strip().upper() for c in df_patio.iloc[cabecalho_idx].values]
        df_p = df_patio.iloc[cabecalho_idx+1:].copy()
        df_p.columns = cols_nome
        
        for _, l in df_p.iterrows():
            dn = str(l.get("DESTINO", "")).strip()
            if not dn or dn == "NAN": continue
            if "TOTAL" in dn.upper(): continue # Pula a linha de total, somaremos na mão
            
            for ch, (cv, ct) in STATUS_COLS.items():
                v = int(safe_to_numeric(l.get(cv, 0)))
                t = forcar_par(safe_to_numeric(l.get(ct, 0)))
                if v > 0 or t > 0:
                    dados_p[ch]["lista"].append({"d": dn, "v": v, "t": t})
                    dados_p[ch]["v"] += v
                    dados_p[ch]["p"] += t

    tvf = dados_p["00"]["v"] + dados_p["01"]["v"] + dados_p["FC"]["v"]
    vpd = forcar_par(dados_p["00"]["p"] + dados_p["01"]["p"] + dados_p["FC"]["p"])

    st.markdown(f'<div class="card-main"><div class="card-head"><div class="icon-sq">🏭</div><div class="card-title">Pátio (Tempo Real)</div></div><div class="kpi-duo"><div class="kpi-box"><div class="kpi-ico">🚚</div><div><div class="kpi-big">{tvf}</div><div class="kpi-lbl">Veículos Físicos</div><div class="kpi-sub" style="color:#64748b; font-size:10px;">Checklist + Apoio + Fila</div></div></div><div class="kpi-sep"></div><div class="kpi-box"><div class="kpi-ico">📦</div><div><div class="kpi-lbl">Carga Disponível</div><div class="kpi-big verde">{fmt(vpd)} <span style="font-size:16px;">t</span></div></div></div></div></div>', unsafe_allow_html=True)

    h_p = ""
    for tit, chv, cor, ico in [("Prog/Chegando", "PR", "#38a9ff", "🚙"), ("Checklist", "00", "#FFD600", "📋"), ("Apoio", "01", "#E67E22", "🚛"), ("Fila de Carreg.", "FC", "#00D672", "✅")]:
        h_linhas = ""
        if dados_p[chv]["lista"]:
            for i in dados_p[chv]["lista"]:
                h_linhas += f'<div class="dest-row"><span class="n" style="color:#e2e8f0;">{html_lib.escape(i["d"])}</span><span class="v" style="color:#38bdf8;">{i["v"]} veíc. <small style="color:#94a3b8;">({fmt(i["t"])} t)</small></span></div>'
            h_linhas += f'<div class="dest-row total" style="border-top:1px solid #12506e; margin-top:8px; padding-top:8px;"><span class="n" style="font-weight:bold; color:#fff;">TOTAL</span><span class="v" style="font-weight:bold; color:#38bdf8;">{dados_p[chv]["v"]} veíc. <small style="color:#94a3b8;">({fmt(dados_p[chv]["p"])} t)</small></span></div>'
        else:
            h_linhas = '<div style="color:#64748b; font-size:12px; padding:8px 0;">Nenhum veículo neste status.</div>'
            
        h_p += f'<details class="st-card" style="--c:{cor}; background-color:#0a1424; border:1px solid {cor}; border-left:6px solid {cor}; border-radius:12px; margin-bottom:12px; padding:4px;"><summary style="display:flex; align-items:center; cursor:pointer;"><div class="st-ico" style="font-size:24px; padding:10px;">{ico}</div><div class="st-txt" style="margin-left:12px; flex:1;"><div class="st-title" style="color:#fff; font-weight:bold;">{tit}</div><div class="st-num" style="color:#fff; font-size:24px; font-weight:bold;">{dados_p[chv]["v"]} <span style="font-size:14px; color:#94a3b8;">veíc. / {fmt(dados_p[chv]["p"])} t</span></div></div></summary><div class="st-body" style="background-color:#070d18; border-top:1px solid #1c2b42; padding:12px; margin-top:8px;">{h_linhas}</div></details>'

    h_p += f'<div class="st-card" style="--c:#95A5A6; background-color:#0a1424; border:1px solid #95A5A6; border-left:6px solid #95A5A6; border-radius:12px; margin-bottom:12px; padding:14px;"><div style="display:flex; align-items:center;"><div class="st-ico" style="font-size:24px; padding:10px;">📄</div><div class="st-txt" style="margin-left:12px; flex:1;"><div class="st-title" style="color:#fff; font-weight:bold;">Termo SAP</div><div class="st-num" style="color:#fff; font-size:24px; font-weight:bold;">{tr_v} <span style="font-size:14px; color:#94a3b8;">veíc. / {fmt(tr_p)} t</span></div></div><div style="color:#64748b; font-size:11px; text-align:right;">Fila de<br>Faturamento</div></div></div>'
    
    st.markdown(h_p, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TELA 3: PRODUÇÃO E MÁQUINAS
# ------------------------------------------------------------------------------
elif st.session_state.aba_ativa == "producao":
    st.markdown(f'<div class="card-main" style="text-align:center;"><div style="color:#E5B800; font-size:14px; font-weight:bold;">PRODUÇÃO DE CELULOSE (HOJE)</div><div style="font-size:36px; font-weight:bold; color:#fff;">{fmt(prod_hoje)} <span style="font-size:16px; color:#64748b;">TON</span></div></div>', unsafe_allow_html=True)
    
    for maq in ["MS1", "MS2"]:
        qd = {}
        if not df_qual.empty:
            for _, rq in df_qual.iterrows():
                if str(rq.get("MAQUINA", "")).strip().upper() == maq:
                    qd = {"mat": str(rq.get("MATERIAL", "--")), "alv": safe_to_numeric(rq.get("ALVURA", 0)), "suj": safe_to_numeric(rq.get("SUJIDADE", 0)), "vis": safe_to_numeric(rq.get("VISCOSIDADE", 0)), "ph": safe_to_numeric(rq.get("PH", 0)), "prod": forcar_par(safe_to_numeric(rq.get("PROD_TOTAL", 0))), "l1": forcar_par(safe_to_numeric(rq.get("PROD_LINHA_1", 0))), "l2": forcar_par(safe_to_numeric(rq.get("PROD_LINHA_2", 0))), "desc": str(rq.get("DESCLASSIFICANDO", "NAO")).upper() == "SIM"}
                    break
        if qd:
            ca, cs, cv, cp = classificar_kpi(qd['alv'], "alvura"), classificar_kpi(qd['suj'], "sujidade"), classificar_kpi(qd['vis'], "viscosidade"), classificar_kpi(qd['ph'], "ph")
            cb = "#E74C3C" if qd['desc'] else "#1c2b42"
            
            st.markdown(f"""
            <div style='background-color:#0a101d; border:1.5px solid {cb}; border-radius:12px; padding:16px; margin-bottom:12px;'>
                <div style='display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1c2b42; padding-bottom:8px; margin-bottom:12px;'>
                    <span style='color:#ffffff; font-weight:bold; font-size:18px;'>⚙️ {maq}</span>
                    <span style='color:#FF9F1C; font-weight:bold; font-size:16px;'>MAT: {qd['mat']}</span>
                    <span style='color:#38bdf8; font-weight:bold; font-size:18px;'>{fmt(qd['prod'])} t</span>
                </div>
                <div style='display:flex; justify-content:space-between; text-align:center;'>
                    <div><div style='font-size:10px; color:#64748b; font-weight:bold;'>ALVURA</div><div style='font-size:16px; font-weight:bold; color:{ca};'>{fmt(qd['alv'], 2)}%</div></div>
                    <div><div style='font-size:10px; color:#64748b; font-weight:bold;'>SUJIDADE</div><div style='font-size:16px; font-weight:bold; color:{cs};'>{fmt(qd['suj'], 2)}</div></div>
                    <div><div style='font-size:10px; color:#64748b; font-weight:bold;'>VISCOSID.</div><div style='font-size:16px; font-weight:bold; color:{cv};'>{fmt(qd['vis'])}</div></div>
                    <div><div style='font-size:10px; color:#64748b; font-weight:bold;'>pH</div><div style='font-size:16px; font-weight:bold; color:{cp};'>{fmt(qd['ph'], 1)}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TELA 4: EXPEDIÇÃO DIÁRIA E BALANÇO
# ------------------------------------------------------------------------------
elif st.session_state.aba_ativa == "expedicao":
    st.markdown(f'<div class="card-main" style="text-align:center;"><div style="color:#00D672; font-size:14px; font-weight:bold;">EXPEDIÇÃO REALIZADA (HOJE)</div><div style="font-size:36px; font-weight:bold; color:#fff;">{fmt(vol_hoje)} <span style="font-size:16px; color:#64748b;">TON</span></div><div style="font-size:12px; color:#94a3b8;">Fechamento de Ontem: {fmt(vol_ontem)} t</div></div>', unsafe_allow_html=True)
    
    # Lógica de Destinos 
    bd_list = []
    tm_exp, tr_exp = 0.0, 0.0
    cab_balanco = -1
    for i in range(min(10, len(df_balanco))):
        if str(df_balanco.iloc[i, 0]).strip().upper() == "DESTINO":
            cab_balanco = i
            break
            
    if cab_balanco != -1:
        df_b = df_balanco.iloc[cab_balanco+1:].copy()
        df_b.columns = [str(c).strip().upper() for c in df_balanco.iloc[cab_balanco].values]
        
        for _, r in df_b.iterrows():
            dn = str(r.get("DESTINO", "")).strip()
            if not dn or dn == "NAN": continue
            mv, rv, sv = forcar_par(safe_to_numeric(r.get("META_DIA_T",0))), forcar_par(safe_to_numeric(r.get("EXPEDIDO_ZLE_T",0))), forcar_par(safe_to_numeric(r.get("SALDO_A_EXPEDIR_T",0)))
            try: av = float(str(r.get("ATINGIMENTO_%",0)).replace('%','').replace(',','.'))
            except: av = 0.0
            
            if "TOTAL" in dn.upper(): tm_exp, tr_exp = mv, rv
            else:
                nm = "MI / LATAM" if "MI" in dn.upper() or "LATAM" in dn.upper() else (f"{dn.split('-')[0].strip()} - {dn.split('-')[1].strip()}" if "-" in dn else dn)
                bd_list.append({"d": nm, "m": mv, "r": rv, "s": sv, "a": av})
                
    if bd_list:
        bd_list.sort(key=lambda x: 99999 if "MI" in x['d'] else (int(re.search(r'\d+', x['d']).group()) if re.search(r'\d+', x['d']) else 0), reverse=True)
        h_b = "<div style='background-color:#0a101d; border:1px solid #1c2b42; border-radius:12px; padding:12px;'><div style='font-size:14px; font-weight:bold; color:#fff; margin-bottom:12px; border-bottom:1px solid #1c2b42; padding-bottom:8px;'>📍 BALANÇO POR DESTINO</div>"
        
        for d in bd_list:
            ca = "#00D672" if d['a'] >= 100 else ("#38bdf8" if d['a'] > 0 else "#64748b")
            h_b += f"<div style='display:flex; justify-content:space-between; margin-bottom:8px; border-bottom:1px dashed #1c2b42; padding-bottom:8px;'><div style='color:#e2e8f0; font-size:13px; font-weight:bold;'>{d['d']}</div><div style='text-align:right;'><span style='color:#38bdf8; font-size:12px; margin-right:8px;'>M: {fmt(d['m'])}t</span><span style='color:#00D672; font-size:12px; margin-right:8px;'>R: {fmt(d['r'])}t</span><span style='color:{ca}; font-size:12px; font-weight:bold;'>{d['a']:.0f}%</span></div></div>"
        h_b += "</div>"
        st.markdown(h_b, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TELA 5: ESTOQUE E MATERIAL
# ------------------------------------------------------------------------------
elif st.session_state.aba_ativa == "estoque":
    st.markdown(f'<div class="card-main" style="text-align:center;"><div style="color:#9b59b6; font-size:14px; font-weight:bold;">ESTOQUE FÍSICO ARMAZÉM</div><div style="font-size:36px; font-weight:bold; color:#fff;">{fmt(estoque_total)} <span style="font-size:16px; color:#64748b;">TON</span></div></div>', unsafe_allow_html=True)
    
    if dados_segregados:
        h_seg = "<div style='display:flex; flex-wrap:wrap; gap:10px; justify-content:center;'>"
        for m, t in sorted(dados_segregados.items(), key=lambda x: x[1], reverse=True):
            cb = "#00D672" if "EQ" in m.upper() else "#38bdf8"
            h_seg += f"<div style='flex:1; min-width:45%; background-color:#0a101d; border:1px solid #1c2b42; border-radius:12px; padding:16px; text-align:center;'><div style='font-size:14px; color:#94a3b8; font-weight:bold;'>{m.upper()}</div><div style='font-size:22px; font-weight:bold; color:{cb}; margin-top:4px;'>{fmt(t)} t</div></div>"
        h_seg += "</div>"
        st.markdown(h_seg, unsafe_allow_html=True)
    else:
        st.info("Aguardando leitura do material do SAP...")

# ------------------------------------------------------------------------------
# TELA 6: FROTA LOGADA HOJE
# ------------------------------------------------------------------------------
elif st.session_state.aba_ativa == "frota":
    st.markdown(f'<div class="card-main" style="text-align:center;"><div style="color:#E67E22; font-size:14px; font-weight:bold;">FROTA EM OPERAÇÃO (HOJE)</div></div>', unsafe_allow_html=True)
    st.info("Navegação de Frota Ativa.") # Pode incluir a mesma lógica de histórico depois


# ==============================================================================
# 🧭 NAVEGAÇÃO INFERIOR ESTRITA (BOTTOM NAV MENU)
# ==============================================================================
st.markdown("""
<div class="bottom-nav-container">
    <div style="display:flex; justify-content:space-around; width:100%;">
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    if st.button("🏠", key="nav_inicio", help="Início", use_container_width=True): mudar_aba("inicio"); st.rerun()
with col2:
    if st.button("🚛", key="nav_patio", help="Pátio", use_container_width=True): mudar_aba("patio"); st.rerun()
with col3:
    if st.button("🏭", key="nav_prod", help="Produção", use_container_width=True): mudar_aba("producao"); st.rerun()
with col4:
    if st.button("🚚", key="nav_exp", help="Expedição", use_container_width=True): mudar_aba("expedicao"); st.rerun()
with col5:
    if st.button("📦", key="nav_est", help="Estoque", use_container_width=True): mudar_aba("estoque"); st.rerun()
with col6:
    if st.button("🚜", key="nav_frota", help="Frota", use_container_width=True): mudar_aba("frota"); st.rerun()

st.markdown("</div></div>", unsafe_allow_html=True)
