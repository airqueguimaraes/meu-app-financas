import streamlit as st
import pandas as pd
from datetime import datetime
import dateutil.relativedelta
from streamlit_gsheets import GSheetsConnection

# Configuração da página
st.set_page_config(page_title="Controle Financeiro", layout="wide", initial_sidebar_state="expanded")

# Puxa o link da planilha direto do arquivo secrets que você já configurou
try:
    SPREADSHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet_url"]
except Exception:
    st.error("Erro: Não foi possível encontrar o link da planilha no arquivo secrets.toml")
    st.stop()

# Injeta a chave privada diretamente por aqui para evitar o erro de formatação do Streamlit Secrets
st.secrets["connections"]["gsheets"]["private_key"] = "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDDwCfI60IKUxHI\njh8rHp+MOYkU/gCL8UB/HJIQbn1FJoTYKG1dwrYws3LvjEjQeS98uU3ZViZ0CEhE\n7VMRfseBtkYcGRcO/3tcswR+7avAkruHvihLseA/BOEM8IeVe5YeafqbqQkWzmNp\nyuPKpIApKfZ3y6XZXu7VK53bXpujHxTkSqyrK7WCbzPuGqQ9ycmJqBLze0s+stfr\n2vcRWBKWM7w/NhcV4QxxPrOg9sGPSUibdc0YhCfwkQyOtUVjBn1f4EVdz7b4+4Be\nTwOj5BBGVYchVEx7Pa5MOVljzt5It/KU2ovvz3dC4zPvg8nWYAdxaJiTPbbl1aL7\nieUGh7krAgMBAAECggEACYYt6V6uReZTdS3vt59eepTKEKq9yBFNkWGzJvgultC6\n90bFm3bqemV2GtBOh/t9eKoOGZxRc/p7LwSvsqg3zh3aPL++bs0LaYU5m3C2Qeu3\nEscJGuBlXWuVWkB8YvoyYaRyZw8gZsBVTJkXNY2EwXv4hqJH8tLloprkAVURvtah\nyUU7nYVtLbd9LyJK0EmWJTW3AOhL59yx2RY90lPG25FVkQH/fMe5uRWiTjHTL++4\nb5xKqKJ6u6rP3sI/wB4YtrJff0+4weSzZr2tJjmT0HVZ5/Ms/Kkoq8ALTVBJqo6w\nRBWCZQBIuASGU64nz5Nj8wxs2m3/EKq8NNpyynbZ4QKBgQDya4pQLepgdbtCEahe\nHJn2620u39jwMYyn0uGwtkfq3HmTyW++EeFSepy/Rts/eDp9U7GQ5+8XB7S6qPeH\nWvM3OLnNHXLsoJo5zwkWiyAYBvlNrsNBkuQ45H3mgh5dJ1Yl5owaVorHQAaHhqaF\nUia5rUDPngU6KGFtykzEQZ/2YwKBgQDOt1hLkau7qxO7YNm852dKjW9hN39JUpLc\n1V38SbNODAes2SX0D/9rHNiYyb7o34kCrT214UbrfD7kh/WiAne5Kdihwco9PHwK\nSMAgs2NpSPROpSp4ltKHDF1gyfVPSUgYkV5a6uPHspW6XNYi7PqPPjYHq+7hXQWP\nMoY3HzoomQKBgQC8y8QMbbX7KbWM3vOhV+UQyIlf2DW72tsQWMwsM8oOv2ZwEpFU\nFdjFw3gP/78Az0G+GVBQ6lDqPrYiKTWd1NdWSndpp2W5o9p46yTIydFU5RmDxneK\nujvDky/6NZwwMFKHceXrHTs3skVjhxpo+nHuaV/wUcEAajJ2rvbaYcGSwQKBgQCC\n5VBQ0dY4CNV+0o4t8y3R5IuBuN2t9U6v7aAM8DJNGosFpZ9F05d+IQ76eM2dsmaU\nvlSURildVhiRJ5Kf2wYqxte5XfgNHK7C6FxYmJ87fQnOfwHMyFxZTbgXYOsoIJQ5\nklt4IMLJokjzcHPcO8lRSSh3ZSTnqbqqeWjJoMl4CQKBgQCcbO7Yy9C7kzB7IzFb\nfp5AVpggR2g/IfYt40OXONapYjEWXqqpIMg97/61SriySoBRDsZB5TdtQ8kr87Kr\noshKbctusiiYkx6CRJ4DMtRuOatPr5tALU+sleYkstGoS+4jkH9CmGspB9ckPKEx\ns8kwm6PMzQBUipYtDcKU3y7crA==\n-----END PRIVATE KEY-----\n"

