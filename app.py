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

# 1. 👈 IMPORTA O REFRESHER
from streamlit_autorefresh import st_autorefresh

# URL direta da logo no seu GitHub para funcionar como ícone da tela inicial
LOGO_ALOVE_URL = "https://raw.githubusercontent.com/cris2026/A.L.O.V.E-/main/logo_alove.png"

st.set_page_config(
    page_title="A.L.O.V.E. Mobile",
    page_icon="🚛",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 👈 INICIA O CRONÔMETRO INVISÍVEL (60.000 milissegundos = 1 minuto)
st_autorefresh(interval=60000, limit=None, key="refresh_mobile")

# ==============================================================================
# 🔑 CONTROLE DE ACESSO - BAFÔMETRO
# ==============================================================================
SENHA_BAFOMETRO = "alove2026"  # 👈 Altere para a senha que preferir

if "bafometro_autenticado" not in st.session_state:
    st.session_state.bafometro_autenticado = False

# ==============================================================================
# 📱 INJEÇÃO DE METATAGS (PWA / APP NATIVO / TELA CHEIA)
# ==============================================================================
st.markdown(f"""
    <!-- Força exibição como App Nativo em iOS (Safari) -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="A.L.O.V.E.">
    <link rel="apple-touch-icon" href="{LOGO_ALOVE_URL}">
    
    <!-- Força exibição como App Nativo em Android (Chrome) -->
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#0a101d">
    <link rel="icon" type="image/png" href="{LOGO_ALOVE_URL}">
    <link rel="manifest" href="https://raw.githubusercontent.com/cris2026/A.L.O.V.E-/main/manifest.json">
    
    <!-- Evita zoom indesejado por toque acidental e trava a proporção mobile -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
""", unsafe_allow_html=True)

# ==============================================================================
# 🎨 CSS AVANÇADO (NOVO LAYOUT DOS CARDS + CABEÇALHO FIXO + REMOÇÃO MARCAS)
# ==============================================================================
st.markdown("""
    <style>
        /* ELIMINA O CONTORNO E AS BORDAS BRANCAS DO MODO EMBED */
        html, body, [data-testid="stAppViewContainer"], .stApp, .main {
            background-color: #0a101d !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
        }

        /* MATA O CABEÇALHO, RODAPÉ E MENU DO STREAMLIT */
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important; display: none !important;}
        header {visibility: hidden !important; display: none !important;}
        
        /* MATA OS BOTÕES FLUTUANTES DA NUVEM (Manage App, GitHub, etc) */
        [data-testid="manage-app-button"] {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        [data-testid="stDecoration"] {display: none !important;}
        [data-testid="stHeader"] {display: none !important;}
        .viewerBadge_container__1QSob {display: none !important;}
        .viewerBadge_link__1S137 {display: none !important;}
        
        /* MATA A ÁREA EM BRANCO NO FUNDO */
        .stAppBottom {display: none !important;}
        .stApp > header {display: none !important;}

        /* EXPULSA AS MARGENS PARA OCUPAR A TELA TODA NO CELULAR */
        .block-container {
            padding-top: 0.2rem !important;
            padding-bottom: 1rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            max-width: 100% !important;
        }

        /* 📌 CABEÇALHO FIXO NO TOPO (LOGO + ATUALIZAR) */
        .cabecalho-fixo {
            position: -webkit-sticky !important;
            position: sticky !important;
            top: 0 !important;
            z-index: 999999 !important;
            background-color: #0a101d !important;
            padding-top: 6px !important;
            padding-bottom: 8px !important;
            margin-bottom: 12px !important;
            border-bottom: 1px solid #1c2b42 !important;
        }
        
        input[type="radio"] { display: none; }
        
        .prev-container { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px; }
        .prev-card-prod { background-color: #05080f; border: 2px solid #00f3ff; border-radius: 8px; padding: 10px; box-shadow: 0 0 8px rgba(0, 243, 255, 0.15); }
        .prev-card-prod .prev-title { color: #00f3ff; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; margin-bottom: 4px; }
        .prev-card-prod .prev-val { color: #ffffff; font-size: 1.4rem; font-weight: bold; line-height: 1.1; margin-bottom: 2px; }
        
        .prev-card-carr { background-color: #05080f; border: 2px solid #ff7700; border-radius: 8px; padding: 10px; box-shadow: 0 0 8px rgba(255, 119, 0, 0.15); }
        .prev-card-carr .prev-title { color: #ff7700; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; margin-bottom: 4px; }
        .prev-card-carr .prev-val { color: #ffffff; font-size: 1.4rem; font-weight: bold; line-height: 1.1; margin-bottom: 2px; }

        summary { list-style: none; outline: none; }
        summary::-webkit-details-marker { display: none; }

        details.master-box { background-color: #0a101d; border-radius: 8px; margin-bottom: 12px; border: 1px solid #1c2b42; border-left: 6px solid; overflow: hidden; }
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
        .master-content { background-color: #0a101d; padding: 0 16px 16px 16px; }

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

        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
""", unsafe_allow_html=True)

SHEET_ID = "10FluiIwlynIlPDA74QI8mpHSIrAc-62H1hZNRBsvfCA"

def forcar_par(valor):
    val_int = int(round(float(valor or 0)))
    if val_int % 2 != 0:
        val_int += 1
    return val_int

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
df_dash = carregar_dados_nuvem("Mobile_Dashboard", cabecalho=0)
df_qual = carregar_dados_nuvem("Mobile_Qualidade", cabecalho=0)
df_alertas = carregar_dados_nuvem("Mobile_Alertas", cabecalho=0)
df_cache = carregar_dados_nuvem("Cache_Painel", cabecalho=0)
df_patio_dest = carregar_dados_nuvem("Patio_Destino_Status", cabecalho=2)
df_status_virada = carregar_dados_nuvem("Status_Virada_Turnos", cabecalho=0)
df_balanco_dest = carregar_dados_nuvem("Balanco_Expedicao_Destino", cabecalho=2)
df_bafometro = carregar_dados_nuvem("Bafometro_Status", cabecalho=0)
if df_bafometro.empty:
    df_bafometro = carregar_dados_nuvem("Auditoria_Bafometro", cabecalho=0)

cache_dict = {str(row.iloc[0]).strip(): str(row.iloc[1]).strip() for _, row in df_cache.iterrows()} if not df_cache.empty else {}
dados_segregados = parse_robusto(cache_dict.get("dados_segregados", "{}"))

ultima_att = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
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
    ultima_att = str(row_d.get("DATA_HORA", ultima_att))
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
# 🎯 CORREÇÃO V6: MAPEAMENTO SEGURO DE COLUNAS E TOTAIS (PÁTIO)
# ==============================================================================
destinos_por_status = {
    "PR": [], "00": [], "01": [], "FC": [], "TR": []
}

dados_patio = {
    "PR": {"veiculos": 0, "peso": 0},
    "00": {"veiculos": 0, "peso": 0},
    "01": {"veiculos": 0, "peso": 0},
    "FC": {"veiculos": 0, "peso": 0},
    "TR": {"veiculos": 0, "peso": 0}
}

if not df_patio_dest.empty:
    def get_col_idx(nome_procurado):
        for i, col in enumerate(df_patio_dest.columns):
            if nome_procurado in str(col).upper():
                return i
        for i, val in enumerate(df_patio_dest.iloc[0]):
            if nome_procurado in str(val).upper():
                return i
        return -1

    idx_pr_v = get_col_idx("PR_VEIC")
    idx_pr_t = get_col_idx("PR_TON")
    idx_00_v = get_col_idx("00_VEIC")
    idx_00_t = get_col_idx("00_TON")
    idx_01_v = get_col_idx("01_VEIC")
    idx_01_t = get_col_idx("01_TON")
    idx_fc_v = get_col_idx("FC_VEIC")
    idx_fc_t = get_col_idx("FC_TON")

    if idx_pr_v == -1: idx_pr_v = 1
    if idx_pr_t == -1: idx_pr_t = 2
    if idx_00_v == -1: idx_00_v = 3
    if idx_00_t == -1: idx_00_t = 4
    if idx_01_v == -1: idx_01_v = 5
    if idx_01_t == -1: idx_01_t = 6
    if idx_fc_v == -1: idx_fc_v = 7
    if idx_fc_t == -1: idx_fc_t = 8

    for idx in range(len(df_patio_dest)):
        try:
            linha = df_patio_dest.iloc[idx]
            dest_nome = str(linha.iloc[0]).strip()
            
            if not dest_nome or dest_nome.upper() in ["NAN", "NONE", "DESTINO", "TOTAL", ""]:
                continue
                
            if "TOTAL GERAL FÁBRICA" in dest_nome.upper():
                dados_patio["PR"]["veiculos"] = int(safe_to_numeric(linha.iloc[idx_pr_v]))
                dados_patio["PR"]["peso"] = forcar_par(safe_to_numeric(linha.iloc[idx_pr_t]))
                dados_patio["00"]["veiculos"] = int(safe_to_numeric(linha.iloc[idx_00_v]))
                dados_patio["00"]["peso"] = forcar_par(safe_to_numeric(linha.iloc[idx_00_t]))
                dados_patio["01"]["veiculos"] = int(safe_to_numeric(linha.iloc[idx_01_v]))
                dados_patio["01"]["peso"] = forcar_par(safe_to_numeric(linha.iloc[idx_01_t]))
                dados_patio["FC"]["veiculos"] = int(safe_to_numeric(linha.iloc[idx_fc_v]))
                dados_patio["FC"]["peso"] = forcar_par(safe_to_numeric(linha.iloc[idx_fc_t]))
                continue
            
            pr_v = int(safe_to_numeric(linha.iloc[idx_pr_v]))
            pr_t = forcar_par(safe_to_numeric(linha.iloc[idx_pr_t]))
            if pr_v > 0 or pr_t > 0:
                destinos_por_status["PR"].append({"destino": dest_nome, "veic": pr_v, "ton": pr_t})

            v00 = int(safe_to_numeric(linha.iloc[idx_00_v]))
            t00 = forcar_par(safe_to_numeric(linha.iloc[idx_00_t]))
            if v00 > 0 or t00 > 0:
                destinos_por_status["00"].append({"destino": dest_nome, "veic": v00, "ton": t00})

            v01 = int(safe_to_numeric(linha.iloc[idx_01_v]))
            t01 = forcar_par(safe_to_numeric(linha.iloc[idx_01_t]))
            if v01 > 0 or t01 > 0:
                destinos_por_status["01"].append({"destino": dest_nome, "veic": v01, "ton": t01})

            vfc = int(safe_to_numeric(linha.iloc[idx_fc_v]))
            tfc = forcar_par(safe_to_numeric(linha.iloc[idx_fc_t]))
            if vfc > 0 or tfc > 0:
                destinos_por_status["FC"].append({"destino": dest_nome, "veic": vfc, "ton": tfc})

        except Exception as e:
            continue

# O Termo SAP continua sendo lido do Dashboard
v_qtd_tr = int(safe_to_numeric(df_dash.iloc[0].get("TR_VEIC", 0))) if not df_dash.empty else 0
v_ton_tr = forcar_par(safe_to_numeric(df_dash.iloc[0].get("TR_TON", 0))) if not df_dash.empty else 0
dados_patio["TR"]["veiculos"] = v_qtd_tr
dados_patio["TR"]["peso"] = v_ton_tr

total_veiculos_fisicos = dados_patio["00"]["veiculos"] + dados_patio["01"]["veiculos"] + dados_patio["FC"]["veiculos"]
vol_patio_disponivel = forcar_par(dados_patio["00"]["peso"] + dados_patio["01"]["peso"] + dados_patio["FC"]["peso"])

# Mapeamento do Status Virada de Linha
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

# Extração do Balanço de Expedição por Destino
balanco_destinos = []
total_expedicao_meta = 0.0
total_expedicao_real = 0.0

if not df_balanco_dest.empty:
    for _, r_b in df_balanco_dest.iterrows():
        dest_nome = str(r_b.get("DESTINO", r_b.iloc[0])).strip()
        if not dest_nome or dest_nome.upper() in ["NAN", "NONE", "DESTINO"]: continue
        
        meta_val = forcar_par(safe_to_numeric(r_b.get("META_DIA_T", r_b.iloc[1])))
        real_val = forcar_par(safe_to_numeric(r_b.get("EXPEDIDO_ZLE_T", r_b.iloc[2])))
        saldo_val = forcar_par(safe_to_numeric(r_b.get("SALDO_A_EXPEDIR_T", r_b.iloc[3])))
        
        try: ating_val = float(str(r_b.get("ATINGIMENTO_%", r_b.iloc[4])).replace('%', '').replace(',', '.'))
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
# 📌 CABEÇALHO SUPERIOR FIXO (STICKY) E PREVISÕES
# ==============================================================================
st.markdown('<div class="cabecalho-fixo">', unsafe_allow_html=True) # 👈 AQUI ABRE O CABEÇALHO FIXO

col_logo, col_status, col_btn = st.columns([3.5, 2.5, 1.2], vertical_alignment="center")

with col_logo:
    try:
        st.image("logo_alove.png", use_container_width=True)
    except:
        st.markdown("<h3 style='margin:0; color:#00f3ff; font-style:italic; font-weight: normal;'>A.L.O.V.E.</h3>", unsafe_allow_html=True)

with col_status:
    st.markdown(f"""
        <div style="text-align: right;">
            <div style="color: #00D672; font-size: 0.85rem; font-weight: normal; display: flex; justify-content: flex-end; align-items: center; gap: 6px;">
                <span style="font-size: 1.1rem;">🎯</span> {ritmo_torre}
            </div>
            <div style="color: #94a3b8; font-size: 0.7rem; font-weight: normal; margin-top: 2px;">
                Sincronizado: {ultima_att}
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_btn:
    if st.button("🔄 Atualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True) # 👈 AQUI FECHA O CABEÇALHO FIXO
# Removemos o st.markdown("<br>") que estava aqui para o corte do topo ficar perfeito

html_previsoes = f"""
<div class="prev-container">
    <div class="prev-card-prod">
        <div class="prev-title">📈 Prev. Produção</div>
        <div class="prev-val">{prev_prod:,.0f} <span style="font-size:0.9rem; color:#64748b;">t</span></div>
    </div>
    <div class="prev-card-carr">
        <div class="prev-title">🎯 Prev. Expedição</div>
        <div class="prev-val">{prev_carr:,.0f} <span style="font-size:0.9rem; color:#64748b;">t</span></div>
    </div>
</div>
"""
st.markdown(html_previsoes, unsafe_allow_html=True)

if not df_alertas.empty:
    linhas_alt = []
    tem_critico = False
    for _, alt_row in df_alertas.iterrows():
        txt_alt = str(alt_row.get("ALERTA", "")).strip()
        nv_alt = str(alt_row.get("NIVEL", "")).strip().upper()
        if txt_alt and "Normal" not in txt_alt:
            linhas_alt.append(f"• {txt_alt}")
            if nv_alt == "CRITICO": tem_critico = True

    if linhas_alt:
        cor_b = "#E74C3C" if tem_critico else "#FF9F1C"
        bg_b = "#2b1111" if tem_critico else "#24180d"
        txt_cor = "#ff9999" if tem_critico else "#ffd299"
        corpo_alt = "<br>".join(linhas_alt[:4])
        st.markdown(f"""
            <div style="background-color: {bg_b}; border-left: 4px solid {cor_b}; padding: 10px 14px; margin-bottom: 12px; border-radius: 6px;">
                <div style="color: {cor_b}; font-size: 11px; font-weight: normal; text-transform: uppercase;">🚨 Observações & Alertas Críticos</div>
                <div style="color: {txt_cor}; font-size: 12px; font-weight: normal; margin-top: 4px;">{corpo_alt}</div>
            </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# 📦 BLOCO 1: PÁTIO DE VEÍCULOS (EXPANSÍVEL POR DESTINOS)
# ==============================================================================
html_patio = '<details class="master-box" style="border-left-color: #38bdf8;" open>'
html_patio += f'''
<summary>
    <div class="header-layout">
        <div class="icon-box" style="background-color: rgba(56, 189, 248, 0.15); color: #38bdf8;">🚛</div>
        <div class="master-metric-title">Pátio da Fábrica (Tempo Real)</div>
    </div>
    <div class="value-layout">
        <div class="master-metric-val">{total_veiculos_fisicos}</div>
        <div class="master-metric-unit">Veículos Físicos</div>
    </div>
    <div class="master-metric-sub" style="color: #38bdf8;">Carga Disponível: {vol_patio_disponivel:,.0f} t</div>
</summary>
<div class="master-content">
    <div style="display:flex; flex-direction:column; gap:8px; padding-top:16px;">
'''

blocos_patio = [
    ("🚙 Prog/Chegando", "PR", "#3498DB"),
    ("📋 Checklist", "00", "#E5B800"),
    ("🚛 Apoio", "01", "#E67E22"),
    ("✅ Fila de Carregamento", "FC", "#00D672")
]

for tit, chv, cor in blocos_patio:
    lista_destinos = destinos_por_status.get(chv, [])
    
    v_qtd = dados_patio.get(chv, {}).get("veiculos", 0)
    v_ton = dados_patio.get(chv, {}).get("peso", 0)

    linhas_dest_html = ""
    if lista_destinos:
        for item in lista_destinos:
            linhas_dest_html += f"""
            <div style="display:flex; justify-content:space-between; align-items:center; padding:5px 0; border-bottom:1px dashed #1c2b42; font-size:0.8rem;">
                <span style="color:#ffffff; font-weight:normal;">{item['destino']}</span>
                <span style="color:#38bdf8; font-weight:normal;">{item['veic']} veíc. <span style="color:#64748b; font-weight:normal;">({item['ton']:,.0f} t)</span></span>
            </div>
            """
    else:
        linhas_dest_html = '<div style="color:#64748b; font-size:0.75rem; padding:4px 0;">Nenhum veículo alocado neste status.</div>'

    html_patio += f"""
    <details style="background-color:#0a101d; border:1px solid #1c2b42; border-left:4px solid {cor}; border-radius:8px; overflow:hidden;">
        <summary style="padding:10px 14px; cursor:pointer; list-style:none; display:flex; justify-content:space-between; align-items:center; -webkit-tap-highlight-color:transparent;">
            <div>
                <span style="color:{cor}; font-weight:normal; font-size:0.85rem; text-transform:uppercase;">{tit}</span>
                <div style="font-size:1.25rem; font-weight:normal; color:#ffffff; margin-top:2px;">
                    {v_qtd} <span style="font-size:0.75rem; color:#64748b; font-weight:normal;">veíc. / <span style="color:#cbd5e1;">{v_ton:,.0f} t</span></span>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.75rem; color:#38bdf8; font-weight:normal;">Tocar para ver Destinos</div>
            </div>
        </summary>
        <div style="background-color:#070d18; padding:10px 14px; border-top:1px solid #1c2b42;">
            {linhas_dest_html}
        </div>
    </details>
    """

v_qtd_tr = dados_patio.get("TR", {}).get("veiculos", 0)
v_ton_tr = dados_patio.get("TR", {}).get("peso", 0)

html_patio += f"""
<div style="background-color:#0a101d; border:1px solid #1c2b42; border-left:4px solid #95A5A6; border-radius:8px; padding:10px 14px; display:flex; justify-content:space-between; align-items:center;">
    <div>
        <span style="color:#95A5A6; font-weight:normal; font-size:0.85rem; text-transform:uppercase;">📄 Termo SAP</span>
        <div style="font-size:1.25rem; font-weight:normal; color:#ffffff; margin-top:2px;">
            {v_qtd_tr} <span style="font-size:0.75rem; color:#64748b; font-weight:normal;">veíc. / <span style="color:#cbd5e1;">{v_ton_tr:,.0f} t</span></span>
        </div>
    </div>
    <div style="text-align:right;">
        <div style="font-size:0.75rem; color:#64748b; font-weight:normal;">Fila de Faturamento</div>
    </div>
</div>
"""
html_patio += '</div></div></details>'
st.markdown(html_patio.replace('\n', ''), unsafe_allow_html=True)

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
        c_ph  = classificar_kpi_mobile(q_ph, "ph")
        
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
                    <span style='font-size:1.1rem; font-weight:normal; color:#ffffff;'>{s_rest:,.0f} t</span>
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
                <span style='color:#38bdf8; font-weight:bold; font-size:1.2rem;'>{p_maq:,.0f} t</span>
            </div>
            
            <div style='display:flex; justify-content:flex-end; gap: 16px; margin-bottom: 12px; font-size: 0.85rem; color: #64748b; font-weight: normal;'>
                <span>{lbl_l1}: <span style='color:#ffffff;'>{l1:,.0f} t</span></span>
                <span>{lbl_l2}: <span style='color:#ffffff;'>{l2:,.0f} t</span></span>
            </div>
            
            <div style='display: flex; justify-content: space-between; text-align: center; border-top: 1px dashed #1c2b42; padding-top: 14px;'>
                <div>
                    <div style='font-size:0.7rem; color:#64748b; font-weight:bold; text-transform:uppercase;'>ALVURA</div>
                    <div style='font-size:1.2rem; font-weight:normal; color:{c_alv}; margin: 4px 0;'>{q_alvura:.2f}%</div>
                    <div style='font-size:0.65rem; color:#475569; font-weight:normal;'>(Mín: 88,5)</div>
                </div>
                <div>
                    <div style='font-size:0.7rem; color:#64748b; font-weight:bold; text-transform:uppercase;'>SUJIDADE</div>
                    <div style='font-size:1.2rem; font-weight:normal; color:{c_suj}; margin: 4px 0;'>{q_suj:.2f}</div>
                    <div style='font-size:0.65rem; color:#475569; font-weight:normal;'>(Máx: 2,5)</div>
                </div>
                <div>
                    <div style='font-size:0.7rem; color:#64748b; font-weight:bold; text-transform:uppercase;'>VISCOSID.</div>
                    <div style='font-size:1.2rem; font-weight:normal; color:{c_vis}; margin: 4px 0;'>{q_visc:,.0f}</div>
                    <div style='font-size:0.65rem; color:#475569; font-weight:normal;'>(Mín: 650)</div>
                </div>
                <div>
                    <div style='font-size:0.7rem; color:#64748b; font-weight:bold; text-transform:uppercase;'>pH</div>
                    <div style='font-size:1.2rem; font-weight:normal; color:{c_ph}; margin: 4px 0;'>{q_ph:.1f}</div>
                    <div style='font-size:0.65rem; color:#475569; font-weight:normal;'>(5,5 - 8,5)</div>
                </div>
            </div>
            {html_virada}
        </div>
        """
    else:
        html_prod_content += f"<div style='color:gray; padding:10px 0;'>Aguardando dados da {maq}...</div>"

html_prod_completo = f"""
<details class="master-box" style="border-left-color: #E5B800;">
    <summary>
        <div class="header-layout">
            <div class="icon-box" style="background-color: rgba(229, 184, 0, 0.15); color: #E5B800;">🏭</div>
            <div class="master-metric-title">Produção de Celulose</div>
        </div>
        <div class="value-layout">
            <div class="master-metric-val">{prod_hoje_calc:,.0f}</div>
            <div class="master-metric-unit">TON</div>
        </div>
        <div class="master-metric-sub" style="color: #E5B800;">MS1: {dados_maquinas['MS1'].get('producao', 0):,.0f} t | MS2: {dados_maquinas['MS2'].get('producao', 0):,.0f} t</div>
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
    agora_br = datetime.utcnow() - timedelta(hours=4)
    hoje_date = agora_br.date()
    is_hoje = (data_alvo == hoje_date)
    letras = descobrir_letras_turnos(data_alvo)
    
    ativo_key = None
    if is_hoje:
        if agora_br.hour < 8: ativo_key = "t1"
        elif agora_br.hour < 16: ativo_key = "t2"
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
            if agora_br.hour < 8: vol_t2, vol_t3 = 0, 0
            elif agora_br.hour < 16: vol_t3 = 0

        turnos_exibir = []
        
        if data_alvo.weekday() in [6, 0]:
            str_vol_t1 = "Folga"
            vol_real_t1 = 0
            lbl_sub_t1 = "Somente Armazen."
        else:
            str_vol_t1 = f"{vol_t1:,.0f} t"
            vol_real_t1 = vol_t1
            lbl_sub_t1 = "00h - 08h"

        turnos_exibir.append({"key": "t1", "letra": f"Turno {letras.get('madrugada', 'D')}", "vol": vol_real_t1, "str_vol": str_vol_t1, "horario": lbl_sub_t1})
        turnos_exibir.append({"key": "t2", "letra": f"Turno {letras.get('08_16', 'C')}", "vol": vol_t2, "str_vol": f"{vol_t2:,.0f} t", "horario": "08h - 16h"})
        turnos_exibir.append({"key": "t3", "letra": f"Turno {letras.get('16_00', 'B')}", "vol": vol_t3, "str_vol": f"{vol_t3:,.0f} t", "horario": "16h - 00h"})
        
        total_dia = vol_real_t1 + vol_t2 + vol_t3
        return {"ativo_key": ativo_key, "turnos": turnos_exibir, "total_dia": total_dia}
    except Exception:
        return None

# ==============================================================================
# 🚚 BLOCO 3: EXPEDIÇÃO DO DIA & TURNOS E DESTINOS
# ==============================================================================
agora_br = datetime.utcnow() - timedelta(hours=4)
hoje_date = agora_br.date()
ontem_date = hoje_date - timedelta(days=1)

dados_exp_hoje = buscar_dados_turnos_historico(hoje_date)
dados_exp_ontem = buscar_dados_turnos_historico(ontem_date)

vol_calculado_hoje = forcar_par(dados_exp_hoje.get("total_dia", 0)) if dados_exp_hoje else 0
vol_exp_hoje = vol_calculado_hoje if vol_hoje == 0 else vol_hoje
vol_exp_ontem = vol_ontem if vol_ontem > 0 else (forcar_par(dados_exp_ontem.get("total_dia", 0)) if dados_exp_ontem else 0)

# Montagem do HTML de Turnos
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
        
        v_str = t.get("str_vol", f"{t['vol']:,.0f} t")
        if v_str == "Folga":
            html_val = f"<div style='font-size:0.85rem; font-weight:normal; color:#E74C3C; padding: 5px 0;'>EM FOLGA</div>"
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
        v_str_o = t.get("str_vol", f"{t['vol']:,.0f} t")
        if v_str_o == "Folga":
            html_val_o = f"<div style='font-size:0.85rem; font-weight:normal; color:#E74C3C; padding: 5px 0;'>EM FOLGA</div>"
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

# ==============================================================================
# 🎯 MONTAGEM DO HTML DE DESTINOS (TABELA COMPACTA NO LUGAR DOS CARDS)
# ==============================================================================
html_destinos = f"""
<div style="display:flex; justify-content:space-around; background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:12px; margin-bottom:14px; text-align:center;">
    <div>
        <div style="font-size:0.75rem; color:#64748b; font-weight:bold; text-transform:uppercase;">Plano Total Diário</div>
        <div style="font-size:1.4rem; color:#ffffff; font-weight:bold;">{total_expedicao_meta:,.0f} <span style="font-size:0.8rem; color:#64748b; font-weight:normal;">t</span></div>
    </div>
    <div style="border-left:1px solid #1c2b42; padding-left:20px;">
        <div style="font-size:0.75rem; color:#38bdf8; font-weight:bold; text-transform:uppercase;">Total Carregado</div>
        <div style="font-size:1.4rem; color:#38bdf8; font-weight:bold;">{total_expedicao_real:,.0f} <span style="font-size:0.8rem; font-weight:normal;">t</span></div>
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
            saldo_str = f"{d['saldo']:,.0f}"
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
                <td style="text-align: center; padding: 10px 4px; color: #38bdf8; font-weight: normal;">{d['meta']:,.0f}</td>
                <td style="text-align: center; padding: 10px 4px; color: #00D672; font-weight: normal;">{d['realizado']:,.0f}</td>
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
<details class="master-box" style="border-left-color: #00D672;" open>
    <summary>
        <div class="header-layout">
            <div class="icon-box" style="background-color: rgba(0, 214, 114, 0.15); color: #00D672;">🚚</div>
            <div class="master-metric-title">Expedição Realizada</div>
        </div>
        <div class="value-layout">
            <div class="master-metric-val">{vol_exp_hoje:,.0f}</div>
            <div class="master-metric-unit">TON</div>
        </div>
        <div class="master-metric-sub" style="color: #00D672;">Consolidado Ontem (D-1): {vol_exp_ontem:,.0f} t</div>
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

# ==============================================================================
# 📦 BLOCO 4: ESTOQUE TOTAL E MATERIAIS
# ==============================================================================
html_est = '<details class="master-box" style="border-left-color: #9b59b6;">'
html_est += f'''
<summary>
    <div class="header-layout">
        <div class="icon-box" style="background-color: rgba(155, 89, 182, 0.15); color: #9b59b6;">📦</div>
        <div class="master-metric-title">Estoque Físico no Armazém</div>
    </div>
    <div class="value-layout">
        <div class="master-metric-val">{estoque_total:,.0f}</div>
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
            "text": f"{t_par:,.0f} t",
            "color": cor_barra
        })
    html_est += build_vertical_chart(chart_data_est)
else:
    html_est += '<div style="color:gray;">Aguardando detalhamento de material...</div>'

html_est += "</div></details>"
st.markdown(html_est, unsafe_allow_html=True)

# ==============================================================================
# 🚜 BLOCO 5: FROTA E EQUIPAMENTOS (VIA HISTÓRICO DKRO)
# ==============================================================================
df_frota = carregar_dados_nuvem("Historico_DKRO", cabecalho=0)

agora_br = datetime.utcnow() - timedelta(hours=4)
hoje_date = agora_br.date()
ontem_date = hoje_date - timedelta(days=1)

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

html_frota = f"""
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
                <div class="f-tag-container" style="margin-bottom:0;"><div class="f-tag-title">🏗 Talhas / Pontes Rolantes</div><div>{render_tags(frota_agrupada['hoje']['08h - 16h']['TALHA'])}</div></div>
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
                <div class="f-tag-container" style="margin-bottom:0;"><div class="f-tag-title">🏗 Talhas / Pontes Rolantes</div><div>{render_tags(frota_agrupada['ontem']['08h - 16h']['TALHA'])}</div></div>
            </div>
            <div id="frota_o_content_16" class="f-content-turno-ontem">
                <div class="f-tag-container"><div class="f-tag-title">🟢 Empilhadeiras Logadas</div><div>{render_tags(frota_agrupada['ontem']['16h - 00h']['EMP'])}</div></div>
                <div class="f-tag-container" style="margin-bottom:0;"><div class="f-tag-title">🏗️ Talhas / Pontes Rolantes</div><div>{render_tags(frota_agrupada['ontem']['16h - 00h']['TALHA'])}</div></div>
            </div>
        </div>
    </div>
</details>
"""
st.markdown(html_frota.replace('\n', ''), unsafe_allow_html=True)

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
                    <div class="master-metric-val">{total_glp_recente:,.0f}</div>
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
                        "text": f"{val_kg_par:,.0f} kg",
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
st.markdown(html_glp, unsafe_allow_html=True)

# ==============================================================================
# 🩺 BLOCO 7: AUDITORIA BAFÔMETRO (PROTEGIDO COM BOTÃO E SENHA)
# ==============================================================================
st.markdown("""
<div style="margin: 14px 0 8px 0; text-align: center;">
""", unsafe_allow_html=True)

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

st.markdown("</div>", unsafe_allow_html=True)

# Modal nativo para digitar a senha
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

# Renderização do Master Box de Bafômetro somente quando autenticado
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
    st.markdown(html_baf, unsafe_allow_html=True)

# ==============================================================================
# 📊 BLOCO 8: COMPARATIVO PRODUÇÃO vs EXPEDIÇÃO (NO FINAL)
# ==============================================================================
hoje_dt = date.today()
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
    txt_variacao = f"+{diff_prod_carr:,.0f} t (Expedição Superando)"
    cor_variacao = "#00D672"
else:
    txt_variacao = f"+{diff_prod_carr:,.0f} t (Produção Superando)"
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
            <div class="master-metric-val">{carr_ano_atual:,.0f}</div>
            <div class="master-metric-unit">t Expedidas</div>
        </div>
        <div class="master-metric-sub" style="color: #007BFF;">Meta Diária Necessária: {meta_diaria_carr:,.0f} t/dia</div>
    </summary>
    <div class="master-content" style="padding-top:16px;">
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
            <div style="background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:10px;">
                <div style="font-size:0.75rem; color:#007BFF; font-weight:bold; text-transform:uppercase;">EXPEDIÇÃO ANUAL</div>
                <div style="font-size:1.4rem; font-weight:bold; color:#fff; margin:4px 0;">{carr_ano_atual:,.0f} <span style="font-size:0.8rem; color:#64748b; font-weight:normal;">t</span></div>
                <div style="font-size:0.7rem; color:#64748b;">Proj. 31/12: <span style="color:#007BFF;">{proj_carr_fechamento:,.0f} t</span></div>
            </div>
            <div style="background-color:#0a101d; border:1px solid #1c2b42; border-radius:8px; padding:10px;">
                <div style="font-size:0.75rem; color:#00D672; font-weight:bold; text-transform:uppercase;">PRODUÇÃO ANUAL</div>
                <div style="font-size:1.4rem; font-weight:bold; color:#fff; margin:4px 0;">{prod_ano_atual:,.0f} <span style="font-size:0.8rem; color:#64748b; font-weight:normal;">t</span></div>
                <div style="font-size:0.7rem; color:#64748b;">Proj. 31/12: <span style="color:#00D672;">{proj_prod_fechamento:,.0f} t</span></div>
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

st.markdown("<br><center><span style='color:#64748b; font-size: 0.75rem; font-weight: normal; letter-spacing: 0.5px;'>A.L.O.V.E - Mobile / Developed by Cristiano Ciriaco</span></center>", unsafe_allow_html=True)
