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

# Configuração da página
st.set_page_config(page_title="Meu App Finanças", layout="wide", initial_sidebar_state="expanded")

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
    font-weight: 600 !important;
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
    grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
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

        function paintCollapsedButton(btn) {
            if (!btn) return;

            btn.style.color = '#388253';
            btn.style.background = 'transparent';
            btn.style.boxShadow = 'none';
            btn.style.overflow = 'visible';

            btn.querySelectorAll('svg, svg *').forEach((el) => {
                el.style.color = '#388253';
                el.style.fill = '#388253';
                el.style.stroke = '#388253';
                el.style.opacity = '1';
                el.style.filter = 'none';
            });
        }

        function updateLabel() {
            const doc = getParentDocument();
            if (!doc || !doc.body) return;

            const label = ensureLabel(doc);

            if (sidebarIsOpen(doc)) {
                label.style.display = 'none';
                return;
            }

            const btn = findCollapsedButton(doc);
            if (btn) {
                const rect = btn.getBoundingClientRect();
                paintCollapsedButton(btn);

                label.style.left = (rect.right + 8) + 'px';
                // Ajuste fino: desce 20% em relação ao ajuste anterior.
                label.style.top = (rect.top + rect.height / 2 - 22) + 'px';
            } else {
                // Fallback fixo: exatamente a região superior esquerda onde a seta aparece.
                label.style.left = '64px';
                label.style.top = '24px';
            }

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


BILLS_SHEET_NAME = "contas_assinaturas"
BILLS_HEADERS = ["name", "category", "amount", "due_day", "payment_method", "notes", "active", "created_at"]

def get_or_create_fixed_bills_worksheet():
    try:
        bills_ws = google_sheets_retry(sh.worksheet, BILLS_SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        bills_ws = google_sheets_retry(sh.add_worksheet, title=BILLS_SHEET_NAME, rows=200, cols=len(BILLS_HEADERS))
        google_sheets_retry(bills_ws.append_row, BILLS_HEADERS, value_input_option="RAW")
        return bills_ws

    try:
        values = google_sheets_retry(bills_ws.get_all_values)
        if not values:
            google_sheets_retry(bills_ws.append_row, BILLS_HEADERS, value_input_option="RAW")
        else:
            current_headers = [clean_text(h) for h in values[0]]
            missing_headers = [h for h in BILLS_HEADERS if h not in current_headers]
            if missing_headers:
                # Mantém compatibilidade caso a aba tenha sido criada manualmente com colunas incompletas.
                google_sheets_retry(bills_ws.update, range_name="A1:H1", values=[BILLS_HEADERS], value_input_option="RAW")
    except Exception:
        pass
    return bills_ws

@st.cache_data(ttl=5)
def load_fixed_bills():
    try:
        bills_ws = get_or_create_fixed_bills_worksheet()
        raw_rows = google_sheets_retry(bills_ws.get_all_values)
        if len(raw_rows) <= 1:
            return []

        headers = [clean_text(h) for h in raw_rows[0]]
        records_list = []
        field_map = {header: headers.index(header) if header in headers else idx for idx, header in enumerate(BILLS_HEADERS)}

        for idx, row in enumerate(raw_rows[1:], start=2):
            while len(row) < len(BILLS_HEADERS):
                row.append("")

            record = {
                "sheet_row_idx": idx,
                "name": clean_text(row[field_map.get("name", 0)]),
                "category": clean_text(row[field_map.get("category", 1)]),
                "amount": safe_float(row[field_map.get("amount", 2)]),
                "due_day": int(safe_float(row[field_map.get("due_day", 3)])) if clean_text(row[field_map.get("due_day", 3)]) else 1,
                "payment_method": clean_text(row[field_map.get("payment_method", 4)]),
                "notes": clean_text(row[field_map.get("notes", 5)]),
                "active": clean_text(row[field_map.get("active", 6)]).upper() != "FALSE",
                "created_at": clean_text(row[field_map.get("created_at", 7)]),
            }

            if record["name"]:
                records_list.append(record)

        return records_list
    except Exception as e:
        st.error(f"Erro ao carregar contas e assinaturas: {e}")
        return []

def render_bills_page(selected_month, selected_year):
    st.markdown("# Contas e assinaturas")
    st.markdown(
        '<div class="page-kicker">Cadastre pagamentos mensais fixos, como aluguel, carro, empréstimos, luz, água, internet, celular e assinaturas.</div>',
        unsafe_allow_html=True
    )

    bills = load_fixed_bills()
    active_bills = [bill for bill in bills if bill.get("active", True)]
    total_monthly = sum(safe_float(bill.get("amount", 0)) for bill in active_bills)
    total_count = len(active_bills)

    today = datetime.now()
    upcoming_bills = []
    for bill in active_bills:
        due_day = max(1, min(31, int(bill.get("due_day", 1) or 1)))
        if selected_month == today.month and selected_year == today.year:
            days_until_due = due_day - today.day
            if 0 <= days_until_due <= 7:
                upcoming_bills.append(bill)
        else:
            upcoming_bills.append(bill)

    next_due_text = "Sem vencimentos próximos"
    if upcoming_bills:
        next_bill = sorted(upcoming_bills, key=lambda b: int(b.get("due_day", 1) or 1))[0]
        next_due_text = f'{next_bill.get("name", "Conta")} — dia {int(next_bill.get("due_day", 1)):02d}'

    summary_html = (
        '<div class="bills-summary-grid">'
        '<div class="bills-summary-card"><div class="bills-summary-label">Total mensal fixo</div><div class="bills-summary-value">' + html.escape(format_currency(total_monthly)) + '</div></div>'
        '<div class="bills-summary-card"><div class="bills-summary-label">Contas ativas</div><div class="bills-summary-value">' + str(total_count) + '</div></div>'
        '<div class="bills-summary-card"><div class="bills-summary-label">Próximo vencimento</div><div class="bills-summary-value" style="font-size: clamp(1rem, 1.35vw, 1.35rem);">' + html.escape(next_due_text) + '</div></div>'
        '</div>'
    )
    st.markdown(summary_html, unsafe_allow_html=True)

    form_col, list_col = st.columns([0.46, 0.54], gap="large")

    with form_col:
        st.subheader("Nova conta fixa")
        bill_name = st.text_input("Nome", placeholder="Ex: Aluguel, Internet, Parcela do carro")
        bill_category = st.selectbox(
            "Categoria",
            ["Moradia", "Transporte", "Empréstimos", "Luz", "Água", "Internet", "Celular", "Assinatura", "Outros"]
        )
        amount_col, due_col = st.columns(2)
        bill_amount_str = amount_col.text_input("Valor mensal (R$)", placeholder="Ex: 120,00")
        bill_due_day = due_col.number_input("Dia de vencimento", min_value=1, max_value=31, value=10, step=1)
        bill_payment_method = st.selectbox(
            "Forma de pagamento",
            ["Pix", "Débito", "Boleto", "Cartão de crédito", "Transferência", "Dinheiro", "Outro"]
        )
        bill_notes = st.text_area("Observações", placeholder="Ex: vence todo mês, contrato, detalhes do plano...")

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
                new_bill_row = [
                    bill_name.strip(),
                    bill_category,
                    round(bill_amount, 2),
                    int(bill_due_day),
                    bill_payment_method,
                    bill_notes,
                    "TRUE",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ]
                google_sheets_retry(bills_ws.append_row, new_bill_row, value_input_option="RAW")
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
            sorted_bills = sorted(active_bills, key=lambda b: (int(b.get("due_day", 1) or 1), b.get("name", "")))
            for bill in sorted_bills:
                due_day = int(bill.get("due_day", 1) or 1)
                name = html.escape(bill.get("name", "Conta"))
                category = html.escape(bill.get("category", "Outros"))
                method = html.escape(bill.get("payment_method", ""))
                notes = html.escape(bill.get("notes", ""))
                amount = html.escape(format_currency(safe_float(bill.get("amount", 0))))

                st.markdown(
                    '<div class="bill-card">'
                    f'<div class="bill-card-title">{name}<span class="bill-status-pill">Ativa</span></div>'
                    f'<div class="bill-card-meta">{category} | Vence dia {due_day:02d} | {method}</div>'
                    f'<div class="bill-card-value">{amount}</div>'
                    + (f'<div class="bill-card-meta" style="margin-top:0.55rem;">{notes}</div>' if notes else '')
                    + '</div>',
                    unsafe_allow_html=True
                )

                if st.button("🗑️ Remover", key=f"remove_bill_{bill['sheet_row_idx']}"):
                    try:
                        bills_ws = get_or_create_fixed_bills_worksheet()
                        google_sheets_retry(bills_ws.delete_rows, bill["sheet_row_idx"])
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

def render_import_csv_page(selected_month, selected_year, records):
    st.markdown("# Importar CSV")
    st.markdown(
        '<div class="page-kicker">Envie um extrato CSV, revise as linhas detectadas e importe apenas as transações aprovadas para sua planilha.</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="import-note-box">O CSV não é salvo no GitHub, no Drive ou na pasta do app. Ele é lido temporariamente, mostrado para revisão e descartado após a sessão. Apenas as transações confirmadas são gravadas no Google Sheets.</div>',
        unsafe_allow_html=True
    )

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

    try:
        df_csv = read_uploaded_csv(uploaded_file)
    except Exception as err:
        st.error(f"Erro ao ler o arquivo CSV: {err}")
        return

    if df_csv.empty:
        st.warning("O CSV foi lido, mas não possui linhas para importar.")
        return

    columns = list(df_csv.columns)
    default_date_col = guess_column(columns, ["data", "date", "dt", "data da transacao", "data transacao", "data de lançamento"])
    default_desc_col = guess_column(columns, ["descricao", "descrição", "lancamento", "lançamento", "historico", "histórico", "title", "nome"])
    default_value_col = guess_column(columns, ["valor", "amount", "vlr", "preco", "preço", "total"])

    st.markdown("### Mapeamento de colunas")
    map_col1, map_col2, map_col3 = st.columns(3)
    date_col = map_col1.selectbox("Coluna de data", columns, index=columns.index(default_date_col) if default_date_col in columns else 0)
    desc_col = map_col2.selectbox("Coluna de descrição", columns, index=columns.index(default_desc_col) if default_desc_col in columns else 0)
    value_col = map_col3.selectbox("Coluna de valor", columns, index=columns.index(default_value_col) if default_value_col in columns else 0)

    default_card = source
    if source == "Mei Fácil":
        default_card = "Mei Fácil"

    duplicate_keys = build_existing_transaction_keys(records)
    preview_rows = []

    for idx, raw_row in df_csv.iterrows():
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

        preview_rows.append({
            "Importar": not is_duplicate,
            "Status": "Possível duplicado" if is_duplicate else "Novo",
            "Data": parsed_date.strftime("%d/%m/%Y"),
            "Descrição": raw_desc or "Sem descrição",
            "Tipo": tx_type,
            "Método": format_payment_method_label(payment_method),
            "Cartão": card,
            "Valor": amount_abs,
            "created_at_raw": parsed_date.strftime("%Y-%m-%d %H:%M:%S"),
            "payment_method_raw": payment_method,
            "type_raw": tx_type,
            "card_raw": card,
            "import_id": import_id,
        })

    if not preview_rows:
        st.warning("Não encontrei linhas válidas para importar nesse CSV.")
        return

    preview_df = pd.DataFrame(preview_rows)
    new_count = int((preview_df["Status"] == "Novo").sum())
    duplicate_count = int((preview_df["Status"] == "Possível duplicado").sum())
    total_income = preview_df.loc[preview_df["type_raw"] == "entrada", "Valor"].sum()
    total_expense = preview_df.loc[preview_df["type_raw"] == "saida", "Valor"].sum()

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

    visible_columns = ["Importar", "Status", "Data", "Descrição", "Tipo", "Método", "Cartão", "Valor"]
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

    selected_indexes = edited_preview.index[edited_preview["Importar"] == True].tolist()
    rows_to_import = preview_df.loc[selected_indexes]
    rows_to_import = rows_to_import[rows_to_import["Status"] != "Possível duplicado"]

    st.caption(f"{len(rows_to_import)} linha(s) selecionada(s) para importar.")

    if st.button("Importar transações selecionadas", type="primary", disabled=rows_to_import.empty):
        rows_for_sheet = []
        for _, row in rows_to_import.iterrows():
            amount = safe_float(row["Valor"])
            payment_method = row["payment_method_raw"]
            tx_type = row["type_raw"]
            card = clean_text(row["card_raw"])
            installment_value = amount
            notes = f"Importado via CSV | Origem: {source} | Arquivo: {uploaded_file.name} | ID: {row['import_id']}"

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
            ])

        try:
            if rows_for_sheet:
                google_sheets_retry(worksheet.append_rows, rows_for_sheet, value_input_option="RAW")
                st.cache_data.clear()
                st.success(f"Importação concluída: {len(rows_for_sheet)} transação(ões) adicionada(s).")
                st.rerun()
        except Exception as err:
            st.error(f"Erro ao importar transações: {err}")


