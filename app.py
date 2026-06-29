import streamlit as st
import pandas as pd
from datetime import datetime
import dateutil.relativedelta
import gspread

# Configuração da página
st.set_page_config(page_title="Controle Financeiro", layout="wide", initial_sidebar_state="expanded")

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

# Montamos as credenciais oficiais do Google (agora com o token_uri obrigatório incluído)
creds_dict = {
    "type": "service_account",
    "project_id": PROJECT_ID,
    "private_key_id": PRIVATE_KEY_ID,
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDDwCfI60IKUxHI\njh8rHp+MOYkU/gCL8UB/HJIQbn1FJoTYKG1dwrYws3LvjEjQeS98uU3ZViZ0CEhE\n7VMRfseBtkYcGRcO/3tcswR+7avAkruHvihLseA/BOEM8IeVe5YeafqbqQkWzmNp\nyuPKpIApKfZ3y6XZXu7VK53bXpujHxTkSqyrK7WCbzPuGqQ9ycmJqBLze0s+stfr\n2vcRWBKWM7w/NhcV4QxxPrOg9sGPSUibdc0YhCfwkQyOtUVjBn1f4EVdz7b4+4Be\nTwOj5BBGVYchVEx7Pa5MOVljzt5It/KU2ovvz3dC4zPvg8nWYAdxaJiTPbbl1aL7\nieUGh7krAgMBAAECggEACYYt6V6uReZTdS3vt59eepTKEKq9yBFNkWGzJvgultC6\n90bFm3bqemV2GtBOh/t9eKoOGZxRc/p7LwSvsqg3zh3aPL++bs0LaYU5m3C2Qeu3\nEscJGuBlXWuVWkB8YvoyYaRyZw8gZsBVTJkXNY2EwXv4hqJH8tLloprkAVURvtah\nyUU7nYVtLbd9LyJK0EmWJTW3AOhL59yx2RY90lPG25FVkQH/fMe5uRWiTjHTL++4\nb5xKqKJ6u6rP3sI/wB4YtrJff0+4weSzZr2tJjmT0HVZ5/Ms/Kkoq8ALTVBJqo6w\nRBWCZQBIuASGU64nz5Nj8wxs2m3/EKq8NNpyynbZ4QKBgQDya4pQLepgdbtCEahe\nHJn2620u39jwMYyn0uGwtkfq3HmTyW++EeFSepy/Rts/eDp9U7GQ5+8XB7S6qPeH\nWvM3OLnNHXLsoJo5zwkWiyAYBvlNrsNBkuQ45H3mgh5dJ1Yl5owaVorHQAaHhqaF\nUia5rUDPngU6KGFtykzEQZ/2YwKBgQDOt1hLkau7qxO7YNm852dKjW9hN39JUpLc\n1V38SbNODAes2SX0D/9rHNiYyb7o34kCrT214UbrfD7kh/WiAne5Kdihwco9PHwK\nSMAgs2NpSPROpSp4ltKHDF1gyfVPSUgYkV5a6uPHspW6XNYi7PqPPjYHq+7hXQWP\nMoY3HzoomQKBgQC8y8QMbbX7KbWM3vOhV+UQyIlf2DW72tsQWMwsM8oOv2ZwEpFU\nFdjFw3gP/78Az0G+GVBQ6lDqPrYiKTWd1NdWSndpp2W5o9p46yTIydFU5RmDxneK\nujvDky/6NZwwMFKHceXrHTs3skVjhxpo+nHuaV/wUcEAajJ2rvbaYcGSwQKBgQCC\n5VBQ0dY4CNV+0o4t8y3R5IuBuN2t9U6v7aAM8DJNGosFpZ9F05d+IQ76eM2dsmaU\nvlSURildVhiRJ5Kf2wYqxte5XfgNHK7C6FxYmJ87fQnOfwHMyFxZTbgXYOsoIJQ5\nklt4IMLJokjzcHPcO8lRSSh3ZSTnqbqqeWjJoMl4CQKBgQCcbO7Yy9C7kzB7IzFb\nfp5AVpggR2g/IfYt40OXONapYjEWXqqpIMg97/61SriySoBRDsZB5TdtQ8kr87Kr\noshKbctusiiYkx6CRJ4DMtRuOatPr5tALU+sleYkstGoS+4jkH9CmGspB9ckPKEx\ns8kwm6PMzQBUipYtDcKU3y7crA==\n-----END PRIVATE KEY-----\n",
    "client_email": CLIENT_EMAIL,
    "client_id": CLIENT_ID,
    "token_uri": "https://oauth2.googleapis.com/token"
}

