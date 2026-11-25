import streamlit as st
from supabase import create_client
from streamlit_js_eval import get_geolocation, streamlit_js_eval
import pandas as pd
import requests
import urllib.parse
import math
import uuid
import hashlib
import os
import io
import re
import base64
from datetime import datetime
from PIL import Image

# --- DADOS OFICIAIS DA EMPRESA ---
NOME_EMPRESA = "Sweets da Bruna"
CNPJ_EMPRESA = "36.810.827/0001-08"
ENDERECO_LOJA = "Rua Nicola Silveira, 470 • Jardim Primavera I, Rondonópolis - MT"
ARQUIVO_LOGO = "logo.png"

# --- CREDENCIAIS E CONFIGURAÇÕES ---
SUPABASE_URL = "https://urghdzleaeocrsrvcnzx.supabase.co"
SUPABASE_KEY = "sb_publishable_Xmc5ZOqss7NH2fuQgIvyFg_iy5DYwN6"

WHATSAPP_LOJA = "5566999892764"       # WhatsApp oficial da loja (55 + 66 + 999892764)
CPF_ADMIN = "062.582.881-03"          # CPF da Bruna
SENHA_ADMIN = "1234"                  # Senha de acesso
CHAVE_PIX = "36810827000108"          # Chave Pix da empresa
NOME_RECEBEDOR = "SWEETS DA BRUNA"    # Até 25 letras, sem acento
CIDADE_RECEBEDOR = "RONDONOPOLIS"     # Até 15 letras, sem acento

# --- LOCALIZAÇÃO EXATA DA DOCERIA (Rua Nicola Silveira, 470 - Jardim Primavera, Rondonópolis - MT) ---
LAT_LOJA = -16.448401
LON_LOJA = -54.614900
LINK_MAPS_LOJA = f"https://www.google.com/maps/search/?api=1&query={LAT_LOJA},{LON_LOJA}"

# --- TABELA DE PREÇOS DO ENTREGADOR ---
TABELA_FRETE = [
    (2.0, 6.00),
    (4.0, 9.00),
    (6.0, 12.00),
    (10.0, 16.00),
]
DISTANCIA_MAXIMA_KM = 10.0

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CONFIGURAÇÕES DA LOJA ---
def obter_config_loja() -> dict:
    try:
        res = supabase.table("config_loja").select("*").eq("id", 1).execute()
        if res.data:
            return res.data[0]
    except Exception:
        pass
    return {
        "aberta": True,
        "fidelidade_ativa": True,
        "meta_valor": 50.0,
        "fidelidade_desconto": 15,
        "ultimo_numero_dia": 0,
        "logo_url": None,
        "inicio_dia": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    }

def salvar_config_loja(dados: dict):
    dados["id"] = 1
    supabase.table("config_loja").upsert(dados).execute()

config_loja = obter_config_loja()
logo_atual_url = config_loja.get("logo_url")

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title=f"{NOME_EMPRESA} | Pronta Entrega",
    page_icon=logo_atual_url if logo_atual_url else (ARQUIVO_LOGO if os.path.exists(ARQUIVO_LOGO) else "🧁"),
    layout="centered"
)