records = load_data()
render_transaction_animation()

# --- PROCESSAMENTO DOS SALDOS ---
current_date = datetime.now()

st.sidebar.markdown('<div class="sidebar-nav-title">Navegação</div>', unsafe_allow_html=True)
nav_options = ["🏠 Home", "📌 Contas e assinaturas", "📥 Importar CSV"]
selected_nav = st.sidebar.radio(
    "Navegação",
    nav_options,
    index=0,
    key="sidebar_navigation",
    label_visibility="collapsed"
)
if selected_nav == nav_options[0]:
    page_key = "home"
elif selected_nav == nav_options[1]:
    page_key = "contas_assinaturas"
else:
    page_key = "importar_csv"

with st.sidebar.expander("Calendário", expanded=True):
    selected_month = st.selectbox(
        "Mês",
        options=list(range(1, 13)),
        index=current_date.month - 1,
        format_func=lambda x: ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"][x-1]
    )
    selected_year = st.selectbox("Ano", options=list(range(current_date.year - 5, current_date.year + 6)), index=5)

with st.sidebar.expander("Cartões de crédito", expanded=True):
    render_credit_cards_sidebar()

bank_balance = 0.0
cash_balance = 0.0
total_income_month = 0.0
total_expense_month = 0.0
filtered_records = []

