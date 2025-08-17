import streamlit as st
from pages import cadastro, agendamento, consulta

st.sidebar.title("📌 Menu")
pagina = st.sidebar.radio("Ir para:", ["Cadastro de Salas", "Agendamento de Salas", "Consulta de Agendamentos"])

if pagina == "Cadastro de Salas":
    cadastro.tela()
elif pagina == "Agendamento de Salas":
    agendamento.tela()
elif pagina == "Consulta de Agendamentos":
    consulta.tela()