# --- VISUAL CLEAN APP (DESIGN MODERNO & TECNOLÓGICO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(180deg, #FFF1F5 0%, #F8FAFC 240px, #F8FAFC 100%);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    div.stButton > button, div.stLinkButton > a, div.stDownloadButton > button {
        border-radius: 14px !important;
        padding: 0.65rem 1.25rem !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.2px !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    div.stButton > button[kind="primary"],
    div.stLinkButton > a[kind="primary"],
    div.stDownloadButton > button[kind="primary"] {
        background: linear-gradient(135deg, #E11D48 0%, #FB7185 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 6px 18px rgba(225, 29, 72, 0.28) !important;
    }

    div.stButton > button[kind="primary"]:hover,
    div.stLinkButton > a[kind="primary"]:hover,
    div.stDownloadButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 24px rgba(225, 29, 72, 0.38) !important;
        filter: brightness(1.04) !important;
    }

    div.stButton > button[kind="secondary"],
    div.stLinkButton > a[kind="secondary"] {
        background: #FFFFFF !important;
        color: #0F172A !important;
        border: 1.5px solid #E2E8F0 !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
    }

    div.stButton > button[kind="secondary"]:hover:not(:disabled),
    div.stLinkButton > a[kind="secondary"]:hover {
        border-color: #E11D48 !important;
        color: #E11D48 !important;
        background: #FFF1F5 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(225, 29, 72, 0.12) !important;
    }

    div.stButton > button:disabled {
        background: #F1F5F9 !important;
        color: #94A3B8 !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: none !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF !important;
        border-radius: 20px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05) !important;
        padding: 16px !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #FDA4AF !important;
        box-shadow: 0 12px 30px rgba(225, 29, 72, 0.09) !important;
    }

    div[data-testid="stImage"] img {
        border-radius: 14px !important;
        object-fit: cover !important;
    }

    div[data-baseweb="tab-list"] {
        gap: 6px !important;
        background: #F1F5F9 !important;
        padding: 5px !important;
        border-radius: 16px !important;
    }

    button[data-baseweb="tab"] {
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        padding: 8px 16px !important;
        color: #475569 !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background: #FFFFFF !important;
        color: #E11D48 !important;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.08) !important;
    }

    div[data-baseweb="tab-highlight"] {
        display: none !important;
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"] > input {
        border-radius: 12px !important;
        border-color: #CBD5E1 !important;
        background-color: #FFFFFF !important;
    }

    div[data-baseweb="input"] > div:focus-within {
        border-color: #E11D48 !important;
        box-shadow: 0 0 0 3px rgba(225, 29, 72, 0.14) !important;
    }

    div[data-testid="stMetric"] {
        background: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 14px 16px !important;
    }

    div[data-testid="stAlert"] {
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04) !important;
    }

    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 6px 0 10px 0;
    }
    .badge-entrega {
        background: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 800;
    }
    .badge-retirada {
        background: #F5F3FF;
        color: #6D28D9;
        border: 1px solid #DDD6FE;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 800;
    }
    .badge-pago {
        background: #ECFDF5;
        color: #047857;
        border: 1px solid #A7F3D0;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 800;
    }
    .badge-pendente {
        background: #FEF3C7;
        color: #B45309;
        border: 1px solid #FDE68A;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# --- CONTROLE DE SESSÃO PERSISTENTE ---
def gerar_token_admin() -> str:
    cpf_limpo = re.sub(r"\D", "", CPF_ADMIN)
    segredo = f"SWEETS_AUTH_{cpf_limpo}_{SENHA_ADMIN}_{CNPJ_EMPRESA}"
    return hashlib.sha256(segredo.encode("utf-8")).hexdigest()

def formatar_telefone(valor: str) -> tuple[str, bool]:
    digitos = re.sub(r"\D", "", valor)[:11]
    if len(digitos) == 10:
        return f"{digitos[:3]}.{digitos[3:6]}-{digitos[6:]}", True
    elif len(digitos) == 11:
        return f"{digitos[:3]}.{digitos[3:7]}-{digitos[7:]}", True
    return digitos, False

def gerar_proximo_numero_dia() -> int:
    cfg = obter_config_loja()
    proximo = int(cfg.get("ultimo_numero_dia", 0)) + 1
    cfg["ultimo_numero_dia"] = proximo
    salvar_config_loja(cfg)
    return proximo

def renderizar_etiquetas_pedido(entrega: str, pago: bool):
    badge_tipo = (
        "<span class='badge-entrega'>🛵 ENTREGA (DELIVERY)</span>"
        if entrega == "Entrega (Delivery)"
        else "<span class='badge-retirada'>🛍️ RETIRADA NO LOCAL</span>"
    )
    badge_pag = (
        "<span class='badge-pago'>✅ PIX PAGO</span>"
        if pago
        else "<span class='badge-pendente'>⏳ PIX PENDENTE</span>"
    )
    st.markdown(f"<div class='badge-row'>{badge_tipo}{badge_pag}</div>", unsafe_allow_html=True)

# --- CANCELAMENTO E DEVOLUÇÃO AUTOMÁTICA AO ESTOQUE ---
def cancelar_pedido_e_devolver_estoque(pedido: dict):
    produtos_db = listar_produtos()
    mapa_por_nome = {p["nome"].strip().lower(): p for p in produtos_db}

    for parte in (pedido.get("itens") or "").split(" | "):
        m = re.match(r"^(\d+)x\s+(.+?)\s+\(R\$", parte)
        if m:
            qtd_devolver = int(m.group(1))
            nome_doce = m.group(2).strip().lower()
            prod = mapa_por_nome.get(nome_doce)
            if prod:
                novo_est = int(prod["estoque"]) + qtd_devolver
                supabase.table("produtos").update({"estoque": novo_est}).eq("id", prod["id"]).execute()

    supabase.table("pedidos").update({
        "status": "cancelado",
        "itens_acrescentados": ""
    }).eq("id", pedido["id"]).execute()

# --- RESUMO FINANCEIRO DO DIA (EXCLUI CANCELADOS) ---
def obter_resumo_financeiro_dia(produtos: list, config: dict) -> dict:
    valor_falta_vender = sum(float(p["preco"]) * int(p["estoque"]) for p in produtos)
    qtd_falta_vender = sum(int(p["estoque"]) for p in produtos)

    inicio_dia = config.get("inicio_dia")
    query = supabase.table("pedidos").select("total, frete, itens").neq("status", "cancelado")
    if inicio_dia:
        query = query.gte("criado_em", inicio_dia)
    pedidos_dia = query.execute().data or []

    valor_vendido = sum(max(0.0, float(p.get("total", 0)) - float(p.get("frete", 0))) for p in pedidos_dia)

    qtd_vendida = 0
    for ped in pedidos_dia:
        for parte in (ped.get("itens") or "").split(" | "):
            m = re.match(r"^(\d+)x\s+", parte)
            if m:
                qtd_vendida += int(m.group(1))

    valor_total_produzido = valor_vendido + valor_falta_vender
    qtd_total_produzida = qtd_vendida + qtd_falta_vender
    percentual_vendido = (valor_vendido / valor_total_produzido * 100) if valor_total_produzido > 0 else 0.0

    return {
        "produzido_rs": valor_total_produzido,
        "produzido_un": qtd_total_produzida,
        "vendido_rs": valor_vendido,
        "vendido_un": qtd_vendida,
        "falta_rs": valor_falta_vender,
        "falta_un": qtd_falta_vender,
        "percentual": percentual_vendido,
    }

# --- RELATÓRIOS POR PERÍODO (EXCLUI CANCELADOS) ---
def gerar_relatorio_periodo(periodo: str, produtos: list) -> dict:
    agora = datetime.now()
    query = supabase.table("pedidos").select("total, frete, itens, criado_em").neq("status", "cancelado")

    if periodo == "Hoje":
        inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        query = query.gte("criado_em", inicio)
    elif periodo == "Este Mês":
        inicio = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        query = query.gte("criado_em", inicio)
    elif periodo == "Este Ano":
        inicio = agora.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        query = query.gte("criado_em", inicio)

    pedidos = query.execute().data or []

    faturamento_doces = 0.0
    total_frete = 0.0
    contagem_produtos = {p["nome"]: {"qtd": 0, "receita": 0.0} for p in produtos}

    for ped in pedidos:
        frete_p = float(ped.get("frete") or 0)
        total_p = float(ped.get("total") or 0)
        total_frete += frete_p
        faturamento_doces += max(0.0, total_p - frete_p)

        for parte in (ped.get("itens") or "").split(" | "):
            m = re.match(r"^(\d+)x\s+(.+?)\s+\(R\$\s*([\d.,]+)\)$", parte)
            if m:
                qtd_i = int(m.group(1))
                nome_i = m.group(2)
                sub_i = float(m.group(3).replace(",", "."))
                if nome_i not in contagem_produtos:
                    contagem_produtos[nome_i] = {"qtd": 0, "receita": 0.0}
                contagem_produtos[nome_i]["qtd"] += qtd_i
                contagem_produtos[nome_i]["receita"] += sub_i

    ranking_produtos = sorted(
        [{"nome": k, "qtd": v["qtd"], "receita": v["receita"]} for k, v in contagem_produtos.items()],
        key=lambda x: (x["qtd"], x["receita"]),
        reverse=True
    )

    mais_vendido = ranking_produtos[0] if ranking_produtos else None
    menos_vendido = ranking_produtos[-1] if ranking_produtos else None
    ticket_medio = (faturamento_doces / len(pedidos)) if pedidos else 0.0

    return {
        "qtd_pedidos": len(pedidos),
        "faturamento_doces": faturamento_doces,
        "total_frete": total_frete,
        "ticket_medio": ticket_medio,
        "mais_vendido": mais_vendido,
        "menos_vendido": menos_vendido,
        "ranking_produtos": ranking_produtos
    }

# --- FIDELIDADE PROGRESSIVA ---
def verificar_premio_fidelidade(telefone_formatado: str, valor_pedido: float, config: dict):
    if not config.get("fidelidade_ativa", True):
        return None
    meta_base = float(config.get("meta_valor", 50.0))
    desconto_pct = float(config.get("fidelidade_desconto", 15))
    if meta_base <= 0 or desconto_pct <= 0:
        return None

    res = supabase.table("fidelidade_clientes").select("*").eq("telefone", telefone_formatado).execute()
    if res.data:
        saldo_atual = float(res.data[0]["saldo_acumulado"])
        nivel = int(res.data[0]["nivel"])
    else:
        saldo_atual = 0.0
        nivel = 1

    meta_atual = meta_base * (2 ** (nivel - 1))
    novo_saldo = saldo_atual + valor_pedido

    if novo_saldo >= meta_atual:
        ultimos_4 = re.sub(r"\D", "", telefone_formatado)[-4:]
        sufixo = uuid.uuid4().hex[:3].upper()
        codigo_gerado = f"VIP-{ultimos_4}-{sufixo}"

        supabase.table("cupons").insert({
            "codigo": codigo_gerado,
            "desconto_percent": desconto_pct,
            "ativo": True,
            "telefone_dono": telefone_formatado,
            "uso_unico": True
        }).execute()

        proximo_nivel = nivel + 1
        proxima_meta = meta_base * (2 ** (proximo_nivel - 1))
        supabase.table("fidelidade_clientes").upsert({
            "telefone": telefone_formatado,
            "saldo_acumulado": 0.0,
            "nivel": proximo_nivel
        }).execute()

        return {
            "ganhou": True,
            "codigo": codigo_gerado,
            "desconto": desconto_pct,
            "meta_atingida": meta_atual,
            "proxima_meta": proxima_meta
        }
    else:
        supabase.table("fidelidade_clientes").upsert({
            "telefone": telefone_formatado,
            "saldo_acumulado": novo_saldo,
            "nivel": nivel
        }).execute()
        return {"ganhou": False, "saldo_atual": novo_saldo, "meta_atual": meta_atual}

# --- LOGO (BANCO OU ARQUIVO LOCAL) ---
def obter_logo_src():
    if logo_atual_url:
        return logo_atual_url
    for ext in ["logo.png", "logo.jpg", "logo.jpeg"]:
        if os.path.exists(ext):
            with open(ext, "rb") as f:
                dados = base64.b64encode(f.read()).decode()
            mime = "image/png" if ext.endswith("png") else "image/jpeg"
            return f"data:{mime};base64,{dados}"
    return None

# --- CÁLCULO DE DISTÂNCIA E FRETE ---
def calcular_distancia_e_rota(lat_cli: float, lon_cli: float):
    distancia_km = None
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{LON_LOJA},{LAT_LOJA};{lon_cli},{lat_cli}?overview=false"
        resp = requests.get(url, timeout=4).json()
        if resp.get("code") == "Ok":
            metros = resp["routes"][0]["distance"]
            distancia_km = round(metros / 1000, 2)
    except Exception:
        pass

    if distancia_km is None:
        r = 6371.0
        dlat = math.radians(lat_cli - LAT_LOJA)
        dlon = math.radians(lon_cli - LON_LOJA)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(LAT_LOJA)) * math.cos(math.radians(lat_cli)) * math.sin(dlon / 2) ** 2
        distancia_km = round(r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)) * 1.25, 2)

    link_rota = f"https://www.google.com/maps/dir/?api=1&origin={LAT_LOJA},{LON_LOJA}&destination={lat_cli},{lon_cli}&travelmode=driving"
    if distancia_km > DISTANCIA_MAXIMA_KM:
        return distancia_km, None, link_rota

    valor_frete = TABELA_FRETE[-1][1]
    for limite_km, preco in TABELA_FRETE:
        if distancia_km <= limite_km:
            valor_frete = preco
            break
    return distancia_km, valor_frete, link_rota

# --- PIX COPIA E COLA ---
def gerar_pix_copia_cola(chave: str, nome: str, cidade: str, valor: float, txid: str = "SWEETSBRUNA") -> str:
    def campo(id_c: str, val: str) -> str:
        return f"{id_c}{len(val):02d}{val}"

    def crc16(payload: str) -> str:
        res = 0xFFFF
        for b in payload.encode("utf-8"):
            res ^= (b << 8)
            for _ in range(8):
                res = ((res << 1) ^ 0x1021) if (res & 0x8000) else (res << 1)
                res &= 0xFFFF
        return f"{res:04X}"

    merchant = campo("00", "br.gov.bcb.pix") + campo("01", chave)
    payload = (
        campo("00", "01")
        + campo("26", merchant)
        + campo("52", "0000")
        + campo("53", "986")
        + campo("54", f"{valor:.2f}")
        + campo("58", "BR")
        + campo("59", nome[:25].upper())
        + campo("60", cidade[:15].upper())
        + campo("62", campo("05", txid[:25]))
        + "6304"
    )
    return payload + crc16(payload)

