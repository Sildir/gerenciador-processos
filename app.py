import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import date

# CONFIGURAÇÕES
SPREADSHEET_ID = "1xX-cUKFpCh4poFpBvghXb0lMO6SW0hAgJCd3KH4_X1s"
CREDENTIALS_FILE = "credentials.json"
SHEET_PROCESSOS = "Processos"
SHEET_PESSOAS = "Pessoas"

# AUTENTICAÇÃO
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)

client = gspread.authorize(creds)

# ACESSO ÀS PLANILHAS
sheet_processos = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_PROCESSOS)
sheet_pessoas = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_PESSOAS)

# Lê dados da aba "Pessoas"
df_pessoas = pd.DataFrame(sheet_pessoas.get_all_records())

# Gera listas dinâmicas
clientes = df_pessoas[df_pessoas["Cliente/Contrária"].str.lower() == "cliente"]["Nome"].tolist()
contrarias = df_pessoas[df_pessoas["Cliente/Contrária"].str.lower() == "contrária"]["Nome"].tolist()

st.title("📂 Gerenciador de Processos")

with st.form("formulario"):
    st.subheader("Cadastrar novo processo")

    numero = st.text_input("Número do Processo")
    cliente = st.selectbox("Cliente", clientes if clientes else ["Nenhum cliente cadastrado"])

    if cliente and cliente != "Nenhum cliente cadastrado":
        dados_cliente = df_pessoas[df_pessoas["Nome"] == cliente]
        if not dados_cliente.empty:
            pessoa = dados_cliente.iloc[0]
            st.markdown(f"""
            **📌 Dados do Cliente Selecionado:**
            - **CPF:** {pessoa['CPF']}
            - **Telefone:** {pessoa['Telefone/WhatsApp']}
            - **Cidade:** {pessoa['Cidade']} - {pessoa['Estado']}
            - **Profissão:** {pessoa['Profissão']}
            - **E-mail:** {pessoa['E-mail']}
            """)

    parte_contraria = st.selectbox("Parte Contrária", contrarias if contrarias else ["Nenhuma parte contrária cadastrada"])

    if parte_contraria and parte_contraria != "Nenhuma parte contrária cadastrada":
        dados_contraria = df_pessoas[df_pessoas["Nome"] == parte_contraria]
        if not dados_contraria.empty:
            pessoa = dados_contraria.iloc[0]
            st.markdown(f"""
            **📌 Dados da Parte Contrária Selecionada:**
            - **CPF:** {pessoa['CPF']}
            - **Telefone:** {pessoa['Telefone/WhatsApp']}
            - **Cidade:** {pessoa['Cidade']} - {pessoa['Estado']}
            - **Profissão:** {pessoa['Profissão']}
            - **E-mail:** {pessoa['E-mail']}
            """)

    tipo_acao = st.text_input("Tipo da Ação")
    comarca = st.text_input("Vara/Comarca")
    situacao = st.selectbox("Situação", ["Ativo", "Suspenso", "Encerrado"])
    data_inicio = st.date_input("Data de Início", value=date.today())
    observacoes = st.text_area("Observações")

    submitted = st.form_submit_button("Cadastrar")

    if submitted:
        nova_linha = [numero, cliente, parte_contraria, tipo_acao, comarca, situacao, str(data_inicio), observacoes]
        sheet_processos.append_row(nova_linha)
        st.success("✅ Processo cadastrado com sucesso!")

st.subheader("📋 Processos Cadastrados")
dados = sheet_processos.get_all_records()
df = pd.DataFrame(dados)

if not df.empty:
    col1, col2 = st.columns(2)
    with col1:
        cliente_filtro = st.selectbox("Filtrar por cliente", ["Todos"] + sorted(df["Cliente"].unique()))
    with col2:
        situacao_filtro = st.selectbox("Filtrar por situação", ["Todos"] + sorted(df["Situação"].unique()))

    if cliente_filtro != "Todos":
        df = df[df["Cliente"] == cliente_filtro]
    if situacao_filtro != "Todos":
        df = df[df["Situação"] == situacao_filtro]

    st.dataframe(df)
else:
    st.info("Nenhum processo cadastrado ainda.")

with st.expander("👤 Cadastrar Pessoa"):
    with st.form("form_pessoa"):
        nome = st.text_input("Nome Completo")
        cpf = st.text_input("CPF")
        rg = st.text_input("RG")
        ctps = st.text_input("CTPS")
        senha_inss = st.text_input("Senha INSS")
        endereco = st.text_input("Endereço")
        numero_end = st.text_input("Número")
        complemento = st.text_input("Complemento")
        bairro = st.text_input("Bairro")
        cidade = st.text_input("Cidade")
        estado = st.text_input("Estado")
        cep = st.text_input("CEP")
        telefone = st.text_input("Telefone/WhatsApp")
        estado_civil = st.text_input("Estado Civil")
        nacionalidade = st.text_input("Nacionalidade")
        profissao = st.text_input("Profissão")
        email = st.text_input("E-mail")
        tipo = st.selectbox("Tipo", ["Cliente", "Contrária"])
        obs = st.text_area("Observações")

        enviar_pessoa = st.form_submit_button("Salvar Pessoa")

        if enviar_pessoa:
            nova_pessoa = [
                nome, cpf, rg, ctps, senha_inss, endereco, numero_end, complemento, bairro, cidade,
                estado, cep, telefone, estado_civil, nacionalidade, profissao, email, tipo, obs
            ]
            sheet_pessoas.append_row(nova_pessoa)
            st.success("Pessoa cadastrada com sucesso!")