# Inicializa o cliente do Google Sheets através do gspread
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

# Função para buscar dados atualizados da planilha
@st.cache_data(ttl=5)
def load_data():
    try:
        data = worksheet.get_all_records()
        if not data:
            return []
        df = pd.DataFrame(data)
        cols = ["type", "description", "amount", "payment_method", "installments", "installment_value", "card", "is_for_someone", "bought_by", "created_at", "notes"]
        for col in cols:
            if col not in df.columns:
                df[col] = ""
        df = df[cols]
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
    try:
        r_date = r["created_at"]
        amount = float(r["amount"]) if r["amount"] != "" else 0.0
        inst_val = float(r["installment_value"]) if r["installment_value"] != "" else 0.0
    except Exception:
        continue
    
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
            expanded_records.append(r)
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
                inst_record["description"] = f"{r['description']} ({i}/{total_inst})"
                inst_record["amount"] = inst_val
                expanded_records.append(inst_record)
                total_expense_month += inst_val

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
    bought_by = ""
    
    if tx_method == "credito_parcelado" and tx_type == "saida":
        c_col1, c_col2 = st.columns(2)
        installments = c_col1.number_input("Parcelas", min_value=2, max_value=48, value=2)
        card_brand = c_col2.selectbox("Cartão", ["Inter", "Mercado Pago", "Nubank", "Nu PJ", "PicPay", "Amazon", "Mei PJ"])
        
        is_for_someone = st.checkbox("Compra de alguém")
        if is_for_someone:
            bought_by = st.text_input("Quem comprou?", placeholder="Ex: João")
            
    use_custom_date = st.checkbox("Usar data diferente de hoje")
    tx_date = datetime.now()
    if use_custom_date:
        tx_date = st.date_input("Data da transação", datetime.now())
        tx_date = datetime.combine(tx_date, datetime.now().time())
        
    tx_notes = st.text_area("Comentários ou observações", placeholder="Ex: Observações sobre esta transação")
    
    submit_btn = st.form_submit_button("Adicionar Transação")
    
    if submit_btn:
        if not tx_desc:
            if tx_method == "saque_dinheiro":
                tx_desc = "Saque dinheiro"
            else:
                st.error("Por favor, preencha a descrição.")
                st.stop()
                
        inst_val = tx_amount / installments if tx_method == "credito_parcelado" else tx_amount
        
        new_row = [
            tx_type,
            tx_desc,
            tx_amount,
            tx_method,
            installments,
            inst_val,
            card_brand,
            "TRUE" if is_for_someone else "FALSE",
            bought_by,
            tx_date.strftime("%Y-%m-%d %H:%M:%S"),
            tx_notes
        ]
        
        try:
            worksheet.append_row(new_row)
            st.cache_data.clear()
            st.success("Transação salva com sucesso!")
            st.rerun()
        except Exception as err:
            st.error(f"Erro ao salvar na planilha: {err}")

st.markdown("---")
st.header("Histórico do Mês Selecionado")

if expanded_records:
    df = pd.DataFrame(expanded_records)
    f_col1, f_col2, f_col3 = st.columns(3)
    f_type = f_col1.selectbox("Filtrar por Tipo", ["Todos", "entrada", "saida"])
    
    cards_available = ["Todos"] + [c for c in df["card"].dropna().unique() if c != ""]
    f_card = f_col2.selectbox("Filtrar por Cartão",