# Inicializa a conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Função para buscar dados atualizados da planilha
@st.cache_data(ttl=5)
def load_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, usecols=[
            "type", "description", "amount", "payment_method", 
            "installments", "installment_value", "card", 
            "is_for_someone", "bought_by", "created_at", "notes"
        ])
        df["created_at"] = pd.to_datetime(df["created_at"])
        return df.to_dict(orient="records")
    except Exception:
        return []

# Carrega os registros
records = load_data()

def format_currency(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- PROCESSAMENTO DOS DADOS ---
st.sidebar.title("Calendário")
current_date = datetime.now()
selected_month = st.sidebar.selectbox(
    "Mês", 
    options=list(range(1, 13)), 
    index=current_date.month - 1,
    format_func=lambda x: ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"][x-1]
)
selected_year = st.sidebar.selectbox("Ano", options=list(range(current_date.year - 5, current_date.year + 6)), index=5)

bank_balance = 0.0
cash_balance = 0.0
total_income_month = 0.0
total_expense_month = 0.0
expanded_records = []

for r in records:
    r_date = r["created_at"]
    
    if r["type"] == "entrada":
        if r["payment_method"] == "pix_conta":
            bank_balance += r["amount"]
        elif r["payment_method"] == "dinheiro_vivo":
            cash_balance += r["amount"]
    else:
        if r["payment_method"] == "saque_dinheiro":
            bank_balance -= r["amount"]
            cash_balance += r["amount"]
        elif r["payment_method"] == "dinheiro_vivo":
            cash_balance -= r["amount"]
        else: 
            bank_balance -= r["amount"]

    if r["payment_method"] != "credito_parcelado":
        if r_date.month == selected_month and r_date.year == selected_year:
            expanded_records.append(r)
            if r["type"] == "entrada":
                total_income_month += r["amount"]
            elif r["payment_method"] != "saque_dinheiro":
                total_expense_month += r["amount"]
    else:
        for i in range(1, int(r["installments"]) + 1):
            inst_date = r_date + dateutil.relativedelta.relativedelta(months=i-1)
            if inst_date.month == selected_month and inst_date.year == selected_year:
                inst_record = r.copy()
                inst_record["description"] = f"{r['description']} ({i}/{int(r['installments'])})"
                inst_record["amount"] = r["installment_value"]
                expanded_records.append(inst_record)
                total_expense_month += r["installment_value"]

# --- LAYOUT INTERFACE ---
st.title("Mini App Finanças")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Saldo em Banco", format_currency(bank_balance))
col2.metric("Dinheiro Vivo", format_currency(cash_balance))
col3.metric("Entradas (Mês)", format_currency(total_income_month))
col4.metric("Saídas (Mês)", format_currency(total_expense_month))

st.markdown("---")

st.header("Nova Transação")
with st.form("transaction_form", clear_on_submit=True):
    t_col1, t_col2 = st.columns(2)
    tx_type = t_col1.selectbox("Tipo", ["entrada", "saida"])
    
    if tx_type == "entrada":
        method_opts = {"pix_conta": "Pix na conta", "dinheiro_vivo": "Dinheiro vivo"}
    else:
        method_opts = {
            "pix": "Pix", "dinheiro_vivo": "Dinheiro vivo", 
            "saque_dinheiro": "Saque dinheiro", "pagamento_fatura": "Pagamento de fatura", 
            "credito_parcelado": "Crédito Parcelado"
        }
        
    tx_method = t_col2.selectbox("Método", options=list(method_opts.keys()), format_func=lambda x: method_opts[x])
    
    d_col1, d_col2 = st.columns(2)
    tx_desc = d_col1.text_input("Descrição", placeholder="Ex: Salário")
    tx_amount = d_col2.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f")
    
    installments = 1
    card_brand = ""
    is_for_someone = False
    bought_by