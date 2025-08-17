from pages import cadastro, agendamento, consulta

import streamlit as st

def main():
    st.sidebar.title("Navegação")
    escolha = st.sidebar.radio("Ir para:", ["Agendamento", "Cadastro", "Consulta"])

    if escolha == "Agendamento":
        agendamento.tela()
    elif escolha == "Cadastro":
        cadastro.tela()
    else:
        consulta.tela()

if __name__ == "__main__":
    main()
