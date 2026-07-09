import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import dateutil.relativedelta
import gspread
import os
import base64
import mimetypes
import html
import math
import time
import io
import re
import unicodedata
import hashlib
import calendar

# Configuração da página
st.set_page_config(page_title="Meu App Finanças", layout="wide", initial_sidebar_state="collapsed")

# 🔐 Trava de acesso por senha
# Configure a senha no Streamlit Secrets como:
# APP_PASSWORD = "sua_senha_aqui"
# ou:
# [auth]
# password = "sua_senha_aqui"
def get_app_access_password():
    candidates = []
    try:
        candidates.append(str(st.secrets.get("APP_PASSWORD", "")).strip())
    except Exception:
        pass
    try:
        auth_secret = st.secrets.get("auth", {})
        if hasattr(auth_secret, "get"):
            candidates.append(str(auth_secret.get("password", "")).strip())
    except Exception:
        pass
    try:
        candidates.append(str(os.environ.get("APP_PASSWORD", "")).strip())
    except Exception:
        pass
    return next((candidate for candidate in candidates if candidate), "")


def render_password_gate():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #f7faf8 0%, #eef5f0 100%) !important;
        }

        .stApp::before {
            content: "";
            position: fixed !important;
            inset: 0 !important;
            z-index: 2147483646 !important;
            background: rgba(255, 255, 255, 0.78) !important;
            backdrop-filter: blur(18px) !important;
            -webkit-backdrop-filter: blur(18px) !important;
        }

        [data-testid="stHeader"],
        header[data-testid="stHeader"],
        [data-testid="stSidebar"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
        }

        .block-container {
            padding: 0 !important;
            max-width: 100vw !important;
        }

        div[data-testid="stForm"] {
            position: fixed !important;
            z-index: 2147483647 !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            width: min(430px, calc(100vw - 40px)) !important;
            padding: 34px 32px 30px 32px !important;
            border-radius: 28px !important;
            background: rgba(255, 255, 255, 0.96) !important;
            border: 1px solid rgba(56, 130, 83, 0.20) !important;
            box-shadow: 0 24px 80px rgba(31, 41, 55, 0.22) !important;
        }

        div[data-testid="stForm"] h1,
        div[data-testid="stForm"] h2,
        div[data-testid="stForm"] h3,
        div[data-testid="stForm"] p,
        div[data-testid="stForm"] label,
        div[data-testid="stForm"] span {
            color: #2f3342 !important;
        }

        div[data-testid="stForm"] input {
            background: #f3f6f5 !important;
            color: #2f3342 !important;
            border: 1px solid rgba(47, 51, 66, 0.18) !important;
            border-radius: 14px !important;
        }

        div[data-testid="stForm"] input:focus {
            border-color: #388253 !important;
            box-shadow: 0 0 0 1px #388253 !important;
        }

        div[data-testid="stForm"] button[kind="primaryFormSubmit"] {
            width: 100% !important;
            background: #388253 !important;
            color: #ffffff !important;
            border: 0 !important;
            border-radius: 14px !important;
            min-height: 46px !important;
            font-weight: 800 !important;
            margin-top: 8px !important;
        }

        div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover {
            background: #2f7048 !important;
            color: #ffffff !important;
        }

        .access-lock-title {
            font-size: 2rem;
            line-height: 1.12;
            font-weight: 900;
            color: #2f3342;
            margin: 0 0 8px 0;
            letter-spacing: -0.04em;
            text-align: center;
        }

        .access-lock-subtitle {
            font-size: 0.98rem;
            line-height: 1.45;
            color: #6b7280;
            margin: 0 0 22px 0;
            text-align: center;
        }

        .access-lock-badge {
            width: 54px;
            height: 54px;
            margin: 0 auto 16px auto;
            border-radius: 18px;
            background: rgba(56, 130, 83, 0.12);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #388253;
            font-size: 1.75rem;
            font-weight: 900;
        }

        @media (prefers-color-scheme: dark) {
            .stApp {
                background: linear-gradient(135deg, #171b23 0%, #222934 100%) !important;
            }
            .stApp::before {
                background: rgba(17, 24, 39, 0.78) !important;
            }
            div[data-testid="stForm"] {
                background: rgba(35, 40, 52, 0.96) !important;
                border-color: rgba(255, 255, 255, 0.10) !important;
                box-shadow: 0 24px 80px rgba(0, 0, 0, 0.40) !important;
            }
            div[data-testid="stForm"] h1,
            div[data-testid="stForm"] h2,
            div[data-testid="stForm"] h3,
            div[data-testid="stForm"] p,
            div[data-testid="stForm"] label,
            div[data-testid="stForm"] span,
            .access-lock-title {
                color: #f9fafb !important;
            }
            .access-lock-subtitle {
                color: #d1d5db !important;
            }
            div[data-testid="stForm"] input {
                background: #111827 !important;
                color: #f9fafb !important;
                border-color: rgba(255, 255, 255, 0.16) !important;
            }
        }
        
.tx-category-line {
    margin: 0.45rem 0 0.35rem 0;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.35rem;
}
.tx-category-pill {
    display: inline-flex;
    align-items: center;
    width: fit-content;
    padding: 0.18rem 0.55rem;
    border-radius: 999px;
    background: rgba(56, 130, 83, 0.12);
    color: #2f6f47;
    font-size: 0.78rem;
    font-weight: 800;
}
.tx-tag {
    display: inline-flex;
    align-items: center;
    padding: 0.15rem 0.45rem;
    border-radius: 999px;
    background: rgba(47, 51, 66, 0.08);
    color: #6b7280;
    font-size: 0.74rem;
    font-weight: 700;
}
@media (prefers-color-scheme: dark) {
    .tx-category-pill { background: rgba(56, 130, 83, 0.26); color: #d6f5df; }
    .tx-tag { background: rgba(255,255,255,0.10); color: #d7dbe3; }
}
</style>
        """,
        unsafe_allow_html=True,
    )

    expected_password = get_app_access_password()
    with st.form("access_password_form", clear_on_submit=False):
        st.markdown('<div class="access-lock-badge">🔒</div>', unsafe_allow_html=True)
        st.markdown('<div class="access-lock-title">Acesso restrito</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="access-lock-subtitle">Digite a senha para abrir o Meu App Finanças.</div>',
            unsafe_allow_html=True,
        )
        typed_password = st.text_input("Senha", type="password", placeholder="Digite a senha")
        submitted = st.form_submit_button("Entrar")

        if not expected_password:
            st.error("Senha de acesso não configurada nos Secrets do Streamlit.")
        elif submitted:
            if typed_password == expected_password:
                st.session_state["app_authenticated"] = True
                st.rerun()
            else:
                st.error("Senha incorreta. Tente novamente.")


if "app_authenticated" not in st.session_state:
    st.session_state["app_authenticated"] = False

if not st.session_state["app_authenticated"]:
    render_password_gate()
    st.stop()

# 🌟 CSS AGRESSIVO: Forçando a remoção do laranja em tudo
st.markdown("""
<style>
/* 1. Cores de Destaque Global (Remove o Laranja) */
:root {
    --primary-color: #388253 !important;
}

/* 2. Fundo Principal */
.stApp {
    background-color: #ffffff !important;
}

/* 2.0 Remove a faixa superior fixa do Streamlit que pode sobrepor/cortar o logo */
[data-testid="stHeader"],
header[data-testid="stHeader"] {
    background: transparent !important;
    background-color: transparent !important;
    box-shadow: none !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

[data-testid="stToolbar"] {
    background: transparent !important;
}

/* 2.1 Reduz o espaço em branco no topo da área principal */
.block-container,
[data-testid="stMain"] .block-container,
[data-testid="stAppViewContainer"] .block-container,
section.main > div.block-container {
    padding-top: 1.6rem !important;
}

/* Mantém um respiro mínimo no topo em telas menores */
@media (max-width: 768px) {
    .block-container,
    [data-testid="stMain"] .block-container,
    [data-testid="stAppViewContainer"] .block-container,
    section.main > div.block-container {
        padding-top: 1rem !important;
    }
}

/* 3. Barra Lateral Escura */
[data-testid="stSidebar"] {
    background-color: #262b35 !important;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
    color: #ffffff !important;
}

/* 3.1 Ajusta o respiro superior da sidebar */
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding-top: 0.55rem !important;
}


/* 4. Botão de Abrir/Fechar Sidebar
   Versão limpa, sem pseudo-elementos, para evitar ícone duplicado.
*/

/* MENU ABERTO: botão de recolher sempre evidente */
[data-testid="stSidebarCollapseButton"] {
    opacity: 1 !important;
    visibility: visible !important;
    display: flex !important;
    pointer-events: auto !important;
}

[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapseButton"] [role="button"] {
    opacity: 1 !important;
    visibility: visible !important;
    background-color: rgba(255, 255, 255, 0.14) !important;
    border: 1px solid rgba(255, 255, 255, 0.35) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    box-shadow: none !important;
}

[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stSidebarCollapseButton"] button:focus,
[data-testid="stSidebarCollapseButton"] button:active,
[data-testid="stSidebarCollapseButton"] [role="button"]:hover,
[data-testid="stSidebarCollapseButton"] [role="button"]:focus,
[data-testid="stSidebarCollapseButton"] [role="button"]:active {
    background-color: rgba(255, 255, 255, 0.22) !important;
    border-color: rgba(255, 255, 255, 0.55) !important;
    color: #ffffff !important;
}

[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarCollapseButton"] svg *,
[data-testid="stSidebarCollapseButton"] svg path {
    opacity: 1 !important;
    color: #ffffff !important;
    fill: #ffffff !important;
    stroke: #ffffff !important;
    filter: brightness(0) invert(1) !important;
}

/* MENU FECHADO: botão de abrir verde #388253 sobre fundo branco */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    opacity: 1 !important;
    visibility: visible !important;
    display: flex !important;
    pointer-events: auto !important;
    background-color: #ffffff !important;
}

[data-testid="collapsedControl"] button,
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] [role="button"],
[data-testid="stSidebarCollapsedControl"] [role="button"] {
    opacity: 1 !important;
    visibility: visible !important;
    background-color: #ffffff !important;
    border: none !important;
    color: #388253 !important;
    box-shadow: none !important;
}

[data-testid="collapsedControl"] button:hover,
[data-testid="collapsedControl"] button:focus,
[data-testid="collapsedControl"] button:active,
[data-testid="stSidebarCollapsedControl"] button:hover,
[data-testid="stSidebarCollapsedControl"] button:focus,
[data-testid="stSidebarCollapsedControl"] button:active,
[data-testid="collapsedControl"] [role="button"]:hover,
[data-testid="collapsedControl"] [role="button"]:focus,
[data-testid="collapsedControl"] [role="button"]:active,
[data-testid="stSidebarCollapsedControl"] [role="button"]:hover,
[data-testid="stSidebarCollapsedControl"] [role="button"]:focus,
[data-testid="stSidebarCollapsedControl"] [role="button"]:active {
    background-color: #ffffff !important;
    color: #388253 !important;
    box-shadow: none !important;
}

[data-testid="collapsedControl"] svg,
[data-testid="collapsedControl"] svg *,
[data-testid="collapsedControl"] svg path,
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg *,
[data-testid="stSidebarCollapsedControl"] svg path {
    opacity: 1 !important;
    color: #388253 !important;
    fill: #388253 !important;
    stroke: #388253 !important;
    filter: brightness(0) saturate(100%) invert(42%) sepia(13%) saturate(1697%) hue-rotate(91deg) brightness(93%) contrast(87%) !important;
}

/* Texto "Mostrar menu" quando a sidebar está fechada
   Agora o texto é criado por JavaScript em posição fixa no canto superior esquerdo.
   Evitamos pseudo-elementos em botões genéricos para não jogar o texto na toolbar do Streamlit. */
#custom-show-menu-label {
    position: fixed !important;
    left: 4.05rem !important;
    top: 1.85rem !important;
    z-index: 9999999 !important;
    color: #6f737b !important;
    font-family: inherit !important;
    font-size: 0.9rem !important;
    font-weight: 400 !important;
    line-height: 1 !important;
    white-space: nowrap !important;
    pointer-events: none !important;
}

/* 4.1 Área de Cartões de Crédito na Sidebar */
.credit-cards-spacer {
    height: 2rem;
}

.sidebar-section-title,
.credit-cards-title {
    color: #ffffff !important;
    font-family: inherit !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    line-height: 1.2 !important;
    margin: 0 0 0.8rem 0 !important;
    letter-spacing: 0 !important;
}

.credit-cards-line {
    width: 100%;
    height: 1px;
    background-color: rgba(255, 255, 255, 0.12);
    margin: 0 0 0.95rem 0;
}

.credit-card-name-block,
.credit-card-info {
    height: 34px !important;
    margin: 0 !important;
    padding: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    transform: translateY(1px);
}

.credit-card-name-block div,
.credit-card-info div {
    margin: 0 !important;
    padding: 0 !important;
}

.credit-card-name {
    color: rgba(255, 255, 255, 0.88) !important;
    font-size: 0.68rem !important;
    font-weight: 800 !important;
    line-height: 1.06 !important;
    white-space: nowrap !important;
}

.credit-card-limit {
    color: rgba(255, 255, 255, 0.62) !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    line-height: 1.06 !important;
    white-space: nowrap !important;
}


.credit-card-info {
    color: rgba(255, 255, 255, 0.62) !important;
    font-size: 0.65rem !important;
    font-weight: 600 !important;
    line-height: 1.06 !important;
    white-space: nowrap !important;
}

.credit-card-gap {
    height: 0.85rem;
}


.credit-card-logo-img {
    width: 34px !important;
    height: 34px !important;
    object-fit: contain !important;
    border-radius: 5px !important;
    display: block !important;
    transform: none !important;
}

.credit-card-logo-fallback {
    transform: none !important;
    width: 34px;
    height: 34px;
    border-radius: 5px;
    background-color: rgba(255, 255, 255, 0.14);
    color: #ffffff !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.68rem;
    font-weight: 700;
}

[data-testid="stSidebar"] [data-testid="stImage"] {
    margin: 0 !important;
    padding: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stImage"] img {
    display: block !important;
    width: 28px !important;
    max-width: 28px !important;
    height: auto !important;
    border-radius: 5px !important;
}

[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] {
    align-items: center !important;
}


/* 4.2 Seções recolhíveis da sidebar */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    margin: 0 0 1.8rem 0 !important;
}

[data-testid="stSidebar"] [data-testid="stExpander"] details {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"] [data-testid="stExpander"] details > summary {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    min-height: 1.9rem !important;
}

[data-testid="stSidebar"] [data-testid="stExpander"] details > summary:hover {
    background: rgba(255, 255, 255, 0.04) !important;
    border-radius: 6px !important;
}

[data-testid="stSidebar"] [data-testid="stExpander"] summary p {
    color: #ffffff !important;
    font-family: inherit !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    line-height: 1.2 !important;
    letter-spacing: 0 !important;
}

/* Seta do expander bem visível no fundo escuro da sidebar */
[data-testid="stSidebar"] [data-testid="stExpander"] summary svg,
[data-testid="stSidebar"] [data-testid="stExpander"] summary svg *,
[data-testid="stSidebar"] [data-testid="stExpander"] summary svg path,
[data-testid="stSidebar"] [data-testid="stExpander"] summary [data-testid="stExpanderToggleIcon"],
[data-testid="stSidebar"] [data-testid="stExpander"] summary [data-testid="stExpanderToggleIcon"] *,
[data-testid="stSidebar"] [data-testid="stExpander"] summary [data-testid="stIconMaterial"],
[data-testid="stSidebar"] [data-testid="stExpander"] summary [data-testid="stIconMaterial"] * {
    color: #e5e7eb !important;
    fill: #e5e7eb !important;
    stroke: #e5e7eb !important;
    opacity: 1 !important;
}

[data-testid="stSidebar"] [data-testid="stExpander"] summary > div:first-child {
    color: #e5e7eb !important;
    opacity: 1 !important;
}

[data-testid="stSidebar"] [data-testid="stExpander"] details > summary:hover svg,
[data-testid="stSidebar"] [data-testid="stExpander"] details > summary:hover svg *,
[data-testid="stSidebar"] [data-testid="stExpander"] details > summary:hover svg path,
[data-testid="stSidebar"] [data-testid="stExpander"] details > summary:hover [data-testid="stExpanderToggleIcon"],
[data-testid="stSidebar"] [data-testid="stExpander"] details > summary:hover [data-testid="stExpanderToggleIcon"] * {
    color: #ffffff !important;
    fill: #ffffff !important;
    stroke: #ffffff !important;
    opacity: 1 !important;
}

[data-testid="stSidebar"] [data-testid="stExpanderDetails"] {
    padding: 0.75rem 0 0 0 !important;
}

[data-testid="stSidebar"] [data-testid="stExpander"] .streamlit-expanderContent {
    padding: 0.75rem 0 0 0 !important;
}


/* 4.3 Menu de navegação da sidebar */
.sidebar-nav-title {
    color: #ffffff !important;
    font-family: inherit !important;
    font-size: 1.05rem !important;
    font-weight: 800 !important;
    line-height: 1.2 !important;
    margin: 0.15rem 0 0.7rem 0 !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 0.35rem !important;
    margin-bottom: 1.35rem !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.10) !important;
    border-radius: 10px !important;
    padding: 0.58rem 0.7rem !important;
    transition: all 0.18s ease !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(255, 255, 255, 0.10) !important;
    border-color: rgba(255, 255, 255, 0.18) !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label p {
    color: rgba(255, 255, 255, 0.90) !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: rgba(56, 130, 83, 0.22) !important;
    border-color: rgba(56, 130, 83, 0.72) !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    color: #ffffff !important;
}

/* 4.4 Página Contas e Assinaturas */
.page-kicker {
    color: #6b7280 !important;
    font-size: 0.92rem !important;
    margin: 0.15rem 0 1.2rem 0 !important;
}

.bills-summary-grid {
    display: grid !important;
    grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
    gap: 1rem !important;
    margin: 1.05rem 0 1.45rem 0 !important;
}

.bills-summary-card {
    border-radius: 18px !important;
    padding: 1.05rem 1.1rem !important;
    border: 1px solid rgba(38, 43, 53, 0.08) !important;
    background: #f8fafc !important;
    box-shadow: 0 14px 30px rgba(17, 24, 39, 0.05) !important;
}

.bills-summary-label {
    font-size: 0.78rem !important;
    font-weight: 800 !important;
    color: #4b5563 !important;
    margin-bottom: 0.4rem !important;
}

.bills-summary-value {
    font-size: clamp(1.25rem, 1.8vw, 1.9rem) !important;
    font-weight: 800 !important;
    color: #2f3140 !important;
    white-space: nowrap !important;
}

.bill-card {
    border: 1px solid rgba(38, 43, 53, 0.12) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
    margin-bottom: 0.75rem !important;
    background: #ffffff !important;
}

.bill-card-title {
    color: #2f3140 !important;
    font-size: 1rem !important;
    font-weight: 800 !important;
    margin-bottom: 0.25rem !important;
}

.bill-card-meta {
    color: #6b7280 !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    margin-bottom: 0.65rem !important;
}

.bill-card-value {
    color: #328655 !important;
    font-size: 1.15rem !important;
    font-weight: 900 !important;
}

.bill-status-pill {
    display: inline-flex !important;
    align-items: center !important;
    border-radius: 999px !important;
    padding: 0.2rem 0.55rem !important;
    background: rgba(56, 130, 83, 0.10) !important;
    color: #328655 !important;
    font-size: 0.72rem !important;
    font-weight: 800 !important;
    margin-left: 0.35rem !important;
}

.bill-card.bill-card-paid {
    background: #e7f6ed !important;
    border-color: #7bc69a !important;
    box-shadow: 0 12px 26px rgba(50, 134, 85, 0.10) !important;
}

.bill-card.bill-card-overdue {
    background: #fde8e8 !important;
    border-color: #ef8e8e !important;
    box-shadow: 0 12px 26px rgba(185, 55, 55, 0.10) !important;
}

.bill-card.bill-card-due-soon {
    background: #fff7d6 !important;
    border-color: #e6bd42 !important;
    box-shadow: 0 12px 26px rgba(194, 148, 23, 0.10) !important;
}

.bill-card.bill-card-pending {
    background: #ffffff !important;
}

.bill-status-pill.bill-status-paid {
    background: rgba(50, 134, 85, 0.16) !important;
    color: #237044 !important;
}

.bill-status-pill.bill-status-overdue {
    background: rgba(196, 55, 55, 0.14) !important;
    color: #b4232b !important;
}

.bill-status-pill.bill-status-due-soon {
    background: rgba(205, 155, 20, 0.18) !important;
    color: #8a6500 !important;
}

.bill-status-pill.bill-status-pending {
    background: rgba(107, 114, 128, 0.12) !important;
    color: #4b5563 !important;
}

.bills-summary-card.bills-summary-remaining-zero {
    background: #e7f6ed !important;
    border-color: #7bc69a !important;
}

.bills-summary-card.bills-summary-remaining-open {
    background: #fff7e8 !important;
    border-color: #edc77f !important;
}

@media (max-width: 900px) {
    .bills-summary-grid {
        grid-template-columns: 1fr !important;
    }
}


/* 5. Remoção de bordas e focos laranjas em Inputs/Selects */
div[data-baseweb="select"] > div {
    border-color: #b4b4b4 !important;
}
div[data-baseweb="select"]:focus-within {
    border-color: #318655 !important;
    box-shadow: 0 0 0 1px #318655 !important;
}

/* 6. Botões Secundários */
div.stButton > button[kind="secondary"] {
    border-color: #b4b4b4 !important;
    color: #262b35 !important;
    background-color: #ffffff !important;
}
div.stButton > button[kind="secondary"]:hover {
    border-color: #318655 !important;
    color: #318655 !important;
}

/* 7. Botão Primário (Salvar) */
div.stButton > button[kind="primary"] {
    background-color: #318655 !important;
    color: white !important;
    border: none !important;
}


/* 8. Cards de resumo financeiro */
.summary-cards-grid {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: clamp(0.55rem, 1.2vw, 0.95rem);
    align-items: stretch;
}

.summary-card {
    border-radius: 22px;
    padding: clamp(0.9rem, 1.5vw, 1.15rem) clamp(0.85rem, 1.6vw, 1.25rem);
    min-height: clamp(98px, 9vw, 118px);
    border: 1px solid rgba(38, 43, 53, 0.06);
    box-shadow: 0 10px 24px rgba(38, 43, 53, 0.055);
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-width: 0;
    overflow: hidden;
    container-type: inline-size;
}

.summary-card-bank {
    background: #f3f4f6;
}

.summary-card-cash {
    background: #fbf0dc;
}

.summary-card-income {
    background: #e7f4ed;
}

.summary-card-expense {
    background: #fde7e7;
}

.summary-card-label {
    color: #2f3341;
    font-size: clamp(0.68rem, 5.2cqw, 0.9rem);
    font-weight: 600;
    line-height: 1.12;
    margin-bottom: clamp(0.35rem, 1.6cqw, 0.55rem);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.summary-card-value {
    color: #2f3341;
    font-size: clamp(1.22rem, 14.5cqw, 2.25rem);
    font-weight: 500;
    line-height: 1.03;
    letter-spacing: -0.045em;
    white-space: nowrap;
    max-width: 100%;
}

@media (max-width: 900px) {
    .summary-cards-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 560px) {
    .summary-cards-grid {
        grid-template-columns: 1fr;
    }
}


/* 9. Mini gráfico Top 10 gastos do mês */
.top-expenses-chart {
    width: 100%;
    height: 116px;
    padding: 0.45rem 0.65rem 0.35rem 0.65rem;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(38, 43, 53, 0.06);
    box-shadow: 0 8px 22px rgba(38, 43, 53, 0.045);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: visible;
    position: relative;
    z-index: 5;
}

.top-expenses-title {
    color: rgba(47, 51, 65, 0.75);
    font-size: 0.64rem;
    font-weight: 700;
    line-height: 1;
    margin: 0 0 0.25rem 0;
    white-space: nowrap;
}

.top-expenses-bars {
    height: 82px;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: clamp(0.22rem, 0.6vw, 0.5rem);
}

.top-expense-bar-slot {
    height: 100%;
    min-width: 0;
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    position: relative;
}

.top-expense-bar {
    width: min(100%, 26px);
    min-height: 7px;
    border-radius: 7px 7px 2px 2px;
    box-shadow: inset 0 -1px 0 rgba(0, 0, 0, 0.08);
    transition: height 0.25s ease;
}

.top-expense-bar-label {
    color: rgba(47, 51, 65, 0.55);
    font-size: 0.45rem;
    font-weight: 600;
    line-height: 1;
    max-width: 100%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-top: 0.16rem;
}

.top-expense-tooltip {
    position: absolute;
    left: 50%;
    bottom: calc(100% + 0.35rem);
    transform: translateX(-50%) translateY(4px);
    min-width: 128px;
    max-width: 190px;
    padding: 0.42rem 0.5rem;
    border-radius: 10px;
    background: rgba(38, 43, 53, 0.96);
    color: #ffffff;
    box-shadow: 0 8px 18px rgba(38, 43, 53, 0.20);
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    z-index: 50;
    transition: opacity 0.16s ease, transform 0.16s ease, visibility 0.16s ease;
    text-align: left;
}

.top-expense-tooltip::after {
    content: "";
    position: absolute;
    left: 50%;
    bottom: -5px;
    transform: translateX(-50%);
    width: 10px;
    height: 10px;
    background: rgba(38, 43, 53, 0.96);
    rotate: 45deg;
}

.top-expense-tooltip-name {
    display: block;
    font-size: 0.62rem;
    font-weight: 700;
    line-height: 1.15;
    white-space: normal;
    word-break: break-word;
    margin-bottom: 0.18rem;
}

.top-expense-tooltip-value {
    display: block;
    font-size: 0.66rem;
    font-weight: 800;
    line-height: 1;
    color: #e8f5ee;
    white-space: nowrap;
}

.top-expense-bar-slot:hover {
    z-index: 60;
}

.top-expense-bar-slot:hover .top-expense-tooltip {
    opacity: 1;
    visibility: visible;
    transform: translateX(-50%) translateY(0);
}

.top-expense-bar-slot:hover .top-expense-bar {
    filter: brightness(0.96);
    transform: translateY(-2px);
}

.top-expense-bar-empty {
    background: rgba(47, 51, 65, 0.08) !important;
    box-shadow: none !important;
}

.top-expenses-chart-empty {
    justify-content: center;
    align-items: center;
    text-align: center;
    color: rgba(47, 51, 65, 0.55);
    font-size: 0.72rem;
    font-weight: 600;
}

@media (max-width: 900px) {
    .top-expenses-chart {
        height: 104px;
    }
    .top-expenses-bars {
        height: 72px;
    }
}


/* 4.5 Página Importar CSV */
.import-summary-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.85rem;
    margin: 1rem 0 1.2rem 0;
}
.import-summary-card {
    background: #f7f9f8;
    border: 1px solid rgba(38, 43, 53, 0.08);
    border-radius: 14px;
    padding: 0.85rem 0.95rem;
    box-shadow: 0 8px 20px rgba(38, 43, 53, 0.04);
}
.import-summary-label {
    font-size: 0.72rem;
    color: #6f7682;
    font-weight: 700;
    margin-bottom: 0.25rem;
}
.import-summary-value {
    font-size: clamp(1rem, 1.45vw, 1.35rem);
    color: #262b35;
    font-weight: 800;
    white-space: nowrap;
}
.import-note-box {
    background: #f4fbf7;
    border: 1px solid rgba(56, 130, 83, 0.16);
    border-radius: 14px;
    padding: 0.9rem 1rem;
    color: #384050;
    font-size: 0.9rem;
    line-height: 1.35;
    margin-bottom: 1rem;
}
@media (max-width: 900px) {
    .import-summary-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}


/* 10. Página Instalar App */
.install-app-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.9rem;
    margin: 1.15rem 0 1.25rem 0;
}
.install-step-card {
    background: #ffffff;
    border: 1px solid rgba(38, 43, 53, 0.08);
    border-radius: 18px;
    padding: 1rem;
    box-shadow: 0 12px 26px rgba(38, 43, 53, 0.055);
    min-height: 130px;
}
.install-step-number {
    width: 30px;
    height: 30px;
    border-radius: 999px;
    background: rgba(50, 134, 85, 0.12);
    color: #328655;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.82rem;
    font-weight: 900;
    margin-bottom: 0.75rem;
}
.install-step-title {
    color: #262b35;
    font-size: 0.95rem;
    font-weight: 850;
    line-height: 1.15;
    margin-bottom: 0.35rem;
}
.install-step-text {
    color: #6b7280;
    font-size: 0.82rem;
    font-weight: 600;
    line-height: 1.35;
}
.install-note-box {
    background: #f4fbf7;
    border: 1px solid rgba(56, 130, 83, 0.16);
    border-radius: 16px;
    padding: 1rem 1.1rem;
    color: #384050;
    font-size: 0.92rem;
    line-height: 1.42;
    margin: 1rem 0 1.25rem 0;
}
.install-mini-list {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.85rem;
    margin: 1rem 0 0 0;
}
.install-mini-card {
    border-radius: 16px;
    padding: 0.9rem 1rem;
    background: #f8fafc;
    border: 1px solid rgba(38, 43, 53, 0.08);
    color: #384050;
    font-size: 0.86rem;
    font-weight: 700;
}
.install-final-note {
    background: #e8f2ff;
    border-radius: 12px;
    padding: 1rem 1.15rem;
    color: #0f5fb3;
    font-size: 0.95rem;
    font-weight: 700;
    line-height: 1.35;
    margin-top: 2.9rem;
}
@media (max-width: 1100px) {
    .install-app-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .install-mini-list {
        grid-template-columns: 1fr;
    }
}
@media (max-width: 650px) {
    .install-app-grid {
        grid-template-columns: 1fr;
    }
}


