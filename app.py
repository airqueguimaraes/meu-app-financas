import streamlit as st
import pandas as pd
from datetime import datetime
import dateutil.relativedelta
from streamlit_gsheets import GSheetsConnection

# Configuração da página
st.set_page_config(page_title="Controle Financeiro", layout="wide", initial_sidebar_state="expanded")

# Puxa o link da planilha direto do arquivo secrets que você acabou de configurar
try:
    SPREADSHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet_url"]
except Exception:
    st.error("Erro: Não foi possível encontrar o link da planilha no arquivo secrets.toml")
    st.stop()

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
        
        new_record = {
            "type": tx_type,
            "description": tx_desc,
            "amount": tx_amount,
            "payment_method": tx_method,
            "installments": installments,
            "installment_value": inst_val,
            "card": card_brand,
            "is_for_someone": is_for_someone,
            "bought_by": bought_by,
            "created_at": tx_date.strftime("%Y-%m-%d %H:%M:%S"),
            "notes": tx_notes
        }
        
        current_df = pd.DataFrame(records) if records else pd.DataFrame(columns=new_record.keys())
        new_row_df = pd.DataFrame([new_record])
        updated_df = pd.concat([current_df, new_row_df], ignore_index=True)
        
        conn.update(spreadsheet=SPREADSHEET_URL, data=updated_df)
        st.cache_data.clear()
        st.success("Transação salva com sucesso!")
        st.rerun()

st.markdown("---")
st.header("Histórico do Mês Selecionado")

if expanded_records:
    df = pd.DataFrame(expanded_records)
    f_col1, f_col2, f_col3 = st.columns(3)
    f_type = f_col1.selectbox("Filtrar por Tipo", ["Todos", "entrada", "saida"])
    
    cards_available = ["Todos"] + [c for c in df["card"].dropna().unique() if c != ""]
    f_card = f_col2.selectbox("Filtrar por Cartão", cards_available)
    
    buyers_available = ["Todos"] + [b for b in df["bought_by"].dropna().unique() if b != ""]
    f_buyer = f_col3.selectbox("Filtrar por Comprador", buyers_available)
    
    if f_type != "Todos":
        df = df[df["type"] == f_type]
    if f_card != "Todos":
        df = df[df["card"] == f_card]
    if f_buyer != "Todos":
        df = df[df["bought_by"] == f_buyer]
        
    for _, row in df.sort_values(by="created_at", ascending=False).iterrows():
        prefix = "+" if row["type"] == "entrada" else ("" if row["payment_method"] == "saque_dinheiro" else "-")
        color = "green" if row["type"] == "entrada" else ("white" if row["payment_method"] == "saque_dinheiro" else "red")
        
        meta = f"{row['payment_method'].replace('_', ' ').title()} | {row['created_at'].strftime('%d/%m/%Y')}"
        if row["card"]:
            meta += f" | Cartão: {row['card']}"
        if row["is_for_someone"] and row["bought_by"]:
            meta += f" | Compra de: {row['bought_by']}"
            
        with st.container():
            c_left, c_right = st.columns([4, 1])
            c_left.markdown(f"**{row['description']}**")
            c_left.caption(meta)
            if row["notes"] and str(row["notes"]) != "nan":
                c_left.markdown(f"*{row['notes']}*")
            c_right.markdown(f"<span style='color:{color}; font-weight:bold; font-size:18px;'>{prefix} {format_currency(row['amount'])}</span>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:0.5em 0px; opacity:0.2;'>", unsafe_allow_html=True)
else:
    st.info("Nenhuma transação registrada para o período selecionado.")