for r in records:
    r_date = r["created_at"]
    amount = r["amount"]
    inst_val = r["installment_value"]
    
    is_change_adjustment = is_cash_change_adjustment(r)

    if r["type"] == "entrada":
        if r["payment_method"] == "pix_conta":
            bank_balance += amount
        elif r["payment_method"] == "dinheiro_vivo" and not is_change_adjustment:
            cash_balance += amount
        elif r["payment_method"] == "troco_dinheiro":
            # Troco/ajuste não é dinheiro novo: ele já fazia parte do valor sacado.
            pass
    else:
        if r["payment_method"] == "saque_dinheiro":
            bank_balance -= amount
            cash_balance += amount
        elif r["payment_method"] == "dinheiro_vivo":
            cash_balance -= amount
        elif r["payment_method"] == "credito_parcelado":
            # Compra no crédito parcelado não muda o saldo em banco no ato da compra.
            # Ela entra apenas como saída mensal, parcela por parcela, no mês correto.
            pass
        else:
            bank_balance -= amount

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
            if os.path.exists("logo.png"):
                st.image("logo.png", width=240)
            else:
                st.title("Meu App Finanças")
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
                    tx_notes
                ]
            
                is_new_transaction = st.session_state.editing_index is None

                try:
                    if st.session_state.editing_index is not None:
                        google_sheets_retry(
                            worksheet.update,
                            range_name=f"A{st.session_state.editing_index}:K{st.session_state.editing_index}",
                            values=[updated_row],
                            value_input_option="RAW"
                        )
                        st.session_state.editing_index = None
                        st.session_state.edit_values = {}
                    else:
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
else:
    render_import_csv_page(selected_month, selected_year, records)