/* 11. Correções para navegação mobile/iOS
   - força tema claro na área central
   - aumenta contraste de títulos, labels e textos
   - impede selects/inputs escuros no Safari/iOS
*/
html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMain"] * {
    color-scheme: light !important;
}

@media (max-width: 768px) {
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMain"] .block-container {
        background-color: #ffffff !important;
    }

    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3,
    [data-testid="stMain"] h4,
    [data-testid="stMain"] h5,
    [data-testid="stMain"] h6,
    [data-testid="stMain"] p,
    [data-testid="stMain"] span,
    [data-testid="stMain"] label,
    [data-testid="stMain"] label p,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"],
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] span {
        color: #2f3341 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #2f3341 !important;
    }

    [data-testid="stMain"] [data-testid="stTextInput"] input,
    [data-testid="stMain"] [data-testid="stNumberInput"] input,
    [data-testid="stMain"] [data-testid="stDateInput"] input,
    [data-testid="stMain"] [data-testid="stTextArea"] textarea,
    [data-testid="stMain"] textarea,
    [data-testid="stMain"] div[data-baseweb="select"] > div,
    [data-testid="stMain"] div[data-baseweb="select"] input,
    [data-testid="stMain"] div[data-baseweb="select"] span,
    [data-testid="stMain"] div[data-baseweb="select"] div {
        background-color: #f1f3f6 !important;
        color: #2f3341 !important;
        -webkit-text-fill-color: #2f3341 !important;
        border-color: #d1d5db !important;
        opacity: 1 !important;
    }

    [data-testid="stMain"] input::placeholder,
    [data-testid="stMain"] textarea::placeholder {
        color: #8a8f9a !important;
        -webkit-text-fill-color: #8a8f9a !important;
        opacity: 1 !important;
    }

    [data-testid="stMain"] div[data-baseweb="select"] svg,
    [data-testid="stMain"] div[data-baseweb="select"] svg path {
        color: #2f3341 !important;
        fill: #2f3341 !important;
        stroke: #2f3341 !important;
    }

    [data-testid="stMain"] [data-testid="stCheckbox"] label,
    [data-testid="stMain"] [data-testid="stCheckbox"] label p,
    [data-testid="stMain"] [data-testid="stCheckbox"] span {
        color: #2f3341 !important;
        -webkit-text-fill-color: #2f3341 !important;
        opacity: 1 !important;
    }

    [data-testid="stMain"] [data-testid="stCheckbox"] div[role="checkbox"] {
        background-color: #ffffff !important;
        border-color: #d1d5db !important;
    }

    [data-testid="stMain"] [data-testid="stCheckbox"] div[role="checkbox"][aria-checked="true"] {
        background-color: #388253 !important;
        border-color: #388253 !important;
    }

    /* Mantém a Home como experiência inicial no celular: sidebar recolhida por padrão */
    [data-testid="stSidebar"] {
        color-scheme: light !important;
    }

    /* Em telas muito estreitas, evita que o formulário encoste nas bordas */
    [data-testid="stMain"] .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
}


/* 12. Correção agressiva do botão de abrir menu no mobile/iOS
   O Streamlit/iOS pode aplicar opacidade no botão recolhido; aqui forçamos
   o controle, seus ancestrais diretos e o SVG a ficarem 100% visíveis. */
@media (max-width: 768px) {
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] *,
    [data-testid="stSidebarCollapsedControl"] * {
        opacity: 1 !important;
        visibility: visible !important;
        filter: none !important;
        color: #388253 !important;
        -webkit-text-fill-color: #388253 !important;
    }

    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        z-index: 9999999 !important;
        background: transparent !important;
        mix-blend-mode: normal !important;
        pointer-events: auto !important;
    }

    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="collapsedControl"] [role="button"],
    [data-testid="stSidebarCollapsedControl"] [role="button"] {
        opacity: 1 !important;
        visibility: visible !important;
        background: transparent !important;
        color: #388253 !important;
        -webkit-text-fill-color: #388253 !important;
        filter: none !important;
        mix-blend-mode: normal !important;
        box-shadow: none !important;
    }

    [data-testid="collapsedControl"] svg,
    [data-testid="collapsedControl"] svg *,
    [data-testid="collapsedControl"] svg path,
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg *,
    [data-testid="stSidebarCollapsedControl"] svg path,
    button[aria-label*="sidebar" i] svg,
    button[aria-label*="sidebar" i] svg *,
    button[aria-label*="sidebar" i] svg path,
    button[title*="sidebar" i] svg,
    button[title*="sidebar" i] svg *,
    button[title*="sidebar" i] svg path {
        opacity: 1 !important;
        visibility: visible !important;
        color: #388253 !important;
        fill: #388253 !important;
        stroke: #388253 !important;
        -webkit-text-fill-color: #388253 !important;
        filter: none !important;
        mix-blend-mode: normal !important;
    }
}


/* 13. Ícone customizado de abrir sidebar no mobile
   Em alguns builds do Streamlit/iOS, o SVG nativo herda opacidade/transparência.
   Em vez de depender da cor do SVG nativo, escondemos o SVG original via JS
   e desenhamos um ícone próprio por cima, sem bloquear o clique. */
#custom-sidebar-open-icon {
    position: fixed !important;
    z-index: 10000000 !important;
    color: #388253 !important;
    -webkit-text-fill-color: #388253 !important;
    font-family: Arial, Helvetica, sans-serif !important;
    font-size: 1.55rem !important;
    font-weight: 800 !important;
    line-height: 1 !important;
    opacity: 1 !important;
    visibility: visible !important;
    filter: none !important;
    mix-blend-mode: normal !important;
    text-shadow: 0 0 0 #388253, 0 1px 1px rgba(0,0,0,0.08) !important;
    pointer-events: none !important;
    transform: translate(-50%, -50%) !important;
}

/* No desktop, usamos apenas o ícone nativo do Streamlit para evitar duplicidade. */
@media (min-width: 769px) {
    #custom-sidebar-open-icon {
        display: none !important;
    }
}

@media (max-width: 768px) {
    #custom-sidebar-open-icon {
        font-size: 1.55rem !important;
    }
}


/* Logo do topo: troca automaticamente entre versão clara e dark mode */
.app-top-logo {
    width: var(--app-logo-width, 240px) !important;
    max-width: 100% !important;
}

.app-top-logo-img {
    width: var(--app-logo-width, 240px) !important;
    max-width: 100% !important;
    height: auto !important;
    display: block !important;
}

.app-top-logo-dark {
    display: none !important;
}

@media (prefers-color-scheme: dark) {
    .app-top-logo-light {
        display: none !important;
    }

    .app-top-logo-dark {
        display: block !important;
    }
}

@media (prefers-color-scheme: light) {
    .app-top-logo-light {
        display: block !important;
    }

    .app-top-logo-dark {
        display: none !important;
    }
}


