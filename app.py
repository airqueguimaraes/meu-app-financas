import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import dateutil.relativedelta
import gspread
import os
import base64
import mimetypes

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
    grid-template-columns: repeat(auto-fit, minmax(205px, 1fr));
    gap: 1rem;
    align-items: stretch;
}

.summary-card {
    border-radius: 22px;
    padding: 1.15rem 1.3rem 1.2rem 1.3rem;
    min-height: 118px;
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
    font-size: clamp(0.82rem, 4.2cqw, 0.92rem);
    font-weight: 600;
    line-height: 1.15;
    margin-bottom: 0.55rem;
    white-space: nowrap;
}

.summary-card-value {
    color: #2f3341;
    font-size: clamp(1.6rem, 15.2cqw, 2.35rem);
    font-weight: 500;
    line-height: 1.05;
    letter-spacing: -0.035em;
    white-space: nowrap;
    max-width: 100%;
}

@media (max-width: 1100px) {
    .summary-cards-grid {
        grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
        gap: 0.85rem;
    }

    .summary-card {
        padding: 1rem;
        min-height: 104px;
    }
}

@media (max-width: 720px) {
    .summary-cards-grid {
        grid-template-columns: 1fr;
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

try:
    gc = get_sheets_client()
    sh = gc.open_by_url(SPREADSHEET_URL)
    worksheet = sh.get_worksheet(0)
except Exception as e:
    st.error(f"Erro ao conectar com a planilha: {e}")
    st.stop()

if "editing_index" not in st.session_state:
    st.session_state.editing_index = None
if "edit_values" not in st.session_state:
    st.session_state.edit_values = {}
if "form_clear_trigger" not in st.session_state:
    st.session_state.form_clear_trigger = False

def safe_float(val):
    if val == "" or pd.isna(val):
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        try:
            return float(str(val).strip().replace(".", "").replace(",", "."))
        except ValueError:
            return 0.0

@st.cache_data(ttl=5)
def load_data():
    try:
        raw_rows = worksheet.get_all_values()
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
                "type": str(row[field_map["type"]]).strip(),
                "description": str(row[field_map["description"]]).strip(),
                "amount": safe_float(row[field_map["amount"]]),
                "payment_method": str(row[field_map["payment_method"]]).strip(),
                "installments": str(row[field_map["installments"]]).strip(),
                "installment_value": safe_float(row[field_map["installment_value"]]),
                "card": str(row[field_map["card"]]).strip(),
                "is_for_someone": str(row[field_map["is_for_someone"]]).strip(),
                "bought_by": str(row[field_map["bought_by"]]).strip(),
                "notes": str(row[field_map["notes"]]).strip(),
            }
            
            raw_date = str(row[field_map["created_at"]]).strip()
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

    st.sidebar.markdown('<div class="credit-cards-spacer"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<h3 class="credit-cards-title">Cartões de crédito</h3>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="credit-cards-line"></div>', unsafe_allow_html=True)

    for card in credit_cards:
        logo_col, name_col, date_col = st.sidebar.columns([0.18, 0.35, 0.47], gap="small", vertical_alignment="center")

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

        st.sidebar.markdown('<div class="credit-card-gap"></div>', unsafe_allow_html=True)

records = load_data()
render_transaction_animation()

# --- PROCESSAMENTO DOS SALDOS ---
st.sidebar.markdown('<h3 class="sidebar-section-title">Calendário</h3>', unsafe_allow_html=True)
current_date = datetime.now()
selected_month = st.sidebar.selectbox(
    "Mês", 
    options=list(range(1, 13)), 
    index=current_date.month - 1,
    format_func=lambda x: ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"][x-1]
)
selected_year = st.sidebar.selectbox("Ano", options=list(range(current_date.year - 5, current_date.year + 6)), index=5)

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
    
    if r["type"] == "entrada":
        if r["payment_method"] == "pix_conta":
            bank_balance += amount
        elif r["payment_method"] == "dinheiro_vivo":
            cash_balance += amount
    else:
        if r["payment_method"] == "saque_dinheiro":
            bank_balance -= amount
            cash_balance += amount
        elif r["payment_method"] == "dinheiro_vivo":
            cash_balance -= amount
        else: 
            bank_balance -= amount

    if r["payment_method"] != "credito_parcelado":
        if r_date.month == selected_month and r_date.year == selected_year:
            r["order_amount"] = amount
            filtered_records.append(r)
            if r["type"] == "entrada":
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
                inst_record["display_description"] = f"{r['description']} ({i}/{total_inst})"
                inst_record["display_amount"] = inst_val
                inst_record["is_installment_view"] = True
                inst_record["order_amount"] = inst_val
                filtered_records.append(inst_record)
                total_expense_month += inst_val

# --- LAYOUT INTERFACE ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=240)
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
else:
    st.title("Meu App Finanças")

# Layout principal: área de resumo + nova transação à esquerda,
# histórico do mês à direita.
main_col, history_col = st.columns([0.68, 0.32], gap="large")

with main_col:
    def summary_card_html(label, value, card_class):
        return f"""
            <div class="summary-card {card_class}">
                <div class="summary-card-label">{label}</div>
                <div class="summary-card-value">{value}</div>
            </div>
        """

    summary_cards_html = "".join([
        summary_card_html("Saldo em Banco", format_currency(bank_balance), "summary-card-bank"),
        summary_card_html("Dinheiro Vivo", format_currency(cash_balance), "summary-card-cash"),
        summary_card_html("Entradas (Mês)", format_currency(total_income_month), "summary-card-income"),
        summary_card_html("Saídas (Mês)", format_currency(total_expense_month), "summary-card-expense"),
    ])

    st.markdown(
        f"""
        <div class="summary-cards-grid">
            {summary_cards_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

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
            method_opts = {"pix_conta": "Pix na conta", "dinheiro_vivo": "Dinheiro vivo"}
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
                    worksheet.update(
                        range_name=f"A{st.session_state.editing_index}:K{st.session_state.editing_index}", 
                        values=[updated_row],
                        value_input_option="RAW"
                    )
                    st.session_state.editing_index = None
                    st.session_state.edit_values = {}
                else:
                    worksheet.append_row(updated_row, value_input_option="RAW")
                    
                if is_new_transaction:
                    st.session_state.screen_animation_emoji = "🤑" if tx_type == "entrada" else "😔"

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
                is_inst = row.get("is_installment_view", False)
                desc = str(row.get("display_description", row.get("description", ""))) if is_inst else str(row.get("description", ""))
                val = row.get("display_amount", row.get("amount", 0)) if is_inst else row.get("amount", 0)
                try:
                    val_float = float(val)
                except Exception:
                    val_float = 0.0
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
                is_inst = row.get("is_installment_view", False)
                desc = row["display_description"] if is_inst else row["description"]
                val = row["display_amount"] if is_inst else row["amount"]
                
                prefix = "+" if row["type"] == "entrada" else ("" if row["payment_method"] == "saque_dinheiro" else "-")
                color = "#318655" if row["type"] == "entrada" else ("#b4b4b4" if row["payment_method"] == "saque_dinheiro" else "red")
                
                dt_obj = pd.to_datetime(row['created_at'])
                meta = f"{str(row['payment_method']).replace('_', ' ').title()} | {format_br_date(dt_obj)}"
                if row["card"]:
                    meta += f" | Cartão: {row['card']}"
                if row["bought_by"]:
                    meta += f" | Compra de: {row['bought_by']}"
                    
                with st.container(border=True):
                    st.markdown(f"**{desc}**")
                    st.caption(meta)

                    clean_notes = str(row["notes"]).strip()
                    clean_desc = str(row["description"]).strip()
                    if clean_notes and clean_notes != "nan" and clean_notes != "" and clean_notes != clean_desc:
                        st.markdown(f"*{row['notes']}*")

                    st.markdown(f"<span style='color:{color}; font-weight:bold; font-size:18px;'>{prefix} {format_currency(float(val))}</span>", unsafe_allow_html=True)

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
                                worksheet.delete_rows(row_to_target)
                                st.cache_data.clear()
                                st.rerun()
                            except Exception:
                                pass
    else:
        st.info("Nenhuma transação registrada para o período selecionado.")
