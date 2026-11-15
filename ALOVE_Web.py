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
# ⚙️ CONFIGURAÇÃO DA PÁGINA (DESKTOP / WIDE)
# ==============================================================================
LOGO_ALOVE_URL = "https://raw.githubusercontent.com/expedicao-mi/A.L.O.V.E-/main/app_icon.png"
BANNER_TOPO_URL = "https://raw.githubusercontent.com/expedicao-mi/A.L.O.V.E-/main/logo_alove.jpg?v=99"
SHEET_ID = "10FluiIwlynIlPDA74QI8mpHSIrAc-62H1hZNRBsvfCA"

st.set_page_config(page_title="A.L.O.V.E. Desktop", page_icon="🚛", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=60000, limit=None, key="refresh_desktop")


def render_html(html_str: str):
    linhas = [l.strip() for l in html_str.splitlines() if l.strip()]
    st.markdown(" ".join(linhas), unsafe_allow_html=True)


st.markdown(f"""
<link rel="icon" type="image/png" href="{LOGO_ALOVE_URL}">
<meta name="theme-color" content="#050911">
""", unsafe_allow_html=True)

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], .stApp {
    background: radial-gradient(ellipse at top left, #0a2a1c 0%, #06101a 45%, #04080f 100%) !important;
    scroll-behavior: smooth;
}
.main, [data-testid="stMain"] { background: transparent !important; }
#MainMenu, footer, header, [data-testid="stHeader"], [data-testid="stFooter"], [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"], [data-testid="stSidebar"],
[data-testid="collapsedControl"], .stAppDeployButton, div[class^="viewerBadge"],
iframe[title="streamlit_autorefresh.st_autorefresh"] { display: none !important; }
.block-container { padding: 14px 22px 40px 252px !important; max-width: 100% !important; }

/* SIDEBAR FIXA */
.sb { position: fixed; top: 0; left: 0; bottom: 0; width: 230px; background: linear-gradient(180deg,#07131c 0%,#050b12 100%);
      border-right: 1px solid #0f3a2a; padding: 18px 14px; z-index: 50; display: flex; flex-direction: column; box-sizing: border-box; }
.sb-logo { text-align: center; margin-bottom: 18px; }
.sb-logo img { width: 86px; height: 86px; object-fit: contain; }
.sb-logo b { display: block; color: #fff; font-size: 1.3rem; letter-spacing: 3px; margin-top: 4px; }
.sb-logo small { color: #94a3b8; font-size: .68rem; }
.sb a { display: flex; align-items: center; gap: 12px; padding: 11px 14px; margin-bottom: 4px; border-radius: 10px;
        color: #cbd5e1; text-decoration: none; font-size: .95rem; font-weight: 600; transition: .2s; }
.sb a:hover { background: rgba(0,214,114,.12); color: #fff; }
.sb a.on { background: linear-gradient(90deg,#1faa3c,#2ecc4f); color: #fff; box-shadow: 0 0 14px rgba(0,214,114,.35); }
.sb-st { margin-top: auto; border: 1.5px solid #0f6b3d; border-radius: 12px; padding: 10px 12px; background: rgba(0,214,114,.06); }
.sb-st b { font-size: .85rem; }
.sb-st small { display: block; color: #94a3b8; font-size: .68rem; margin-top: 3px; }

/* HEADER */
.hd { display: flex; align-items: center; justify-content: space-between; background: linear-gradient(90deg,#06131a,#0a2a1c);
      border: 1px solid #0f3a2a; border-radius: 16px; padding: 12px 22px; margin-bottom: 14px; }
.hd img { height: 62px; object-fit: contain; border-radius: 8px; }
.hd .sub { color: #e2e8f0; font-size: .95rem; letter-spacing: .5px; text-align: center; }
.hd .up { display: flex; align-items: center; gap: 10px; color: #cbd5e1; font-size: .78rem; text-align: right; }
.hd .up a { width: 40px; height: 40px; border-radius: 50%; border: 1.5px solid #00b4ff; display: flex; align-items: center;
            justify-content: center; color: #fff; text-decoration: none; font-size: 1.1rem; }
.dot { display: inline-block; width: 11px; height: 11px; border-radius: 50%; }

/* GRIDS */
.g5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 14px; }
.g2 { display: grid; grid-template-columns: 1.6fr 1fr; gap: 12px; margin-bottom: 14px; }
.g2e { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px; }
.g3 { display: grid; grid-template-columns: 1fr 1.5fr 1fr; gap: 12px; margin-bottom: 14px; }
@media (max-width: 1300px) { .g5 { grid-template-columns: repeat(3,1fr); } .g2, .g2e, .g3 { grid-template-columns: 1fr; } }

/* PAINÉIS */
.pn { background: linear-gradient(180deg,#0b1830 0%,#08111f 100%); border: 1.5px solid #12506e; border-radius: 16px; padding: 16px;
      box-shadow: 0 0 14px rgba(0,180,255,.08); min-width: 0; }
.pn-t { color: #fff; font-weight: 800; font-size: .95rem; text-transform: uppercase; letter-spacing: .4px; margin-bottom: 12px;
        display: flex; align-items: center; gap: 8px; }
.pn-t small { margin-left: auto; color: #64748b; font-weight: 600; font-size: .7rem; text-transform: none; }
.kpi { border-left: 4px solid var(--c); }
.kpi .l { color: #cbd5e1; font-size: .8rem; text-transform: uppercase; font-weight: 700; }
.kpi .v { color: #fff; font-size: 2rem; font-weight: 800; line-height: 1.1; margin: 4px 0; }
.kpi .v span { font-size: 1rem; color: #94a3b8; font-weight: 500; }
.kpi .s { font-size: .75rem; color: var(--c); font-weight: 700; }
.bar { width: 100%; height: 6px; background: #14243b; border-radius: 999px; overflow: hidden; margin-top: 8px; }
.bar > div { height: 100%; border-radius: 999px; background: var(--c); }

/* TABELAS */
table.tb { width: 100%; border-collapse: collapse; font-size: .8rem; color: #fff; }
table.tb th { color: #64748b; font-size: .68rem; text-transform: uppercase; text-align: center; padding: 6px 4px; border-bottom: 1px solid #1c2b42; }
table.tb td { padding: 8px 4px; text-align: center; border-bottom: 1px dashed #1c2b42; }
table.tb th:first-child, table.tb td:first-child { text-align: left; }
.pill { display: inline-block; padding: 3px 12px; border-radius: 999px; font-size: .72rem; font-weight: 800; }
.row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #12304a; font-size: .85rem; color: #e2e8f0; }
.row:last-child { border-bottom: none; }
.ring { width: 92px; height: 92px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 6px; }
.ring > div { width: 70px; height: 70px; border-radius: 50%; background: #08111f; display: flex; align-items: center;
              justify-content: center; color: #fff; font-weight: 800; font-size: 1.05rem; }
.mini { background: #070d18; border: 1px solid #1c2b42; border-radius: 12px; padding: 10px; text-align: center; }
.mini .a { color: #94a3b8; font-size: .72rem; font-weight: 700; }
.mini .b { color: #fff; font-size: 1.3rem; font-weight: 800; margin-top: 2px; }
.cols { display: flex; gap: 10px; }
.cols > * { flex: 1; min-width: 0; }
.sec-lbl { color: #94a3b8; font-size: .72rem; font-weight: 800; text-transform: uppercase; margin: 10px 0 6px 0; padding-left: 6px; border-left: 3px solid #38bdf8; }
.scroll { max-height: 360px; overflow-y: auto; }
</style>
""", unsafe_allow_html=True)


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


def safe_to_numeric(val):
    if pd.isna(val) or val == "" or val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = re.sub(r'[^\d,\.\-]', '', str(val).strip())
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0


def esc(x):
    return html_lib.escape(str(x))


@st.cache_data(ttl=20)
def carregar_dados_nuvem(worksheet_name: str, cabecalho=0):
    sheet_encoded = urllib.parse.quote(worksheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_encoded}&headers=1"
    try:
        df = pd.read_csv(url, header=cabecalho, on_bad_lines="skip")
        return df.dropna(how="all", axis=1).dropna(how="all", axis=0)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=15)
def carregar_tabela_cega(worksheet_name: str, coluna_chave: str = "DESTINO"):
    import os
    import unicodedata

    def norm_txt(s):
        s_str = str(s).strip().upper()
        return "".join(c for c in unicodedata.normalize("NFD", s_str) if unicodedata.category(c) != "Mn")

    try:
        if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
            cliente = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        elif os.path.exists("credentials.json"):
            cliente = gspread.service_account(filename="credentials.json")
        else:
            return pd.DataFrame(), None

        planilha = cliente.open_by_key(SHEET_ID)
        alvo_norm = norm_txt(worksheet_name)
        aba = None
        todas_abas = planilha.worksheets()
        for ws in todas_abas:
            if norm_txt(ws.title) == alvo_norm:
                aba = ws
                break
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

        carimbo_att = None
        if len(linhas[0]) >= 2 and "ATUALIZADO" in norm_txt(linhas[0][0]):
            carimbo_att = str(linhas[0][1]).strip()

        header_idx = -1
        chave_norm = norm_txt(coluna_chave)
        for i, row in enumerate(linhas[:10]):
            if chave_norm in [norm_txt(x) for x in row]:
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
            if not carimbo_att and "ULTIMA_ATUALIZACAO" in df.columns and not df.empty:
                carimbo_att = str(df.iloc[0]["ULTIMA_ATUALIZACAO"]).strip()
            return df, carimbo_att
    except Exception:
        pass
    return pd.DataFrame(), None


@st.cache_data(ttl=15)
def carregar_prancheta_direto():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=806839882"
    try:
        return pd.read_csv(url, dtype=str, keep_default_na=False)
    except Exception:
        try:
            return carregar_dados_nuvem("Prancheta_Operacao_Core", cabecalho=0)
        except Exception:
            return pd.DataFrame()


@st.cache_data(ttl=15)
def carregar_ultimos_logs_core(qtd_linhas=80):
    try:
        import os
        if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
            cliente = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        elif os.path.exists("credentials.json"):
            cliente = gspread.service_account(filename="credentials.json")
        else:
            return pd.DataFrame()
        aba = cliente.open_by_key(SHEET_ID).worksheet("Live_Logs_Core")
        total_linhas = len(aba.col_values(1))
        if total_linhas <= 1:
            return pd.DataFrame(columns=["DATA_HORA", "MODULO", "EVENTO"])
        linha_inicio = max(2, total_linhas - qtd_linhas)
        valores = aba.get_values(f"A{linha_inicio}:C{total_linhas}")
        df = pd.DataFrame(valores, columns=["DATA_HORA", "MODULO", "EVENTO"])
        return df.iloc[::-1].reset_index(drop=True)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=60)
def carregar_csv_expedicao():
    try:
        r = requests.get(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0", timeout=10)
        r.encoding = 'utf-8'
        return list(csv.reader(StringIO(r.text)))
    except Exception:
        return []


def parse_robusto(texto):
    if not texto or str(texto).strip() in ["", "None"]:
        return {}
    try:
        return json.loads(str(texto).strip())
    except Exception:
        try:
            return ast.literal_eval(str(texto).strip())
        except Exception:
            return {}


def descobrir_letras_turnos(data_alvo):
    data_referencia = date(2026, 9, 22)
    dias_passados = (data_alvo - data_referencia).days
    turnos = {"08_16": "C", "16_00": "B", "madrugada": "D"}
    for letra, dia in [("C", (0 + dias_passados) % 6), ("B", (2 + dias_passados) % 6), ("A", (4 + dias_passados) % 6)]:
        if dia in [0, 1]:
            turnos["08_16"] = letra
        elif dia in [2, 3]:
            turnos["16_00"] = letra
    return turnos


def classificar_kpi(valor, tipo):
    if valor == 0.0:
        return "#94a3b8"
    if tipo == "alvura":
        return "#E74C3C" if valor < 88.50 else ("#FFD600" if valor < 88.70 else "#00D672")
    if tipo == "sujidade":
        return "#E74C3C" if valor > 2.50 else ("#FFD600" if valor > 2.00 else "#00D672")
    if tipo == "viscosidade":
        return "#E74C3C" if valor < 650.0 else ("#FFD600" if valor < 680.0 else "#00D672")
    if tipo == "ph":
        return "#E74C3C" if valor > 0 and (valor < 5.50 or valor > 8.50) else ("#FFD600" if valor > 0 and ((5.50 <= valor < 6.00) or (8.00 < valor <= 8.50)) else "#00D672")
    return "#00D672"


# ==============================================================================
# 🚀 CARREGAMENTO DE DADOS
# ==============================================================================
agora_br = datetime.utcnow() - timedelta(hours=4)
hoje_date = agora_br.date()
ontem_date = hoje_date - timedelta(days=1)

if st.query_params.get("refresh") == "1":
    st.cache_data.clear()
    st.query_params.clear()
    st.rerun()


@st.cache_data(ttl=60)
def carregar_dados_otimizados():
    d_dash = carregar_dados_nuvem("Mobile_Dashboard", cabecalho=0)
    d_qual = carregar_dados_nuvem("Mobile_Qualidade", cabecalho=0)
    d_alert = carregar_dados_nuvem("Mobile_Alertas", cabecalho=0)
    d_cache = carregar_dados_nuvem("Cache_Painel", cabecalho=0)
    d_virada = carregar_dados_nuvem("Status_Virada_Turnos", cabecalho=0)
    d_baf = carregar_dados_nuvem("Bafometro_Status", cabecalho=0)
    if d_baf.empty:
        d_baf = carregar_dados_nuvem("Auditoria_Bafometro", cabecalho=0)
    d_bal, _ = carregar_tabela_cega("Balanco_Expedicao_Destino", "DESTINO")
    d_pat, h_pat = carregar_tabela_cega("Patio_Destino_Status", "DESTINO")
    d_tr, _ = carregar_tabela_cega("Status_TR", "PLACA")
    d_sinal, h_sinal = carregar_tabela_cega("Sinal_de_Vida", "APLICATIVO")
    d_prev, h_prev = carregar_tabela_cega("Preventiva_Inspecao", "TAG")
    d_pran = carregar_prancheta_direto()
    return d_dash, d_qual, d_alert, d_cache, d_virada, d_bal, d_baf, d_pran, d_pat, h_pat, d_tr, d_sinal, h_sinal, d_prev, h_prev


(df_dash, df_qual, df_alertas, df_cache, df_status_virada, df_balanco_dest, df_bafometro, df_prancheta,
 df_patio_dest, hora_att_patio, df_status_tr, df_sinal_vida, hora_att_sinal, df_prev_insp, hora_att_prev) = carregar_dados_otimizados()

cache_dict = {str(r.iloc[0]).strip(): str(r.iloc[1]).strip() for _, r in df_cache.iterrows()} if not df_cache.empty else {}
dados_segregados = parse_robusto(cache_dict.get("dados_segregados", "{}"))

# ==============================================================================
# ⚙️ DASHBOARD & PREVISÕES
# ==============================================================================
ultima_att = None
vol_hoje = vol_ontem = prev_carr = prod_hoje_calc = prev_prod = estoque_total = 0
status_transbordo = ritmo_torre = "NORMAL"


def pegar_val(chave_termo, padrao=0):
    if df_dash.empty:
        return padrao
    row_d = df_dash.iloc[0]
    for col_name in df_dash.columns:
        if chave_termo in col_name:
            return row_d.get(col_name, padrao)
    return padrao


if not df_dash.empty:
    df_dash.columns = [str(c).strip().upper() for c in df_dash.columns]
    ultima_att = str(pegar_val("DATA_HORA", "")).strip() or None
    vol_hoje = forcar_par(safe_to_numeric(pegar_val("EXPEDICAO_HOJE", 0)))
    vol_ontem = forcar_par(safe_to_numeric(pegar_val("EXPEDICAO_ONTEM", 0)))
    prev_carr = forcar_par(safe_to_numeric(pegar_val("PREV_EXPEDICAO", 0)))
    prod_hoje_calc = forcar_par(safe_to_numeric(pegar_val("PRODUCAO_HOJE", 0)))
    prev_prod = forcar_par(safe_to_numeric(pegar_val("PREV_PRODUCAO", 0)))
    estoque_total = forcar_par(safe_to_numeric(pegar_val("ESTOQUE_TOTAL", 0)))
    status_transbordo = str(pegar_val("STATUS_TRANSBORDO", "NORMAL"))

horas_corridas = max(0.1, agora_br.hour + (agora_br.minute / 60.0))
if prev_prod == 0 and prod_hoje_calc > 0:
    prev_prod = forcar_par((prod_hoje_calc / horas_corridas) * 24.0)
if prev_carr == 0 and vol_hoje > 0:
    prev_carr = forcar_par((vol_hoje / horas_corridas) * 24.0)

try:
    dt_att = datetime.strptime(ultima_att[:19], "%d/%m/%Y %H:%M:%S")
except Exception:
    dt_att = agora_br
minutos_inativos = (agora_br - dt_att).total_seconds() / 60.0
conn_ok = minutos_inativos <= 15
conn_cor = "#00D672" if conn_ok else "#E74C3C"
conn_data_full = dt_att.strftime("%d/%m/%Y - %H:%M")

# ==============================================================================
# ⚙️ PÁTIO
# ==============================================================================
mapa_status_colunas = [
    ("Prog/Chegando", "PR", "PR_VEIC", "PR_TON", "#38a9ff", "🚙"),
    ("Checklist", "00", "00_VEIC", "00_TON", "#FFD600", "📋"),
    ("Apoio", "01", "01_VEIC", "01_TON", "#E67E22", "🚛"),
    ("Fila de Carregamento", "FC", "FC_VEIC", "FC_TON", "#00D672", "✅"),
    ("Termo SAP", "TR", "TR_VEIC", "TR_TON", "#95A5A6", "📄"),
]
dados_patio, destinos_por_status = {}, {}
if not df_patio_dest.empty:
    df_patio_dest.columns = [str(c).strip().upper() for c in df_patio_dest.columns]

for tit, chv, col_v, col_t, cor, ico in mapa_status_colunas:
    dest_list = []
    if chv != "TR" and not df_patio_dest.empty and "DESTINO" in df_patio_dest.columns:
        for _, row in df_patio_dest.iterrows():
            d_nome = str(row.get("DESTINO", "")).strip()
            if not d_nome or "TOTAL" in d_nome.upper() or d_nome.upper() in ["NAN", "NONE"]:
                continue
            q = int(safe_to_numeric(row.get(col_v, 0)))
            t = forcar_par(safe_to_numeric(row.get(col_t, 0)))
            if q > 0 or t > 0:
                dest_list.append({"destino": d_nome, "veic": q, "ton": t})
    elif chv == "TR" and not df_status_tr.empty and "PLACA" in df_status_tr.columns:
        agr_tr = {}
        for _, r_tr in df_status_tr.iterrows():
            pl = str(r_tr.get("PLACA", "")).strip()
            if not pl or pl.upper() in ["NAN", "NONE", "PLACA"]:
                continue
            d_tr = str(r_tr.get("DESTINO", "NÃO IDENTIFICADO")).strip()
            if not d_tr or d_tr.upper() in ["N/I", "NAN", ""]:
                d_tr = "EM ANÁLISE / N/I"
            t_tr = safe_to_numeric(r_tr.get("TONELADAS", 45.0))
            if t_tr <= 0:
                t_tr = 45.0
            agr_tr.setdefault(d_tr, {"veic": 0, "ton": 0.0})
            agr_tr[d_tr]["veic"] += 1
            agr_tr[d_tr]["ton"] += t_tr
        for d_k, i_k in agr_tr.items():
            dest_list.append({"destino": d_k, "veic": i_k["veic"], "ton": forcar_par(i_k["ton"])})
    dest_list.sort(key=lambda x: x["veic"], reverse=True)
    if dest_list:
        v_qtd = sum(x["veic"] for x in dest_list)
        v_ton = forcar_par(sum(x["ton"] for x in dest_list))
    else:
        v_qtd = int(safe_to_numeric(pegar_val(col_v, 0)))
        v_ton = forcar_par(safe_to_numeric(pegar_val(col_t, 0)))
    dados_patio[chv] = {"veiculos": v_qtd, "peso": v_ton}
    destinos_por_status[chv] = dest_list

total_veiculos_fisicos = sum(dados_patio[k]["veiculos"] for k in ["00", "01", "FC"])
vol_patio_disponivel = forcar_par(sum(dados_patio[k]["peso"] for k in ["00", "01", "FC"]))

# ==============================================================================
# ⚙️ PRODUÇÃO & VIRADA
# ==============================================================================
viradas_info = {}
if not df_status_virada.empty:
    for _, r in df_status_virada.iterrows():
        linha = str(r.get("LINHA", "")).strip().upper()
        viradas_info[linha] = {"prox_mat": str(r.get("PROXIMO_MATERIAL", "--")), "prev_virada": str(r.get("PREVISAO_VIRADA", "--"))}

qualidade_json = parse_robusto(cache_dict.get("qualidade", "{}"))
dados_maquinas = {"MS1": {}, "MS2": {}}
for m_nome in ["MS1", "MS2"]:
    q_m = qualidade_json.get(m_nome, qualidade_json.get(m_nome.lower(), {}))
    if isinstance(q_m, dict) and q_m:
        q_tipo = str(q_m.get("qualidade_tipo", "EQ")).strip().upper() or "EQ"
        dados_maquinas[m_nome] = {
            "material": str(q_m.get("material", "--")).strip(), "qualidade_tipo": q_tipo,
            "alvura": safe_to_numeric(q_m.get("alvura", 0)), "sujidade": safe_to_numeric(q_m.get("sujidade", 0)),
            "viscosidade": safe_to_numeric(q_m.get("viscosidade", 0)), "ph": safe_to_numeric(q_m.get("ph", 0)),
            "producao": forcar_par(safe_to_numeric(q_m.get("producao", 0))),
            "l1": forcar_par(safe_to_numeric(q_m.get("l1", 0))), "l2": forcar_par(safe_to_numeric(q_m.get("l2", 0))),
            "desclassificando": q_tipo in ["SQ", "OS", "BQ"],
        }
soma_prod_json = dados_maquinas["MS1"].get("producao", 0) + dados_maquinas["MS2"].get("producao", 0)
if soma_prod_json > 0:
    prod_hoje_calc = forcar_par(soma_prod_json)

# ==============================================================================
# ⚙️ EXPEDIÇÃO (BALANÇO + TURNOS + SÉRIE DO GRÁFICO)
# ==============================================================================
balanco_destinos = []
total_exp_meta = total_exp_real = 0.0
if not df_balanco_dest.empty:
    for _, r in df_balanco_dest.iterrows():
        dn = str(r.get("DESTINO", "")).strip()
        if not dn or dn.upper() in ["NAN", "NONE", "DESTINO"]:
            continue
        meta = forcar_par(safe_to_numeric(r.get("META_DIA_T", 0)))
        real = forcar_par(safe_to_numeric(r.get("EXPEDIDO_ZLE_T", 0)))
        saldo = forcar_par(safe_to_numeric(r.get("SALDO_A_EXPEDIR_T", 0)))
        try:
            ating = float(str(r.get("ATINGIMENTO_%", 0)).replace('%', '').replace(',', '.'))
        except Exception:
            ating = 0.0
        if "TOTAL" in dn.upper():
            total_exp_meta, total_exp_real = meta, real
        else:
            balanco_destinos.append({"destino": dn, "meta": meta, "realizado": real, "saldo": saldo, "atingimento": ating})
total_exp_falta = forcar_par(max(0.0, total_exp_meta - total_exp_real))

lins_exp = carregar_csv_expedicao()


def func_exp_dados(dt_a):
    ls = descobrir_letras_turnos(dt_a)
    if not lins_exp:
        return []
    c00 = c08 = c16 = cfim = 0.0
    h00 = datetime.combine(dt_a, datetime.min.time())
    h08, h16, hfim = h00.replace(hour=8), h00.replace(hour=16), h00.replace(hour=23, minute=59, second=59)
    for row in lins_exp[1:]:
        if len(row) > 3:
            try:
                dtr = datetime.strptime(row[0].strip(), "%d/%m/%Y %H:%M:%S")
                v = safe_to_numeric(row[3])
                if dtr <= h00: c00 = v
                if dtr <= h08: c08 = v
                if dtr <= h16: c16 = v
                if dtr <= hfim: cfim = v
            except Exception:
                pass
    v1 = forcar_par(c08) if c08 < c00 else forcar_par(max(0.0, c08 - c00))
    v2 = forcar_par(c16) if c16 < c08 else forcar_par(max(0.0, c16 - c08))
    v3 = forcar_par(cfim) if cfim < c16 else forcar_par(max(0.0, cfim - c16))
    if dt_a == hoje_date:
        if agora_br.hour < 8: v2, v3 = 0, 0
        elif agora_br.hour < 16: v3 = 0
    tns = []
    if dt_a.weekday() in [6, 0]:
        tns.append({"letra": f"Turno {ls['madrugada']}", "v": 0, "s": "EM FOLGA", "h": "00h - 08h"})
    else:
        tns.append({"letra": f"Turno {ls['madrugada']}", "v": v1, "s": f"{fmt(v1)} t", "h": "00h - 08h"})
    tns.append({"letra": f"Turno {ls['08_16']}", "v": v2, "s": f"{fmt(v2)} t", "h": "08h - 16h"})
    tns.append({"letra": f"Turno {ls['16_00']}", "v": v3, "s": f"{fmt(v3)} t", "h": "16h - 00h"})
    return tns


def serie_expedicao(dt_a):
    h00 = datetime.combine(dt_a, datetime.min.time())
    c00, pts = 0.0, []
    for row in lins_exp[1:]:
        if len(row) > 3:
            try:
                dtr = datetime.strptime(row[0].strip(), "%d/%m/%Y %H:%M:%S")
                v = safe_to_numeric(row[3])
                if dtr <= h00: c00 = v
                elif dtr.date() == dt_a: pts.append((dtr, v))
            except Exception:
                pass
    out, cum, prev = [(0.0, 0.0)], 0.0, c00
    for dtr, v in pts:
        cum += (v - prev) if v >= prev else v   # se o contador zerou, soma o novo valor
        prev = v
        out.append(((dtr - h00).total_seconds() / 3600.0, cum))
    return out


tns_hoje, tns_ontem = func_exp_dados(hoje_date), func_exp_dados(ontem_date)
pct_prog = min(100.0, max(0.0, (vol_hoje / prev_carr * 100.0))) if prev_carr > 0 else 0.0
pct_prod = min(100.0, max(0.0, (prod_hoje_calc / prev_prod * 100.0))) if prev_prod > 0 else 0.0

# ==============================================================================
# ⚙️ SINAL DE VIDA (TELEMETRIA)
# ==============================================================================
modulos = [
    {"chave": "CORE", "nome": "CORE", "sub": "Motor SAP", "ico": "🤖", "status": "OFFLINE", "pulso": "--:--"},
    {"chave": "TORRE", "nome": "TORRE", "sub": "Controle YMS", "ico": "📡", "status": "OFFLINE", "pulso": "--:--"},
    {"chave": "TOTEM", "nome": "TOTEM", "sub": "Autoatend.", "ico": "📱", "status": "OFFLINE", "pulso": "--:--"},
    {"chave": "TV", "nome": "TV", "sub": "Painel Pátio", "ico": "📺", "status": "OFFLINE", "pulso": "--:--"},
]
sinal_expirado = False
if hora_att_sinal:
    try:
        dt_sinal = datetime.strptime(hora_att_sinal[:19], "%d/%m/%Y %H:%M:%S")
        if (agora_br - dt_sinal).total_seconds() / 60.0 > 20:
            sinal_expirado = True
    except Exception:
        pass
if not df_sinal_vida.empty and "APLICATIVO" in df_sinal_vida.columns:
    for _, rs in df_sinal_vida.iterrows():
        app = str(rs.get("APLICATIVO", "")).strip().upper()
        st_app = str(rs.get("STATUS", "OFFLINE")).strip().upper()
        pulso = str(rs.get("ÚLTIMO_PULSO", rs.get("ULTIMO_PULSO", "--:--"))).strip() or "--:--"
        for m in modulos:
            if m["chave"] in app:
                m["pulso"] = pulso
                m["status"] = "OFFLINE" if sinal_expirado else ("ONLINE" if "ONLINE" in st_app else "OFFLINE")
qtd_online_mod = sum(1 for m in modulos if m["status"] == "ONLINE")
if sinal_expirado or qtd_online_mod == 0:
    st_geral_txt, st_geral_cor = "SISTEMA OFFLINE", "#E74C3C"
elif qtd_online_mod < 4:
    st_geral_txt, st_geral_cor = f"OPERAÇÃO PARCIAL ({qtd_online_mod}/4)", "#FFD600"
else:
    st_geral_txt, st_geral_cor = "SISTEMA 100% ONLINE", "#00D672"

# ==============================================================================
# ⚙️ ESTOQUE
# ==============================================================================
CAPACIDADE_MAX_ARMAZEM = 25000.0
CORES_CLASSE = {"EQ": "#00FF7F", "SQ": "#FFD600", "BQ": "#FF8C00", "OS": "#FF2E2E"}
raw_seg = str(cache_dict.get("dados_segregados", "{}")).strip()
if '""' in raw_seg and not dados_segregados:
    dados_segregados = parse_robusto(raw_seg.replace('""', '"'))
itens_estoque, tot_on, tot_off = [], 0.0, 0.0
for m_raw, v_raw in (dados_segregados or {}).items():
    t_val = forcar_par(safe_to_numeric(v_raw))
    if t_val <= 0:
        continue
    m_str = str(m_raw).strip().upper()
    mc = re.search(r'\(([^)]+)\)', m_str)
    if mc: cls = mc.group(1).strip().upper()
    elif "OS" in m_str: cls = "OS"
    elif "BQ" in m_str: cls = "BQ"
    elif "SQ" in m_str: cls = "SQ"
    else: cls = "EQ"
    cod = re.sub(r'\([^)]*\)', '', m_str).strip() or m_str.split()[0]
    if cls == "EQ": tot_on += t_val
    else: tot_off += t_val
    itens_estoque.append({"material": cod, "classe": cls, "ton": t_val})
soma_seg = forcar_par(tot_on + tot_off)
if soma_seg > 0:
    estoque_total = soma_seg
else:
    e4 = forcar_par(safe_to_numeric(cache_dict.get("estoque_total", 0)))
    if e4 > 0: estoque_total = e4
pct_ocup = min(100.0, max(0.0, estoque_total / CAPACIDADE_MAX_ARMAZEM * 100.0))
tot_calc = soma_seg if soma_seg > 0 else (estoque_total if estoque_total > 0 else 1.0)
pct_on, pct_off = tot_on / tot_calc * 100.0, tot_off / tot_calc * 100.0
itens_estoque.sort(key=lambda x: (-x["ton"], x["material"]))

# ==============================================================================
# ⚙️ FROTA / PREVENTIVA
# ==============================================================================
def peso_sev(a):
    a = str(a).upper()
    if "VENCIDA" in a: return 0
    if "CRITICO" in a or "CRÍTICO" in a: return 1
    if any(x in a for x in ["ATENCAO", "ATENÇÃO", "PROXIMA", "PRÓXIMA"]): return 2
    if "NORMAL" in a or "EM DIA" in a: return 3
    return 4


def ordem_tipo(t):
    t = str(t).upper()
    for i, k in enumerate(["EMPILHADEIRA", "TRANSPALETEIRA", "VARREDEIRA", "LAVADORA", "TALHA", "BICICLETA"]):
        if k in t: return i
    return 6


def fmt_horim(v):
    s = str(v).strip()
    if not s or s.upper() in ["NAN", "NONE", "--", "-"]: return "--"
    if "/" in s: return s[:10]
    n = safe_to_numeric(s)
    return f"{fmt(n)} h" if n > 0 else s


frota = []
if not df_prev_insp.empty and "TAG" in df_prev_insp.columns:
    for _, rp in df_prev_insp.iterrows():
        tag = str(rp.get("TAG", "")).strip().upper()
        if not tag or tag in ["NAN", "NONE", "TAG"]:
            continue
        tipo = str(rp.get("TIPO_EQUIPAMENTO", "Outros")).strip() or "Outros"
        st_op = str(rp.get("STATUS_OPERACAO", "")).strip().upper()
        disp = str(rp.get("DISPONIBILIDADE", "ONLINE")).strip().upper()
        a_prev = str(rp.get("ALERTA_PREVENTIVA", "--")).strip()
        a_insp = str(rp.get("ALERTA_INSPECAO", "SEM META")).strip()
        sev = min(peso_sev(a_prev), peso_sev(a_insp))
        off = ("OFFLINE" in disp) or ("INDISP" in disp) or ("MANUT" in st_op)
        frota.append({"tag": tag, "tipo": tipo, "off": off, "sev": sev, "horim": fmt_horim(rp.get("HORIMETRO_ATUAL", "--")),
                      "a_prev": a_prev, "a_insp": a_insp, "meta": fmt_horim(rp.get("META_PREVENTIVA", "--"))})
total_online = sum(1 for e in frota if not e["off"])
total_offline = sum(1 for e in frota if e["off"])
total_frota = total_online + total_offline
qtd_criticos = sum(1 for e in frota if e["sev"] <= 1)
disp_frota = (total_online / total_frota * 100.0) if total_frota else 0.0

# ==============================================================================
# ⚙️ BAFÔMETRO
# ==============================================================================
df_baf = df_bafometro.copy()
lst_ok, lst_troca, lst_pend = [], [], []
hora_base_baf = ""
letras_atuais = descobrir_letras_turnos(hoje_date)
if agora_br.hour < 8: letra_v, per_rot = letras_atuais["madrugada"], "Madrugada"
elif agora_br.hour < 16: letra_v, per_rot = letras_atuais["08_16"], "Manhã"
else: letra_v, per_rot = letras_atuais["16_00"], "Tarde"
if not df_baf.empty:
    df_baf.columns = [str(c).strip().upper() for c in df_baf.columns]
    col_dh = "DATA_HORA" if "DATA_HORA" in df_baf.columns else df_baf.columns[0]
    vdh = [str(x).strip() for x in df_baf[col_dh].dropna().tolist() if str(x).strip() not in ["", "nan", "None", "DATA_HORA"]]
    if vdh:
        hora_base_baf = vdh[-1].split(" ")[1][:5] if " " in vdh[-1] else vdh[-1][:5]
    c_turno = next((c for c in df_baf.columns if "TURNO" in c), None)
    if c_turno:
        vt = [str(x).strip() for x in df_baf[c_turno].dropna().tolist() if str(x).strip() not in ["", "nan", "None", "TURNO"]]
        if vt: per_rot = vt[-1].capitalize()
    for _, r in df_baf.iterrows():
        colab = str(r.get("COLABORADOR", "")).strip()
        if not colab or colab.upper() in ["NAN", "NONE", "", "COLABORADOR"]:
            continue
        funcao = str(r.get("FUNCAO", r.get("FUNÇÃO", "--"))).strip()
        status = str(r.get("STATUS", "")).strip().upper()
        res = str(r.get("RESULTADO", "")).strip().upper()
        d = {"nome": colab, "funcao": funcao, "status": status, "res": res}
        if any(x in status for x in ["TROCA", "NÃO CADAST", "NAO CADAST"]) or "TROCA" in res: lst_troca.append(d)
        elif any(x in status for x in ["PEND", "FALTA", "NÃO REALIZ", "NAO REALIZ"]) or any(x in res for x in ["PEND", "FALTA"]): lst_pend.append(d)
        elif any(x in status for x in ["REALIZ", "APROV", "OK"]) or any(x in res for x in ["APROV", "OK", "0.00", "0,00", "NEGATIVO"]): lst_ok.append(d)
        else: lst_pend.append(d)
total_baf = len(lst_ok) + len(lst_troca) + len(lst_pend)
conf_baf = ((len(lst_ok) + len(lst_troca)) / total_baf * 100.0) if total_baf else 0.0

# ==============================================================================
# ⚙️ PEDIDOS ZLE087
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
            idx = None
            for i in range(min(6, len(df_raw))):
                if any("FLUXO" in str(x).strip().upper() for x in df_raw.iloc[i].tolist()):
                    idx = i
                    break
            if idx is None:
                return pd.DataFrame(), "--:--"
            df = df_raw.iloc[idx + 1:].copy()
            df.columns = [str(c).strip().upper() for c in df_raw.iloc[idx].tolist()]
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df, (carimbo if carimbo else "--:--")
    except Exception:
        return pd.DataFrame(), "--:--"


df_pedidos, hora_att_ped = carregar_pedidos_zle087()
pedidos_transf, pedidos_mi = [], []
tot_saldo_transf = tot_saldo_mi = 0.0


def obter_val(reg, obrig, proib=[]):
    for k in reg.index:
        ku = str(k).strip().upper()
        if all(t in ku for t in obrig) and not any(p in ku for p in proib):
            v = reg.get(k)
            if pd.notna(v) and str(v).strip() not in ["", "nan", "None"]:
                return v
    return None


if not df_pedidos.empty:
    for _, r in df_pedidos.iterrows():
        fluxo = str(obter_val(r, ["FLUXO"]) or "").strip().upper()
        destino = str(obter_val(r, ["DESTINO"]) or "").strip()
        if not destino or destino.lower() in ["nan", "none"]:
            continue
        saldo = safe_to_numeric(obter_val(r, ["SALDO"], ["PROX"]) or 0)
        item = {"destino": destino, "pedido": str(obter_val(r, ["PEDIDO"], ["PROX"]) or "").strip(),
                "material": str(obter_val(r, ["MAT"], ["PROX"]) or "").strip(),
                "qtd_ini": safe_to_numeric(obter_val(r, ["QTD"]) or 0), "saldo": saldo,
                "prox": f'{str(obter_val(r, ["PROX", "PED"]) or "--").strip()} • {str(obter_val(r, ["PROX", "MAT"]) or "--").strip()}',
                "is_fim": 0 < saldo <= 100.0}
        if "TRANSF" in fluxo:
            pedidos_transf.append(item); tot_saldo_transf += saldo
        else:
            pedidos_mi.append(item); tot_saldo_mi += saldo
pedidos_transf.sort(key=lambda x: (not x["is_fim"], x["destino"]))
pedidos_mi.sort(key=lambda x: (not x["is_fim"], x["destino"]))
tot_saldo_geral = tot_saldo_transf + tot_saldo_mi

# ==============================================================================
# ⚙️ COMPARATIVO ANUAL
# ==============================================================================
def parse_num_ano(v):
    if v is None or pd.isna(v): return 0.0
    s = re.sub(r'[^\d,\.\-]', '', str(v).strip())
    if not s or s in ["-", "."]: return 0.0
    if "," in s and "." in s: s = s.replace(".", "").replace(",", ".")
    elif "," in s: s = s.replace(",", ".")
    elif "." in s and len(s.split(".")[-1]) == 3: s = s.replace(".", "")
    try: return float(s)
    except Exception: return 0.0


df_param, _ = carregar_tabela_cega("Parametros_Ano", "PARAMETRO")
if df_param.empty:
    df_param = carregar_dados_nuvem("Parametros_Ano", cabecalho=0)
params, data_ref_ano = {}, ""
if not df_param.empty:
    df_param.columns = [str(c).strip().upper() for c in df_param.columns]
    for _, r in df_param.iterrows():
        k = str(r.get("PARAMETRO", "")).strip().upper()
        if not k or k in ["NAN", "NONE", "PARAMETRO"]: continue
        params[k] = parse_num_ano(r.get("VALOR", 0))
        dp = str(r.get("DATA", "")).strip()
        if dp and dp not in ["-", "--", "nan", "None"] and not data_ref_ano: data_ref_ano = dp

d_res = max(1, (date(hoje_date.year, 12, 31) - hoje_date).days)
carr_base, prod_base = params.get("CARREGAMENTO_BASE", 0.0), params.get("PRODUCAO_BASE", 0.0)
meta_est = forcar_par(params.get("META_ESTOQUE_ANO", 3468.0))
if meta_est < 100: meta_est = 3468
carr_dia, prod_dia = params.get("CARREGAMENTO_DIA", 0.0), params.get("PRODUCAO_DIA", 0.0)
tot_carr, tot_prod = params.get("TOTAL_CARREGAMENTO", 0.0), params.get("TOTAL_PRODUCAO", 0.0)
ca_at = forcar_par(max(tot_carr, carr_base + max(vol_hoje, carr_dia))) if carr_base > 0 else forcar_par(tot_carr if tot_carr > 0 else (1604858.0 + vol_hoje))
pa_at = forcar_par(max(tot_prod, prod_base + max(prod_hoje_calc, prod_dia))) if prod_base > 0 else forcar_par(tot_prod if tot_prod > 0 else (1607494.0 + prod_hoje_calc))
df_pc = forcar_par(abs(pa_at - ca_at))
if ca_at >= pa_at: tv, cv = f"+{fmt(df_pc)} t (Expedição Superando)", "#00D672"
else: tv, cv = f"+{fmt(df_pc)} t (Produção Superando)", "#FF9F1C"
mdc = forcar_par(5200.0 + (max(0.0, estoque_total - meta_est) / d_res))
ppf = forcar_par(pa_at + d_res * 5200.0)
pcf = forcar_par(ca_at + ((estoque_total + d_res * 5200.0) - meta_est))

# ==============================================================================
# 🖨️ HELPERS DE RENDER
# ==============================================================================
def pn(titulo, ico, corpo, extra="", cor="#12506e", id_=""):
    return f'<div class="pn" id="{id_}" style="border-color:{cor};"><div class="pn-t"><span>{ico}</span>{titulo}<small>{extra}</small></div>{corpo}</div>'


def kpi(titulo, ico, valor, unid, sub, cor, pct=None):
    barra = f'<div class="bar"><div style="width:{pct:.0f}%"></div></div>' if pct is not None else ""
    return f'<div class="pn kpi" style="--c:{cor};"><div class="l">{ico} {titulo}</div><div class="v">{valor} <span>{unid}</span></div><div class="s">{sub}</div>{barra}</div>'


def ring(pct, cor, rotulo):
    p = max(0, min(100, pct))
    return f'<div style="text-align:center;"><div class="ring" style="background:conic-gradient({cor} {p}%, #14243b 0);"><div>{p:.0f}%</div></div><div style="color:#cbd5e1;font-size:.76rem;">{rotulo}</div></div>'


def pill(txt, cor, fg="#0a101d"):
    return f'<span class="pill" style="background:{cor};color:{fg};">{esc(txt)}</span>'


def _noop(*a, **k):
    pass


# ==============================================================================
# 🖨️ SIDEBAR + HEADER
# ==============================================================================
menu = [("sec-topo", "🏠", "Início", True), ("sec-prod", "🏭", "Produção", False), ("sec-exp", "🚚", "Expedição", False),
        ("sec-patio", "🏢", "Pátio", False), ("sec-frota", "🚜", "Frota", False), ("sec-baf", "🩺", "Bafômetro", False),
        ("sec-tele", "📊", "Telemetria", False), ("sec-ano", "📈", "Relatórios", False)]
links = "".join(f'<a href="#{i}" class="{"on" if on else ""}"><span>{ic}</span>{nm}</a>' for i, ic, nm, on in menu)

_noop(f"""
<div class="sb">
  <div class="sb-logo"><img src="{LOGO_ALOVE_URL}"><b>A.L.O.V.E.</b><small>Logística em Tempo Real</small></div>
  {links}
  <div class="sb-st" style="border-color:{st_geral_cor};"><b style="color:{st_geral_cor};">● {st_geral_txt}</b><small>Atualização automática a cada 1 minuto</small></div>
</div>
<div id="sec-topo"></div>
<div class="hd">
  <div style="width:240px;"><img src="{BANNER_TOPO_URL}"></div>
  <div class="sub">Assistente Logístico Virtual da Expedição</div>
  <div class="up"><span class="dot" style="background:{conn_cor};box-shadow:0 0 8px {conn_cor};"></span>
    <div>Última atualização:<br><b style="color:#fff;">{conn_data_full}</b></div>
    <a href="?refresh=1" target="_self">🔄</a></div>
</div>
""")

# ==============================================================================
# 🖨️ LINHA 1: KPIs
# ==============================================================================
cor_baf = "#00D672" if not lst_pend else "#E74C3C"
_noop('<div class="g5">' +
    kpi("Produção Hoje", "🏭", fmt(prod_hoje_calc), "t", f"Prev. 24h: {fmt(prev_prod)} t", "#38bdf8", pct_prod) +
    kpi("Expedição Hoje", "🚚", fmt(vol_hoje), "t", f"Prev. 24h: {fmt(prev_carr)} t", "#00D672", pct_prog) +
    kpi("Pátio Atual", "🏗️", fmt(vol_patio_disponivel), "t", f"{total_veiculos_fisicos} veículos físicos", "#FF9F1C") +
    kpi("Frota Ativa", "🚜", f"{disp_frota:.0f}", "%", f"{total_online}/{total_frota} online • {qtd_criticos} prev. críticas", "#a78bfa", disp_frota) +
    kpi("Bafômetro", "🩺", f"{conf_baf:.0f}", "%", f"{len(lst_pend)} pendências", cor_baf, conf_baf) +
    '</div>')

# ==============================================================================
# 🖨️ LINHA 2: GRÁFICO EVOLUÇÃO (EXPEDIÇÃO HOJE x ONTEM) + STATUS DA OPERAÇÃO
# ==============================================================================
def svg_evolucao():
    sh, so = serie_expedicao(hoje_date), serie_expedicao(ontem_date)
    W, H, L, B, T = 700, 300, 46, 26, 10
    ymax = max([p[1] for p in sh + so] + [prev_carr * 0.0, 1000.0])
    step = 1000 if ymax <= 6000 else 2000
    ymax = (int(ymax // step) + 1) * step

    def xy(p):
        return f"{L + p[0] / 24.0 * (W - L - 10):.1f},{T + (H - T - B) * (1 - p[1] / ymax):.1f}"

    g = ""
    for v in range(0, int(ymax) + 1, int(step)):
        y = T + (H - T - B) * (1 - v / ymax)
        g += f'<line x1="{L}" x2="{W-10}" y1="{y:.1f}" y2="{y:.1f}" stroke="#1c2b42" stroke-dasharray="3"/><text x="{L-6}" y="{y+4:.1f}" fill="#94a3b8" font-size="11" text-anchor="end">{v//1000}k</text>'
    for h in range(0, 25, 4):
        x = L + h / 24.0 * (W - L - 10)
        g += f'<text x="{x:.1f}" y="{H-6}" fill="#cbd5e1" font-size="11" text-anchor="middle">{h:02d}h</text>'
    ph = " ".join(xy(p) for p in sh)
    po = " ".join(xy(p) for p in so)
    area = f'{ph} {xy((sh[-1][0], 0))} {xy((0, 0))}'
    return (f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:100%;">{g}'
            f'<polygon points="{area}" fill="rgba(0,214,114,.18)"/>'
            f'<polyline points="{po}" fill="none" stroke="#38bdf8" stroke-width="2" stroke-dasharray="5 4"/>'
            f'<polyline points="{ph}" fill="none" stroke="#00D672" stroke-width="3"/></svg>')


grafico = (svg_evolucao() if lins_exp else '<div style="color:#64748b;padding:30px;text-align:center;">Sem dados de expedição.</div>')
leg = '<div style="display:flex;gap:18px;justify-content:center;font-size:.8rem;color:#cbd5e1;margin-bottom:6px;"><span><span class="dot" style="background:#00D672;"></span> Expedição acumulada hoje</span><span><span class="dot" style="background:#38bdf8;"></span> Ontem</span></div>'

n_prod_ok = "Operacional" if prod_hoje_calc > 0 and not any(m.get("desclassificando") for m in dados_maquinas.values() if m) else ("Atenção" if prod_hoje_calc > 0 else "Parado")
st_rows = [
    ("Produção", n_prod_ok, "#00D672" if n_prod_ok == "Operacional" else ("#FFD600" if n_prod_ok == "Atenção" else "#E74C3C")),
    ("Expedição", "Operacional" if vol_hoje > 0 else "Sem carga", "#00D672" if vol_hoje > 0 else "#FFD600"),
    ("Pátio", "Normal" if total_veiculos_fisicos > 0 else "Vazio", "#38bdf8" if total_veiculos_fisicos > 0 else "#FFD600"),
    ("Frota", "Normal" if total_offline == 0 else f"{total_offline} offline", "#38bdf8" if total_offline == 0 else "#FFD600"),
    ("Bafômetro", f"{conf_baf:.0f}%" if not lst_pend else f"{len(lst_pend)} pend.", "#00D672" if not lst_pend else "#E74C3C"),
    ("Telemetria", "Online" if qtd_online_mod == 4 and not sinal_expirado else f"{qtd_online_mod}/4", "#00D672" if qtd_online_mod == 4 and not sinal_expirado else "#E74C3C"),
]
st_html = "".join(f'<div class="row"><span>✅ {n}</span>{pill(t, c)}</div>' for n, t, c in st_rows)
st_html += f'<div class="row"><span>🔁 Transbordo</span>{pill(status_transbordo, "#1c2b42", "#e2e8f0")}</div>'

_noop('<div class="g2">' + pn("Evolução Operacional", "📊", leg + grafico, "Hoje vs Ontem") + pn("Status da Operação", "🚚", st_html) + '</div>')

# ==============================================================================
# 🖨️ LINHA 3: ÚLTIMAS ATUALIZAÇÕES | INDICADORES | TELEMETRIA
# ==============================================================================
df_logs = carregar_ultimos_logs_core()
ult_html = ""
if not df_logs.empty:
    for _, rl in df_logs.head(5).iterrows():
        ev = str(rl["EVENTO"])
        h = str(rl["DATA_HORA"]).split(" ")[-1][:5]
        c = "#E74C3C" if any(x in ev.upper() for x in ["ERRO", "FALHA", "CRÍTICO", "❌", "🚨"]) else ("#FF9F1C" if "⚠️" in ev else "#00D672")
        ult_html += f'<div class="row"><span><span class="dot" style="background:{c};width:9px;height:9px;"></span>&nbsp; <b style="font-family:monospace;">{h}</b> &nbsp;<span style="color:#94a3b8;">{esc(ev[:70])}</span></span></div>'
else:
    ult_html = '<div style="color:#64748b;padding:12px;">Sem logs disponíveis.</div>'

ind_html = '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px;">' + \
    ring(pct_prod, "#38bdf8", "Meta Produção") + ring(pct_prog, "#00D672", "Meta Expedição") + \
    ring(disp_frota, "#FF9F1C", "Disponib. Frota") + ring(conf_baf, "#00FF7F", "Conformid. Bafômetro") + '</div>'

tele_html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">'
for m in modulos:
    on = m["status"] == "ONLINE"
    c = "#00D672" if on else "#E74C3C"
    tele_html += f'<div class="mini" style="border-color:{c};"><div class="a">{m["ico"]} {m["nome"]}</div><div class="b" style="color:{c};font-size:.95rem;">{m["status"]}</div><div class="a" style="font-family:monospace;">🕒 {esc(m["pulso"])}</div></div>'
tele_html += '</div>'

_noop('<div class="g3">' + pn("Últimas Atualizações", "📋", ult_html) + pn("Indicadores Principais", "🎯", ind_html) +
            pn("Telemetria do Ecossistema", "🛡️", tele_html, id_="sec-tele") + '</div>')

# ==============================================================================
# 🖨️ LINHA 4: PÁTIO | PRODUÇÃO
# ==============================================================================
patio_html = ""
for tit, chv, _, _, cor, ico in mapa_status_colunas:
    lst = destinos_por_status.get(chv, [])
    d = dados_patio[chv]
    linhas = "".join(f'<tr><td>{esc(i["destino"])}</td><td>{i["veic"]}</td><td>{fmt(i["ton"])} t</td></tr>' for i in lst) or '<tr><td colspan="3" style="color:#64748b;">Nenhum veículo.</td></tr>'
    patio_html += (f'<div style="border:1.5px solid {cor};border-left:6px solid {cor};border-radius:12px;padding:10px 12px;margin-bottom:10px;background:#0a1424;">'
                   f'<div style="display:flex;justify-content:space-between;align-items:center;"><b style="color:#fff;text-transform:uppercase;font-size:.85rem;">{ico} {tit}</b>'
                   f'<span style="color:#fff;font-weight:800;font-size:1.2rem;">{d["veiculos"]} <small style="color:#9fb3cc;font-weight:400;font-size:.75rem;">veíc. / {fmt(d["peso"])} t</small></span></div>'
                   f'<details><summary style="color:{cor};font-size:.72rem;cursor:pointer;margin-top:4px;">ver destinos</summary>'
                   f'<table class="tb"><tr><th>Destino</th><th>Veíc.</th><th>Ton</th></tr>{linhas}</table></details></div>')
txt_pat = f"Base {hora_att_patio.split(' ')[1][:5]}" if hora_att_patio and " " in hora_att_patio else ""
patio_resumo = f'<div class="cols" style="margin-bottom:12px;"><div class="mini"><div class="a">VEÍCULOS FÍSICOS</div><div class="b">{total_veiculos_fisicos}</div></div><div class="mini"><div class="a">CARGA DISPONÍVEL</div><div class="b" style="color:#38a9ff;">{fmt(vol_patio_disponivel)} t</div></div></div>'

prod_html = ""
for maq in ["MS1", "MS2"]:
    q = dados_maquinas.get(maq, {})
    if not q:
        prod_html += f'<div style="color:gray;padding:10px;">Aguardando dados da {maq}...</div>'
        continue
    t = q["qualidade_tipo"]
    cor_m = "#E74C3C" if t in ["OS", "BQ"] else ("#FFD600" if t == "SQ" else "#00D672")
    l1n, l2n = ("Linha A", "Linha B") if maq == "MS1" else ("Linha C", "Linha D")
    iv = viradas_info.get(maq, {})
    prod_html += (f'<div style="background:#0c1524;border:1.5px solid #1c2b42;border-left:5px solid {cor_m};border-radius:14px;padding:14px;margin-bottom:12px;">'
                  f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;"><div><b style="color:#fff;font-size:1.1rem;">⚙️ {maq}</b> '
                  f'<span style="color:#FF9F1C;font-weight:800;">📦 MAT: {esc(q["material"])}</span> <span class="pill" style="background:{cor_m};color:#0a101d;">{t}</span></div>'
                  f'<div style="color:#fff;font-size:.9rem;">{l1n}: <b style="color:#38bdf8;">{fmt(q["l1"])} t</b> &nbsp; {l2n}: <b style="color:#38bdf8;">{fmt(q["l2"])} t</b></div></div>'
                  f'<div class="cols" style="text-align:center;border-top:1px dashed #1c2b42;padding-top:10px;">'
                  f'<div><div style="font-size:.68rem;color:#64748b;">ALVURA</div><b style="color:{classificar_kpi(q["alvura"],"alvura")};font-size:1.1rem;">{fmt(q["alvura"],2)}%</b></div>'
                  f'<div><div style="font-size:.68rem;color:#64748b;">SUJIDADE</div><b style="color:{classificar_kpi(q["sujidade"],"sujidade")};font-size:1.1rem;">{fmt(q["sujidade"],2)}</b></div>'
                  f'<div><div style="font-size:.68rem;color:#64748b;">VISCOSID.</div><b style="color:{classificar_kpi(q["viscosidade"],"viscosidade")};font-size:1.1rem;">{fmt(q["viscosidade"])}</b></div>'
                  f'<div><div style="font-size:.68rem;color:#64748b;">pH</div><b style="color:{classificar_kpi(q["ph"],"ph")};font-size:1.1rem;">{fmt(q["ph"],1)}</b></div></div>'
                  f'<div style="border-top:1px solid #14243b;margin-top:10px;padding-top:8px;text-align:center;font-size:.8rem;color:#94a3b8;">PROX MAT: <b style="color:#fff;">{esc(iv.get("prox_mat","--"))}</b> &nbsp;|&nbsp; PREV: <b style="color:#fff;">{esc(iv.get("prev_virada","--"))}</b></div></div>')
prod_resumo = f'<div class="cols" style="margin-bottom:12px;"><div class="mini"><div class="a">PRODUÇÃO TOTAL</div><div class="b">{fmt(prod_hoje_calc)} t</div></div><div class="mini"><div class="a">PREV. FECHAMENTO</div><div class="b" style="color:#E5B800;">{fmt(prev_prod)} t</div></div></div>'

_noop('<div class="g2e">' + pn("Pátio da Fábrica", "🏭", patio_resumo + patio_html, txt_pat, "#38a9ff", "sec-patio") +
            pn("Produção de Celulose", "🏭", prod_resumo + prod_html, "", "#E5B800", "sec-prod") + '</div>')

# ==============================================================================
# 🖨️ LINHA 5: EXPEDIÇÃO | PEDIDOS ZLE087
# ==============================================================================
def cards_turno(tns, ativo=False):
    h = ""
    for i, t in enumerate(tns):
        atv = ativo and ((agora_br.hour < 8 and i == 0) or (8 <= agora_br.hour < 16 and i == 1) or (agora_br.hour >= 16 and i == 2))
        cor = "#FF9F1C" if atv else ("#E74C3C" if t["s"] == "EM FOLGA" else ("#fff" if t["v"] > 0 else "#64748b"))
        borda = "#FF9F1C" if atv else "#1c2b42"
        h += f'<div class="mini" style="border-color:{borda};"><div class="a">{t["letra"]} {"🟢" if atv else ""}</div><div class="a" style="font-size:.65rem;">{t["h"]}</div><div class="b" style="color:{cor};">{t["s"]}</div></div>'
    return f'<div class="cols">{h}</div>'


def ordena_dest(d):
    n = str(d["destino"]).upper()
    if "MI" in n or "LATAM" in n: return 999999
    try: return int(re.search(r'\d+', n).group())
    except Exception: return 0


tab_dest = ""
for d in sorted(balanco_destinos, key=ordena_dest, reverse=True):
    n = str(d["destino"]).upper()
    nome = "MI / LATAM" if ("MI" in n or "LATAM" in n) else (f"{n.split('-')[0].strip()} - {n.split('-')[1].strip()}" if len(n.split('-')) >= 2 else n)
    sd = ("0", "#00D672") if d["saldo"] <= 0 and d["realizado"] > 0 else (fmt(d["saldo"]), "#E5B800")
    ca = "#00D672" if d["atingimento"] >= 100 else ("#38bdf8" if d["atingimento"] > 0 else "#64748b")
    tab_dest += f'<tr><td><b>{esc(nome)}</b></td><td style="color:#38bdf8;">{fmt(d["meta"])}</td><td style="color:#00D672;">{fmt(d["realizado"])}</td><td style="color:{sd[1]};">{sd[0]}</td><td style="color:{ca};">{d["atingimento"]:.0f}%</td></tr>'
tab_dest = f'<table class="tb"><tr><th>Destino</th><th>Plano</th><th>Carr.</th><th>Falta</th><th>%</th></tr>{tab_dest}</table>' if tab_dest else '<div style="color:#64748b;text-align:center;">Nenhum destino ativo.</div>'
totais = f'<div class="cols" style="margin-top:12px;"><div class="mini"><div class="a">PLANO TOTAL</div><div class="b">{fmt(total_exp_meta)} t</div></div><div class="mini"><div class="a" style="color:#38bdf8;">CARREGADO</div><div class="b" style="color:#38bdf8;">{fmt(total_exp_real)} t</div></div><div class="mini"><div class="a" style="color:#FF9F1C;">PENDENTE</div><div class="b" style="color:#FF9F1C;">{fmt(total_exp_falta)} t</div></div></div>'

exp_html = (f'<div class="bar" style="--c:#00D672;height:8px;margin:0 0 14px 0;"><div style="width:{pct_prog:.0f}%"></div></div>'
            f'<div style="color:#cbd5e1;font-size:.8rem;margin-bottom:10px;">Progresso: <b style="color:#fff;">{fmt(vol_hoje)} t</b> de <b style="color:#fff;">{fmt(prev_carr)} t</b> ({pct_prog:.0f}%) • Ontem (D-1): <b style="color:#00D672;">{fmt(vol_ontem)} t</b></div>'
            f'<div class="sec-lbl" style="border-color:#00D672;">Turnos hoje</div>{cards_turno(tns_hoje, True)}'
            f'<div class="sec-lbl">Turnos ontem</div>{cards_turno(tns_ontem)}'
            f'<div class="sec-lbl" style="border-color:#E5B800;">Plano vs Expedido</div>{tab_dest}{totais}')


def tab_pedidos(lst):
    if not lst:
        return '<div style="color:#64748b;text-align:center;padding:10px;">Nenhum pedido ativo.</div>'
    h = '<table class="tb"><tr><th>Destino / Ordem</th><th>Material</th><th>Saldo</th><th>Meta</th><th>Atend.</th><th>Próximo</th></tr>'
    for i in lst:
        m = i["material"].upper()
        cm = "#FF2E2E" if "OS" in m else ("#FF8C00" if "BQ" in m else ("#FFD600" if "SQ" in m else "#00FF7F"))
        pct = min(100.0, max(0.0, (i["qtd_ini"] - i["saldo"]) / i["qtd_ini"] * 100.0)) if i["qtd_ini"] > 0 else 0
        fim = ' <span class="pill" style="background:rgba(255,46,46,.2);color:#ff8080;font-size:.6rem;">FIM</span>' if i["is_fim"] else ""
        h += (f'<tr style="{"background:rgba(255,46,46,.07);" if i["is_fim"] else ""}"><td><b>{esc(i["destino"])}</b>{fim}<br><small style="color:#64748b;">{esc(i["pedido"])}</small></td>'
              f'<td style="color:{cm};font-weight:800;">{esc(i["material"])}</td><td style="color:{"#FF2E2E" if i["is_fim"] else "#38bdf8"};font-weight:800;">{fmt(i["saldo"])}</td>'
              f'<td>{fmt(i["qtd_ini"])}</td><td style="color:#00FF7F;">{pct:.0f}%</td><td style="font-size:.7rem;color:#94a3b8;">{esc(i["prox"])}</td></tr>')
    return h + '</table>'


txt_ped = f"Base {hora_att_ped.split(' ')[1][:5]}" if hora_att_ped and " " in hora_att_ped else (f"Base {hora_att_ped[:5]}" if hora_att_ped and hora_att_ped != "--:--" else "")
ped_html = (f'<div class="cols" style="margin-bottom:10px;"><div class="mini"><div class="a">TOTAL PENDENTE</div><div class="b">{fmt(tot_saldo_geral)} t</div></div>'
            f'<div class="mini" style="border-color:#0084FF;"><div class="a">🚛 TRANSF. ({len(pedidos_transf)})</div><div class="b">{fmt(tot_saldo_transf)} t</div></div>'
            f'<div class="mini" style="border-color:#00D672;"><div class="a">🏢 MI/LATAM ({len(pedidos_mi)})</div><div class="b">{fmt(tot_saldo_mi)} t</div></div></div>'
            f'<div class="scroll"><div class="sec-lbl" style="border-color:#0084FF;">Transferência</div>{tab_pedidos(pedidos_transf)}'
            f'<div class="sec-lbl" style="border-color:#00D672;">MI / LATAM</div>{tab_pedidos(pedidos_mi)}</div>')

_noop('<div class="g2e">' + pn("Expedição Realizada", "🚚", exp_html, "", "#00D672", "sec-exp") + pn("Análise de Pedidos (ZLE087)", "📑", ped_html, txt_ped, "#0084FF") + '</div>')

# ==============================================================================
# 🖨️ LINHA 6: ESTOQUE | FROTA
# ==============================================================================
linhas_est = "".join(
    f'<tr><td>📦 <b>{esc(i["material"])}</b></td><td><span class="pill" style="background:transparent;border:1px solid {CORES_CLASSE.get(i["classe"],"#38bdf8")};color:{CORES_CLASSE.get(i["classe"],"#38bdf8")};">{esc(i["classe"])}</span></td>'
    f'<td style="text-align:right;color:{CORES_CLASSE.get(i["classe"],"#38bdf8")};font-weight:800;">{fmt(i["ton"])} t</td></tr>' for i in itens_estoque) or '<tr><td colspan="3" style="color:#64748b;">Aguardando dados segregados...</td></tr>'
est_html = (f'<div style="color:#cbd5e1;font-size:.8rem;">Ocupação: <b style="color:#fff;">{fmt(estoque_total)} t</b> de <b style="color:#fff;">{fmt(CAPACIDADE_MAX_ARMAZEM)} t</b> ({pct_ocup:.0f}%)</div>'
            f'<div class="bar" style="--c:#00FF7F;height:8px;margin-bottom:12px;"><div style="width:{pct_ocup:.1f}%"></div></div>'
            f'<div class="scroll" style="max-height:230px;"><table class="tb"><tr><th>Material</th><th>Classe</th><th style="text-align:right;">Ton</th></tr>{linhas_est}</table></div>'
            f'<div style="display:flex;height:8px;border-radius:999px;overflow:hidden;background:#14243b;margin:12px 0;"><div style="width:{pct_on:.1f}%;background:#00FF7F;"></div><div style="width:{pct_off:.1f}%;background:linear-gradient(90deg,#FFD600,#FF8C00,#FF2E2E);"></div></div>'
            f'<div class="cols"><div class="mini" style="border-color:#00FF7F;"><div class="a" style="color:#00FF7F;">ON-GRADE</div><div class="b">{fmt(tot_on)} t <small style="font-size:.7rem;color:#64748b;">({pct_on:.0f}%)</small></div></div>'
            f'<div class="mini" style="border-color:#FF8C00;"><div class="a" style="color:#FF8C00;">OFF-GRADE</div><div class="b">{fmt(tot_off)} t <small style="font-size:.7rem;color:#64748b;">({pct_off:.0f}%)</small></div></div></div>')

tipos = sorted({e["tipo"] for e in frota}, key=lambda t: (ordem_tipo(t), t))
linhas_fr = "".join(
    f'<tr><td><b>{esc(t)}</b></td><td style="color:#00D672;">{sum(1 for e in frota if e["tipo"]==t and not e["off"])}</td>'
    f'<td style="color:#E74C3C;">{sum(1 for e in frota if e["tipo"]==t and e["off"])}</td><td style="color:#FFD600;">{sum(1 for e in frota if e["tipo"]==t and e["sev"]<=1)}</td></tr>' for t in tipos) or '<tr><td colspan="4" style="color:#64748b;">Aguardando Preventiva_Inspecao...</td></tr>'


def cor_alerta(a):
    a = str(a).upper()
    if any(x in a for x in ["VENCIDA", "CRITICO", "CRÍTICO"]): return "#E74C3C"
    if any(x in a for x in ["ATENCAO", "ATENÇÃO", "PROXIMA", "PRÓXIMA"]): return "#FFD600"
    if "SEM META" in a or a in ["--", "NAN", ""]: return "#64748b"
    return "#00D672"


crit = sorted([e for e in frota if e["sev"] <= 2], key=lambda e: (e["sev"], ordem_tipo(e["tipo"]), e["tag"]))
linhas_crit = "".join(
    f'<tr><td>{"🔴" if e["off"] else "🟢"} <b>{esc(e["tag"])}</b></td><td style="font-family:monospace;color:#38bdf8;">{esc(e["horim"])}</td>'
    f'<td style="color:{cor_alerta(e["a_prev"])};font-weight:800;">{esc(e["a_prev"])}</td><td style="color:{cor_alerta(e["a_insp"])};font-weight:800;">{esc(e["a_insp"])}</td></tr>' for e in crit) or '<tr><td colspan="4" style="color:#00D672;">Nenhuma preventiva crítica/próxima.</td></tr>'
off_tags = ", ".join(e["tag"] for e in frota if e["off"]) or "nenhum"
txt_prev = f"Base {hora_att_prev.split(' ')[1][:5]}" if hora_att_prev and " " in hora_att_prev else ""
fr_html = (f'<div class="cols" style="margin-bottom:10px;"><div class="mini"><div class="a">ONLINE</div><div class="b" style="color:#00D672;">{total_online}</div></div>'
           f'<div class="mini"><div class="a">OFFLINE</div><div class="b" style="color:#E74C3C;">{total_offline}</div></div>'
           f'<div class="mini"><div class="a">PREV. CRÍTICAS</div><div class="b" style="color:#FFD600;">{qtd_criticos}</div></div></div>'
           f'<table class="tb"><tr><th>Tipo</th><th>Online</th><th>Offline</th><th>Críticas</th></tr>{linhas_fr}</table>'
           f'<div style="color:#94a3b8;font-size:.75rem;margin:8px 0;">🔴 Offline: <b style="color:#E74C3C;">{esc(off_tags)}</b></div>'
           f'<div class="sec-lbl" style="border-color:#E67E22;">Preventiva / Inspeção (críticas e próximas)</div>'
           f'<div class="scroll" style="max-height:200px;"><table class="tb"><tr><th>TAG</th><th>Horím.</th><th>Prevent.</th><th>Inspeção</th></tr>{linhas_crit}</table></div>')

_noop('<div class="g2e">' + pn("Estoque Físico no Armazém", "📦", est_html, "", "#00FF7F", "sec-est") + pn("Frota & Manutenção", "🚜", fr_html, txt_prev, "#E67E22", "sec-frota") + '</div>')

# ==============================================================================
# 🖨️ LINHA 7: BAFÔMETRO | COMPARATIVO ANUAL
# ==============================================================================
def lista_baf(lst, cor):
    if not lst: return '<div style="color:#64748b;font-size:.75rem;padding:4px;">Nenhum colaborador.</div>'
    return "".join(f'<div class="row" style="font-size:.78rem;"><span><b style="color:#fff;">{esc(i["nome"])}</b><br><small style="color:#64748b;">{esc(i["funcao"])}</small></span><span style="color:{cor};font-weight:800;">{esc(i["res"] if i["res"] not in ["", "--", "NAN", "NONE"] else (i["status"] or "--"))}</span></div>' for i in sorted(lst, key=lambda x: x["nome"]))


txt_baf = f"Atualizado {hora_base_baf}" if hora_base_baf else ""
baf_html = (f'<div style="color:#cbd5e1;font-weight:700;margin-bottom:10px;">Turno {letra_v} ({esc(per_rot)}) &nbsp;|&nbsp; {total_baf} auditados</div>'
            f'<div class="cols">'
            f'<div style="background:#070d18;border:1px solid #142842;border-left:3.5px solid #E74C3C;border-radius:10px;padding:10px;"><div style="color:#E74C3C;font-weight:800;font-size:.75rem;">🚨 PENDENTES ({len(lst_pend)})</div><div class="scroll" style="max-height:260px;">{lista_baf(lst_pend,"#E74C3C")}</div></div>'
            f'<div style="background:#070d18;border:1px solid #142842;border-left:3.5px solid #38bdf8;border-radius:10px;padding:10px;"><div style="color:#38bdf8;font-weight:800;font-size:.75rem;">🔄 TROCAS ({len(lst_troca)})</div><div class="scroll" style="max-height:260px;">{lista_baf(lst_troca,"#38bdf8")}</div></div>'
            f'<div style="background:#070d18;border:1px solid #142842;border-left:3.5px solid #00D672;border-radius:10px;padding:10px;"><div style="color:#00D672;font-weight:800;font-size:.75rem;">✅ APROVADOS ({len(lst_ok)})</div><div class="scroll" style="max-height:260px;">{lista_baf(lst_ok,"#00D672")}</div></div></div>')

ano_html = (f'<div class="cols" style="margin-bottom:12px;"><div class="mini" style="text-align:left;"><div class="a" style="color:#007BFF;">EXPEDIÇÃO ANUAL</div><div class="b">{fmt(ca_at)} t</div><div class="a">Proj. 31/12: <span style="color:#007BFF;">{fmt(pcf)} t</span></div></div>'
            f'<div class="mini" style="text-align:left;"><div class="a" style="color:#00D672;">PRODUÇÃO ANUAL</div><div class="b">{fmt(pa_at)} t</div><div class="a">Proj. 31/12: <span style="color:#00D672;">{fmt(ppf)} t</span></div></div></div>'
            f'<div class="mini" style="text-align:left;font-size:.85rem;color:#cbd5e1;">Variação: <b style="color:{cv};">{tv}</b><br>Estoque Meta: <b style="color:#38bdf8;">{fmt(meta_est)} t</b><br>Meta diária necessária: <b style="color:#007BFF;">{fmt(mdc)} t/dia</b></div>')
txt_ano = f"Base {data_ref_ano}" if data_ref_ano else ""

_noop('<div class="g2">' + pn("Auditoria Bafômetro (H&S)", "🩺", baf_html, txt_baf, cor_baf, "sec-baf") +
            pn("Comparativo Produção vs Expedição", "📊", ano_html, txt_ano, "#007BFF", "sec-ano") + '</div>')



# ==============================================================================
# 🖥️ LAYOUT COMPACTO: TUDO EM 1 TELA + BLOCOS QUE EXPANDEM AO CLICAR
#     (modal 100% CSS via :target — não depende de JavaScript nem de rerun)
# ==============================================================================
CSS_COMPACTO = """
<style>
html, body, [data-testid="stAppViewContainer"], .stApp, [data-testid="stMain"] { overflow: hidden !important; height: 100vh !important; }
.block-container { padding: 10px 14px 0 244px !important; height: 100vh !important; max-width: 100% !important; overflow: hidden !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }
.dash { display: grid; grid-template-rows: 54px 92px minmax(0,1.45fr) minmax(0,1fr); gap: 10px; height: calc(100vh - 20px); }
.r2 { display: grid; grid-template-columns: repeat(5,1fr); gap: 10px; min-height: 0; }
.r3 { display: grid; grid-template-columns: 6fr 3fr 3fr; gap: 10px; min-height: 0; }
.r4 { display: grid; grid-template-columns: repeat(5,1fr); gap: 10px; min-height: 0; }
.dash .pn { padding: 10px 14px; overflow: hidden; min-height: 0; }
.dash .pn-t { margin-bottom: 8px; font-size: .85rem; }
.dash .hd { margin: 0; padding: 4px 18px; }
.dash .hd img { height: 40px; }
.dash .kpi .v { font-size: 1.7rem; margin: 2px 0; }
.dash .row { padding: 5px 0; }
.dash .ring { width: 84px; height: 84px; }
.dash .ring > div { width: 64px; height: 64px; }
.big { color: #fff; font-size: 1.8rem; font-weight: 800; line-height: 1.1; margin-bottom: 6px; }
.big span { font-size: .85rem; color: #94a3b8; font-weight: 500; }

/* BLOCOS CLICÁVEIS */
a.tile { display: flex; flex-direction: column; position: relative; text-decoration: none !important; color: inherit !important; cursor: pointer; transition: .18s; }
a.tile:hover { transform: translateY(-2px); box-shadow: 0 0 18px rgba(0,214,114,.28); border-color: #00D672 !important; }
a.tile .exp { position: absolute; top: 8px; right: 12px; color: #64748b; font-size: .95rem; }
a.tile:hover .exp { color: #00D672; }
.flexfill { flex: 1; min-height: 0; }

/* MODAL (EXPANDIR) */
.md { display: none; position: fixed; inset: 0; z-index: 1000; align-items: center; justify-content: center;
      background: rgba(2,6,12,.82); backdrop-filter: blur(4px); }
.md:target { display: flex; }
.md-bg { position: absolute; inset: 0; cursor: default; }
.md-box { position: relative; width: min(1180px, 92vw); max-height: 90vh; overflow-y: auto; box-shadow: 0 0 40px rgba(0,0,0,.7); padding: 18px 22px !important; }
.md-x { position: absolute; top: 12px; right: 16px; width: 34px; height: 34px; border-radius: 50%; border: 1.5px solid #E74C3C;
        color: #fff !important; text-decoration: none !important; display: flex; align-items: center; justify-content: center; font-weight: 800; }
.md-x:hover { background: #E74C3C; }

@media (max-height: 760px) {
  html, body, [data-testid="stAppViewContainer"], .stApp, [data-testid="stMain"], .block-container { overflow: auto !important; height: auto !important; }
  .dash { height: auto; grid-template-rows: 54px 92px 420px 330px; }
}
</style>
"""
st.markdown(CSS_COMPACTO, unsafe_allow_html=True)


def eh_erro_real(texto):
    t = str(texto).upper()
    if "SINCRONIZAÇÃO CONCLUÍDA" in t or "SINCRONIZACAO CONCLUIDA" in t:
        return False
    if any(x in t for x in ["ERRO", "FALHA", "CRÍTICO", "CRITICO", "DEADLOCK", "HARD KILL", "MODO DE RECUPERAÇÃO", "MODO DE RECUPERACAO", "REINICIANDO EM", "SEM CONEXÃO", "SEM CONEXAO"]):
        return True
    if "❌" in t and "EXCLUÍDA" not in t and "EXCLUIDA" not in t: return True
    if "🚨" in t and "TEMPO CRÍTICO" not in t: return True
    return False


def ktile(href, titulo, ico, valor, unid, sub, cor, pct=None):
    barra = f'<div class="bar"><div style="width:{pct:.0f}%"></div></div>' if pct is not None else ""
    return (f'<a class="pn kpi tile" href="#{href}" style="--c:{cor};"><span class="exp">⤢</span>'
            f'<div class="l">{ico} {titulo}</div><div class="v">{valor} <span>{unid}</span></div><div class="s">{sub}</div>{barra}</a>')


def tile(href, titulo, ico, corpo, cor="#12506e"):
    return (f'<a class="pn tile" href="#{href}" style="border-color:{cor};"><span class="exp">⤢</span>'
            f'<div class="pn-t"><span>{ico}</span>{titulo}</div><div class="flexfill">{corpo}</div></a>')


def box(titulo, ico, corpo, cor="#12506e"):
    return (f'<div class="pn" style="border-color:{cor};display:flex;flex-direction:column;">'
            f'<div class="pn-t"><span>{ico}</span>{titulo}</div><div class="flexfill">{corpo}</div></div>')


def modal(id_, titulo, ico, corpo, cor="#12506e", extra=""):
    return (f'<div class="md" id="{id_}"><a class="md-bg" href="#sec-topo"></a>'
            f'<div class="md-box pn" style="border-color:{cor};"><a class="md-x" href="#sec-topo">✕</a>'
            f'<div class="pn-t" style="font-size:1.05rem;"><span>{ico}</span>{titulo}<small>{extra}</small></div>{corpo}</div></div>')


# ---------- LOGS (modal) ----------
def logs_modal_html():
    if df_logs.empty:
        return '<div style="color:#64748b;padding:16px;">Nenhum log disponível (aba Live_Logs_Core sem dados ou sem acesso).</div>'
    qtd = int(df_logs["EVENTO"].apply(eh_erro_real).sum())
    out = f'<div style="color:#cbd5e1;font-size:.85rem;margin-bottom:10px;">Últimos {len(df_logs)} eventos • Erros reais: <b style="color:{"#E74C3C" if qtd else "#00D672"};">{qtd}</b></div><div class="scroll" style="max-height:62vh;">'
    for _, r in df_logs.iterrows():
        ev, mod = str(r["EVENTO"]), str(r["MODULO"])
        h = str(r["DATA_HORA"]).split(" ")[-1]
        if eh_erro_real(ev) or any(x in ev.upper() for x in ["❌", "🚨"]): bc, tc, bg = "#EF4444", "#FCA5A5", "#241010"
        elif any(x in ev.upper() for x in ["⚠️", "ATENÇÃO", "PAUSA"]): bc, tc, bg = "#F59E0B", "#FDE68A", "#261A08"
        elif "✅" in ev: bc, tc, bg = "#10B981", "#A7F3D0", "#081E15"
        else: bc, tc, bg = "#12506e", "#CBD5E1", "#08111f"
        out += f'<div style="background:{bg};border-left:3px solid {bc};border-radius:6px;padding:6px 10px;margin-bottom:5px;font-family:monospace;font-size:.78rem;"><span style="color:#64748B;">[{h}]</span> <b style="color:#38bdf8;">[{esc(mod)}]</b> <span style="color:{tc};">{esc(ev)}</span></div>'
    return out + '</div>'


# ---------- SIDEBAR + HEADER ----------
menu_c = [("sec-topo", "🏠", "Início", True), ("md-prod", "🏭", "Produção", False), ("md-exp", "🚚", "Expedição", False),
          ("md-patio", "🏢", "Pátio", False), ("md-frota", "🚜", "Frota", False), ("md-baf", "🩺", "Bafômetro", False),
          ("md-ped", "📑", "Pedidos", False), ("md-est", "📦", "Estoque", False), ("md-tele", "📡", "Telemetria", False),
          ("md-ano", "📈", "Relatórios", False)]
links_c = "".join(f'<a href="#{i}" class="{"on" if on else ""}"><span>{ic}</span>{nm}</a>' for i, ic, nm, on in menu_c)

sidebar_hd = f"""
<div class="sb">
  <div class="sb-logo"><img src="{LOGO_ALOVE_URL}"><b>A.L.O.V.E.</b><small>Logística em Tempo Real</small></div>
  {links_c}
  <div class="sb-st" style="border-color:{st_geral_cor};"><b style="color:{st_geral_cor};">● {st_geral_txt}</b><small>Atualização automática a cada 1 minuto</small></div>
</div>
<div id="sec-topo"></div>
"""
header_c = f"""
<div class="hd">
  <div style="width:200px;"><img src="{BANNER_TOPO_URL}"></div>
  <div class="sub">Assistente Logístico Virtual da Expedição</div>
  <div class="up"><span class="dot" style="background:{conn_cor};box-shadow:0 0 8px {conn_cor};"></span>
    <div>Última atualização:<br><b style="color:#fff;">{conn_data_full}</b></div>
    <a href="?refresh=1" target="_self">🔄</a></div>
</div>
"""

# ---------- LINHA 2: KPIs (clicáveis) ----------
kpis_c = (
    ktile("md-prod", "Produção Hoje", "🏭", fmt(prod_hoje_calc), "t", f"Prev. 24h: {fmt(prev_prod)} t", "#38bdf8", pct_prod) +
    ktile("md-exp", "Expedição Hoje", "🚚", fmt(vol_hoje), "t", f"Prev. 24h: {fmt(prev_carr)} t", "#00D672", pct_prog) +
    ktile("md-patio", "Pátio Atual", "🏗️", fmt(vol_patio_disponivel), "t", f"{total_veiculos_fisicos} veículos físicos", "#FF9F1C") +
    ktile("md-frota", "Frota Ativa", "🚜", f"{disp_frota:.0f}", "%", f"{total_online}/{total_frota} online • {qtd_criticos} prev. críticas", "#a78bfa", disp_frota) +
    ktile("md-baf", "Bafômetro", "🩺", f"{conf_baf:.0f}", "%", f"{len(lst_pend)} pendências", cor_baf, conf_baf)
)

# ---------- LINHA 3: GRÁFICO | STATUS | INDICADORES ----------
grafico_tile = tile("md-exp", "Evolução Operacional", "📊", leg + f'<div style="height:calc(100% - 26px);">{grafico}</div>')
status_tile = box("Status da Operação", "🚚", st_html)
ind_tile = box("Indicadores Principais", "🎯", f'<div style="display:flex;align-items:center;height:100%;">{ind_html.replace("grid-template-columns:repeat(4,1fr)", "grid-template-columns:repeat(2,1fr);width:100%").replace("gap:6px", "gap:14px 6px")}</div>')

# ---------- LINHA 4: TILES RESUMO ----------
n_fim = sum(1 for i in pedidos_transf + pedidos_mi if i["is_fim"])
ped_tile = tile("md-ped", "Pedidos ZLE087", "📑",
                f'<div class="big">{fmt(tot_saldo_geral)} <span>t pendentes</span></div>'
                f'<div class="row"><span>🚛 Transf. ({len(pedidos_transf)})</span><b>{fmt(tot_saldo_transf)} t</b></div>'
                f'<div class="row"><span>🏢 MI/LATAM ({len(pedidos_mi)})</span><b>{fmt(tot_saldo_mi)} t</b></div>'
                f'<div class="row"><span>⚠️ Fim de pedido</span><b style="color:{"#FF2E2E" if n_fim else "#00D672"};">{n_fim}</b></div>', "#0084FF")
est_tile = tile("md-est", "Estoque Físico", "📦",
                f'<div class="big">{fmt(estoque_total)} <span>t • {pct_ocup:.0f}% de {fmt(CAPACIDADE_MAX_ARMAZEM)} t</span></div>'
                f'<div class="bar" style="--c:#00FF7F;height:8px;margin:0 0 8px 0;"><div style="width:{pct_ocup:.1f}%"></div></div>'
                f'<div class="row"><span style="color:#00FF7F;">● On-grade</span><b>{fmt(tot_on)} t ({pct_on:.0f}%)</b></div>'
                f'<div class="row"><span style="color:#FF8C00;">● Off-grade</span><b>{fmt(tot_off)} t ({pct_off:.0f}%)</b></div>', "#00FF7F")
ano_tile = tile("md-ano", "Produção vs Expedição (Ano)", "📊",
                f'<div class="row"><span style="color:#007BFF;">Expedição anual</span><b>{fmt(ca_at)} t</b></div>'
                f'<div class="row"><span style="color:#00D672;">Produção anual</span><b>{fmt(pa_at)} t</b></div>'
                f'<div class="row"><span>Variação</span><b style="color:{cv};font-size:.78rem;">{tv}</b></div>'
                f'<div class="row"><span>Meta diária necessária</span><b style="color:#007BFF;">{fmt(mdc)} t/dia</b></div>', "#007BFF")
tele_mini = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">' + "".join(
    f'<div class="mini" style="border-color:{"#00D672" if m["status"] == "ONLINE" else "#E74C3C"};padding:8px;"><div class="a">{m["ico"]} {m["nome"]}</div><div class="a" style="color:{"#00D672" if m["status"] == "ONLINE" else "#E74C3C"};font-weight:800;">{m["status"]}</div></div>'
    for m in modulos) + '</div>'
tele_tile = tile("md-tele", "Telemetria", "📡", f'<div style="color:{st_geral_cor};font-weight:800;font-size:.8rem;margin-bottom:8px;">● {st_geral_txt}</div>{tele_mini}', st_geral_cor)
logs_tile = tile("md-logs", "Últimas Atualizações", "📋", ult_html)

# ---------- MODAIS ----------
modais = (
    modal("md-prod", "Produção de Celulose", "🏭", f'<div class="g2e" style="margin:0;">{prod_resumo}<div></div></div>{prod_html}', "#E5B800") +
    modal("md-exp", "Expedição Realizada", "🚚", exp_html, "#00D672") +
    modal("md-patio", "Pátio da Fábrica", "🏭", patio_resumo + patio_html, "#38a9ff", txt_pat) +
    modal("md-frota", "Frota & Manutenção", "🚜", fr_html, "#E67E22", txt_prev) +
    modal("md-baf", "Auditoria Bafômetro (H&S)", "🩺", baf_html, cor_baf, txt_baf) +
    modal("md-ped", "Análise de Pedidos (ZLE087)", "📑", ped_html, "#0084FF", txt_ped) +
    modal("md-est", "Estoque Físico no Armazém", "📦", est_html, "#00FF7F") +
    modal("md-ano", "Comparativo Produção vs Expedição", "📊", ano_html, "#007BFF", txt_ano) +
    modal("md-tele", "Telemetria do Ecossistema", "🛡️", tele_html, st_geral_cor) +
    modal("md-logs", "Console de Logs do Core", "🛠️", logs_modal_html(), "#12506e")
)

render_html(f"""
{sidebar_hd}
<div class="dash">
  {header_c}
  <div class="r2">{kpis_c}</div>
  <div class="r3">{grafico_tile}{status_tile}{ind_tile}</div>
  <div class="r4">{ped_tile}{est_tile}{ano_tile}{tele_tile}{logs_tile}</div>
</div>
{modais}
""")