/* Categoria, subcategoria e tags nas transações */
.tx-category-line {
    margin: 0.45rem 0 0.35rem 0;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.35rem;
}
.tx-category-pill {
    display: inline-flex;
    align-items: center;
    width: fit-content;
    padding: 0.18rem 0.55rem;
    border-radius: 999px;
    background: rgba(56, 130, 83, 0.12);
    color: #2f6f47;
    font-size: 0.78rem;
    font-weight: 800;
}
.tx-tag {
    display: inline-flex;
    align-items: center;
    padding: 0.15rem 0.45rem;
    border-radius: 999px;
    background: rgba(47, 51, 66, 0.08);
    color: #6b7280;
    font-size: 0.74rem;
    font-weight: 700;
}
@media (prefers-color-scheme: dark) {
    .tx-category-pill { background: rgba(56, 130, 83, 0.26) !important; color: #d6f5df !important; }
    .tx-tag { background: rgba(255,255,255,0.10) !important; color: #d7dbe3 !important; }
}

</style>
""", unsafe_allow_html=True)

# Ajuste de tema automático: claro/escuro conforme preferência do dispositivo
st.markdown("""
<style>
/* =========================================================
   Tema adaptativo por preferência do dispositivo
   - modo claro: mantém a experiência atual
   - modo escuro: aplica contraste real na área central
   ========================================================= */

:root {
    color-scheme: light dark !important;
}

@media (prefers-color-scheme: dark) {
    html,
    body,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMain"] .block-container,
    section.main,
    section.main > div {
        background-color: #0f1117 !important;
        color: #f4f6fb !important;
        color-scheme: dark !important;
    }

    [data-testid="stHeader"],
    header[data-testid="stHeader"],
    [data-testid="stToolbar"] {
        background: transparent !important;
        background-color: transparent !important;
        color: #f4f6fb !important;
    }

    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3,
    [data-testid="stMain"] h4,
    [data-testid="stMain"] h5,
    [data-testid="stMain"] h6,
    [data-testid="stMain"] p,
    [data-testid="stMain"] span,
    [data-testid="stMain"] label,
    [data-testid="stMain"] label p,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"],
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] span {
        color: #f4f6fb !important;
        -webkit-text-fill-color: #f4f6fb !important;
        opacity: 1 !important;
    }

    [data-testid="stMain"] label,
    [data-testid="stMain"] label p {
        color: #d8dce6 !important;
        -webkit-text-fill-color: #d8dce6 !important;
        font-weight: 650 !important;
    }

    [data-testid="stMain"] small,
    [data-testid="stMain"] .page-kicker,
    [data-testid="stMain"] .bill-card-meta,
    [data-testid="stMain"] .install-step-text,
    [data-testid="stMain"] .import-summary-label,
    [data-testid="stMain"] .bills-summary-label {
        color: #aeb6c5 !important;
        -webkit-text-fill-color: #aeb6c5 !important;
    }

    /* Inputs, selects, textareas e popovers */
    [data-testid="stMain"] [data-testid="stTextInput"] input,
    [data-testid="stMain"] [data-testid="stNumberInput"] input,
    [data-testid="stMain"] [data-testid="stDateInput"] input,
    [data-testid="stMain"] [data-testid="stTextArea"] textarea,
    [data-testid="stMain"] textarea,
    [data-testid="stMain"] input,
    [data-testid="stMain"] div[data-baseweb="select"] > div,
    [data-testid="stMain"] div[data-baseweb="select"] input,
    [data-testid="stMain"] div[data-baseweb="select"] span,
    [data-testid="stMain"] div[data-baseweb="select"] div {
        background-color: #1d222d !important;
        color: #f4f6fb !important;
        -webkit-text-fill-color: #f4f6fb !important;
        border-color: #3a4150 !important;
        opacity: 1 !important;
        caret-color: #f4f6fb !important;
    }

    [data-testid="stMain"] input::placeholder,
    [data-testid="stMain"] textarea::placeholder {
        color: #9aa3b2 !important;
        -webkit-text-fill-color: #9aa3b2 !important;
        opacity: 1 !important;
    }

    [data-testid="stMain"] div[data-baseweb="select"] svg,
    [data-testid="stMain"] div[data-baseweb="select"] svg path {
        color: #f4f6fb !important;
        fill: #f4f6fb !important;
        stroke: #f4f6fb !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="popover"] *,
    div[data-baseweb="menu"],
    div[data-baseweb="menu"] * {
        background-color: #1d222d !important;
        color: #f4f6fb !important;
        -webkit-text-fill-color: #f4f6fb !important;
        border-color: #3a4150 !important;
    }

    div[data-baseweb="calendar"],
    div[data-baseweb="calendar"] *,
    [role="dialog"],
    [role="dialog"] * {
        background-color: #1d222d !important;
        color: #f4f6fb !important;
        -webkit-text-fill-color: #f4f6fb !important;
    }

    /* Checkbox */
    [data-testid="stMain"] [data-testid="stCheckbox"] label,
    [data-testid="stMain"] [data-testid="stCheckbox"] label p,
    [data-testid="stMain"] [data-testid="stCheckbox"] span {
        color: #d8dce6 !important;
        -webkit-text-fill-color: #d8dce6 !important;
        opacity: 1 !important;
    }

    [data-testid="stMain"] [data-testid="stCheckbox"] div[role="checkbox"] {
        background-color: #151922 !important;
        border-color: #4b5563 !important;
    }

    [data-testid="stMain"] [data-testid="stCheckbox"] div[role="checkbox"][aria-checked="true"] {
        background-color: #388253 !important;
        border-color: #388253 !important;
    }

    /* Cards de saldo no modo escuro */
    .summary-card {
        border-color: rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 12px 26px rgba(0, 0, 0, 0.22) !important;
    }

    .summary-card-bank {
        background: #1b202a !important;
    }

    .summary-card-cash {
        background: #302a1e !important;
    }

    .summary-card-income {
        background: #173225 !important;
    }

    .summary-card-expense {
        background: #3a2021 !important;
    }

    .summary-card-label,
    .summary-card-value {
        color: #f4f6fb !important;
        -webkit-text-fill-color: #f4f6fb !important;
    }

    /* Top 10 gastos */
    .top-expenses-chart {
        background: #171c26 !important;
        border-color: rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.20) !important;
    }

    .top-expenses-title,
    .top-expense-bar-label,
    .top-expenses-chart-empty {
        color: #cbd2df !important;
        -webkit-text-fill-color: #cbd2df !important;
    }

    .top-expense-bar-empty {
        background: rgba(255, 255, 255, 0.13) !important;
    }

    .top-expense-tooltip,
    .top-expense-tooltip::after {
        background: rgba(7, 10, 16, 0.97) !important;
    }

    .top-expense-tooltip-name,
    .top-expense-tooltip-value {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* Cards e blocos internos */
    .bill-card,
    .bills-summary-card,
    .import-summary-card,
    .install-step-card,
    .install-mini-card {
        background: #171c26 !important;
        border-color: rgba(255, 255, 255, 0.09) !important;
        box-shadow: 0 12px 26px rgba(0, 0, 0, 0.20) !important;
    }

    .bill-card-title,
    .bills-summary-value,
    .import-summary-value,
    .install-step-title,
    .install-mini-card {
        color: #f4f6fb !important;
        -webkit-text-fill-color: #f4f6fb !important;
    }

    .bill-card-value {
        color: #5fd08b !important;
        -webkit-text-fill-color: #5fd08b !important;
    }

    .bill-status-pill {
        background: rgba(95, 208, 139, 0.16) !important;
        color: #72e19f !important;
        -webkit-text-fill-color: #72e19f !important;
    }

    .bill-card.bill-card-paid {
        background: #173225 !important;
        border-color: #3f9b67 !important;
        box-shadow: 0 12px 26px rgba(0, 0, 0, 0.22) !important;
    }

    .bill-card.bill-card-overdue {
        background: #3a2021 !important;
        border-color: #a64f55 !important;
        box-shadow: 0 12px 26px rgba(0, 0, 0, 0.22) !important;
    }

    .bill-card.bill-card-due-soon {
        background: #3b3217 !important;
        border-color: #b99735 !important;
        box-shadow: 0 12px 26px rgba(0, 0, 0, 0.22) !important;
    }

    .bill-card.bill-card-pending {
        background: #171c26 !important;
        border-color: rgba(255, 255, 255, 0.09) !important;
    }

    .bill-status-pill.bill-status-paid {
        background: rgba(95, 208, 139, 0.18) !important;
        color: #72e19f !important;
        -webkit-text-fill-color: #72e19f !important;
    }

    .bill-status-pill.bill-status-overdue {
        background: rgba(255, 115, 122, 0.18) !important;
        color: #ff9a9f !important;
        -webkit-text-fill-color: #ff9a9f !important;
    }

    .bill-status-pill.bill-status-due-soon {
        background: rgba(237, 193, 67, 0.18) !important;
        color: #f1cf67 !important;
        -webkit-text-fill-color: #f1cf67 !important;
    }

    .bill-status-pill.bill-status-pending {
        background: rgba(174, 182, 197, 0.14) !important;
        color: #cbd2df !important;
        -webkit-text-fill-color: #cbd2df !important;
    }

    .bills-summary-card.bills-summary-remaining-zero {
        background: #173225 !important;
        border-color: #3f9b67 !important;
    }

    .bills-summary-card.bills-summary-remaining-open {
        background: #302a1e !important;
        border-color: #8a7130 !important;
    }

    .import-note-box,
    .install-note-box {
        background: #13251b !important;
        border-color: rgba(95, 208, 139, 0.22) !important;
        color: #d8f3e2 !important;
        -webkit-text-fill-color: #d8f3e2 !important;
    }

    .install-final-note {
        background: #142033 !important;
        color: #c9ddff !important;
        -webkit-text-fill-color: #c9ddff !important;
    }

    .install-step-number {
        background: rgba(95, 208, 139, 0.18) !important;
        color: #72e19f !important;
        -webkit-text-fill-color: #72e19f !important;
    }

    /* Histórico, expanders, tabelas e botões */
    [data-testid="stMain"] [data-testid="stExpander"] details,
    [data-testid="stMain"] [data-testid="stExpander"] details > summary {
        background-color: #171c26 !important;
        border-color: rgba(255, 255, 255, 0.10) !important;
        color: #f4f6fb !important;
    }

    [data-testid="stMain"] [data-testid="stExpander"] summary p,
    [data-testid="stMain"] [data-testid="stExpander"] summary svg,
    [data-testid="stMain"] [data-testid="stExpander"] summary svg * {
        color: #f4f6fb !important;
        fill: #f4f6fb !important;
        stroke: #f4f6fb !important;
        -webkit-text-fill-color: #f4f6fb !important;
    }

    div.stButton > button[kind="secondary"] {
        border-color: #3a4150 !important;
        color: #f4f6fb !important;
        background-color: #171c26 !important;
    }

    div.stButton > button[kind="secondary"]:hover {
        border-color: #5fd08b !important;
        color: #72e19f !important;
        background-color: #1d2430 !important;
    }

    div.stButton > button[kind="primary"] {
        background-color: #328655 !important;
        color: #ffffff !important;
    }

    [data-testid="stAlert"] {
        background-color: #171c26 !important;
        color: #f4f6fb !important;
        border-color: rgba(255, 255, 255, 0.10) !important;
    }

    [data-testid="stAlert"] *,
    [data-testid="stInfo"] *,
    [data-testid="stSuccess"] *,
    [data-testid="stError"] * {
        color: inherit !important;
        -webkit-text-fill-color: inherit !important;
    }

    hr,
    [data-testid="stDivider"] {
        border-color: rgba(255, 255, 255, 0.12) !important;
    }

    /* Dataframes / tabelas do Streamlit
       Observação: o st.data_editor usa canvas/Glide Data Grid. Em dark mode,
       forçar só o fundo do container escuro deixa a prévia invisível. Por isso,
       a grade de pré-visualização fica em tema claro controlado por variáveis
       do Glide, mesmo quando o resto do app está em modo escuro. */
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        color-scheme: light !important;
        background-color: #ffffff !important;
        color: #2f3342 !important;
        -webkit-text-fill-color: #2f3342 !important;
        border-color: rgba(47, 51, 66, 0.12) !important;
        --gdg-bg-cell: #ffffff !important;
        --gdg-bg-cell-medium: #f8fafc !important;
        --gdg-bg-header: #f3f5f8 !important;
        --gdg-bg-header-hovered: #edf1f5 !important;
        --gdg-bg-header-has-focus: #e8eef3 !important;
        --gdg-text-dark: #2f3342 !important;
        --gdg-text-medium: #4b5563 !important;
        --gdg-text-light: #6b7280 !important;
        --gdg-text-header: #4b5563 !important;
        --gdg-border-color: rgba(47, 51, 66, 0.12) !important;
        --gdg-accent-color: #328655 !important;
        --gdg-accent-light: rgba(50, 134, 85, 0.14) !important;
    }

    [data-testid="stDataFrame"] *,
    [data-testid="stTable"] * {
        color: #2f3342 !important;
        -webkit-text-fill-color: #2f3342 !important;
        border-color: rgba(47, 51, 66, 0.12) !important;
    }

    [data-testid="stDataFrame"] canvas,
    [data-testid="stDataFrame"] div[role="grid"],
    [data-testid="stDataFrame"] div[role="row"],
    [data-testid="stDataFrame"] div[role="columnheader"],
    [data-testid="stDataFrame"] div[role="gridcell"] {
        background-color: #ffffff !important;
        color: #2f3342 !important;
        -webkit-text-fill-color: #2f3342 !important;
    }

    /* Mantém a sidebar escura e consistente */
    [data-testid="stSidebar"] {
        background-color: #262b35 !important;
        color-scheme: dark !important;
    }
}

@media (prefers-color-scheme: light) {
    html,
    body,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMain"] .block-container {
        color-scheme: light !important;
        background-color: #ffffff !important;
        color: #2f3341 !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Fallback em JavaScript para exibir "Mostrar menu" quando a sidebar estiver recolhida.
# O texto é posicionado no canto superior esquerdo, ao lado da seta,
# sem procurar botões genéricos da toolbar do Streamlit.
components.html(
    """
    <script>
    (function () {
        function getParentDocument() {
            try {
                return window.parent && window.parent.document ? window.parent.document : null;
            } catch (e) {
                return null;
            }
        }

        function sidebarIsOpen(doc) {
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return false;

            const rect = sidebar.getBoundingClientRect();
            const style = window.parent.getComputedStyle(sidebar);
            return rect.width > 120 && style.display !== 'none' && style.visibility !== 'hidden' && rect.left < 20;
        }

        function findCollapsedButton(doc) {
            const specificControls = [
                '[data-testid="collapsedControl"]',
                '[data-testid="stSidebarCollapsedControl"]'
            ];

            for (const selector of specificControls) {
                const control = doc.querySelector(selector);
                if (!control) continue;

                const target = control.querySelector('button, [role="button"]') || control;
                const rect = target.getBoundingClientRect();
                if (rect.left >= 0 && rect.left < 120 && rect.top >= 0 && rect.top < 120) {
                    return target;
                }
            }

            // Fallback seguro: somente elementos com SVG no canto superior esquerdo.
            // Isso evita pegar botões da toolbar, que ficam no canto superior direito.
            const candidates = Array.from(doc.querySelectorAll('button, [role="button"]'))
                .filter((el) => {
                    const rect = el.getBoundingClientRect();
                    return (
                        el.querySelector('svg') &&
                        rect.left >= 0 &&
                        rect.left < 110 &&
                        rect.top >= 0 &&
                        rect.top < 120 &&
                        rect.width > 0 &&
                        rect.width < 90 &&
                        rect.height > 0 &&
                        rect.height < 90
                    );
                })
                .sort((a, b) => {
                    const ar = a.getBoundingClientRect();
                    const br = b.getBoundingClientRect();
                    return (ar.left + ar.top) - (br.left + br.top);
                });

            return candidates.length ? candidates[0] : null;
        }

        function ensureLabel(doc) {
            let label = doc.getElementById('custom-show-menu-label');
            if (!label) {
                label = doc.createElement('div');
                label.id = 'custom-show-menu-label';
                label.textContent = 'Mostrar menu';
                label.style.position = 'fixed';
                label.style.zIndex = '9999999';
                label.style.color = '#6f737b';
                label.style.fontFamily = 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
                label.style.fontSize = '0.9rem';
                label.style.fontWeight = '400';
                label.style.lineHeight = '1';
                label.style.whiteSpace = 'nowrap';
                label.style.pointerEvents = 'none';
                label.style.transform = 'translateY(-50%)';
                doc.body.appendChild(label);
            }
            return label;
        }

        function ensureOpenIcon(doc) {
            let icon = doc.getElementById('custom-sidebar-open-icon');
            if (!icon) {
                icon = doc.createElement('div');
                icon.id = 'custom-sidebar-open-icon';
                icon.textContent = '»';
                icon.setAttribute('aria-hidden', 'true');
                icon.style.position = 'fixed';
                icon.style.zIndex = '10000000';
                icon.style.color = '#388253';
                icon.style.webkitTextFillColor = '#388253';
                icon.style.fontFamily = 'Arial, Helvetica, sans-serif';
                icon.style.fontSize = window.parent.innerWidth <= 768 ? '1.55rem' : '1.55rem';
                icon.style.fontWeight = '800';
                icon.style.lineHeight = '1';
                icon.style.opacity = '1';
                icon.style.visibility = 'visible';
                icon.style.filter = 'none';
                icon.style.mixBlendMode = 'normal';
                icon.style.pointerEvents = 'none';
                icon.style.transform = 'translate(-50%, -50%)';
                icon.style.textShadow = '0 0 0 #388253, 0 1px 1px rgba(0,0,0,0.08)';
                doc.body.appendChild(icon);
            }
            return icon;
        }

        function paintCollapsedButton(btn, isMobile) {
            if (!btn) return;

            // No iOS o Streamlit pode deixar o ícone translúcido aplicando
            // opacity/filter no próprio botão ou em wrappers acima dele.
            // Por isso pintamos o botão e também alguns ancestrais diretos.
            let node = btn;
            for (let i = 0; i < 6 && node; i++) {
                node.style.opacity = '1';
                node.style.visibility = 'visible';
                node.style.filter = 'none';
                node.style.mixBlendMode = 'normal';
                node = node.parentElement;
            }

            btn.style.color = '#388253';
            btn.style.background = 'transparent';
            btn.style.boxShadow = 'none';
            btn.style.overflow = 'visible';
            btn.style.opacity = '1';
            btn.style.visibility = 'visible';
            btn.style.filter = 'none';
            btn.style.mixBlendMode = 'normal';

            btn.querySelectorAll('svg, svg *, path').forEach((el) => {
                el.style.setProperty('color', '#388253', 'important');
                el.style.setProperty('fill', '#388253', 'important');
                el.style.setProperty('stroke', '#388253', 'important');
                el.style.setProperty('filter', 'none', 'important');
                el.style.setProperty('mix-blend-mode', 'normal', 'important');

                if (isMobile) {
                    // No mobile/iOS, o SVG nativo pode continuar translúcido.
                    // Escondemos só no mobile e usamos o ícone customizado alinhado ao texto.
                    el.style.setProperty('opacity', '0', 'important');
                    el.style.setProperty('visibility', 'hidden', 'important');
                } else {
                    // No desktop, mantemos o SVG nativo para não duplicar a seta.
                    el.style.setProperty('opacity', '1', 'important');
                    el.style.setProperty('visibility', 'visible', 'important');
                }
            });
        }

        function updateLabel() {
            const doc = getParentDocument();
            if (!doc || !doc.body) return;

            const label = ensureLabel(doc);
            const icon = ensureOpenIcon(doc);

            if (sidebarIsOpen(doc)) {
                label.style.display = 'none';
                icon.style.display = 'none';
                return;
            }

            const isMobile = window.parent.innerWidth <= 768;
            const btn = findCollapsedButton(doc);
            if (btn) {
                const rect = btn.getBoundingClientRect();
                paintCollapsedButton(btn, isMobile);

                const labelY = rect.top + rect.height / 2 - (isMobile ? 9 : 18);

                label.style.left = (rect.right + 8) + 'px';
                label.style.top = labelY + 'px';

                // Desktop: não usamos overlay para evitar seta duplicada.
                // Mobile: usamos overlay pequeno e centralizado no eixo do texto.
                icon.style.left = (rect.left + rect.width / 2) + 'px';
                // Mobile: sobe a seta cerca de 15% do tamanho visual do ícone,
                // sem alterar o alinhamento do texto "Mostrar menu".
                icon.style.top = (labelY - (isMobile ? 4 : 0)) + 'px';
                icon.style.fontSize = isMobile ? '1.55rem' : '1.55rem';
            } else {
                const isMobileFallback = window.parent.innerWidth <= 768;
                icon.style.left = '28px';
                icon.style.top = isMobileFallback ? '29px' : '42px';
                label.style.left = '64px';
                label.style.top = isMobileFallback ? '33px' : '24px';
            }

            icon.style.display = (window.parent.innerWidth <= 768) ? 'block' : 'none';
            label.style.display = 'block';
        }

        const doc = getParentDocument();
        if (!doc || !doc.body) return;

        updateLabel();
        const observer = new MutationObserver(updateLabel);
        observer.observe(doc.body, { childList: true, subtree: true, attributes: true });
        window.parent.addEventListener('resize', updateLabel);
        window.setInterval(updateLabel, 350);
    })();
    </script>
    """,
    height=0,
    width=0,
)



def get_query_param_value(name, default=""):
    try:
        value = st.query_params.get(name, default)
        if isinstance(value, list):
            return value[0] if value else default
        return value if value is not None else default
    except Exception:
        try:
            params = st.experimental_get_query_params()
            values = params.get(name, [default])
            return values[0] if values else default
        except Exception:
            return default

def is_running_installed_webapp():
    return str(get_query_param_value("installed_app", "")).lower() in ["1", "true", "yes"]

# Metadados para deixar o app pronto para uso como Web App no iPhone.
# O JavaScript também identifica quando o app já está aberto em modo instalado
# e sinaliza isso para o Streamlit por query param, para ocultar a opção de instalação.
components.html(
    """
    <script>
    (function () {
        function getParentWindow() {
            try {
                return window.parent || window;
            } catch (e) {
                return window;
            }
        }

        function getParentDocument() {
            try {
                return window.parent && window.parent.document ? window.parent.document : document;
            } catch (e) {
                return document;
            }
        }

        const parentWindow = getParentWindow();
        const parentDocument = getParentDocument();
        if (!parentDocument || !parentDocument.head) return;

        function ensureMeta(name, content) {
            let meta = parentDocument.querySelector('meta[name="' + name + '"]');
            if (!meta) {
                meta = parentDocument.createElement('meta');
                meta.setAttribute('name', name);
                parentDocument.head.appendChild(meta);
            }
            meta.setAttribute('content', content);
        }

        function ensureLink(rel, href) {
            let link = parentDocument.querySelector('link[rel="' + rel + '"]');
            if (!link) {
                link = parentDocument.createElement('link');
                link.setAttribute('rel', rel);
                parentDocument.head.appendChild(link);
            }
            link.setAttribute('href', href);
        }

        ensureLink('manifest', '/app/static/manifest.webmanifest');
        ensureLink('apple-touch-icon', '/app/static/apple-touch-icon.png');
        ensureMeta('theme-color', '#328655');
        ensureMeta('apple-mobile-web-app-capable', 'yes');
        ensureMeta('apple-mobile-web-app-status-bar-style', 'default');
        ensureMeta('apple-mobile-web-app-title', 'Meu App Finanças');
        ensureMeta('mobile-web-app-capable', 'yes');

        try {
            const standaloneByMedia = parentWindow.matchMedia && parentWindow.matchMedia('(display-mode: standalone)').matches;
            const standaloneByIos = parentWindow.navigator && parentWindow.navigator.standalone === true;
            const isStandalone = Boolean(standaloneByMedia || standaloneByIos);
            const url = new URL(parentWindow.location.href);
            const current = url.searchParams.get('installed_app');

            if (isStandalone && current !== '1') {
                url.searchParams.set('installed_app', '1');
                parentWindow.location.replace(url.toString());
            } else if (!isStandalone && current === '1') {
                url.searchParams.delete('installed_app');
                parentWindow.history.replaceState({}, '', url.toString());
            }
        } catch (e) {}
    })();
    </script>
    """,
    height=0,
    width=0,
)

# Ajuste visual do date_input para PT-BR.
# O parâmetro format="DD/MM/YYYY" define o campo; este JS traduz somente o calendário pop-up.
components.html(
    """
    <script>
    (function () {
        function getParentDocument() {
            try {
                return window.parent && window.parent.document ? window.parent.document : null;
            } catch (e) {
                return null;
            }
        }

        const exactTranslations = {
            'January': 'Janeiro',
            'February': 'Fevereiro',
            'March': 'Março',
            'April': 'Abril',
            'May': 'Maio',
            'June': 'Junho',
            'July': 'Julho',
            'August': 'Agosto',
            'September': 'Setembro',
            'October': 'Outubro',
            'November': 'Novembro',
            'December': 'Dezembro',
            'Jan': 'Jan',
            'Feb': 'Fev',
            'Mar': 'Mar',
            'Apr': 'Abr',
            'Jun': 'Jun',
            'Jul': 'Jul',
            'Aug': 'Ago',
            'Sep': 'Set',
            'Oct': 'Out',
            'Nov': 'Nov',
            'Dec': 'Dez',
            'Su': 'Dom',
            'Mo': 'Seg',
            'Tu': 'Ter',
            'We': 'Qua',
            'Th': 'Qui',
            'Fr': 'Sex',
            'Sa': 'Sáb',
            'Sunday': 'Domingo',
            'Monday': 'Segunda',
            'Tuesday': 'Terça',
            'Wednesday': 'Quarta',
            'Thursday': 'Quinta',
            'Friday': 'Sexta',
            'Saturday': 'Sábado'
        };

        const monthPattern = 'January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec';
        const weekdayPattern = 'Su|Mo|Tu|We|Th|Fr|Sa|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday';
        const calendarPattern = new RegExp(monthPattern + '|' + weekdayPattern);

        function getCalendarRoots(doc) {
            const selectors = [
                '[data-baseweb="popover"]',
                '[data-baseweb="calendar"]',
                '[role="dialog"]'
            ];

            const roots = [];
            selectors.forEach((selector) => {
                doc.querySelectorAll(selector).forEach((el) => {
                    const text = el.innerText || '';
                    if (calendarPattern.test(text) || /20[0-9]{2}/.test(text)) {
                        roots.push(el);
                    }
                });
            });

            return [...new Set(roots)];
        }

        function translateRoot(root) {
            const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
            const nodes = [];
            while (walker.nextNode()) nodes.push(walker.currentNode);

            nodes.forEach((node) => {
                const original = node.nodeValue;
                const trimmed = original.trim();
                if (!trimmed) return;

                if (exactTranslations[trimmed]) {
                    node.nodeValue = original.replace(trimmed, exactTranslations[trimmed]);
                }
            });
        }

        function tuneCalendarTypography(root) {
            root.querySelectorAll('*').forEach((el) => {
                const txt = (el.innerText || '').trim();
                if (/^(Dom|Seg|Ter|Qua|Qui|Sex|Sáb)$/.test(txt)) {
                    el.style.fontSize = '0.9rem';
                    el.style.fontWeight = '600';
                }
            });
        }

        function updateDateLocale() {
            const doc = getParentDocument();
            if (!doc || !doc.body) return;
            doc.documentElement.setAttribute('lang', 'pt-BR');

            getCalendarRoots(doc).forEach((root) => {
                translateRoot(root);
                tuneCalendarTypography(root);
            });
        }

        const doc = getParentDocument();
        if (!doc || !doc.body) return;

        updateDateLocale();
        const observer = new MutationObserver(updateDateLocale);
        observer.observe(doc.body, { childList: true, subtree: true, characterData: true });
        window.setInterval(updateDateLocale, 500);
    })();
    </script>
    """,
    height=0,
    width=0,
)

# Puxa os dados básicos salvos no Secrets do site
try:
    SPREADSHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet_url"]
    PROJECT_ID = st.secrets["connections"]["gsheets"]["project_id"]
    CLIENT_EMAIL = st.secrets["connections"]["gsheets"]["client_email"]
    PRIVATE_KEY_ID = st.secrets["connections"]["gsheets"]["private_key_id"]
    CLIENT_ID = st.secrets["connections"]["gsheets"]["client_id"]
except Exception:
    st.error("Erro: Não foi possível encontrar todas as configurações no Secrets do Streamlit.")
    st.stop()

# Montamos as credenciais oficiais do Google
creds_dict = {
    "type": "service_account",
    "project_id": PROJECT_ID,
    "private_key_id": PRIVATE_KEY_ID,
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDDwCfI60IKUxHI\njh8rHp+MOYkU/gCL8UB/HJIQbn1FJoTYKG1dwrYws3LvjEjQeS98uU3ZViZ0CEhE\n7VMRfseBtkYcGRcO/3tcswR+7avAkruHvihLseA/BOEM8IeVe5YeafqbqQkWzmNp\nyuPKpIApKfZ3y6XZXu7VK53bXpujHxTkSqyrK7WCbzPuGqQ9ycmJqBLze0s+stfr\n2vcRWBKWM7w/NhcV4QxxPrOg9sGPSUibdc0YhCfwkQyOtUVjBn1f4EVdz7b4+4Be\nTwOj5BBGVYchVEx7Pa5MOVljzt5It/KU2ovvz3dC4zPvg8nWYAdxaJiTPbbl1aL7\nieUGh7krAgMBAAECggEACYYt6V6uReZTdS3vt59eepTKEKq9yBFNkWGzJvgultC6\n90bFm3bqemV2GtBOh/t9eKoOGZxRc/p7LwSvsqg3zh3aPL++bs0LaYU5m3C2Qeu3\nEscJGuBlXWuVWkB8YvoyYaRyZw8gZsBVTJkXNY2EwXv4hqJH8tLloprkAVURvtah\nyUU7nYVtLbd9LyJK0EmWJTW3AOhL59yx2RY90lPG25FVkQH/fMe5uRWiTjHTL++4\nb5xKqKJ6u6rP3sI/wB4YtrJff0+4weSzZr2tJjmT0HVZ5/Ms/Kkoq8ALTVBJqo6w\nRBWCZQBIuASGU64nz5Nj8wxs2m3/EKq8NNpyynbZ4QKBgQDya4pQLepgdbtCEahe\nHJn2620u39jwMYyn0uGwtkfq3HmTyW++EeFSepy/Rts/eDp9U7GQ5+8XB7S6qPeH\nWvM3OLnNHXLsoJo5zwkWiyAYBvlNrsNBkuQ45H3mgh5dJ1Yl5owaVorHQAaHhqaF\nUia5rUDPngU6KGFtykzEQZ/2YwKBgQDOt1hLkau7qxO7YNm852dKjW9hN39JUpLc\n1V38SbNODAes2SX0D/9rHNiYyb7o34kCrT214UbrfD7kh/WiAne5Kdihwco9PHwK\nSMAgs2NpSPROpSp4ltKHDF1gyfVPSUgYkV5a6uPHspW6XNYi7PqPPjYHq+7hXQWP\nMoY3HzoomQKBgQC8y8QMbbX7KbWM3vOhV+UQyIlf2DW72tsQWMwsM8oOv2ZwEpFU\nFdjFw3gP/78Az0G+GVBQ6lDqPrYiKTWd1NdWSndpp2W5o9p46yTIydFU5RmDxneK\nujvDky/6NZwwMFKHceXrHTs3skVjhxpo+nHuaV/wUcEAajJ2rvbaYcGSwQKBgQCC\n5VBQ0dY4CNV+0o4t8y3R5IuBuN2t9U6v7aAM8DJNGosFpZ9F05d+IQ76eM2dsmaU\nvlSURildVhiRJ5Kf2wYqxte5XfgNHK7C6FxYmJ87fQnOfwHMyFxZTbgXYOsoIJQ5\nklt4IMLJokjzcHPcO8lRSSh3ZSTnqbqqeWjJoMl4CQKBgQCcbO7Yy9C7kzB7IzFb\nfp5AVpggR2g/IfYt40OXONapYjEWXqqpIMg97/61SriySoBRDsZB5TdtQ8kr87Kr\noshKbctusiiYkx6CRJ4DMtRuOatPr5tALU+sleYkstGoS+4jkH9CmGspB9ckPKEx\ns8kwm6PMzQBUipYtDcKU3y7crA==\n-----END PRIVATE KEY-----\n",
    "client_email": CLIENT_EMAIL,
    "client_id": CLIENT_ID,
    "token_uri": "https://oauth2.googleapis.com/token"
}

@st.cache_resource
def get_sheets_client():
    return gspread.service_account_from_dict(creds_dict)

def google_sheets_retry(action, *args, attempts=4, base_delay=1.2, **kwargs):
    """Executa chamadas ao Google Sheets com novas tentativas para erros temporários como 503."""
    last_error = None
    for attempt in range(attempts):
        try:
            return action(*args, **kwargs)
        except Exception as err:
            last_error = err
            error_text = str(err)
            is_temporary = any(code in error_text for code in ["503", "500", "502", "504", "429"])
            if not is_temporary or attempt == attempts - 1:
                raise
            time.sleep(base_delay * (attempt + 1))
    raise last_error

try:
    gc = get_sheets_client()
    sh = google_sheets_retry(gc.open_by_url, SPREADSHEET_URL)
    worksheet = google_sheets_retry(sh.get_worksheet, 0)
except Exception as e:
    st.error(
        "Erro ao conectar com a planilha. O Google Sheets retornou instabilidade temporária. "
        f"Tente atualizar a página em alguns segundos. Detalhe: {e}"
    )
    st.stop()

if "editing_index" not in st.session_state:
    st.session_state.editing_index = None
if "edit_values" not in st.session_state:
    st.session_state.edit_values = {}
if "form_clear_trigger" not in st.session_state:
    st.session_state.form_clear_trigger = False

def clean_text(val):
    if val is None or pd.isna(val):
        return ""
    text_val = str(val).strip()
    if text_val.lower() in ["nan", "none", "null"]:
        return ""
    return text_val

def is_true_value(val):
    return val is True or clean_text(val).lower() == "true"

def is_cash_change_adjustment(record):
    """Identifica troco/ajuste de dinheiro vivo que não representa nova entrada de renda.

    Exemplo: sacar R$ 100, usar uma nota de R$ 50, gastar R$ 20 e receber R$ 30 de troco.
    Esse R$ 30 já faz parte do dinheiro sacado, então não deve somar em Entradas do mês
    nem aumentar novamente o saldo de Dinheiro Vivo.
    """
    payment_method = clean_text(record.get("payment_method", "")).lower()
    tx_type = clean_text(record.get("type", "")).lower()
    description = clean_text(record.get("description", "")).lower()
    notes = clean_text(record.get("notes", "")).lower()
    combined_text = f"{description} {notes}"

    return (
        tx_type == "entrada"
        and (
            payment_method == "troco_dinheiro"
            or (payment_method == "dinheiro_vivo" and "troco" in combined_text)
        )
    )

def format_payment_method_label(payment_method):
    labels = {
        "pix_conta": "Pix Conta",
        "dinheiro_vivo": "Dinheiro Vivo",
        "troco_dinheiro": "Troco / Ajuste",
        "pix": "Pix",
        "saque_dinheiro": "Saque Dinheiro",
        "pagamento_fatura": "Pagamento de Fatura",
        "credito_parcelado": "Crédito Parcelado",
    }
    cleaned = clean_text(payment_method)
    return labels.get(cleaned, cleaned.replace("_", " ").title())

# --- Categorias, subcategorias e tags ---
TRANSACTION_HEADERS = [
    "type", "description", "amount", "payment_method", "installments", "installment_value",
    "card", "is_for_someone", "bought_by", "created_at", "notes",
    "category", "subcategory", "tags", "impact_current_balance", "historical_only"
]

CATEGORY_LIBRARY = {
    "Receitas": [
        "Salário", "Freela", "Cliente recorrente", "Cliente pontual", "Venda de produto",
        "Venda de serviço", "Vendas / maquininhas", "Reembolso", "Estorno", "Cashback",
        "Rendimento", "Ajuda / presente", "Outras receitas"
    ],
    "Transferências/Ajustes": [
        "Transferência entre contas", "Saque dinheiro", "Depósito dinheiro vivo",
        "Troco / ajuste dinheiro vivo", "Pagamento de fatura", "Ajuste de saldo", "Saldo inicial"
    ],
    "Alimentação": [
        "Mercado", "Feira", "Delivery", "Restaurante", "Padaria", "Cafeteria", "Lanche",
        "Bebidas", "Açougue", "Hortifruti", "Atacado"
    ],
    "Moradia": [
        "Aluguel", "Condomínio", "Luz", "Água", "Gás", "Internet", "IPTU",
        "Seguro residencial", "Manutenção", "Móveis", "Decoração", "Limpeza"
    ],
    "Transporte": [
        "Uber / 99 / Táxi", "Transporte público", "Combustível", "Estacionamento",
        "Pedágio", "Manutenção veículo", "Seguro auto", "IPVA / Licenciamento", "Multa"
    ],
    "Saúde": [
        "Farmácia", "Consulta", "Exames", "Dentista", "Psicólogo", "Plano de saúde",
        "Medicamentos", "Vacinas", "Fisioterapia"
    ],
    "Cuidados pessoais": [
        "Cabelo", "Barba", "Unha", "Estética", "Skincare", "Perfume", "Cosméticos",
        "Higiene", "Academia", "Roupas de treino"
    ],
    "Educação": [
        "Curso", "Faculdade", "Mentoria", "Livro", "E-book", "Certificação", "Idioma", "Material escolar"
    ],
    "Trabalho/PJ": [
        "Software", "Ferramentas", "Contabilidade", "Impostos PJ", "DAS MEI", "Domínio / hospedagem",
        "Material de escritório", "Marketing", "Anúncios", "Transporte trabalho", "Almoço trabalho"
    ],
    "Assinaturas": [
        "Streaming", "Música", "Software", "Nuvem / armazenamento", "Clube de assinatura",
        "Newsletter", "Academia recorrente", "Outras assinaturas"
    ],
    "Família": [
        "Ajuda familiar", "Presente", "Criança / bebê", "Escola", "Brinquedos", "Passeio em família", "Despesa compartilhada"
    ],
    "Pets": [
        "Ração", "Pet shop", "Veterinário", "Vacina", "Medicamento", "Banho e tosa", "Acessórios"
    ],
    "Lazer": [
        "Cinema", "Show", "Teatro", "Bar", "Festa", "Passeio", "Praia", "Jogos", "Hobby", "Ingresso"
    ],
    "Compras": [
        "Roupas", "Calçados", "Acessórios", "Eletrônicos", "Celular", "Computador",
        "Casa", "Presentes", "Marketplace", "Amazon", "Mercado Livre", "Shopee", "Shein", "AliExpress"
    ],
    "Viagens": [
        "Passagem", "Hospedagem", "Airbnb", "Hotel", "Seguro viagem", "Aluguel de carro",
        "Alimentação viagem", "Passeios", "Compras viagem", "Câmbio", "Bagagem"
    ],
    "Cartões/Bancos": [
        "Tarifa bancária", "Juros", "Anuidade", "IOF", "Taxa Pix", "Taxa saque", "Multa atraso",
        "Empréstimo", "Financiamento", "Parcela carro", "Renegociação", "Taxas de maquininha"
    ],
    "Impostos/Documentos": [
        "IRPF", "IPTU", "IPVA", "Cartório", "Documentos", "Passaporte", "DARF", "DAS", "INSS", "Multa"
    ],
    "Investimentos/Reservas": [
        "Reserva emergência", "Tesouro Direto", "CDB", "Ações", "FIIs", "Cripto", "Previdência", "Poupança", "Aporte", "Resgate"
    ],
    "Outros": ["Geral", "Revisar", "Não identificado"]
}

# Regras em ordem de prioridade. O texto é normalizado sem acentos e em minúsculas.
AUTO_CATEGORY_RULES = [
    # Alimentação
    (["ifood", "i-food", "rappi", "uber eats", "ubereats", "delivery much", "aiqfome"], "Alimentação", "Delivery", "delivery, comida, automatico"),
    (["mercado", "supermercado", "super market", "assai", "atacadao", "guanabara", "mundial", "extra", "carrefour", "pao de acucar", "zona sul", "hortifruti", "horti fruti", "sacolao"], "Alimentação", "Mercado", "mercado, casa, automatico"),
    (["feira", "quitanda", "hortifruti", "horti fruti"], "Alimentação", "Feira", "feira, comida, automatico"),
    (["padaria", "panificadora", "bakery"], "Alimentação", "Padaria", "padaria, comida, automatico"),
    (["restaurante", "restaurant", "lanchonete", "pizzaria", "hamburguer", "hamburger", "burger", "sushi", "japones", "churrascaria", "bistro", "cafeteria", "cafe ", "starbucks"], "Alimentação", "Restaurante", "restaurante, comida, automatico"),

    # Transporte
    (["uber", "99app", "99 pop", "99pop", "taxi", "cabify", "indrive"], "Transporte", "Uber / 99 / Táxi", "transporte, app, automatico"),
    (["metro", "metrô", "supervia", "bilhete unico", "riocard", "onibus", "ônibus", "brt", "cptm", "trem"], "Transporte", "Transporte público", "transporte, automatico"),
    (["posto", "gasolina", "etanol", "combustivel", "combustível", "shell", "ipiranga", "petrobras", "br mania", "esso", "texaco", "ale combustiveis"], "Transporte", "Combustível", "carro, combustivel, automatico"),
    (["estacionamento", "parking", "zona azul", "parebem", "estapar"], "Transporte", "Estacionamento", "carro, automatico"),
    (["pedagio", "pedágio", "sem parar", "conectcar", "veloe"], "Transporte", "Pedágio", "carro, automatico"),

    # Moradia / contas fixas
    (["aluguel", "locacao", "locação"], "Moradia", "Aluguel", "casa, recorrente, automatico"),
    (["condominio", "condomínio"], "Moradia", "Condomínio", "casa, recorrente, automatico"),
    (["enel", "light", "energia", "conta de luz", "eletricidade"], "Moradia", "Luz", "casa, recorrente, automatico"),
    (["cedae", "aguas do rio", "águas do rio", "saneamento", "conta de agua", "conta de água"], "Moradia", "Água", "casa, recorrente, automatico"),
    (["naturgy", "gas natural", "gás natural", "conta de gas", "conta de gás"], "Moradia", "Gás", "casa, recorrente, automatico"),
    (["claro", "net claro", "vivo fibra", "tim live", "oi fibra", "internet", "banda larga"], "Moradia", "Internet", "casa, recorrente, automatico"),

    # Saúde
    (["farmacia", "farmácia", "drogaria", "drogasil", "droga raia", "raia", "pacheco", "venancio", "venâncio", "pague menos"], "Saúde", "Farmácia", "saude, automatico"),
    (["consulta", "clinica", "clínica", "laboratorio", "laboratório", "exame", "diagnostico", "diagnóstico", "dentista", "odontologia"], "Saúde", "Consulta", "saude, automatico"),
    (["unimed", "amil", "bradesco saude", "sulamerica saude", "notredame", "hapvida"], "Saúde", "Plano de saúde", "saude, recorrente, automatico"),

    # Trabalho/PJ e software
    (["adobe", "creative cloud", "photoshop", "illustrator", "canva", "figma", "capcut", "envato", "freepik", "shutterstock"], "Trabalho/PJ", "Software", "trabalho, software, automatico"),
    (["openai", "chatgpt", "claude", "notion", "trello", "slack", "google workspace", "microsoft", "office 365", "zoom"], "Trabalho/PJ", "Ferramentas", "trabalho, software, automatico"),
    (["registro.br", "godaddy", "hostinger", "hostgator", "cloudflare", "dominio", "domínio", "hospedagem"], "Trabalho/PJ", "Domínio / hospedagem", "trabalho, web, automatico"),
    (["contabil", "contábil", "contabilidade", "contador", "certificado digital", "das mei", "simples nacional"], "Trabalho/PJ", "Contabilidade", "pj, imposto, automatico"),
    (["facebook ads", "meta ads", "google ads", "tiktok ads", "impulsionamento", "anuncio", "anúncio"], "Trabalho/PJ", "Anúncios", "marketing, trabalho, automatico"),

    # Assinaturas
    (["netflix", "prime video", "amazon prime", "disney", "disney+", "globoplay", "max.com", "hbo", "paramount", "crunchyroll"], "Assinaturas", "Streaming", "assinatura, recorrente, automatico"),
    (["spotify", "deezer", "youtube premium", "apple music"], "Assinaturas", "Música", "assinatura, recorrente, automatico"),
    (["icloud", "google one", "dropbox", "onedrive"], "Assinaturas", "Nuvem / armazenamento", "assinatura, recorrente, automatico"),

    # Compras / marketplaces
    (["amazon", "mercado livre", "mercadolivre", "magalu", "magazine luiza", "americanas", "shopee", "shein", "aliexpress", "casas bahia", "ponto frio"], "Compras", "Marketplace", "compras, automatico"),
    (["renner", "riachuelo", "cea", "c&a", "zara", "centauro", "nike", "adidas"], "Compras", "Roupas", "compras, roupas, automatico"),

    # Cartões, bancos e maquininhas
    (["tarifa", "cesta", "pacote de servicos", "pacote de serviços", "juros", "iof", "encargo", "multa"], "Cartões/Bancos", "Tarifa bancária", "banco, taxa, automatico"),
    (["anuidade"], "Cartões/Bancos", "Anuidade", "cartao, taxa, automatico"),
    (["emprestimo", "empréstimo", "financiamento", "parcela carro", "consignado"], "Cartões/Bancos", "Empréstimo", "divida, automatico"),
    # Educação, lazer, família
    (["curso", "hotmart", "udemy", "alura", "domestika", "coursera", "rocketseat", "faculdade", "universidade", "escola"], "Educação", "Curso", "educacao, automatico"),
    (["cinema", "ingresso", "sympla", "eventim", "ticketmaster", "show", "teatro"], "Lazer", "Ingresso", "lazer, automatico"),
    (["presente", "aniversario", "aniversário", "brinquedo", "roupinha", "maria helena", "maria-helena"], "Família", "Presente", "familia, presente, automatico"),

    # Pets
    (["pet", "petz", "cobasi", "veterinario", "veterinário", "racao", "ração", "banho e tosa"], "Pets", "Pet shop", "pet, automatico"),
]

INCOME_RULES = [
    (["freela", "freelance", "cliente", "design", "social media", "servico", "serviço", "consultoria"], "Receitas", "Freela", "trabalho, receita, automatico"),
    (["salario", "salário", "pagamento salario", "pro labore", "pró-labore", "13", "decimo terceiro", "décimo terceiro"], "Receitas", "Salário", "receita, automatico"),
    (["reembolso", "estorno", "devolucao", "devolução"], "Receitas", "Reembolso", "reembolso, automatico"),
    (["cashback"], "Receitas", "Cashback", "cashback, automatico"),
    (["dividendo", "rendimento", "juros sobre capital", "tesouro", "cdb", "fii"], "Receitas", "Rendimento", "investimento, automatico"),
    (["pagseguro", "pag seguro", "stone", "ton ", "sumup", "cielo", "rede", "getnet", "safrapay", "infinitepay", "mercado pago", "maquininha"], "Receitas", "Vendas / maquininhas", "maquininha, vendas, automatico"),
]

def worksheet_column_letter(col_number):
    result = ""
    while col_number:
        col_number, remainder = divmod(col_number - 1, 26)
        result = chr(65 + remainder) + result
    return result

def ensure_transaction_headers():
    try:
        values = google_sheets_retry(worksheet.get_all_values)
        if not values:
            google_sheets_retry(worksheet.append_row, TRANSACTION_HEADERS, value_input_option="RAW")
            return TRANSACTION_HEADERS

        current_headers = [str(h).strip() for h in values[0]]
        final_headers = current_headers[:]
        changed = False
        for header in TRANSACTION_HEADERS:
            if header not in final_headers:
                final_headers.append(header)
                changed = True

        if changed:
            last_col = worksheet_column_letter(len(final_headers))
            google_sheets_retry(
                worksheet.update,
                range_name=f"A1:{last_col}1",
                values=[final_headers],
                value_input_option="RAW"
            )
        return final_headers
    except Exception:
        return []

def get_category_options():
    return ["Sem categoria"] + list(CATEGORY_LIBRARY.keys())

def get_subcategory_options(category):
    category = clean_text(category)
    if category == "Sem categoria" or category not in CATEGORY_LIBRARY:
        return ["Sem subcategoria"]
    return ["Sem subcategoria"] + CATEGORY_LIBRARY.get(category, [])

def normalize_rule_text(value):
    return strip_accents(value).lower()

def join_tags(*tag_values):
    tags = []
    for tag_value in tag_values:
        for tag in clean_text(tag_value).replace("#", "").split(","):
            cleaned = strip_accents(tag).strip().replace(" ", "-")
            if cleaned and cleaned not in tags:
                tags.append(cleaned)
    return ", ".join(tags)

def suggest_category(description, tx_type="saida", payment_method="", source="", notes=""):
    desc_text = clean_text(description)
    # A origem do arquivo/banco vira tag, mas não deve influenciar a categoria.
    # Ex.: uma fatura do cartão Amazon Prime não significa que toda compra seja assinatura Amazon.
    combined = normalize_rule_text(f"{description} {payment_method} {notes}")
    tx_type = clean_text(tx_type).lower()
    payment_method = clean_text(payment_method).lower()

    if payment_method == "saque_dinheiro":
        return "Transferências/Ajustes", "Saque dinheiro", "ajuste, dinheiro-vivo"
    if payment_method == "troco_dinheiro" or "troco" in combined:
        return "Transferências/Ajustes", "Troco / ajuste dinheiro vivo", "ajuste, dinheiro-vivo"
    if payment_method == "pagamento_fatura":
        return "Transferências/Ajustes", "Pagamento de fatura", "cartao, ajuste"

    rules = INCOME_RULES if tx_type == "entrada" else AUTO_CATEGORY_RULES
    for keywords, category, subcategory, tags in rules:
        if any(normalize_rule_text(keyword) in combined for keyword in keywords):
            if tx_type == "entrada" and category not in ["Receitas", "Transferências/Ajustes"]:
                return "Receitas", "Outras receitas", join_tags(tags, "receita", "automatico")
            return category, subcategory, join_tags(tags)

    if tx_type == "entrada":
        if desc_text:
            return "Receitas", "Outras receitas", "receita, revisar"
        return "Sem categoria", "Sem subcategoria", ""

    return "Outros", "Revisar", "revisar"

def normalize_category_for_save(category):
    category = clean_text(category)
    return "" if category == "Sem categoria" else category

def normalize_subcategory_for_save(subcategory):
    subcategory = clean_text(subcategory)
    return "" if subcategory == "Sem subcategoria" else subcategory

def category_badge_html(category, subcategory, tags):
    category = clean_text(category)
    subcategory = clean_text(subcategory)
    tags = clean_text(tags)
    if not category and not subcategory and not tags:
        return ""
    label = html.escape(category or "Sem categoria")
    if subcategory:
        label += f" › {html.escape(subcategory)}"
    tag_html = ""
    if tags:
        tag_parts = [html.escape(tag.strip()) for tag in tags.split(",") if tag.strip()]
        tag_html = "".join(f'<span class="tx-tag">#{tag}</span>' for tag in tag_parts[:4])
    return f'<div class="tx-category-line"><span class="tx-category-pill">{label}</span>{tag_html}</div>'

def safe_float(val):
    if val is None or pd.isna(val):
        return 0.0

    raw = str(val).strip()
    if raw == "" or raw.lower() in ["nan", "none", "null"]:
        return 0.0

    try:
        parsed = float(raw)
    except (ValueError, TypeError):
        try:
            parsed = float(raw.replace(".", "").replace(",", "."))
        except (ValueError, TypeError):
            return 0.0

    if math.isnan(parsed) or math.isinf(parsed):
        return 0.0
    return parsed

@st.cache_data(ttl=5)
def load_data():
    try:
        ensure_transaction_headers()
        raw_rows = google_sheets_retry(worksheet.get_all_values)
        if len(raw_rows) <= 1:
            return []
            
        headers = [str(h).strip() for h in raw_rows[0]]
        records_list = []
        
        field_map = {
            "type": headers.index("type") if "type" in headers else 0,
            "description": headers.index("description") if "description" in headers else 1,
            "amount": headers.index("amount") if "amount" in headers else 2,
            "payment_method": headers.index("payment_method") if "payment_method" in headers else 3,
            "installments": headers.index("installments") if "installments" in headers else 4,
            "installment_value": headers.index("installment_value") if "installment_value" in headers else 5,
            "card": headers.index("card") if "card" in headers else 6,
            "is_for_someone": headers.index("is_for_someone") if "is_for_someone" in headers else 7,
            "bought_by": headers.index("bought_by") if "bought_by" in headers else 8,
            "created_at": headers.index("created_at") if "created_at" in headers else 9,
            "notes": headers.index("notes") if "notes" in headers else 10,
            "category": headers.index("category") if "category" in headers else 11,
            "subcategory": headers.index("subcategory") if "subcategory" in headers else 12,
            "tags": headers.index("tags") if "tags" in headers else 13,
            "impact_current_balance": headers.index("impact_current_balance") if "impact_current_balance" in headers else None,
            "historical_only": headers.index("historical_only") if "historical_only" in headers else None,
        }

        for idx, row in enumerate(raw_rows[1:], start=2):
            while len(row) < len(headers):
                row.append("")
                
            r = {
                "sheet_row_idx": idx,
                "type": clean_text(row[field_map["type"]]),
                "description": clean_text(row[field_map["description"]]),
                "amount": safe_float(row[field_map["amount"]]),
                "payment_method": clean_text(row[field_map["payment_method"]]),
                "installments": clean_text(row[field_map["installments"]]),
                "installment_value": safe_float(row[field_map["installment_value"]]),
                "card": clean_text(row[field_map["card"]]),
                "is_for_someone": clean_text(row[field_map["is_for_someone"]]),
                "bought_by": clean_text(row[field_map["bought_by"]]),
                "notes": clean_text(row[field_map["notes"]]),
                "category": clean_text(row[field_map["category"]]) if field_map["category"] < len(row) else "",
                "subcategory": clean_text(row[field_map["subcategory"]]) if field_map["subcategory"] < len(row) else "",
                "tags": clean_text(row[field_map["tags"]]) if field_map["tags"] < len(row) else "",
                "impact_current_balance": clean_text(row[field_map["impact_current_balance"]]) if field_map["impact_current_balance"] is not None and field_map["impact_current_balance"] < len(row) else "TRUE",
                "historical_only": clean_text(row[field_map["historical_only"]]) if field_map["historical_only"] is not None and field_map["historical_only"] < len(row) else "FALSE",
            }
            
            raw_date = clean_text(row[field_map["created_at"]])
            try:
                r["created_at"] = pd.to_datetime(raw_date, errors='raise')
            except Exception:
                try:
                    r["created_at"] = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    r["created_at"] = datetime.now()
                    
            records_list.append(r)
            
        return records_list
    except Exception as e:
        st.error(f"Erro crítico no processamento dos dados: {e}")
        return []

def format_currency(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_br_date(dt):
    dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    dia_semana = dias[dt.weekday()]
    return f"{dia_semana}, {dt.strftime('%d/%m/%Y')}"

def render_transaction_animation():
    animation_emoji = st.session_state.get("screen_animation_emoji")
    if not animation_emoji:
        return

    # Evita repetir a animação em próximos reruns.
    del st.session_state.screen_animation_emoji

    positions = [
        (8, 18, 0.00), (18, 72, 0.18), (29, 34, 0.08), (41, 63, 0.24),
        (53, 22, 0.12), (64, 78, 0.30), (76, 42, 0.04), (88, 68, 0.20),
        (12, 52, 0.36), (34, 84, 0.16), (58, 50, 0.28), (82, 18, 0.10)
    ]

    emoji_spans = "".join(
        f'<span style="left:{left}vw; top:{top}vh; animation-delay:{delay}s;">{animation_emoji}</span>'
        for left, top, delay in positions
    )

    st.markdown(f'''
    <style>
    .transaction-emoji-overlay {{
        position: fixed;
        inset: 0;
        z-index: 99999999;
        pointer-events: none;
        overflow: hidden;
        animation: transactionOverlayFade 1.9s ease-out forwards;
    }}

    .transaction-emoji-overlay span {{
        position: absolute;
        font-size: 1.7rem;
        opacity: 0;
        transform: translate(-50%, -50%) scale(0.65);
        animation: transactionEmojiPop 1.45s ease-out forwards;
        filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.18));
    }}

    @keyframes transactionEmojiPop {{
        0% {{ opacity: 0; transform: translate(-50%, -35%) scale(0.55) rotate(-8deg); }}
        18% {{ opacity: 1; transform: translate(-50%, -50%) scale(1.08) rotate(4deg); }}
        58% {{ opacity: 1; transform: translate(-50%, -62%) scale(1.0) rotate(-3deg); }}
        100% {{ opacity: 0; transform: translate(-50%, -92%) scale(0.8) rotate(8deg); }}
    }}

    @keyframes transactionOverlayFade {{
        0% {{ opacity: 1; }}
        78% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
    }}
    </style>
    <div class="transaction-emoji-overlay">
        {emoji_spans}
    </div>
    ''', unsafe_allow_html=True)

def image_to_data_uri(image_path):
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "image/png"
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"

def render_app_logo(width=240):
    # Renderiza o logo correto conforme o tema do dispositivo.
    # No modo claro usa logo.png; no modo escuro usa logo-dark.png quando existir.
    has_light_logo = os.path.exists("logo.png")
    has_dark_logo = os.path.exists("logo-dark.png")

    if has_light_logo and has_dark_logo:
        light_logo_uri = image_to_data_uri("logo.png")
        dark_logo_uri = image_to_data_uri("logo-dark.png")
        st.markdown(
            f"""
            <div class="app-top-logo" style="--app-logo-width: {width}px;">
                <img class="app-top-logo-img app-top-logo-light" src="{light_logo_uri}" alt="Meu App Finanças - modo claro" />
                <img class="app-top-logo-img app-top-logo-dark" src="{dark_logo_uri}" alt="Meu App Finanças - modo escuro" />
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif has_light_logo:
        st.image("logo.png", width=width)
    elif has_dark_logo:
        st.image("logo-dark.png", width=width)
    else:
        st.title("Meu App Finanças")

def render_credit_cards_sidebar():
    credit_cards = [
        {"name": "Nubank", "limit": "R$1.600", "logo": "nubank.png", "closing_date": "02", "due_date": "09"},
        {"name": "Mercado Pago", "limit": "R$13.200", "logo": "mercado-pago.png", "closing_date": "05", "due_date": "10"},
        {"name": "Inter", "limit": "R$9.300", "logo": "inter.png", "closing_date": "06", "due_date": "12"},
        {"name": "Nu PJ", "limit": "R$4.700", "logo": "nu-pj.png", "closing_date": "10", "due_date": "17"},
        {"name": "PicPay", "limit": "R$2.040", "logo": "picpay.webp", "closing_date": "02", "due_date": "10"},
        {"name": "Amazon Prime", "limit": "R$1.400", "logo": "prime.png", "closing_date": "25", "due_date": "10"},
        {"name": "Mei", "limit": "R$950", "logo": "mei.webp", "closing_date": "07", "due_date": "13"},
    ]

    st.markdown('<div class="credit-cards-line"></div>', unsafe_allow_html=True)

    for card in credit_cards:
        logo_col, name_col, date_col = st.columns([0.18, 0.35, 0.47], gap="small", vertical_alignment="center")

        with logo_col:
            if os.path.exists(card["logo"]):
                logo_uri = image_to_data_uri(card["logo"])
                st.markdown(
                    f'<img class="credit-card-logo-img" src="{logo_uri}" alt="{card["name"]}">',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(f'<div class="credit-card-logo-fallback">{card["name"][:2]}</div>', unsafe_allow_html=True)

        with name_col:
            st.markdown(
                f'<div class="credit-card-name-block"><div class="credit-card-name">{card["name"]}</div><div class="credit-card-limit">{card["limit"]}</div></div>',
                unsafe_allow_html=True
            )

        with date_col:
            st.markdown(
                f'<div class="credit-card-info"><div>Fechamento: {card["closing_date"]}</div><div>Vencimento: {card["due_date"]}</div></div>',
                unsafe_allow_html=True
            )

        st.markdown('<div class="credit-card-gap"></div>', unsafe_allow_html=True)

def build_top_expenses_chart_html(filtered_records):
    expenses = []

    for r in filtered_records:
        if r.get("type") != "saida":
            continue
        if r.get("payment_method") == "saque_dinheiro":
            continue

        is_inst = is_true_value(r.get("is_installment_view", False))
        desc = clean_text(r.get("display_description", r.get("description", ""))) if is_inst else clean_text(r.get("description", ""))
        amount = r.get("display_amount", r.get("amount", 0)) if is_inst else r.get("amount", 0)
        amount_float = safe_float(amount)

        if amount_float <= 0:
            continue

        expenses.append({"description": desc or "Sem descrição", "amount": amount_float})

    expenses = sorted(expenses, key=lambda item: item["amount"], reverse=True)[:10]

    if not expenses:
        return '<div class="top-expenses-chart top-expenses-chart-empty">Sem gastos no mês selecionado</div>'

    max_amount = max(item["amount"] for item in expenses) or 1
    colors = [
        "#5b7cfa", "#a78bfa", "#f8b55f", "#ffd65c", "#f87171",
        "#e879c6", "#5fd0c8", "#63c982", "#a3a328", "#9b9b00"
    ]

    bars_html = []
    for idx in range(10):
        if idx < len(expenses):
            item = expenses[idx]
            height = max(10, (item["amount"] / max_amount) * 100)
            desc = html.escape(item["description"])
            short_desc = html.escape(item["description"][:14])
            value = html.escape(format_currency(item["amount"]))
            color = colors[idx % len(colors)]
            bars_html.append(
                f'<div class="top-expense-bar-slot">'
                f'<div class="top-expense-tooltip">'
                f'<span class="top-expense-tooltip-name">{desc}</span>'
                f'<span class="top-expense-tooltip-value">{value}</span>'
                f'</div>'
                f'<div class="top-expense-bar" style="height:{height:.1f}%; background:{color};"></div>'
                f'<div class="top-expense-bar-label">{idx + 1}</div>'
                f'</div>'
            )
        else:
            bars_html.append(
                '<div class="top-expense-bar-slot">'
                '<div class="top-expense-bar top-expense-bar-empty" style="height:10%;"></div>'
                '<div class="top-expense-bar-label">-</div>'
                '</div>'
            )

    return (
        '<div class="top-expenses-chart">'
        '<div class="top-expenses-title">Top 10 gastos do mês</div>'
        '<div class="top-expenses-bars">'
        + ''.join(bars_html) +
        '</div>'
        '</div>'
    )


APP_CONFIG_SHEET_NAME = "app_config"
APP_CONFIG_HEADERS = ["key", "value", "updated_at"]

def default_app_start_date():
    today = datetime.now().date()
    return today.replace(day=1)

def get_or_create_app_config_worksheet():
    try:
        config_ws = google_sheets_retry(sh.worksheet, APP_CONFIG_SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        config_ws = google_sheets_retry(sh.add_worksheet, title=APP_CONFIG_SHEET_NAME, rows=50, cols=len(APP_CONFIG_HEADERS))
        google_sheets_retry(config_ws.append_row, APP_CONFIG_HEADERS, value_input_option="RAW")
    try:
        values = google_sheets_retry(config_ws.get_all_values)
        if not values:
            google_sheets_retry(config_ws.append_row, APP_CONFIG_HEADERS, value_input_option="RAW")
        elif [clean_text(h) for h in values[0]] != APP_CONFIG_HEADERS:
            google_sheets_retry(config_ws.update, range_name="A1:C1", values=[APP_CONFIG_HEADERS], value_input_option="RAW")
    except Exception:
        pass
    return config_ws

@st.cache_data(ttl=5)
def load_app_config():
    defaults = {
        "app_start_date": default_app_start_date().strftime("%Y-%m-%d"),
        "initial_bank_balance": "0",
        "initial_cash_balance": "0",
    }
    try:
        config_ws = get_or_create_app_config_worksheet()
        rows = google_sheets_retry(config_ws.get_all_records)
        config = defaults.copy()
        for row in rows:
            key = clean_text(row.get("key", ""))
            value = clean_text(row.get("value", ""))
            if key:
                config[key] = value
        return config
    except Exception:
        return defaults

def parse_app_config_date(value):
    try:
        parsed = pd.to_datetime(value, dayfirst=False, errors="raise").date()
    except Exception:
        parsed = default_app_start_date()
    return parsed

def save_app_config(updates):
    config_ws = get_or_create_app_config_worksheet()
    values = google_sheets_retry(config_ws.get_all_values)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    key_to_row = {}
    for idx, row in enumerate(values[1:], start=2):
        if row:
            key_to_row[clean_text(row[0])] = idx
    for key, value in updates.items():
        value = clean_text(value)
        if key in key_to_row:
            row_idx = key_to_row[key]
            google_sheets_retry(config_ws.update, range_name=f"A{row_idx}:C{row_idx}", values=[[key, value, now]], value_input_option="RAW")
        else:
            google_sheets_retry(config_ws.append_row, [key, value, now], value_input_option="RAW")
    st.cache_data.clear()

def is_historical_record(record):
    return is_true_value(record.get("historical_only", "FALSE"))

def should_record_impact_current_balance(record, app_start_date):
    if is_historical_record(record):
        return False
    if not is_true_value(record.get("impact_current_balance", "TRUE")):
        return False
    try:
        return record["created_at"].date() >= app_start_date
    except Exception:
        return False

def should_record_appear_in_home(record, app_start_date):
    if is_historical_record(record):
        return False
    try:
        return record["created_at"].date() >= app_start_date
    except Exception:
        return False

BILLS_SHEET_NAME = "contas_assinaturas"
BILLS_HEADERS = ["name", "category", "amount", "due_day", "payment_method", "notes", "active", "created_at", "bill_id"]

BILLS_STATUS_SHEET_NAME = "contas_assinaturas_status"
BILLS_STATUS_HEADERS = ["bill_id", "month", "year", "paid", "paid_at"]


def make_fixed_bill_id(name, created_at, row_idx=None):
    seed = f"{clean_text(name)}|{clean_text(created_at)}|{row_idx or ''}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:18]


def get_or_create_fixed_bills_worksheet():
    try:
        bills_ws = google_sheets_retry(sh.worksheet, BILLS_SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        bills_ws = google_sheets_retry(
            sh.add_worksheet,
            title=BILLS_SHEET_NAME,
            rows=200,
            cols=len(BILLS_HEADERS),
        )
        google_sheets_retry(bills_ws.append_row, BILLS_HEADERS, value_input_option="RAW")
        return bills_ws

    try:
        values = google_sheets_retry(bills_ws.get_all_values)
        if not values:
            google_sheets_retry(bills_ws.append_row, BILLS_HEADERS, value_input_option="RAW")
            return bills_ws

        current_headers = [clean_text(h) for h in values[0]]
        if current_headers != BILLS_HEADERS:
            google_sheets_retry(
                bills_ws.update,
                range_name="A1:I1",
                values=[BILLS_HEADERS],
                value_input_option="RAW",
            )

        # Gera um ID estável para contas já existentes sem mexer nos dados atuais.
        for row_idx, row in enumerate(values[1:], start=2):
            padded = list(row) + [""] * max(0, len(BILLS_HEADERS) - len(row))
            name = clean_text(padded[0])
            created_at = clean_text(padded[7])
            current_bill_id = clean_text(padded[8])
            if name and not current_bill_id:
                bill_id = make_fixed_bill_id(name, created_at, row_idx)
                google_sheets_retry(bills_ws.update_cell, row_idx, 9, bill_id)
    except Exception:
        pass

    return bills_ws


def get_or_create_fixed_bills_status_worksheet():
    try:
        status_ws = google_sheets_retry(sh.worksheet, BILLS_STATUS_SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        status_ws = google_sheets_retry(
            sh.add_worksheet,
            title=BILLS_STATUS_SHEET_NAME,
            rows=500,
            cols=len(BILLS_STATUS_HEADERS),
        )
        google_sheets_retry(status_ws.append_row, BILLS_STATUS_HEADERS, value_input_option="RAW")
        return status_ws

    try:
        values = google_sheets_retry(status_ws.get_all_values)
        if not values:
            google_sheets_retry(status_ws.append_row, BILLS_STATUS_HEADERS, value_input_option="RAW")
        else:
            current_headers = [clean_text(h) for h in values[0]]
            if current_headers != BILLS_STATUS_HEADERS:
                google_sheets_retry(
                    status_ws.update,
                    range_name="A1:E1",
                    values=[BILLS_STATUS_HEADERS],
                    value_input_option="RAW",
                )
    except Exception:
        pass

    return status_ws


@st.cache_data(ttl=5)
def load_fixed_bills():
    try:
        bills_ws = get_or_create_fixed_bills_worksheet()
        raw_rows = google_sheets_retry(bills_ws.get_all_values)
        if len(raw_rows) <= 1:
            return []

        headers = [clean_text(h) for h in raw_rows[0]]
        records_list = []
        field_map = {
            header: headers.index(header) if header in headers else idx
            for idx, header in enumerate(BILLS_HEADERS)
        }

        for idx, row in enumerate(raw_rows[1:], start=2):
            row = list(row)
            while len(row) < len(BILLS_HEADERS):
                row.append("")

            name = clean_text(row[field_map.get("name", 0)])
            created_at = clean_text(row[field_map.get("created_at", 7)])
            bill_id = clean_text(row[field_map.get("bill_id", 8)]) or make_fixed_bill_id(name, created_at, idx)

            record = {
                "sheet_row_idx": idx,
                "bill_id": bill_id,
                "name": name,
                "category": clean_text(row[field_map.get("category", 1)]),
                "amount": safe_float(row[field_map.get("amount", 2)]),
                "due_day": int(safe_float(row[field_map.get("due_day", 3)]))
                if clean_text(row[field_map.get("due_day", 3)])
                else 1,
                "payment_method": clean_text(row[field_map.get("payment_method", 4)]),
                "notes": clean_text(row[field_map.get("notes", 5)]),
                "active": clean_text(row[field_map.get("active", 6)]).upper() != "FALSE",
                "created_at": created_at,
            }

            if record["name"]:
                records_list.append(record)

        return records_list
    except Exception as e:
        st.error(f"Erro ao carregar contas e assinaturas: {e}")
        return []


@st.cache_data(ttl=5)
def load_fixed_bill_statuses(selected_month, selected_year):
    try:
        status_ws = get_or_create_fixed_bills_status_worksheet()
        raw_rows = google_sheets_retry(status_ws.get_all_values)
        if len(raw_rows) <= 1:
            return {}

        headers = [clean_text(h) for h in raw_rows[0]]
        field_map = {
            header: headers.index(header) if header in headers else idx
            for idx, header in enumerate(BILLS_STATUS_HEADERS)
        }

        statuses = {}
        for row in raw_rows[1:]:
            row = list(row)
            while len(row) < len(BILLS_STATUS_HEADERS):
                row.append("")

            month = int(safe_float(row[field_map.get("month", 1)])) if clean_text(row[field_map.get("month", 1)]) else 0
            year = int(safe_float(row[field_map.get("year", 2)])) if clean_text(row[field_map.get("year", 2)]) else 0

            if month == int(selected_month) and year == int(selected_year):
                bill_id = clean_text(row[field_map.get("bill_id", 0)])
                if bill_id:
                    statuses[bill_id] = is_true_value(row[field_map.get("paid", 3)])

        return statuses
    except Exception as e:
        st.error(f"Erro ao carregar status mensal das contas: {e}")
        return {}


def set_fixed_bill_paid_status(bill_id, selected_month, selected_year, paid):
    status_ws = get_or_create_fixed_bills_status_worksheet()
    raw_rows = google_sheets_retry(status_ws.get_all_values)

    headers = [clean_text(h) for h in raw_rows[0]] if raw_rows else BILLS_STATUS_HEADERS
    field_map = {
        header: headers.index(header) if header in headers else idx
        for idx, header in enumerate(BILLS_STATUS_HEADERS)
    }

    target_row_idx = None
    for row_idx, row in enumerate(raw_rows[1:], start=2):
        row = list(row)
        while len(row) < len(BILLS_STATUS_HEADERS):
            row.append("")

        row_bill_id = clean_text(row[field_map.get("bill_id", 0)])
        row_month = int(safe_float(row[field_map.get("month", 1)])) if clean_text(row[field_map.get("month", 1)]) else 0
        row_year = int(safe_float(row[field_map.get("year", 2)])) if clean_text(row[field_map.get("year", 2)]) else 0

        if (
            row_bill_id == clean_text(bill_id)
            and row_month == int(selected_month)
            and row_year == int(selected_year)
        ):
            target_row_idx = row_idx
            break

    paid_value = "TRUE" if paid else "FALSE"
    paid_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if paid else ""

    if target_row_idx:
        google_sheets_retry(
            status_ws.update,
            range_name=f"D{target_row_idx}:E{target_row_idx}",
            values=[[paid_value, paid_at]],
            value_input_option="RAW",
        )
    else:
        google_sheets_retry(
            status_ws.append_row,
            [
                clean_text(bill_id),
                int(selected_month),
                int(selected_year),
                paid_value,
                paid_at,
            ],
            value_input_option="RAW",
        )

    st.cache_data.clear()


def delete_fixed_bill_statuses(bill_id):
    try:
        status_ws = get_or_create_fixed_bills_status_worksheet()
        raw_rows = google_sheets_retry(status_ws.get_all_values)
        rows_to_delete = []

        for row_idx, row in enumerate(raw_rows[1:], start=2):
            if row and clean_text(row[0]) == clean_text(bill_id):
                rows_to_delete.append(row_idx)

        for row_idx in sorted(rows_to_delete, reverse=True):
            google_sheets_retry(status_ws.delete_rows, row_idx)
    except Exception:
        pass


def get_bill_due_date(selected_month, selected_year, due_day):
    due_day = max(1, min(31, int(due_day or 1)))
    last_day = calendar.monthrange(int(selected_year), int(selected_month))[1]
    return datetime(
        int(selected_year),
        int(selected_month),
        min(due_day, last_day),
    ).date()


def get_bill_visual_status(bill, is_paid, selected_month, selected_year, today_date):
    if is_paid:
        return "paid", "Pago", "bill-card-paid", "bill-status-paid"

    due_date = get_bill_due_date(
        selected_month,
        selected_year,
        bill.get("due_day", 1),
    )
    days_until_due = (due_date - today_date).days

    if days_until_due < 0:
        return "overdue", "Vencida", "bill-card-overdue", "bill-status-overdue"

    if days_until_due <= 2:
        if days_until_due == 0:
            label = "Vence hoje"
        elif days_until_due == 1:
            label = "Vence amanhã"
        else:
            label = "Vence em 2 dias"
        return "due_soon", label, "bill-card-due-soon", "bill-status-due-soon"

    return "pending", "Não pago", "bill-card-pending", "bill-status-pending"


def render_bills_page(selected_month, selected_year):
    st.markdown("# Contas e assinaturas")
    st.markdown(
        '<div class="page-kicker">Cadastre pagamentos mensais fixos, como aluguel, carro, empréstimos, luz, água, internet, celular e assinaturas.</div>',
        unsafe_allow_html=True,
    )

    bills = load_fixed_bills()
    active_bills = [bill for bill in bills if bill.get("active", True)]
    monthly_statuses = load_fixed_bill_statuses(selected_month, selected_year)

    total_monthly = sum(safe_float(bill.get("amount", 0)) for bill in active_bills)
    remaining_monthly = sum(
        safe_float(bill.get("amount", 0))
        for bill in active_bills
        if not monthly_statuses.get(bill.get("bill_id"), False)
    )
    total_count = len(active_bills)

    today_date = datetime.now().date()

    unpaid_bills = [
        bill
        for bill in active_bills
        if not monthly_statuses.get(bill.get("bill_id"), False)
    ]

    next_due_text = "Tudo pago neste mês" if active_bills and not unpaid_bills else "Sem vencimentos próximos"
    if unpaid_bills:
        next_bill = sorted(
            unpaid_bills,
            key=lambda bill: get_bill_due_date(
                selected_month,
                selected_year,
                bill.get("due_day", 1),
            ),
        )[0]
        next_due_text = (
            f'{next_bill.get("name", "Conta")} — dia '
            f'{int(next_bill.get("due_day", 1) or 1):02d}'
        )

    remaining_summary_class = (
        "bills-summary-remaining-zero"
        if remaining_monthly <= 0.00001
        else "bills-summary-remaining-open"
    )

    summary_html = (
        '<div class="bills-summary-grid">'
        '<div class="bills-summary-card">'
        '<div class="bills-summary-label">Total mensal fixo</div>'
        '<div class="bills-summary-value">'
        + html.escape(format_currency(total_monthly))
        + "</div></div>"
        f'<div class="bills-summary-card {remaining_summary_class}">'
        '<div class="bills-summary-label">Restante a pagar desse mês</div>'
        '<div class="bills-summary-value">'
        + html.escape(format_currency(remaining_monthly))
        + "</div></div>"
        '<div class="bills-summary-card">'
        '<div class="bills-summary-label">Contas ativas</div>'
        '<div class="bills-summary-value">'
        + str(total_count)
        + "</div></div>"
        '<div class="bills-summary-card">'
        '<div class="bills-summary-label">Próximo vencimento</div>'
        '<div class="bills-summary-value" style="font-size: clamp(1rem, 1.35vw, 1.35rem);">'
        + html.escape(next_due_text)
        + "</div></div>"
        "</div>"
    )
    st.markdown(summary_html, unsafe_allow_html=True)

    form_col, list_col = st.columns([0.46, 0.54], gap="large")

    with form_col:
        st.subheader("Nova conta fixa")
        bill_name = st.text_input("Nome", placeholder="Ex: Aluguel, Internet, Parcela do carro")
        bill_category = st.selectbox(
            "Categoria",
            ["Moradia", "Transporte", "Empréstimos", "Luz", "Água", "Internet", "Celular", "Assinatura", "Outros"],
        )
        amount_col, due_col = st.columns(2)
        bill_amount_str = amount_col.text_input("Valor mensal (R$)", placeholder="Ex: 120,00")
        bill_due_day = due_col.number_input(
            "Dia de vencimento",
            min_value=1,
            max_value=31,
            value=10,
            step=1,
        )
        bill_payment_method = st.selectbox(
            "Forma de pagamento",
            ["Pix", "Débito", "Boleto", "Cartão de crédito", "Transferência", "Dinheiro", "Outro"],
        )
        bill_notes = st.text_area(
            "Observações",
            placeholder="Ex: vence todo mês, contrato, detalhes do plano...",
        )

        if st.button("Adicionar conta fixa", type="primary"):
            if not bill_name.strip():
                st.error("Preencha o nome da conta ou assinatura.")
                st.stop()
            if not bill_amount_str.strip():
                st.error("Preencha o valor mensal.")
                st.stop()

            try:
                clean_amount_str = bill_amount_str.strip().replace(" ", "")
                if "," in clean_amount_str and "." in clean_amount_str:
                    clean_amount_str = clean_amount_str.replace(".", "")
                clean_amount_str = clean_amount_str.replace(",", ".")
                bill_amount = float(clean_amount_str)
            except ValueError:
                st.error("Valor inválido! Digite apenas números, por exemplo: 120,00.")
                st.stop()

            try:
                bills_ws = get_or_create_fixed_bills_worksheet()
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                bill_id = make_fixed_bill_id(
                    bill_name.strip(),
                    created_at,
                    f"{time.time_ns()}",
                )
                new_bill_row = [
                    bill_name.strip(),
                    bill_category,
                    round(bill_amount, 2),
                    int(bill_due_day),
                    bill_payment_method,
                    bill_notes,
                    "TRUE",
                    created_at,
                    bill_id,
                ]
                google_sheets_retry(
                    bills_ws.append_row,
                    new_bill_row,
                    value_input_option="RAW",
                )
                st.cache_data.clear()
                st.success("Conta fixa adicionada.")
                st.rerun()
            except Exception as err:
                st.error(f"Erro ao salvar conta fixa: {err}")

    with list_col:
        st.subheader("Contas cadastradas")
        if not active_bills:
            st.info("Nenhuma conta ou assinatura cadastrada ainda.")
        else:
            sorted_bills = sorted(
                active_bills,
                key=lambda b: (
                    int(b.get("due_day", 1) or 1),
                    b.get("name", ""),
                ),
            )

            for bill in sorted_bills:
                due_day = int(bill.get("due_day", 1) or 1)
                bill_id = bill.get("bill_id")
                is_paid = monthly_statuses.get(bill_id, False)

                _, status_label, card_class, pill_class = get_bill_visual_status(
                    bill,
                    is_paid,
                    selected_month,
                    selected_year,
                    today_date,
                )

                name = html.escape(bill.get("name", "Conta"))
                category = html.escape(bill.get("category", "Outros"))
                method = html.escape(bill.get("payment_method", ""))
                notes = html.escape(bill.get("notes", ""))
                amount = html.escape(format_currency(safe_float(bill.get("amount", 0))))

                st.markdown(
                    f'<div class="bill-card {card_class}">'
                    f'<div class="bill-card-title">{name}'
                    f'<span class="bill-status-pill {pill_class}">{html.escape(status_label)}</span>'
                    "</div>"
                    f'<div class="bill-card-meta">{category} | Vence dia {due_day:02d} | {method}</div>'
                    f'<div class="bill-card-value">{amount}</div>'
                    + (
                        f'<div class="bill-card-meta" style="margin-top:0.55rem;">{notes}</div>'
                        if notes
                        else ""
                    )
                    + "</div>",
                    unsafe_allow_html=True,
                )

                status_col, remove_col = st.columns([0.68, 0.32])
                with status_col:
                    status_button_label = (
                        "↩️ Marcar como não pago"
                        if is_paid
                        else "✅ Marcar como pago"
                    )
                    if st.button(
                        status_button_label,
                        key=f"toggle_bill_paid_{bill_id}_{selected_year}_{selected_month}",
                        use_container_width=True,
                    ):
                        try:
                            set_fixed_bill_paid_status(
                                bill_id,
                                selected_month,
                                selected_year,
                                not is_paid,
                            )
                            st.rerun()
                        except Exception as err:
                            st.error(f"Erro ao atualizar o status da conta: {err}")

                with remove_col:
                    if st.button(
                        "🗑️ Remover",
                        key=f"remove_bill_{bill['sheet_row_idx']}",
                        use_container_width=True,
                    ):
                        try:
                            bills_ws = get_or_create_fixed_bills_worksheet()
                            google_sheets_retry(
                                bills_ws.delete_rows,
                                bill["sheet_row_idx"],
                            )
                            delete_fixed_bill_statuses(bill_id)
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as err:
                            st.error(f"Erro ao remover conta fixa: {err}")


def strip_accents(text):
    text = clean_text(text).lower()
    return "".join(
        char for char in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(char)
    )

def parse_import_amount(value):
    raw = clean_text(value)
    if not raw:
        return 0.0

    raw = raw.replace("R$", "").replace("r$", "").replace(" ", "")
    raw = raw.replace("\u00a0", "")
    raw = re.sub(r"[^0-9,\.\-\+]", "", raw)

    if raw in ["", "+", "-", ",", "."]:
        return 0.0

    negative = raw.startswith("-") or raw.endswith("-")
    raw = raw.replace("+", "").replace("-", "")

    if "," in raw and "." in raw:
        # padrão BR: 1.234,56
        raw = raw.replace(".", "").replace(",", ".")
    elif "," in raw:
        raw = raw.replace(",", ".")

    try:
        parsed = float(raw)
    except Exception:
        parsed = 0.0

    return -abs(parsed) if negative else parsed

def read_uploaded_csv(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    encodings = ["utf-8-sig", "utf-8", "latin1", "cp1252"]
    separators = [None, ";", ",", "\t", "|"]

    last_error = None
    for encoding in encodings:
        for sep in separators:
            try:
                buffer = io.BytesIO(file_bytes)
                if sep is None:
                    df = pd.read_csv(buffer, encoding=encoding, sep=None, engine="python")
                else:
                    df = pd.read_csv(buffer, encoding=encoding, sep=sep)

                df = df.dropna(how="all")
                df.columns = [clean_text(col) or f"Coluna {idx+1}" for idx, col in enumerate(df.columns)]
                if len(df.columns) >= 2 and len(df) > 0:
                    return df
            except Exception as err:
                last_error = err
                continue

    raise ValueError(f"Não foi possível ler o CSV. Último erro: {last_error}")

def guess_column(columns, candidates):
    normalized = {col: strip_accents(col) for col in columns}
    for candidate in candidates:
        normalized_candidate = strip_accents(candidate)
        for col, col_norm in normalized.items():
            if normalized_candidate == col_norm or normalized_candidate in col_norm:
                return col
    return columns[0] if columns else None

def build_duplicate_key(date_value, description, amount, payment_method, card):
    try:
        parsed_date = pd.to_datetime(date_value).strftime("%Y-%m-%d")
    except Exception:
        parsed_date = clean_text(date_value)[:10]

    desc = strip_accents(description)
    method = clean_text(payment_method).lower()
    card_clean = strip_accents(card)
    amount_float = abs(safe_float(amount))
    return f"{parsed_date}|{desc}|{amount_float:.2f}|{method}|{card_clean}"

def build_existing_transaction_keys(records):
    keys = set()
    for record in records:
        keys.add(
            build_duplicate_key(
                record.get("created_at", ""),
                record.get("description", ""),
                record.get("amount", 0),
                record.get("payment_method", ""),
                record.get("card", ""),
            )
        )
    return keys


def parse_import_note_metadata(notes):
    """Extrai metadados de importações antigas e novas a partir do campo notes."""
    notes_clean = clean_text(notes)
    if "Importado via CSV" not in notes_clean:
        return None

    def pick(label):
        match = re.search(rf"{re.escape(label)}\s*:\s*([^|]+)", notes_clean, flags=re.IGNORECASE)
        return clean_text(match.group(1)) if match else ""

    source = pick("Origem") or "Origem não identificada"
    file_name = pick("Arquivo") or "Arquivo não identificado"
    import_id = pick("ID")
    batch_id = pick("Lote")
    imported_at = pick("Importado em")

    # Importações antigas não tinham Lote. Agrupamos por origem + arquivo para permitir desfazer.
    if not batch_id:
        batch_base = f"legacy|{source}|{file_name}"
        batch_id = hashlib.sha1(batch_base.encode("utf-8")).hexdigest()[:12]

    return {
        "batch_id": batch_id,
        "source": source,
        "file_name": file_name,
        "import_id": import_id,
        "imported_at": imported_at,
        "is_legacy": "Lote:" not in notes_clean,
    }


def build_import_history(records):
    groups = {}
    for record in records:
        meta = parse_import_note_metadata(record.get("notes", ""))
        if not meta:
            continue

        batch_id = meta["batch_id"]
        if batch_id not in groups:
            groups[batch_id] = {
                "batch_id": batch_id,
                "source": meta["source"],
                "file_name": meta["file_name"],
                "imported_at": meta["imported_at"],
                "is_legacy": meta["is_legacy"],
                "rows": [],
                "count": 0,
                "income": 0.0,
                "expense": 0.0,
                "start_date": None,
                "end_date": None,
            }

        group = groups[batch_id]
        group["rows"].append(int(record.get("sheet_row_idx", 0)))
        group["count"] += 1

        amount = abs(safe_float(record.get("amount", 0)))
        if clean_text(record.get("type", "")).lower() == "entrada":
            group["income"] += amount
        elif clean_text(record.get("type", "")).lower() == "saida":
            group["expense"] += amount

        record_date = record.get("created_at")
        if isinstance(record_date, pd.Timestamp):
            record_date = record_date.to_pydatetime()
        if isinstance(record_date, datetime):
            if group["start_date"] is None or record_date < group["start_date"]:
                group["start_date"] = record_date
            if group["end_date"] is None or record_date > group["end_date"]:
                group["end_date"] = record_date

    history = list(groups.values())
    history.sort(key=lambda item: item["end_date"] or datetime.min, reverse=True)
    return history


def delete_import_batch(row_indices):
    rows = sorted([int(row) for row in row_indices if int(row) > 1], reverse=True)
    for row_idx in rows:
        google_sheets_retry(worksheet.delete_rows, row_idx)
    st.cache_data.clear()
    return len(rows)


def render_import_history(records):
    history = build_import_history(records)

    st.markdown("### Histórico de importações")
    st.caption("Use esta área para desfazer rapidamente um CSV importado. Ao desfazer, todas as transações criadas por aquela importação são removidas da planilha.")

    if not history:
        st.info("Nenhuma importação CSV encontrada ainda.")
        return

    pending_key = st.session_state.get("pending_import_delete")

    for item in history:
        period = "Período não identificado"
        if item["start_date"] and item["end_date"]:
            if item["start_date"].date() == item["end_date"].date():
                period = item["start_date"].strftime("%d/%m/%Y")
            else:
                period = f"{item['start_date'].strftime('%d/%m/%Y')} a {item['end_date'].strftime('%d/%m/%Y')}"

        imported_label = item["imported_at"] or "Importação anterior"
        legacy_label = " · importação antiga" if item.get("is_legacy") else ""
        title = f"{item['source']} · {item['count']} transação(ões) · {period}"

        with st.expander(title, expanded=False):
            st.markdown(
                f"""
                **Arquivo:** {item['file_name']}  
                **Lote:** `{item['batch_id']}`{legacy_label}  
                **Importado em:** {imported_label}  
                **Entradas:** {format_currency(item['income'])}  
                **Saídas:** {format_currency(item['expense'])}
                """
            )

            if pending_key == item["batch_id"]:
                st.warning(f"Confirme para remover {item['count']} transação(ões) dessa importação da planilha.")
                confirm_col, cancel_col = st.columns([0.55, 0.45])
                if confirm_col.button("Confirmar exclusão da importação", type="primary", key=f"confirm_delete_import_{item['batch_id']}"):
                    try:
                        deleted_count = delete_import_batch(item["rows"])
                        st.session_state["import_success_message"] = f"Importação desfeita: {deleted_count} transação(ões) removida(s)."
                        st.session_state.pop("pending_import_delete", None)
                        st.rerun()
                    except Exception as err:
                        st.error(f"Erro ao desfazer importação: {err}")
                if cancel_col.button("Cancelar", key=f"cancel_delete_import_{item['batch_id']}"):
                    st.session_state.pop("pending_import_delete", None)
                    st.rerun()
            else:
                if st.button("🗑️ Desfazer esta importação", key=f"delete_import_{item['batch_id']}"):
                    st.session_state["pending_import_delete"] = item["batch_id"]
                    st.rerun()

def render_import_csv_page(selected_month, selected_year, records):
    st.markdown("# Importe os dados do seu banco")
    st.markdown(
        '<div class="page-kicker">Envie um extrato CSV, revise as linhas detectadas e importe apenas as transações aprovadas para sua planilha.</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="import-note-box">O arquivo que você importar não é salvo em nenhum local, ou pasta do app. Ele é lido temporariamente para sua segurança.</div>',
        unsafe_allow_html=True
    )

    success_message = st.session_state.pop("import_success_message", "") if "import_success_message" in st.session_state else ""
    if success_message:
        st.success(success_message)

    render_import_history(records)
    st.divider()

    setup_col, help_col = st.columns([0.48, 0.52], gap="large")

    with setup_col:
        uploaded_file = st.file_uploader("Enviar extrato CSV", type=["csv"], help="Baixe o CSV no app ou internet banking e envie aqui para revisar antes de importar.")
        import_type = st.selectbox(
            "Tipo de extrato",
            ["Conta bancária / Pix / Débito", "Cartão de crédito"],
            help="Extratos bancários alteram saldo; compras de cartão não reduzem Saldo em Banco no ato da compra."
        )
        source = st.selectbox(
            "Origem",
            ["Nubank", "Nu PJ", "Inter", "Mercado Pago", "PicPay", "Amazon Prime", "Mei Fácil", "Outro"],
        )
        import_as_historical = st.checkbox(
            "Importar como histórico antigo",
            value=False,
            help="Use para meses anteriores à data em que você começou a usar o app. Esses dados serão guardados para relatórios futuros, mas não alteram saldo atual nem a Home."
        )
        if import_as_historical:
            st.info("Histórico antigo: essas linhas serão salvas, mas não entram no saldo atual nem nos cards da Home. Elas ficam disponíveis para relatórios futuros.")

    with help_col:
        st.subheader("Como funciona")
        st.markdown(
            """
            1. O app lê o arquivo temporariamente.  
            2. Você escolhe quais colunas representam data, descrição e valor.  
            3. O app mostra uma prévia com possíveis duplicados.  
            4. Só as linhas marcadas como **Importar** entram na planilha.
            """
        )

    if uploaded_file is None:
        st.info("Envie um arquivo CSV para começar a importação.")
        return

    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    progress_bar = progress_placeholder.progress(0)
    status_placeholder.caption("Upload recebido. Preparando leitura do arquivo...")
    progress_bar.progress(8)

    try:
        df_csv = read_uploaded_csv(uploaded_file)
        progress_bar.progress(28)
        status_placeholder.caption("Arquivo lido. Validando colunas...")
    except Exception as err:
        progress_placeholder.empty()
        status_placeholder.empty()
        st.error(f"Erro ao ler o arquivo CSV: {err}")
        return

    if df_csv.empty:
        progress_placeholder.empty()
        status_placeholder.empty()
        st.warning("O CSV foi lido, mas não possui linhas para importar.")
        return

    columns = list(df_csv.columns)
    default_date_col = guess_column(columns, ["data", "date", "dt", "data da transacao", "data transacao", "data de lançamento", "transaction_date"])
    default_desc_col = guess_column(columns, ["descricao", "descrição", "lancamento", "lançamento", "historico", "histórico", "title", "nome", "description", "detail", "transaction_type"])
    default_value_col = guess_column(columns, ["settlement_net_amount", "real_amount", "valor", "amount", "vlr", "preco", "preço", "total", "transaction_amount"])

    st.markdown("### Mapeamento de colunas")
    map_col1, map_col2, map_col3 = st.columns(3)
    date_col = map_col1.selectbox("Coluna de data", columns, index=columns.index(default_date_col) if default_date_col in columns else 0)
    desc_col = map_col2.selectbox("Coluna de descrição", columns, index=columns.index(default_desc_col) if default_desc_col in columns else 0)
    value_col = map_col3.selectbox("Coluna de valor", columns, index=columns.index(default_value_col) if default_value_col in columns else 0)

    progress_bar.progress(42)
    status_placeholder.caption("Mapeamento aplicado. Processando linhas...")

    default_card = source
    if source == "Mei Fácil":
        default_card = "Mei Fácil"

    duplicate_keys = build_existing_transaction_keys(records)
    preview_rows = []
    total_csv_rows = max(len(df_csv), 1)

    for position, (idx, raw_row) in enumerate(df_csv.iterrows(), start=1):
        raw_date = raw_row.get(date_col, "")
        raw_desc = clean_text(raw_row.get(desc_col, ""))
        raw_amount = parse_import_amount(raw_row.get(value_col, 0))

        if not raw_desc and raw_amount == 0:
            continue

        parsed_date = pd.to_datetime(raw_date, dayfirst=True, errors="coerce")
        if pd.isna(parsed_date):
            parsed_date = datetime(selected_year, selected_month, 1)

        amount_abs = abs(raw_amount)
        if amount_abs == 0:
            continue

        if import_type == "Cartão de crédito":
            tx_type = "saida"
            payment_method = "credito_parcelado"
            card = default_card
        else:
            card = ""
            if raw_amount >= 0:
                tx_type = "entrada"
                payment_method = "pix_conta"
            else:
                tx_type = "saida"
                payment_method = "pix"

        import_id_base = f"{uploaded_file.name}|{source}|{parsed_date.strftime('%Y-%m-%d')}|{raw_desc}|{amount_abs:.2f}|{idx}"
        import_id = hashlib.sha1(import_id_base.encode("utf-8")).hexdigest()[:12]
        duplicate_key = build_duplicate_key(parsed_date, raw_desc, amount_abs, payment_method, card)
        is_duplicate = duplicate_key in duplicate_keys
        auto_category, auto_subcategory, auto_tags = suggest_category(raw_desc, tx_type, payment_method, source)
        if auto_tags:
            auto_tags = join_tags(auto_tags, "importado", source)
        else:
            auto_tags = join_tags("importado", source)

        preview_rows.append({
            "Importar": not is_duplicate,
            "Status": "Possível duplicado" if is_duplicate else "Novo",
            "Data": parsed_date.strftime("%d/%m/%Y"),
            "Descrição": raw_desc or "Sem descrição",
            "Tipo": tx_type,
            "Método": format_payment_method_label(payment_method),
            "Cartão": card,
            "Valor": amount_abs,
            "Categoria": auto_category,
            "Subcategoria": auto_subcategory,
            "Tags": auto_tags,
            "created_at_raw": parsed_date.strftime("%Y-%m-%d %H:%M:%S"),
            "payment_method_raw": payment_method,
            "type_raw": tx_type,
            "card_raw": card,
            "import_id": import_id,
        })

        if position == total_csv_rows or position % max(1, total_csv_rows // 20) == 0:
            progress_value = 42 + int((position / total_csv_rows) * 48)
            progress_bar.progress(min(progress_value, 90))
            status_placeholder.caption(f"Processando linhas... {position}/{total_csv_rows}")

    if not preview_rows:
        progress_placeholder.empty()
        status_placeholder.empty()
        st.warning("Não encontrei linhas válidas para importar nesse CSV.")
        return

    preview_df = pd.DataFrame(preview_rows)
    new_count = int((preview_df["Status"] == "Novo").sum())
    duplicate_count = int((preview_df["Status"] == "Possível duplicado").sum())
    total_income = preview_df.loc[preview_df["type_raw"] == "entrada", "Valor"].sum()
    total_expense = preview_df.loc[preview_df["type_raw"] == "saida", "Valor"].sum()

    progress_bar.progress(100)
    status_placeholder.success("Carregamento concluído")

    summary_html = (
        '<div class="import-summary-grid">'
        f'<div class="import-summary-card"><div class="import-summary-label">Linhas válidas</div><div class="import-summary-value">{len(preview_df)}</div></div>'
        f'<div class="import-summary-card"><div class="import-summary-label">Novas</div><div class="import-summary-value">{new_count}</div></div>'
        f'<div class="import-summary-card"><div class="import-summary-label">Duplicadas</div><div class="import-summary-value">{duplicate_count}</div></div>'
        f'<div class="import-summary-card"><div class="import-summary-label">Saídas detectadas</div><div class="import-summary-value">{html.escape(format_currency(total_expense))}</div></div>'
        '</div>'
    )
    st.markdown(summary_html, unsafe_allow_html=True)

    st.markdown("### Prévia da importação")
    st.caption("Desmarque as linhas que você não quer importar. Linhas marcadas como possível duplicado já vêm desmarcadas.")

    visible_columns = ["Importar", "Status", "Data", "Descrição", "Tipo", "Método", "Cartão", "Valor", "Categoria", "Subcategoria", "Tags"]
    edited_preview = st.data_editor(
        preview_df[visible_columns],
        use_container_width=True,
        hide_index=True,
        disabled=["Status", "Data", "Descrição", "Tipo", "Método", "Cartão", "Valor"],
        column_config={
            "Importar": st.column_config.CheckboxColumn("Importar"),
            "Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
        },
        key=f"csv_preview_{uploaded_file.name}_{source}_{import_type}",
    )

    edited_full_preview = preview_df.copy()
    for editable_col in visible_columns:
        if editable_col in edited_preview.columns:
            edited_full_preview[editable_col] = edited_preview[editable_col]

    selected_indexes = edited_preview.index[edited_preview["Importar"] == True].tolist()
    rows_to_import = edited_full_preview.loc[selected_indexes]
    rows_to_import = rows_to_import[rows_to_import["Status"] != "Possível duplicado"]

    st.caption(f"{len(rows_to_import)} linha(s) selecionada(s) para importar.")

    if st.button("Importar transações selecionadas", type="primary", disabled=rows_to_import.empty):
        import_progress_placeholder = st.empty()
        import_status_placeholder = st.empty()
        import_progress = import_progress_placeholder.progress(0)
        import_status_placeholder.caption("Preparando importação para o Google Sheets...")

        rows_for_sheet = []
        batch_base = f"{uploaded_file.name}|{source}|{import_type}|{datetime.now().isoformat()}"
        batch_id = hashlib.sha1(batch_base.encode("utf-8")).hexdigest()[:12]
        imported_at = datetime.now().strftime("%d/%m/%Y %H:%M")
        total_to_import = max(len(rows_to_import), 1)

        for position, (_, row) in enumerate(rows_to_import.iterrows(), start=1):
            amount = safe_float(row["Valor"])
            payment_method = row["payment_method_raw"]
            tx_type = row["type_raw"]
            card = clean_text(row["card_raw"])
            installment_value = amount
            notes = (
                f"Importado via CSV | Origem: {source} | Arquivo: {uploaded_file.name} | "
                f"Lote: {batch_id} | Importado em: {imported_at} | ID: {row['import_id']} | "
                f"Histórico antigo: {'TRUE' if import_as_historical else 'FALSE'}"
            )
            impact_current_balance = "FALSE" if import_as_historical else "TRUE"
            historical_only = "TRUE" if import_as_historical else "FALSE"

            rows_for_sheet.append([
                tx_type,
                clean_text(row["Descrição"]),
                round(amount, 2),
                payment_method,
                1,
                round(installment_value, 2),
                card,
                "FALSE",
                "",
                row["created_at_raw"],
                notes,
                normalize_category_for_save(row.get("Categoria", "")),
                normalize_subcategory_for_save(row.get("Subcategoria", "")),
                clean_text(row.get("Tags", "")),
                impact_current_balance,
                historical_only,
            ])

            if position == total_to_import or position % max(1, total_to_import // 10) == 0:
                import_progress.progress(min(80, int((position / total_to_import) * 80)))
                import_status_placeholder.caption(f"Preparando linhas... {position}/{total_to_import}")

        try:
            if rows_for_sheet:
                ensure_transaction_headers()
                import_progress.progress(88)
                import_status_placeholder.caption("Enviando para o Google Sheets...")
                google_sheets_retry(worksheet.append_rows, rows_for_sheet, value_input_option="RAW")
                import_progress.progress(100)
                import_status_placeholder.success("Importação concluída")
                st.cache_data.clear()
                st.session_state["import_success_message"] = f"Importação concluída: {len(rows_for_sheet)} transação(ões) adicionada(s). Lote: {batch_id}"
                st.rerun()
        except Exception as err:
            import_status_placeholder.empty()
            st.error(f"Erro ao importar transações: {err}")

def render_install_app_page():
    installed = is_running_installed_webapp()

    st.markdown("# Instalar no iPhone")
    st.markdown(
        '<div class="page-kicker">Adicione o app à tela inicial para abrir como aplicativo, com ícone próprio e acesso mais rápido.</div>',
        unsafe_allow_html=True
    )

    if installed:
        st.success("Você já está usando o app em modo instalado. Por isso, esta opção fica oculta no menu lateral quando o app é aberto pela tela inicial.")
        return

    st.markdown(
        '<div class="install-note-box">Para instalar, abra este app pelo Safari no iPhone. Depois siga os passos abaixo. O app continuará rodando na web!</div>',
        unsafe_allow_html=True
    )

    steps_html = (
        '<div class="install-app-grid">'
        '<div class="install-step-card"><div class="install-step-number">1</div><div class="install-step-title">Abra no Safari</div><div class="install-step-text">No iPhone, acesse o link do app usando o navegador Safari.</div></div>'
        '<div class="install-step-card"><div class="install-step-number">2</div><div class="install-step-title">Toque em compartilhar</div><div class="install-step-text">Use o botão de compartilhamento do Safari, na barra inferior.</div></div>'
        '<div class="install-step-card"><div class="install-step-number">3</div><div class="install-step-title">Adicionar à Tela de Início</div><div class="install-step-text">Escolha a opção para criar o atalho do app na tela inicial.</div></div>'
        '<div class="install-step-card"><div class="install-step-number">4</div><div class="install-step-title">Confirme em Adicionar</div><div class="install-step-text">Depois disso, abra pelo novo ícone do Meu App Finanças.</div></div>'
        '</div>'
    )
    st.markdown(steps_html, unsafe_allow_html=True)

    st.markdown("### O que muda")
    st.markdown(
        '<div class="install-mini-list">'
        '<div class="install-mini-card">✅ Ícone próprio na tela inicial</div>'
        '<div class="install-mini-card">✅ Acesso mais rápido ao app</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="install-final-note">Depois de instalar, abra o app pelo ícone da tela inicial. Nessa condição, a opção de instalação será ocultada automaticamente da sidebar.</div>',
        unsafe_allow_html=True
    )


records = load_data()
app_config = load_app_config()
app_start_date = parse_app_config_date(app_config.get("app_start_date", ""))
initial_bank_balance = safe_float(app_config.get("initial_bank_balance", 0))
initial_cash_balance = safe_float(app_config.get("initial_cash_balance", 0))
render_transaction_animation()

# --- PROCESSAMENTO DOS SALDOS ---
current_date = datetime.now()

st.sidebar.markdown('<div class="sidebar-nav-title">Navegação</div>', unsafe_allow_html=True)
nav_options = ["🏠 Home", "📌 Contas e assinaturas", "🏦 Trazer do banco"]
if not is_running_installed_webapp():
    nav_options.append("📱 Instalar app")

if "sidebar_navigation" in st.session_state and st.session_state["sidebar_navigation"] not in nav_options:
    st.session_state["sidebar_navigation"] = nav_options[0]

selected_nav = st.sidebar.radio(
    "Navegação",
    nav_options,
    index=0,
    key="sidebar_navigation",
    label_visibility="collapsed"
)
if selected_nav == "🏠 Home":
    page_key = "home"
elif selected_nav == "📌 Contas e assinaturas":
    page_key = "contas_assinaturas"
elif selected_nav == "🏦 Trazer do banco":
    page_key = "importar_csv"
else:
    page_key = "instalar_app"

with st.sidebar.expander("Calendário", expanded=True):
    selected_month = st.selectbox(
        "Mês",
        options=list(range(1, 13)),
        index=current_date.month - 1,
        format_func=lambda x: ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"][x-1]
    )
    selected_year = st.selectbox("Ano", options=list(range(current_date.year - 5, current_date.year + 6)), index=5)

with st.sidebar.expander("Configuração inicial", expanded=False):
    st.caption("Defina a data em que você começou a usar o app e os saldos reais daquele dia. Transações anteriores não alteram o saldo atual.")
    start_date_input = st.date_input(
        "Comecei a usar o app no dia:",
        value=app_start_date,
        format="DD/MM/YYYY",
        key="config_app_start_date"
    )
    initial_bank_input = st.text_input(
        "Saldo inicial em banco (R$)",
        value=format_currency(initial_bank_balance).replace("R$ ", ""),
        key="config_initial_bank"
    )
    initial_cash_input = st.text_input(
        "Dinheiro vivo inicial (R$)",
        value=format_currency(initial_cash_balance).replace("R$ ", ""),
        key="config_initial_cash"
    )
    if st.button("Salvar configuração inicial", type="primary", key="save_initial_config"):
        save_app_config({
            "app_start_date": start_date_input.strftime("%Y-%m-%d"),
            "initial_bank_balance": str(parse_import_amount(initial_bank_input)),
            "initial_cash_balance": str(parse_import_amount(initial_cash_input)),
        })
        st.success("Configuração inicial salva.")
        st.rerun()

with st.sidebar.expander("Cartões de crédito", expanded=True):
    render_credit_cards_sidebar()

bank_balance = initial_bank_balance
cash_balance = initial_cash_balance
total_income_month = 0.0
total_expense_month = 0.0
filtered_records = []

for r in records:
    r_date = r["created_at"]
    amount = r["amount"]
    inst_val = r["installment_value"]
    
    is_change_adjustment = is_cash_change_adjustment(r)
    affects_current_balance = should_record_impact_current_balance(r, app_start_date)
    appears_in_home = should_record_appear_in_home(r, app_start_date)

    # Saldo atual: parte dos saldos iniciais e só considera transações a partir da data de início.
    # Importações marcadas como histórico antigo ficam guardadas para relatórios futuros, mas não mexem no saldo.
    if affects_current_balance:
        if r["type"] == "entrada":
            if r["payment_method"] == "pix_conta":
                bank_balance += amount
            elif r["payment_method"] == "dinheiro_vivo" and not is_change_adjustment:
                cash_balance += amount
            elif r["payment_method"] == "troco_dinheiro":
                pass
        else:
            if r["payment_method"] == "saque_dinheiro":
                bank_balance -= amount
                cash_balance += amount
            elif r["payment_method"] == "dinheiro_vivo":
                cash_balance -= amount
            elif r["payment_method"] == "credito_parcelado":
                pass
            else:
                bank_balance -= amount

    # Home e dashboards mensais: não exibem histórico antigo nem transações anteriores à data de início.
    if not appears_in_home:
        continue

    if r["payment_method"] != "credito_parcelado":
        if r_date.month == selected_month and r_date.year == selected_year:
            r["order_amount"] = amount
            filtered_records.append(r)
            if r["type"] == "entrada":
                if not is_change_adjustment:
                    total_income_month += amount
            elif r["payment_method"] != "saque_dinheiro":
                total_expense_month += amount
    else:
        try:
            total_inst = int(r["installments"]) if r["installments"] != "" else 1
        except Exception:
            total_inst = 1
        for i in range(1, total_inst + 1):
            inst_date = r_date + dateutil.relativedelta.relativedelta(months=i-1)
            if inst_date.month == selected_month and inst_date.year == selected_year:
                inst_record = r.copy()
                base_desc = clean_text(r.get("description", "")) or "Compra parcelada"
                inst_record["display_description"] = f"{base_desc} ({i}/{total_inst})"
                inst_record["display_amount"] = inst_val
                inst_record["is_installment_view"] = True
                inst_record["order_amount"] = inst_val
                filtered_records.append(inst_record)
                total_expense_month += inst_val

# --- LAYOUT INTERFACE ---
if page_key == "home":
    # Layout principal: área de resumo + nova transação à esquerda,
    # histórico do mês à direita.
    main_col, history_col = st.columns([0.68, 0.32], gap="large")

    with main_col:
        logo_col, chart_col = st.columns([0.34, 0.66], gap="large", vertical_alignment="center")
        with logo_col:
            render_app_logo(width=240)
        with chart_col:
            st.markdown(build_top_expenses_chart_html(filtered_records), unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 1.35rem;'></div>", unsafe_allow_html=True)
        def summary_card_html(label, value, card_class):
            # HTML sem indentação inicial: evita que o Markdown do Streamlit trate como bloco de código.
            return (
                f'<div class="summary-card {card_class}">'
                f'<div class="summary-card-label">{label}</div>'
                f'<div class="summary-card-value">{value}</div>'
                f'</div>'
            )

        summary_cards_html = (
            '<div class="summary-cards-grid">'
            + "".join([
                summary_card_html("Saldo em Banco", format_currency(bank_balance), "summary-card-bank"),
                summary_card_html("Dinheiro Vivo", format_currency(cash_balance), "summary-card-cash"),
                summary_card_html("Entradas (Mês)", format_currency(total_income_month), "summary-card-income"),
                summary_card_html("Saídas (Mês)", format_currency(total_expense_month), "summary-card-expense"),
            ])
            + '</div>'
        )

        st.markdown(summary_cards_html, unsafe_allow_html=True)

        st.markdown("---")

        if st.session_state.editing_index is not None:
            st.warning(f"✏️ Você está EDITANDO a transação: **{st.session_state.edit_values.get('description')}**")
            if st.button("Cancelar Edição"):
                st.session_state.editing_index = None
                st.session_state.edit_values = {}
                st.rerun()

        # Mantém o formulário compacto e centralizado dentro da coluna principal.
        form_left_pad, form_area, form_right_pad = st.columns([0.02, 0.96, 0.02])

        with form_area:
            st.header("Nova Transação" if st.session_state.editing_index is None else "Editar Transação")

            t_col1, t_col2 = st.columns(2)
            default_type_idx = 0 if st.session_state.edit_values.get("type", "entrada") == "entrada" else 1
            tx_type = t_col1.selectbox("Tipo", ["entrada", "saida"], index=default_type_idx)

            if tx_type == "entrada":
                method_opts = {
                    "pix_conta": "Pix na conta",
                    "dinheiro_vivo": "Dinheiro vivo",
                    "troco_dinheiro": "Troco / ajuste de dinheiro vivo"
                }
            else:
                method_opts = {
                    "pix": "Pix", "dinheiro_vivo": "Dinheiro vivo", 
                    "saque_dinheiro": "Saque dinheiro", "pagamento_fatura": "Pagamento de fatura", 
                    "credito_parcelado": "Crédito Parcelado"
                }

            method_keys = list(method_opts.keys())
            default_method_str = st.session_state.edit_values.get("payment_method", method_keys[0])
            default_method_idx = method_keys.index(default_method_str) if default_method_str in method_keys else 0

            tx_method = t_col2.selectbox("Método", options=method_keys, index=default_method_idx, format_func=lambda x: method_opts[x])

            if st.session_state.editing_index is not None:
                try:
                    raw_amount = st.session_state.edit_values.get("amount", 0.01)
                    default_amount_str = f"{float(raw_amount):.2f}".replace(".", ",")
                except Exception:
                    default_amount_str = "0,01"
            else:
                default_amount_str = ""

            state_modifier = datetime.now().strftime("%M%S") if st.session_state.form_clear_trigger else ""
            state_key = f"new_{state_modifier}" if st.session_state.editing_index is None else f"edit_{st.session_state.editing_index}"

            st.session_state.form_clear_trigger = False

            d_col1, d_col2 = st.columns(2)
            tx_desc = d_col1.text_input("Descrição", value=st.session_state.edit_values.get("description", ""), placeholder="Ex: Mercado", key=f"desc_{state_key}")
            tx_amount_str = d_col2.text_input("Valor Total (R$)", value=default_amount_str, placeholder="Ex: 45,50", key=f"amount_str_{state_key}")

            suggested_category, suggested_subcategory, suggested_tags = suggest_category(tx_desc, tx_type, tx_method)
            existing_category = clean_text(st.session_state.edit_values.get("category", ""))
            existing_subcategory = clean_text(st.session_state.edit_values.get("subcategory", ""))
            existing_tags = clean_text(st.session_state.edit_values.get("tags", ""))

            category_options = get_category_options()
            default_category = existing_category or suggested_category or "Sem categoria"
            if default_category not in category_options:
                default_category = "Sem categoria"

            cat_col1, cat_col2 = st.columns(2)
            tx_category = cat_col1.selectbox(
                "Categoria",
                category_options,
                index=category_options.index(default_category),
                key=f"cat_{state_key}",
                help="Use categoria e subcategoria para alimentar relatórios e orçamentos."
            )

            subcategory_options = get_subcategory_options(tx_category)
            default_subcategory = existing_subcategory or (suggested_subcategory if tx_category == suggested_category else "Sem subcategoria")
            if default_subcategory not in subcategory_options:
                default_subcategory = "Sem subcategoria"
            tx_subcategory = cat_col2.selectbox(
                "Subcategoria",
                subcategory_options,
                index=subcategory_options.index(default_subcategory),
                key=f"subcat_{state_key}"
            )

            tx_tags = st.text_input(
                "Tags",
                value=existing_tags or suggested_tags,
                placeholder="Ex: casa, família, trabalho",
                key=f"tags_{state_key}",
                help="Separe tags por vírgula. Ex: casa, família, parcelado"
            )
            if tx_desc and suggested_category not in ["", "Sem categoria"]:
                st.caption(f"✨ Sugestão automática: **{suggested_category} › {suggested_subcategory}**")

            installments = int(st.session_state.edit_values.get("installments", 1)) if st.session_state.edit_values.get("installments") else 1
            card_brand = st.session_state.edit_values.get("card", "")
            is_for_someone = True if st.session_state.edit_values.get("is_for_someone") in ["TRUE", True] else False
            bought_by = st.session_state.edit_values.get("bought_by", "")

            if st.session_state.editing_index is not None:
                tx_date = pd.to_datetime(st.session_state.edit_values.get("created_at", datetime.now()))
            else:
                tx_date = datetime.now()

            if tx_method == "credito_parcelado" and tx_type == "saida":
                st.markdown("##### 💳 Detalhes do Parcelamento")
                c_col1, c_col2 = st.columns(2)
                installments = c_col1.number_input("Parcelas", min_value=1, max_value=48, value=max(1, installments), key=f"inst_{state_key}")
            
                card_opts = ["Inter", "Mercado Pago", "Nubank", "Nu PJ", "PicPay", "Amazon Prime", "Mei Fácil", "Amazon", "Mei PJ"]
                default_card_idx = card_opts.index(card_brand) if card_brand in card_opts else 0
                card_brand = c_col2.selectbox("Cartão", card_opts, index=default_card_idx, key=f"card_{state_key}")
            
                is_for_someone = st.checkbox("Compra de alguém", value=is_for_someone, key=f"someone_{state_key}")
                if is_for_someone:
                    bought_by = st.text_input("Quem comprou?", value=bought_by, placeholder="Ex: Nome da pessoa", key=f"buyer_{state_key}")

            use_custom_date = st.checkbox("Usar data diferente de hoje" if st.session_state.editing_index is None else "Alterar data da transação", value=st.session_state.editing_index is not None, key=f"cust_date_{state_key}")
            if use_custom_date:
                custom_d = st.date_input("Data da transação", tx_date.date(), format="DD/MM/YYYY", key=f"date_pick_{state_key}")
                st.caption(f"📅 Data selecionada: **{format_br_date(custom_d)}**")
                tx_date = datetime.combine(custom_d, tx_date.time())

            tx_notes = st.text_area("Comentários ou observações", value=st.session_state.edit_values.get("notes", ""), placeholder="Ex: Detalhes da compra...", key=f"notes_{state_key}")

            button_label = "Salvar Alterações" if st.session_state.editing_index is not None else "Adicionar Transação"
            submit_btn = st.button(button_label, type="primary")

            if submit_btn:
                if not tx_desc:
                    if tx_method == "saque_dinheiro":
                        tx_desc = "Saque dinheiro"
                    else:
                        st.error("Por favor, preencha a descrição.")
                        st.stop()
                    
                if not tx_amount_str:
                    st.error("Por favor, insira o valor da transação.")
                    st.stop()
                
                try:
                    clean_amount_str = tx_amount_str.strip().replace(" ", "")
                    if "," in clean_amount_str and "." in clean_amount_str:
                        clean_amount_str = clean_amount_str.replace(".", "")
                    clean_amount_str = clean_amount_str.replace(",", ".")
                    processed_amount = float(clean_amount_str)
                except ValueError:
                    st.error("Valor inválido! Digite apenas números (Ex: 45,50).")
                    st.stop()
                
                processed_inst_val = processed_amount / installments if tx_method == "credito_parcelado" else processed_amount
            
                updated_row = [
                    tx_type,
                    tx_desc,
                    round(processed_amount, 2),       
                    tx_method,
                    int(installments),                
                    round(processed_inst_val, 2),     
                    card_brand,
                    "TRUE" if is_for_someone else "FALSE",
                    bought_by,
                    tx_date.strftime("%Y-%m-%d %H:%M:%S"),
                    tx_notes,
                    normalize_category_for_save(tx_category),
                    normalize_subcategory_for_save(tx_subcategory),
                    clean_text(tx_tags),
                    clean_text(st.session_state.edit_values.get("impact_current_balance", "TRUE")) or "TRUE",
                    clean_text(st.session_state.edit_values.get("historical_only", "FALSE")) or "FALSE"
                ]
            
                is_new_transaction = st.session_state.editing_index is None

                try:
                    if st.session_state.editing_index is not None:
                        google_sheets_retry(
                            worksheet.update,
                            range_name=f"A{st.session_state.editing_index}:P{st.session_state.editing_index}",
                            values=[updated_row],
                            value_input_option="RAW"
                        )
                        st.session_state.editing_index = None
                        st.session_state.edit_values = {}
                    else:
                        ensure_transaction_headers()
                        google_sheets_retry(worksheet.append_row, updated_row, value_input_option="RAW")
                    
                    if is_new_transaction:
                        if tx_type == "entrada" and tx_method != "troco_dinheiro":
                            st.session_state.screen_animation_emoji = "🤑"
                        elif tx_type == "saida":
                            st.session_state.screen_animation_emoji = "😔"

                    st.session_state.form_clear_trigger = True
                    st.session_state.edit_values = {}
                    st.cache_data.clear()
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar na planilha: {err}")

    with history_col:
        st.subheader("Histórico")
        history_search = st.text_input(
            "Pesquisar",
            placeholder="Buscar por nome ou valor...",
            key=f"history_search_{selected_month}_{selected_year}",
            help="Pesquise pelo nome da transação ou pelo valor exibido no mês selecionado."
        )

        if filtered_records:
            df_hist = pd.DataFrame(filtered_records)

            with st.expander("Filtros e ordenação", expanded=False):
                f_type = st.selectbox("Filtrar por Tipo", ["Todos", "entrada", "saida"], key="hist_filter_type")
                f_card = st.selectbox("Filtrar por Cartão", ["Todos"] + [c for c in df_hist["card"].dropna().unique() if str(c) != ""], key="hist_filter_card")
                f_buyer = st.selectbox("Filtrar por Comprador", ["Todos"] + [b for b in df_hist["bought_by"].dropna().unique() if str(b) != ""], key="hist_filter_buyer")
                f_category = st.selectbox("Filtrar por Categoria", ["Todos"] + [c for c in df_hist["category"].dropna().unique() if str(c) != ""], key="hist_filter_category")
                sort_option = st.selectbox(
                    "Ordenar por",
                    options=[
                        "Data: mais recente no topo",
                        "Data: mais antigo no topo",
                        "Valor: do maior para o menor",
                        "Valor: do menor para o maior"
                    ],
                    index=0,
                    key="hist_sort_option"
                )

            if history_search.strip():
                q = history_search.strip().lower()
                q_digits = "".join(ch for ch in q if ch.isdigit())

                def row_matches_search(row):
                    is_inst = is_true_value(row.get("is_installment_view", False))
                    desc = clean_text(row.get("display_description", row.get("description", ""))) if is_inst else clean_text(row.get("description", ""))
                    val = row.get("display_amount", row.get("amount", 0)) if is_inst else row.get("amount", 0)
                    val_float = safe_float(val)
                    search_parts = [
                        desc,
                        str(row.get("notes", "")),
                        str(row.get("payment_method", "")),
                        str(row.get("card", "")),
                        str(row.get("bought_by", "")),
                        str(row.get("category", "")),
                        str(row.get("subcategory", "")),
                        str(row.get("tags", "")),
                        format_currency(val_float),
                        f"{val_float:.2f}",
                        f"{val_float:.2f}".replace(".", ","),
                        str(val),
                    ]
                    joined = " ".join(search_parts).lower()
                    joined_digits = "".join(ch for ch in joined if ch.isdigit())
                    return bool(q in joined or (q_digits != "" and q_digits in joined_digits))

                search_mask = df_hist.apply(row_matches_search, axis=1)
                if not search_mask.empty:
                    search_mask = search_mask.astype(bool)
                    df_hist = df_hist.loc[search_mask]
                else:
                    df_hist = df_hist.iloc[0:0]

            if f_type != "Todos":
                df_hist = df_hist[df_hist["type"] == f_type]
            if f_card != "Todos":
                df_hist = df_hist[df_hist["card"] == f_card]
            if f_buyer != "Todos":
                df_hist = df_hist[df_hist["bought_by"] == f_buyer]
            if f_category != "Todos":
                df_hist = df_hist[df_hist["category"] == f_category]
            
            if sort_option == "Data: mais recente no topo":
                df_hist = df_hist.sort_values(by="created_at", ascending=False)
            elif sort_option == "Data: mais antigo no topo":
                df_hist = df_hist.sort_values(by="created_at", ascending=True)
            elif sort_option == "Valor: do maior para o menor":
                df_hist = df_hist.sort_values(by="order_amount", ascending=False)
            elif sort_option == "Valor: do menor para o maior":
                df_hist = df_hist.sort_values(by="order_amount", ascending=True)

            if df_hist.empty:
                st.info("Nenhuma transação encontrada para a busca/filtros aplicados.")
            else:
                st.caption(f"{len(df_hist)} transação(ões) no mês selecionado")
                for idx, row in df_hist.iterrows():
                    is_inst = is_true_value(row.get("is_installment_view", False))
                    desc = clean_text(row.get("display_description", row.get("description", ""))) if is_inst else clean_text(row.get("description", ""))
                    val = safe_float(row.get("display_amount", row.get("amount", 0)) if is_inst else row.get("amount", 0))
                    clean_notes = clean_text(row.get("notes", ""))
                    if not desc:
                        desc = clean_notes[:60] if clean_notes else "Sem descrição"
                
                    row_dict = row.to_dict() if hasattr(row, "to_dict") else dict(row)
                    is_change_adjustment_row = is_cash_change_adjustment(row_dict)

                    if is_change_adjustment_row:
                        prefix = ""
                        color = "#8a8f98"
                    else:
                        prefix = "+" if row["type"] == "entrada" else ("" if row["payment_method"] == "saque_dinheiro" else "-")
                        color = "#318655" if row["type"] == "entrada" else ("#b4b4b4" if row["payment_method"] == "saque_dinheiro" else "red")
                
                    dt_obj = pd.to_datetime(row['created_at'])
                    meta = f"{format_payment_method_label(row['payment_method'])} | {format_br_date(dt_obj)}"
                    if is_change_adjustment_row:
                        meta += " | Não soma como entrada"
                    clean_card = clean_text(row.get("card", ""))
                    clean_bought_by = clean_text(row.get("bought_by", ""))
                    if clean_card:
                        meta += f" | Cartão: {clean_card}"
                    if clean_bought_by:
                        meta += f" | Compra de: {clean_bought_by}"
                    
                    with st.container(border=True):
                        st.markdown(f"**{desc}**")
                        st.caption(meta)
                        badge_html = category_badge_html(row.get("category", ""), row.get("subcategory", ""), row.get("tags", ""))
                        if badge_html:
                            st.markdown(badge_html, unsafe_allow_html=True)

                        clean_desc = clean_text(row.get("description", ""))
                        if clean_notes and clean_notes != clean_desc:
                            st.markdown(f"*{clean_notes}*")

                        st.markdown(f"<span style='color:{color}; font-weight:bold; font-size:18px;'>{prefix} {format_currency(val)}</span>", unsafe_allow_html=True)

                        row_to_target = row["sheet_row_idx"]
                        edit_key = f"edit_{row_to_target}_{idx}"
                        del_key = f"del_{row_to_target}_{idx}"
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if st.button("✏️ Editar", key=edit_key, help="Editar esta transação", use_container_width=True):
                                st.session_state.editing_index = row_to_target
                                st.session_state.edit_values = row.copy()
                                st.rerun()
                        with btn_col2:
                            if st.button("🗑️ Excluir", key=del_key, help="Excluir permanentemente", use_container_width=True):
                                try:
                                    google_sheets_retry(worksheet.delete_rows, row_to_target)
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception:
                                    pass
        else:
            st.info("Nenhuma transação registrada para o período selecionado.")

elif page_key == "contas_assinaturas":
    render_bills_page(selected_month, selected_year)
elif page_key == "importar_csv":
    render_import_csv_page(selected_month, selected_year, records)
else:
    render_install_app_page()