# --- BANCO & IMAGEM ---
def listar_produtos():
    return supabase.table("produtos").select("*").order("estoque", desc=True).order("id", desc=True).execute().data

def buscar_cupom(codigo: str):
    if not codigo.strip():
        return None
    res = supabase.table("cupons").select("*").eq("codigo", codigo.strip().upper()).eq("ativo", True).execute()
    return res.data[0] if res.data else None

def upload_foto(arquivo, tamanho=(800, 800)):
    if not arquivo:
        return None
    img = Image.open(arquivo).convert("RGB")
    img.thumbnail(tamanho)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    nome_arq = f"{uuid.uuid4().hex}.jpg"
    supabase.storage.from_("fotos").upload(nome_arq, buf.getvalue(), {"content-type": "image/jpeg"})
    return supabase.storage.from_("fotos").get_public_url(nome_arq)

# --- MODAIS ---
@st.dialog("📷 Foto de Perfil / Logo da Loja")
def modal_logo_loja():
    st.caption("Escolha uma imagem da sua galeria ou computador para usar como foto de perfil da Sweets da Bruna:")
    nova_logo = st.file_uploader("Selecionar imagem da logo", type=["jpg", "jpeg", "png"])
    if nova_logo:
        st.image(nova_logo, width=150)
        if st.button("✅ Salvar como Logo Oficial", type="primary", use_container_width=True):
            url_logo = upload_foto(nova_logo, tamanho=(500, 500))
            config_loja["logo_url"] = url_logo
            salvar_config_loja(config_loja)
            st.toast("Logo atualizada com sucesso!")
            st.rerun()

@st.dialog("❌ Cancelar Pedido")
def modal_cancelar_pedido(pedido):
    num_sacola = f"#{int(pedido.get('numero_dia') or pedido['id']):02d}"
    st.warning(f"Tem certeza que deseja cancelar a **Sacola {num_sacola}** de **{pedido['cliente']}**?")
    st.write("**Itens que voltarão automaticamente para o estoque:**")
    for parte in (pedido.get("itens") or "").split(" | "):
        st.write(f"• {parte}")

    if st.button("🗑️ Confirmar Cancelamento e Devolver ao Estoque", type="primary", use_container_width=True):
        cancelar_pedido_e_devolver_estoque(pedido)
        st.toast(f"Sacola {num_sacola} cancelada e itens devolvidos ao estoque!")
        st.rerun()

@st.dialog("📦 Quantos você fez hoje?")
def modal_estoque(produto):
    if produto.get("imagem_url"):
        st.image(produto["imagem_url"], use_container_width=True)
    st.subheader(produto["nome"])
    st.caption(f"Valor: R$ {float(produto['preco']):.2f}")
    nova_qtd = st.number_input("Quantidade disponível agora:", min_value=0, value=int(produto["estoque"]), step=1)
    if st.button("✅ Salvar", type="primary", use_container_width=True):
        supabase.table("produtos").update({"estoque": nova_qtd}).eq("id", produto["id"]).execute()
        st.rerun()
    st.divider()
    if st.button("🗑️ Apagar este doce do catálogo", use_container_width=True):
        supabase.table("produtos").delete().eq("id", produto["id"]).execute()
        st.rerun()

@st.dialog("🗑️ Excluir Doce do Catálogo")
def modal_excluir_produto(produto):
    if produto.get("imagem_url"):
        st.image(produto["imagem_url"], width=160)
    st.warning(f"Tem certeza que deseja excluir **{produto['nome']}** permanentemente do catálogo?")
    st.caption("Ele deixará de aparecer na vitrine e na aba de produção.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with c2:
        if st.button("🗑️ Sim, Excluir", type="primary", use_container_width=True):
            supabase.table("produtos").delete().eq("id", produto["id"]).execute()
            st.toast(f"'{produto['nome']}' excluído do catálogo!")
            st.rerun()

@st.dialog("🧁 Escolher Quantidade")
def modal_selecionar_doce(produto):
    if produto.get("imagem_url"):
        st.image(produto["imagem_url"], use_container_width=True)
    st.subheader(produto["nome"])
    st.markdown(f"### R$ {float(produto['preco']):.2f}")
    st.caption(f"🟢 Disponível agora: {produto['estoque']} unidade(s)")
    pid = produto["id"]
    qtd_atual = st.session_state.carrinho.get(pid, 1)
    qtd = st.number_input("Quantos você quer?", min_value=1, max_value=int(produto["estoque"]), value=min(qtd_atual, int(produto["estoque"])), step=1)
    if st.button("🛒 Colocar no Carrinho", type="primary", use_container_width=True):
        st.session_state.carrinho[pid] = qtd
        st.session_state.pedido_concluido = None
        st.rerun()

@st.dialog("✏️ Acrescentar Itens na Sacola")
def modal_editar_pedido_separado(pedido, produtos):
    num_sacola = f"#{int(pedido.get('numero_dia') or pedido['id']):02d}"
    st.subheader(f"Sacola {num_sacola} — {pedido['cliente']}")
    st.info("✅ **Itens já separados dentro da sacola (não serão repetidos):**")
    for parte in pedido["itens"].split(" | "):
        st.write(f"• {parte}")

    st.divider()
    st.markdown("**➕ Selecione o que o cliente pediu para acrescentar:**")

    produtos_disp = [p for p in produtos if int(p["estoque"]) > 0]
    if not produtos_disp:
        st.warning("Não há outros produtos com estoque disponível no momento.")
        return

    acrescimos = []
    valor_extra = 0.0

    for prod in produtos_disp:
        c1, c2 = st.columns([2.5, 1])
        with c1:
            st.write(f"**{prod['nome']}** (R$ {float(prod['preco']):.2f})")
            st.caption(f"Estoque: {prod['estoque']} un.")
        with c2:
            qtd_add = st.number_input(
                "Qtd",
                min_value=0,
                max_value=int(prod["estoque"]),
                value=0,
                step=1,
                key=f"edit_add_{pedido['id']}_{prod['id']}",
                label_visibility="collapsed"
            )
            if qtd_add > 0:
                sub = qtd_add * float(prod["preco"])
                valor_extra += sub
                acrescimos.append((prod, qtd_add, sub))

    if acrescimos:
        st.success(f"Valor do acréscimo: **+R$ {valor_extra:.2f}** (Novo total: **R$ {float(pedido['total']) + valor_extra:.2f}**)")

    if st.button("🔄 Voltar para 'A Separar' só com o Acréscimo", type="primary", use_container_width=True):
        if not acrescimos:
            st.warning("Escolha a quantidade de pelo menos 1 item para acrescentar.")
        else:
            novos_trechos = []
            for prod, qtd_add, sub in acrescimos:
                novo_est = int(prod["estoque"]) - qtd_add
                supabase.table("produtos").update({"estoque": novo_est}).eq("id", prod["id"]).execute()
                novos_trechos.append(f"{qtd_add}x {prod['nome']} (R$ {sub:.2f})")

            str_acrescimo = " | ".join(novos_trechos)
            itens_completos = f"{pedido['itens']} | {str_acrescimo}"
            novo_total = float(pedido["total"]) + valor_extra

            # Mantém o status de pagamento (se já estava pago, volta como separado_pendente porém marcado pago)
            status_atual_ped = pedido.get("status", "")
            novo_status = "a_separar_pago" if "pago" in status_atual_ped else "pendente"

            supabase.table("pedidos").update({
                "itens": itens_completos,
                "itens_acrescentados": str_acrescimo,
                "total": novo_total,
                "status": novo_status
            }).eq("id", pedido["id"]).execute()

            st.toast(f"Sacola {num_sacola} voltou para separar apenas os itens acrescentados!")
            st.rerun()

# --- ESTADO DA SESSÃO ---
if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}
if "pedido_concluido" not in st.session_state:
    st.session_state.pedido_concluido = None
if "abrir_wa_auto" not in st.session_state:
    st.session_state.abrir_wa_auto = False
if "buscar_gps" not in st.session_state:
    st.session_state.buscar_gps = False
if "dados_entrega" not in st.session_state:
    st.session_state.dados_entrega = None
if "cupom_aplicado" not in st.session_state:
    st.session_state.cupom_aplicado = None
if "admin_logado" not in st.session_state:
    st.session_state.admin_logado = False
if "gravar_login_ls" not in st.session_state:
    st.session_state.gravar_login_ls = False
if "limpar_login_ls" not in st.session_state:
    st.session_state.limpar_login_ls = False

aberta = bool(config_loja.get("aberta", True))
eh_admin = st.query_params.get("admin") == "1"

# Persistência de login no navegador
if eh_admin:
    token_esperado = gerar_token_admin()
    if st.session_state.gravar_login_ls:
        streamlit_js_eval(js_expressions=f"localStorage.setItem('sweets_bruna_auth', '{token_esperado}')", key="js_save_auth")
        st.session_state.gravar_login_ls = False
    if st.session_state.limpar_login_ls:
        streamlit_js_eval(js_expressions="localStorage.removeItem('sweets_bruna_auth')", key="js_clear_auth")
        st.session_state.limpar_login_ls = False
    elif not st.session_state.admin_logado:
        token_salvo = streamlit_js_eval(js_expressions="localStorage.getItem('sweets_bruna_auth')", key="js_read_auth")
        if token_salvo == token_esperado:
            st.session_state.admin_logado = True
            st.rerun()

# --- CABEÇALHO MODERNO COM FOTO DE PERFIL ---
logo_src = obter_logo_src()
if logo_src:
    st.markdown(
        f"""
        <div style='text-align: center; padding: 14px 0 10px 0;'>
            <img src='{logo_src}' style='width: 116px; height: 116px; object-fit: cover; border-radius: 50%; border: 4px solid #FFFFFF; box-shadow: 0 8px 24px rgba(225, 29, 72, 0.22); margin-bottom: 10px;' />
            <h1 style='margin: 0; font-size: 30px; font-weight: 800; color: #0F172A; letter-spacing: -0.5px;'>{NOME_EMPRESA}</h1>
            <div style='display: inline-block; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 999px; padding: 4px 14px; margin-top: 6px; font-size: 12px; font-weight: 600; color: #64748B;'>
                CNPJ: {CNPJ_EMPRESA} • Pronta Entrega
            </div>
            <div style='font-size: 11px; color: #64748B; margin-top: 4px;'>📍 {ENDERECO_LOJA}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if eh_admin:
        st.sidebar.markdown(
            f"<div style='text-align:center;'><img src='{logo_src}' style='width:80px; height:80px; border-radius:50%; object-fit:cover; border: 2px solid #E11D48;'/></div>",
            unsafe_allow_html=True
        )
else:
    st.markdown(
        f"""
        <div style='text-align: center; padding: 14px 0 10px 0;'>
            <div style='display: inline-flex; align-items: center; justify-content: center; width: 76px; height: 76px; border-radius: 50%; background: linear-gradient(135deg, #E11D48 0%, #FB7185 100%); color: white; font-size: 36px; border: 4px solid #FFFFFF; box-shadow: 0 8px 20px rgba(225, 29, 72, 0.25); margin-bottom: 10px;'>
                🧁
            </div>
            <h1 style='margin: 0; font-size: 30px; font-weight: 800; color: #0F172A; letter-spacing: -0.5px;'>{NOME_EMPRESA}</h1>
            <div style='display: inline-block; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 999px; padding: 4px 14px; margin-top: 6px; font-size: 12px; font-weight: 600; color: #64748B;'>
                CNPJ: {CNPJ_EMPRESA} • Pronta Entrega
            </div>
            <div style='font-size: 11px; color: #64748B; margin-top: 4px;'>📍 {ENDERECO_LOJA}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

if not eh_admin:
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    modo = "🧁 Vitrine do Cliente"
else:
    modo = st.sidebar.radio(f"{NOME_EMPRESA}", ["🔐 Área da Confeiteira", "🧁 Vitrine do Cliente"])
    st.sidebar.caption(f"CNPJ: {CNPJ_EMPRESA}")

# ==========================================
# TELA 1: VITRINE DO CLIENTE
# ==========================================
if modo == "🧁 Vitrine do Cliente":
    if not aberta:
        st.error("🔴 **LOJA FECHADA NO MOMENTO** — No momento não estamos aceitando pedidos. Volte em breve!")
    else:
        st.success("🟢 **LOJA ABERTA** — Escolha seus doces abaixo e finalize com Pix!")
        if config_loja.get("fidelidade_ativa"):
            st.info(f"🎁 **Fidelidade:** Acumule **R$ {float(config_loja.get('meta_valor', 50)):.2f}** em pedidos e ganhe um cupom automático de **{int(config_loja.get('fidelidade_desconto', 15))}% OFF**!")

    produtos = listar_produtos()
    mapa_prod = {p["id"]: p for p in produtos}

    for pid in list(st.session_state.carrinho.keys()):
        if pid not in mapa_prod or mapa_prod[pid]["estoque"] <= 0:
            del st.session_state.carrinho[pid]
        elif st.session_state.carrinho[pid] > mapa_prod[pid]["estoque"]:
            st.session_state.carrinho[pid] = mapa_prod[pid]["estoque"]

    total_itens = sum(st.session_state.carrinho.values())
    aba_loja, aba_carrinho = st.tabs(["🍰 Escolher Doces", f"🛒 Carrinho ({total_itens})"])

    with aba_loja:
        if not produtos:
            st.info("Vitrine em preparação! Volte em instantes.")
        else:
            cols = st.columns(2)
            for idx, prod in enumerate(produtos):
                pid = prod["id"]
                estoque = prod["estoque"]
                with cols[idx % 2]:
                    with st.container(border=True):
                        if prod.get("imagem_url"):
                            st.image(prod["imagem_url"], use_container_width=True)
                        st.markdown(f"**{prod['nome']}**")
                        st.markdown(f"<h3 style='margin: 2px 0 6px 0; color: #E11D48; font-weight: 800;'>R$ {float(prod['preco']):.2f}</h3>", unsafe_allow_html=True)
                        if estoque <= 0:
                            st.error("🔴 INDISPONÍVEL")
                        else:
                            st.caption(f"🟢 {estoque} disponíveis")
                            no_carrinho = st.session_state.carrinho.get(pid, 0)
                            texto_btn = "🔒 Loja Fechada" if not aberta else (f"🛒 No carrinho ({no_carrinho})" if no_carrinho > 0 else "👆 Selecionar")
                            tipo_btn = "primary" if (aberta and no_carrinho == 0) else "secondary"
                            if st.button(texto_btn, key=f"sel_{pid}", type=tipo_btn, disabled=(not aberta), use_container_width=True):
                                modal_selecionar_doce(prod)

            if aberta and total_itens > 0:
                st.success(f"Você tem **{total_itens} doce(s)** no carrinho! Toque na aba **🛒 Carrinho ({total_itens})** acima para pagar.")

    with aba_carrinho:
        if not aberta:
            st.warning("🔴 A loja fechou agora e não é possível finalizar novos pedidos no momento.")
        elif st.session_state.pedido_concluido:
            dados = st.session_state.pedido_concluido

            if st.session_state.abrir_wa_auto:
                streamlit_js_eval(js_expressions=f"window.open('{dados['link_wa']}', '_blank')", key=f"wa_auto_{dados['numero_dia']}")
                st.session_state.abrir_wa_auto = False

            st.success("🎉 Pedido reservado e enviado para o WhatsApp da loja!")

            st.markdown(
                f"""
                <div style='background: linear-gradient(135deg, #FFF1F5 0%, #FFE4E6 100%); border: 2px dashed #E11D48; border-radius: 20px; padding: 20px; text-align: center; margin-bottom: 16px; box-shadow: 0 8px 20px rgba(225, 29, 72, 0.1);'>
                    <p style='margin:0; font-size:12px; font-weight:800; color:#BE123C; text-transform:uppercase; letter-spacing: 1px;'>Número do seu Pedido</p>
                    <h1 style='margin:4px 0; font-size:52px; font-weight:800; color:#E11D48;'>#{dados['numero_dia']:02d}</h1>
                    <p style='margin:0; font-size:13px; color:#881337; font-weight: 500;'>Informe este número na retirada ou entrega</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if dados.get("entrega") == "Retirar no local":
                with st.container(border=True):
                    st.markdown("### 📍 Local para Retirada")
                    st.write(f"**{NOME_EMPRESA}**")
                    st.write(ENDERECO_LOJA)
                    st.link_button("🗺️ Abrir Localização no Google Maps", LINK_MAPS_LOJA, use_container_width=True)

            if dados.get("premio_fidelidade") and dados["premio_fidelidade"].get("ganhou"):
                premio = dados["premio_fidelidade"]
                st.balloons()
                with st.container(border=True):
                    st.markdown(f"### 🏆 PARABÉNS! VOCÊ GANHOU {int(premio['desconto'])}% OFF!")
                    st.write(f"Você atingiu a meta de R$ {premio['meta_atingida']:.2f}! Use este cupom na próxima compra (próxima meta: R$ {premio['proxima_meta']:.2f}):")
                    st.code(premio["codigo"], language=None)

            st.markdown(f"### Total a Pagar: R$ {dados['total']:.2f}")
            st.caption(f"Favorecido: **{NOME_EMPRESA}** • CNPJ: **{CNPJ_EMPRESA}**")
            st.code(dados["pix_code"], language=None)
            st.link_button("📲 Abrir WhatsApp da Loja / Enviar Comprovante", dados["link_wa"], type="primary", use_container_width=True)

            if st.button("Fazer novo pedido", use_container_width=True):
                st.session_state.pedido_concluido = None
                st.session_state.dados_entrega = None
                st.session_state.buscar_gps = False
                st.session_state.cupom_aplicado = None
                st.rerun()

        elif not st.session_state.carrinho:
            st.info("Seu carrinho está vazio.")
        else:
            subtotal_doces = 0.0
            itens_lista = []
            for pid, qtd in list(st.session_state.carrinho.items()):
                p = mapa_prod[pid]
                sub = float(p["preco"]) * qtd
                subtotal_doces += sub
                itens_lista.append((pid, p["nome"], qtd, sub))
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"**{qtd}x** {p['nome']} — R$ {sub:.2f}")
                with c2:
                    if st.button("Remover", key=f"rm_{pid}", use_container_width=True):
                        del st.session_state.carrinho[pid]
                        st.rerun()

            st.divider()
            c_cup1, c_cup2 = st.columns([2.5, 1])
            with c_cup1:
                codigo_digitado = st.text_input("Cupom de Desconto", placeholder="Ex: BRUNA10 ou VIP-...", label_visibility="collapsed")
            with c_cup2:
                if st.button("Aplicar", use_container_width=True):
                    cup = buscar_cupom(codigo_digitado)
                    if cup:
                        st.session_state.cupom_aplicado = cup
                        st.rerun()
                    else:
                        st.session_state.cupom_aplicado = None
                        st.error("Cupom inválido ou já utilizado.")

            valor_desconto = 0.0
            codigo_cupom_str = ""
            if st.session_state.cupom_aplicado:
                cup = st.session_state.cupom_aplicado
                pct = float(cup["desconto_percent"])
                valor_desconto = round(subtotal_doces * (pct / 100.0), 2)
                codigo_cupom_str = cup["codigo"]
                col_ci, col_cr = st.columns([3, 1])
                with col_ci:
                    st.success(f"Cupom **{codigo_cupom_str}** aplicado (-R$ {valor_desconto:.2f})")
                with col_cr:
                    if st.button("Tirar", use_container_width=True):
                        st.session_state.cupom_aplicado = None
                        st.rerun()

            st.divider()
            entrega = st.radio("Como deseja receber?", ["Retirar no local", "Entrega (Delivery)"], horizontal=True)

            valor_frete = 0.0
            distancia_km = 0.0
            link_rota_entregador = ""
            endereco_texto = ""

            if entrega == "Retirar no local":
                st.info(f"📍 **Endereço de Retirada:** {ENDERECO_LOJA}\n\n🗺️ [Ver no Google Maps]({LINK_MAPS_LOJA})")
            elif entrega == "Entrega (Delivery)":
                if st.button("📍 Calcular Frete com Minha Localização", use_container_width=True):
                    st.session_state.buscar_gps = True
                if st.session_state.buscar_gps:
                    loc = get_geolocation()
                    if loc and "coords" in loc:
                        km, frete_calc, rota_url = calcular_distancia_e_rota(loc["coords"]["latitude"], loc["coords"]["longitude"])
                        st.session_state.dados_entrega = {"km": km, "frete": frete_calc, "rota": rota_url}
                        st.session_state.buscar_gps = False
                        st.rerun()
                if st.session_state.dados_entrega:
                    info_ent = st.session_state.dados_entrega
                    distancia_km = info_ent["km"]
                    link_rota_entregador = info_ent["rota"]
                    if info_ent["frete"] is None:
                        st.error(f"Distância ({distancia_km} km) fora do raio máximo ({DISTANCIA_MAXIMA_KM} km).")
                    else:
                        valor_frete = info_ent["frete"]
                        st.success(f"🛵 Distância: **{distancia_km} km** • Entrega: **R$ {valor_frete:.2f}**")
                endereco_texto = st.text_input("Rua, Número, Bairro e Complemento *")

            total_geral = max(0.0, subtotal_doces - valor_desconto + valor_frete)
            st.markdown(f"## Total Final: R$ {total_geral:.2f}")

            nome_cli = st.text_input("Seu Nome *")
            tel_raw = st.text_input("WhatsApp / Telefone *", placeholder="669.999-9999", max_chars=14)
            tel_formatado, tel_valido = formatar_telefone(tel_raw)
            if tel_raw:
                st.caption(f"📱 Contato formatado: **{tel_formatado}**" if tel_valido else "⚠️ Digite DDD + número (ex: 6699999999 -> **669.999-9999**)")

            if st.button("✅ Confirmar Pedido e Enviar no WhatsApp", type="primary", use_container_width=True):
                if not bool(obter_config_loja().get("aberta", True)):
                    st.error("🔴 A loja fechou.")
                elif not nome_cli.strip() or not tel_valido:
                    st.warning("Preencha seu nome e telefone no padrão 669.999-9999.")
                elif entrega == "Entrega (Delivery)" and (not st.session_state.dados_entrega or st.session_state.dados_entrega["frete"] is None or not endereco_texto.strip()):
                    st.warning("Calcule o frete pela localização e preencha o endereço.")
                else:
                    prod_atualizados = {p["id"]: p for p in listar_produtos()}
                    erro = next((f"'{n}' agora só tem {prod_atualizados[pid]['estoque']} un." for pid, n, q, _ in itens_lista if prod_atualizados[pid]["estoque"] < q), None)
                    if erro:
                        st.error(erro)
                    else:
                        resumo_txt = []
                        for pid, nome_p, qtd, sub in itens_lista:
                            supabase.table("produtos").update({"estoque": prod_atualizados[pid]["estoque"] - qtd}).eq("id", pid).execute()
                            resumo_txt.append(f"{qtd}x {nome_p} (R$ {sub:.2f})")

                        num_dia = gerar_proximo_numero_dia()
                        itens_str = " | ".join(resumo_txt)
                        supabase.table("pedidos").insert({
                            "numero_dia": num_dia,
                            "status": "pendente",
                            "cliente": nome_cli.strip(),
                            "telefone": tel_formatado,
                            "itens": itens_str,
                            "itens_acrescentados": "",
                            "cupom": codigo_cupom_str,
                            "desconto": valor_desconto,
                            "total": total_geral,
                            "entrega": entrega,
                            "endereco": endereco_texto if entrega == "Entrega (Delivery)" else ENDERECO_LOJA,
                            "frete": valor_frete,
                            "distancia_km": distancia_km,
                            "rota_maps": link_rota_entregador if entrega == "Entrega (Delivery)" else LINK_MAPS_LOJA
                        }).execute()

                        if st.session_state.cupom_aplicado and st.session_state.cupom_aplicado.get("uso_unico"):
                            supabase.table("cupons").update({"ativo": False}).eq("id", st.session_state.cupom_aplicado["id"]).execute()

                        premio = verificar_premio_fidelidade(tel_formatado, max(0.0, subtotal_doces - valor_desconto), config_loja)
                        pix_code = gerar_pix_copia_cola(CHAVE_PIX, NOME_RECEBEDOR, CIDADE_RECEBEDOR, total_geral, f"PED{num_dia:02d}")

                        msg = [
                            f"*{NOME_EMPRESA.upper()}* 🧁",
                            f"_CNPJ: {CNPJ_EMPRESA}_",
                            f"*PEDIDO #{num_dia:02d}*",
                            f"*Cliente:* {nome_cli.strip()} ({tel_formatado})",
                            "",
                            "*Itens:*",
                        ] + [f"• {l}" for l in resumo_txt] + [
                            "",
                            f"*Total Geral:* R$ {total_geral:.2f}",
                            f"*Recebimento:* {entrega}",
                        ]
                        if entrega == "Retirar no local":
                            msg.append(f"*📍 Local de Retirada:* {ENDERECO_LOJA}")
                            msg.append(f"*🗺️ Localização no Mapa:* {LINK_MAPS_LOJA}")
                        else:
                            if endereco_texto:
                                msg.append(f"*Endereço:* {endereco_texto}")
                            if link_rota_entregador:
                                msg.append(f"*🛵 Rota p/ Entregador:* {link_rota_entregador}")
                        if premio and premio.get("ganhou"):
                            msg.append(f"\n🎁 *Ganhei o cupom fidelidade:* {premio['codigo']} ({int(premio['desconto'])}% OFF)")
                        msg.append("*Pagamento:* Pix (confirmando pedido e enviando comprovante)")

                        link_wa = f"https://wa.me/{WHATSAPP_LOJA}?text={urllib.parse.quote(chr(10).join(msg))}"

                        st.session_state.carrinho = {}
                        st.session_state.cupom_aplicado = None
                        st.session_state.abrir_wa_auto = True
                        st.session_state.pedido_concluido = {
                            "numero_dia": num_dia,
                            "total": total_geral,
                            "entrega": entrega,
                            "pix_code": pix_code,
                            "link_wa": link_wa,
                            "premio_fidelidade": premio
                        }
                        st.rerun()

# ==========================================
# TELA 2: ÁREA DA CONFEITEIRA
# ==========================================
elif modo == "🔐 Área da Confeiteira":
    if not st.session_state.admin_logado:
        with st.container(border=True):
            st.markdown("### 🔐 Acesso da Confeiteira")
            st.caption("Entre com seu CPF e senha. Você continuará logada neste dispositivo.")
            with st.form("form_login_admin"):
                cpf_digitado = st.text_input("CPF", placeholder="062.582.881-03", max_chars=14)
                senha_digitada = st.text_input("Senha", type="password", placeholder="••••")
                manter_conectada = st.checkbox("Manter conectada neste dispositivo", value=True)
                if st.form_submit_button("🔓 Entrar na Bancada", type="primary", use_container_width=True):
                    cpf_dig_limpo = re.sub(r"\D", "", cpf_digitado)
                    cpf_cad_limpo = re.sub(r"\D", "", CPF_ADMIN)
                    if cpf_dig_limpo == cpf_cad_limpo and senha_digitada == SENHA_ADMIN:
                        st.session_state.admin_logado = True
                        if manter_conectada:
                            st.session_state.gravar_login_ls = True
                        st.rerun()
                    else:
                        st.error("CPF ou senha incorretos.")
    else:
        c_top1, c_top2, c_top3 = st.columns([2.2, 1.3, 0.9])
        with c_top1:
            st.subheader("🔐 Bancada da Confeiteira")
        with c_top2:
            if st.button("📷 Foto / Logo", use_container_width=True):
                modal_logo_loja()
        with c_top3:
            if st.button("🚪 Sair", use_container_width=True):
                st.session_state.admin_logado = False
                st.session_state.limpar_login_ls = True
                st.rerun()

        with st.container(border=True):
            c_st, c_b1, c_b2 = st.columns([1.8, 1.1, 1.3])
            with c_st:
                if aberta:
                    st.markdown("### 🟢 Loja Aberta")
                    st.caption(f"Senha atual do dia: **#{int(config_loja.get('ultimo_numero_dia', 0)):02d}**")
                else:
                    st.markdown("### 🔴 Loja Fechada")
                    st.caption("Pedidos bloqueados.")
            with c_b1:
                st.write("")
                if aberta:
                    if st.button("🔴 Fechar", use_container_width=True):
                        config_loja["aberta"] = False
                        salvar_config_loja(config_loja)
                        st.rerun()
                else:
                    if st.button("🟢 Abrir", type="primary", use_container_width=True):
                        config_loja["aberta"] = True
                        salvar_config_loja(config_loja)
                        st.rerun()
            with c_b2:
                st.write("")
                if st.button("🧹 Novo Dia (#01)", help="Zera estoque sobrando e reinicia contagem no #01", use_container_width=True):
                    supabase.table("produtos").update({"estoque": 0}).neq("id", 0).execute()
                    config_loja["ultimo_numero_dia"] = 0
                    config_loja["inicio_dia"] = datetime.now().isoformat()
                    salvar_config_loja(config_loja)
                    st.toast("Estoque zerado e numeração reiniciada para #01!")
                    st.rerun()

        produtos_atual = listar_produtos()
        resumo = obter_resumo_financeiro_dia(produtos_atual, config_loja)

        with st.container(border=True):
            st.markdown("### 📊 Resumo Financeiro de Hoje")
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("🧁 Produzido Hoje", f"R$ {resumo['produzido_rs']:.2f}", delta=f"{resumo['produzido_un']} un.", delta_color="off")
            with m2:
                st.metric("✅ Já Vendido", f"R$ {resumo['vendido_rs']:.2f}", delta=f"{resumo['vendido_un']} un. ({resumo['percentual']:.0f}%)")
            with m3:
                st.metric("📦 Falta Vender", f"R$ {resumo['falta_rs']:.2f}", delta=f"{resumo['falta_un']} un.", delta_color="off")
            st.progress(min(1.0, resumo["percentual"] / 100.0))

        aba_fila, aba_separados, aba_cancelados, aba_estoque, aba_novo, aba_cupons, aba_ranking, aba_relatorios, aba_excel = st.tabs([
            "📦 A Separar",
            "✅ Separados",
            "❌ Cancelados",
            "📸 Produção",
            "➕ Novo",
            "🎟️ Cupons",
            "🏆 Top 5",
            "📈 Relatórios",
            "📊 Excel"
        ])

        # --- ABA 1: SACOLAS A SEPARAR (SOMENTE CONFIRMAÇÃO DO FUNCIONÁRIO) ---
        with aba_fila:
            pedidos_a_separar = supabase.table("pedidos").select("*").in_("status", ["pendente", "a_separar_pago"]).order("id", desc=False).execute().data

            c_gel1, c_gel2 = st.columns(2)
            with c_gel1:
                with st.container(border=True):
                    st.markdown("**🧊 Pegar da geladeira (A Separar)**")
                    if not pedidos_a_separar:
                        st.caption("Nenhum item pendente para separar.")
                    else:
                        resumo_geladeira = {}
                        for ped in pedidos_a_separar:
                            texto_alvo = ped.get("itens_acrescentados") if ped.get("itens_acrescentados") else ped["itens"]
                            for parte in texto_alvo.split(" | "):
                                m = re.match(r"^(\d+)x\s+(.+?)\s+\(R\$", parte)
                                if m:
                                    qtd_i = int(m.group(1))
                                    nome_i = m.group(2)
                                    resumo_geladeira[nome_i] = resumo_geladeira.get(nome_i, 0) + qtd_i
                        for n, q in resumo_geladeira.items():
                            st.write(f"• **{q}x** {n}")

            with c_gel2:
                with st.container(border=True):
                    st.markdown("**🟢 Disponível para Venda (Vitrine)**")
                    if not produtos_atual:
                        st.caption("Nenhum doce cadastrado.")
                    else:
                        for p in produtos_atual:
                            est_p = int(p["estoque"])
                            if est_p > 0:
                                st.write(f"• **{est_p} un.** — {p['nome']}")
                            else:
                                st.caption(f"• 🔴 0 un. — {p['nome']} (Esgotado)")

            if not pedidos_a_separar:
                st.success("🎉 Tudo separado! Nenhuma sacola aguardando separação.")
            else:
                st.divider()

                for ped in pedidos_a_separar:
                    num_sacola = f"#{int(ped.get('numero_dia') or ped['id']):02d}"
                    status_atual = ped.get("status", "pendente")
                    ja_pago = (status_atual == "a_separar_pago")
                    tem_acrescimo = bool(ped.get("itens_acrescentados"))

                    with st.container(border=True):
                        st.markdown(f"## 🛍️ Sacola {num_sacola} — {ped['cliente']}")
                        renderizar_etiquetas_pedido(ped["entrega"], ja_pago)

                        if tem_acrescimo:
                            st.warning(f"⚠️ **ACRÉSCIMO NA SACOLA {num_sacola}** — Colocar apenas os itens abaixo:")
                        else:
                            st.caption(f"✍️ **Escreva {num_sacola} na sacola** • 📱 {ped.get('telefone', '')}")

                        itens_para_conferir = ped["itens_acrescentados"] if tem_acrescimo else ped["itens"]
                        st.markdown("**Marque cada doce conforme colocar na sacola:**")
                        for idx_i, parte in enumerate(itens_para_conferir.split(" | ")):
                            limpo = re.sub(r"\s+\(R\$.*?\)$", "", parte)
                            st.checkbox(limpo, key=f"chk_{ped['id']}_{idx_i}_{len(itens_para_conferir)}")

                        st.write(f"**Total:** R$ {float(ped['total']):.2f}")
                        if ped["entrega"] == "Entrega (Delivery)" and ped.get("endereco"):
                            st.caption(f"📍 Endereço: {ped['endereco']}")

                        col_ok, col_canc = st.columns([2.2, 1])
                        with col_ok:
                            if st.button("✔️ Marcar como Separado", key=f"sep_ok_{ped['id']}", type="primary", use_container_width=True):
                                novo_st = "separado_pago" if ja_pago else "separado_pendente"
                                supabase.table("pedidos").update({
                                    "status": novo_st,
                                    "itens_acrescentados": ""
                                }).eq("id", ped["id"]).execute()
                                st.toast(f"Sacola {num_sacola} marcada como separada!")
                                st.rerun()
                        with col_canc:
                            if st.button("❌ Cancelar", key=f"cancel_fila_{ped['id']}", use_container_width=True):
                                modal_cancelar_pedido(ped)

        # --- ABA 2: PEDIDOS SEPARADOS (PAGAMENTO, AVISAR CLIENTE E ENTREGADOR) ---
        with aba_separados:
            st.markdown("### ✅ Sacolas Separadas — Pagamento & Envio")
            st.caption("Confirme o Pix do cliente, avise quando estiver pronto/saiu e envie a rota ao entregador:")

            pedidos_separados = supabase.table("pedidos").select("*").in_("status", ["separado_pendente", "separado_pago", "concluido", "separando"]).order("id", desc=True).limit(50).execute().data
            if not pedidos_separados:
                st.info("Nenhuma sacola separada ainda.")
            else:
                for ped in pedidos_separados:
                    num_sacola = f"#{int(ped.get('numero_dia') or ped['id']):02d}"
                    st_ped = ped.get("status", "separado_pendente")
                    esta_pago = st_ped in ("separado_pago", "concluido")
                    tel_limpo = re.sub(r"\D", "", ped.get("telefone", ""))
                    tel_wa = f"55{tel_limpo}" if len(tel_limpo) in (10, 11) else ""

                    with st.container(border=True):
                        st.markdown(f"### 🛍️ Sacola {num_sacola} — {ped['cliente']}")
                        renderizar_etiquetas_pedido(ped["entrega"], esta_pago)

                        st.write(f"**Itens:** {ped['itens']}")
                        st.write(f"**Total:** R$ {float(ped['total']):.2f} • **Contato:** {ped.get('telefone', '')}")
                        if ped["entrega"] == "Entrega (Delivery)" and ped.get("endereco"):
                            st.caption(f"📍 **Endereço de Entrega:** {ped['endereco']}")

                        # --- BLOCO DE CONTROLE FÁCIL DE PAGAMENTO ---
                        if not esta_pago:
                            st.warning(f"⏳ **Pagamento Pendente (R$ {float(ped['total']):.2f})** — Confirme abaixo assim que o Pix cair:")
                            cp1, cp2 = st.columns(2)
                            with cp1:
                                if st.button("✅ Confirmar Pix Pago", key=f"pg_ok_{ped['id']}", type="primary", use_container_width=True):
                                    supabase.table("pedidos").update({"status": "separado_pago"}).eq("id", ped["id"]).execute()
                                    st.toast(f"Pagamento da Sacola {num_sacola} confirmado!")
                                    st.rerun()
                            with cp2:
                                if tel_wa:
                                    msg_cobrar = urllib.parse.quote(
                                        f"Oi {ped['cliente']}! 🧁 Tudo bem? Sua *Sacola {num_sacola}* na *{NOME_EMPRESA}* já está separadinha! "
                                        f"Estamos só aguardando a confirmação do Pix de *R$ {float(ped['total']):.2f}* para liberar. Qualquer coisa me manda o comprovante por aqui! 💕"
                                    )
                                    st.link_button("💬 Lembrar Pix no WhatsApp", f"https://wa.me/{tel_wa}?text={msg_cobrar}", use_container_width=True)
                        else:
                            cp_pago1, cp_pago2 = st.columns([2.5, 1.2])
                            with cp_pago1:
                                st.success(f"✅ **Pagamento Confirmado (R$ {float(ped['total']):.2f})**")
                            with cp_pago2:
                                if st.button("↩️ Voltar p/ Pendente", key=f"pg_undo_{ped['id']}", use_container_width=True):
                                    supabase.table("pedidos").update({"status": "separado_pendente"}).eq("id", ped["id"]).execute()
                                    st.rerun()

                        # --- BOTÕES DE AVISAR CLIENTE E MANDAR PARA ENTREGADOR ---
                        st.markdown("**📲 Comunicação & Despacho:**")
                        if ped["entrega"] == "Entrega (Delivery)":
                            ca1, ca2 = st.columns(2)
                            with ca1:
                                if tel_wa:
                                    msg_saiu = urllib.parse.quote(
                                        f"Oi {ped['cliente']}! 🛵💨 Seu *Pedido {num_sacola}* da *{NOME_EMPRESA}* acabou de sair para entrega!"
                                    )
                                    st.link_button("🛵 Avisar Cliente (Saiu)", f"https://wa.me/{tel_wa}?text={msg_saiu}", type="primary", use_container_width=True)
                            with ca2:
                                rota_txt = ped.get("rota_maps") or ""
                                msg_motoboy = urllib.parse.quote(
                                    f"🛵 *Entrega {NOME_EMPRESA} — Sacola {num_sacola}*\n"
                                    f"*Cliente:* {ped['cliente']} ({ped.get('telefone', '')})\n"
                                    f"*Endereço:* {ped.get('endereco', '')}\n"
                                    f"*Pagamento:* {'✅ JÁ PAGO' if esta_pago else f'⏳ COBRAR R$ {float(ped[\"total\"]):.2f}'}\n"
                                    f"*Rota:* {rota_txt}"
                                )
                                st.link_button("🗺️ Enviar p/ Entregador", f"https://wa.me/?text={msg_motoboy}", use_container_width=True)
                        else:
                            if tel_wa:
                                itens_msg_ret = ped["itens"].replace(" | ", "\n• ")
                                msg_pronto = urllib.parse.quote(
                                    f"Oi {ped['cliente']}! 🛍️✨ Seu *Pedido {num_sacola}* da *{NOME_EMPRESA}* já está prontinho para retirada!\n\n"
                                    f"*Itens:*\n• {itens_msg_ret}\n"
                                    f"*Total:* R$ {float(ped['total']):.2f} ({'Pix Pago ✅' if esta_pago else 'Pagamento Pendente ⏳'})\n\n"
                                    f"📍 *Endereço:* {ENDERECO_LOJA}\n"
                                    f"🗺️ *Localização:* {LINK_MAPS_LOJA}"
                                )
                                st.link_button("🛍️ Avisar Cliente (Pronto + Localização)", f"https://wa.me/{tel_wa}?text={msg_pronto}", type="primary", use_container_width=True)

                        # --- EDITAR / ACRESCENTAR OU CANCELAR ---
                        ce1, ce2 = st.columns(2)
                        with ce1:
                            if st.button("✏️ Editar / Acrescentar", key=f"edit_sep_{ped['id']}", use_container_width=True):
                                modal_editar_pedido_separado(ped, produtos_atual)
                        with ce2:
                            if st.button("❌ Cancelar Pedido", key=f"cancel_sep_{ped['id']}", use_container_width=True):
                                modal_cancelar_pedido(ped)

        # --- ABA 3: PEDIDOS CANCELADOS ---
        with aba_cancelados:
            st.markdown("### ❌ Pedidos Cancelados")
            st.caption("Pedidos cancelados tiveram seus doces devolvidos automaticamente ao estoque.")
            pedidos_canc = supabase.table("pedidos").select("*").eq("status", "cancelado").order("id", desc=True).limit(30).execute().data
            if not pedidos_canc:
                st.info("Nenhum pedido cancelado.")
            else:
                for ped in pedidos_canc:
                    num_sacola = f"#{int(ped.get('numero_dia') or ped['id']):02d}"
                    tel_limpo = re.sub(r"\D", "", ped.get("telefone", ""))
                    tel_wa = f"55{tel_limpo}" if len(tel_limpo) in (10, 11) else ""
                    with st.container(border=True):
                        cc1, cc2 = st.columns([2.4, 1.3])
                        with cc1:
                            st.markdown(f"**🔴 Sacola {num_sacola} — {ped['cliente']}** ({ped.get('telefone', '')})")
                            st.write(ped["itens"])
                            st.caption(f"Valor cancelado: R$ {float(ped['total']):.2f}")
                        with cc2:
                            if tel_wa:
                                msg_canc = urllib.parse.quote(
                                    f"Oi {ped['cliente']}! Passando para avisar que o seu *Pedido {num_sacola}* na *{NOME_EMPRESA}* foi cancelado conforme combinado. Qualquer dúvida estamos à disposição! 🧁"
                                )
                                st.link_button("📲 Avisar Cliente", f"https://wa.me/{tel_wa}?text={msg_canc}", use_container_width=True)

        # --- ABA 4: PRODUÇÃO DO DIA & ESTOQUE DISPONÍVEL ---
        with aba_estoque:
            if produtos_atual:
                total_disp_un = sum(int(p["estoque"]) for p in produtos_atual)
                total_disp_rs = sum(int(p["estoque"]) * float(p["preco"]) for p in produtos_atual)
                st.info(f"🟢 **Disponível para venda agora:** **{total_disp_un} unidade(s)** (Total em vitrine: **R$ {total_disp_rs:.2f}**)")

            st.caption("Gerencie a quantidade disponível para venda hoje ou exclua doces do catálogo:")
            if not produtos_atual:
                st.info("Você ainda não cadastrou nenhum doce. Vá na aba **➕ Novo** ao lado!")
            else:
                cols = st.columns(2)
                for idx, prod in enumerate(produtos_atual):
                    with cols[idx % 2]:
                        with st.container(border=True):
                            if prod.get("imagem_url"):
                                st.image(prod["imagem_url"], use_container_width=True)
                            st.markdown(f"**{prod['nome']}**")
                            st.caption(f"R$ {float(prod['preco']):.2f}")
                            est = prod["estoque"]
                            if est > 0:
                                st.success(f"Disponível: {est}")
                            else:
                                st.error("Esgotado (0)")
                            b_qtd, b_del = st.columns([1.4, 1])
                            with b_qtd:
                                if st.button("✏️ Qtd", key=f"adm_{prod['id']}", use_container_width=True):
                                    modal_estoque(prod)
                            with b_del:
                                if st.button("🗑️ Excluir", key=f"del_{prod['id']}", use_container_width=True):
                                    modal_excluir_produto(prod)

        # --- ABA 5: NOVO DOCE ---
        with aba_novo:
            with st.form("novo_doce", clear_on_submit=True):
                foto_p = st.file_uploader("1. Escolha a foto do doce", type=["jpg", "jpeg", "png"])
                nome_p = st.text_input("2. Nome do doce")
                preco_p = st.number_input("3. Valor (R$)", min_value=0.0, step=0.50)
                if st.form_submit_button("✅ Salvar Doce", type="primary", use_container_width=True):
                    if not nome_p.strip() or preco_p <= 0:
                        st.warning("Coloque o nome e o valor do doce.")
                    else:
                        url_img = upload_foto(foto_p)
                        supabase.table("produtos").insert({"nome": nome_p.strip(), "preco": preco_p, "estoque": 0, "imagem_url": url_img}).execute()
                        st.success(f"'{nome_p}' salvo! Agora clique nele na aba **📸 Produção** para colocar a quantidade.")
                        st.rerun()

        # --- ABA 6: CUPONS & FIDELIDADE ---
        with aba_cupons:
            with st.container(border=True):
                st.markdown("### 🎁 Cupom Automático por Meta Progressiva")
                with st.form("form_fidelidade"):
                    fid_ativa = st.checkbox("Ativar recompensa automática", value=bool(config_loja.get("fidelidade_ativa", True)))
                    c_m1, c_m2 = st.columns(2)
                    with c_m1:
                        meta_val = st.number_input("Meta inicial (R$)", min_value=5.0, value=float(config_loja.get("meta_valor", 50.0)), step=5.0)
                    with c_m2:
                        desc_fid = st.number_input("Desconto ganho (%)", min_value=1, max_value=100, value=int(config_loja.get("fidelidade_desconto", 15)), step=1)
                    if st.form_submit_button("💾 Salvar Regra", type="primary", use_container_width=True):
                        config_loja["fidelidade_ativa"] = fid_ativa
                        config_loja["meta_valor"] = meta_val
                        config_loja["fidelidade_desconto"] = desc_fid
                        salvar_config_loja(config_loja)
                        st.success("Regra salva!")
                        st.rerun()

            st.divider()
            with st.form("novo_cupom", clear_on_submit=True):
                c1, c2 = st.columns([2, 1])
                with c1:
                    cod_cupom = st.text_input("Novo Cupom Manual (ex: BRUNA10)")
                with c2:
                    pct_cupom = st.number_input("Desconto (%)", min_value=1, max_value=100, value=10, step=1)
                if st.form_submit_button("🎟️ Criar Cupom", use_container_width=True):
                    if cod_cupom.strip():
                        supabase.table("cupons").upsert({"codigo": cod_cupom.strip().upper(), "desconto_percent": pct_cupom, "ativo": True, "uso_unico": False}, on_conflict="codigo").execute()
                        st.rerun()

            for cup in supabase.table("cupons").select("*").eq("ativo", True).order("id", desc=True).execute().data:
                ca, cb = st.columns([3, 1])
                with ca:
                    dono = f" • Cliente: {cup['telefone_dono']}" if cup.get("telefone_dono") else " • Geral"
                    st.write(f"🎟️ **{cup['codigo']}** ({int(cup['desconto_percent'])}% OFF){dono}")
                with cb:
                    if st.button("🗑️", key=f"dc_{cup['id']}"):
                        supabase.table("cupons").delete().eq("id", cup["id"]).execute()
                        st.rerun()

        # --- ABA 7: TOP 5 CLIENTES ---
        with aba_ranking:
            st.markdown("### 🏆 Top 5 Clientes com Mais Pedidos")
            todos = supabase.table("pedidos").select("cliente, telefone, total").neq("status", "cancelado").execute().data
            if not todos:
                st.info("Ainda não há pedidos registrados.")
            else:
                ranking_map = {}
                for ped in todos:
                    tel = (ped.get("telefone") or "").strip()
                    if not tel:
                        continue
                    if tel not in ranking_map:
                        ranking_map[tel] = {"telefone": tel, "cliente": ped.get("cliente", ""), "qtd": 0, "total": 0.0}
                    ranking_map[tel]["qtd"] += 1
                    ranking_map[tel]["total"] += float(ped.get("total", 0))
                    ranking_map[tel]["cliente"] = ped.get("cliente", ranking_map[tel]["cliente"])

                top5 = sorted(ranking_map.values(), key=lambda x: (x["qtd"], x["total"]), reverse=True)[:5]
                medalhas = ["🥇 1º", "🥈 2º", "🥉 3º", "4º", "5º"]
                for i, item in enumerate(top5):
                    with st.container(border=True):
                        ci, ca = st.columns([2.3, 1.2])
                        with ci:
                            st.markdown(f"**{medalhas[i]} — {item['cliente']}** ({item['telefone']})")
                            st.caption(f"🛍️ **{item['qtd']} pedido(s)** • Total acumulado: **R$ {item['total']:.2f}**")
                        with ca:
                            tel_limpo = re.sub(r"\D", "", item["telefone"])
                            if len(tel_limpo) in (10, 11):
                                msg_brinde = urllib.parse.quote(
                                    f"Olá {item['cliente']}! 🧁🎉 Aqui é da *{NOME_EMPRESA}*!\nVocê está no nosso *Top 5 clientes com mais pedidos* ({item['qtd']} pedidos) e ganhou um *brinde especial* no seu próximo pedido! 🎁✨"
                                )
                                st.link_button("🎁 Mandar Brinde", f"https://wa.me/55{tel_limpo}?text={msg_brinde}", use_container_width=True)

        # --- ABA 8: RELATÓRIOS ---
        with aba_relatorios:
            st.markdown("### 📈 Desempenho & Acumulado")
            filtro_periodo = st.radio("Selecione o período:", ["Hoje", "Este Mês", "Este Ano", "Todo o Período"], horizontal=True)
            rel = gerar_relatorio_periodo(filtro_periodo, produtos_atual)

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("💰 Vendido (Doces)", f"R$ {rel['faturamento_doces']:.2f}")
            with c2:
                st.metric("🛍️ Pedidos Feitos", f"{rel['qtd_pedidos']}")
            with c3:
                st.metric("🧾 Ticket Médio", f"R$ {rel['ticket_medio']:.2f}")

            st.caption(f"🛵 Total repassado em entregas no período: R$ {rel['total_frete']:.2f}")
            st.divider()

            if rel["mais_vendido"] and rel["menos_vendido"]:
                col_mv, col_lv = st.columns(2)
                with col_mv:
                    with st.container(border=True):
                        st.markdown("#### 🔥 Mais Vendido")
                        st.subheader(rel["mais_vendido"]["nome"])
                        st.success(f"**{rel['mais_vendido']['qtd']} un.** vendidas (R$ {rel['mais_vendido']['receita']:.2f})")
                with col_lv:
                    with st.container(border=True):
                        st.markdown("#### 📉 Menos Vendido")
                        st.subheader(rel["menos_vendido"]["nome"])
                        st.warning(f"**{rel['menos_vendido']['qtd']} un.** vendidas (R$ {rel['menos_vendido']['receita']:.2f})")

                st.markdown("#### 📋 Ranking Completo de Produtos")
                for idx_p, item_p in enumerate(rel["ranking_produtos"], start=1):
                    st.write(f"**{idx_p}º.** {item_p['nome']} — **{item_p['qtd']} un.** (R$ {item_p['receita']:.2f})")

        # --- ABA 9: EXCEL ---
        with aba_excel:
            pedidos = supabase.table("pedidos").select("*").neq("status", "cancelado").order("id", desc=True).execute().data
            if not pedidos:
                st.info("Nenhum pedido registrado ainda.")
            else:
                df = pd.DataFrame(pedidos)
                df["criado_em"] = pd.to_datetime(df["criado_em"]).dt.strftime("%d/%m/%Y %H:%M")
                cols_exp = ["numero_dia", "criado_em", "cliente", "telefone", "itens", "cupom", "desconto", "frete", "total", "entrega", "endereco", "rota_maps"]
                for col in cols_exp:
                    if col not in df.columns:
                        df[col] = ""
                df_export = df[cols_exp]
                df_export.columns = ["Sacola #", "Data/Hora", "Cliente", "Contato", "Itens", "Cupom", "Desconto (R$)", "Frete (R$)", "Total (R$)", "Recebimento", "Endereço", "Rota"]
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    pd.DataFrame([[f"{NOME_EMPRESA} — CNPJ: {CNPJ_EMPRESA}"]]).to_excel(writer, index=False, header=False, sheet_name="Pedidos", startrow=0)
                    df_export.to_excel(writer, index=False, sheet_name="Pedidos", startrow=2)
                st.download_button(
                    label="📥 Gerar Excel (.xlsx)",
                    data=buf.getvalue(),
                    file_name=f"sweets_da_bruna_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True
                )

# --- RODAPÉ OFICIAL ---
st.divider()
st.markdown(
    f"<div style='text-align: center; color: #64748B; font-size: 12px; font-weight: 500;'>{NOME_EMPRESA} • CNPJ: {CNPJ_EMPRESA}</div>",
    unsafe_allow_html=True
)