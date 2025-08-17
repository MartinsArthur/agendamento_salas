import streamlit as st
from database import get_connection
import datetime

def _inicio_da_semana(d: datetime.date) -> datetime.date:
    return d - datetime.timedelta(days=d.weekday())

def tela():
    st.title("Consulta de Agendamentos 🔍")
    conn, cursor = get_connection()

    opcao = st.radio("Consultar por:", ["Sala", "Semana"], horizontal=True)

    if opcao == "Sala":
        cursor.execute("SELECT id, nome FROM salas ORDER BY nome")
        salas = cursor.fetchall()
        if not salas:
            st.warning("Nenhuma sala cadastrada.")
            return
        sala_sel = st.selectbox("Escolha a sala", salas, format_func=lambda x: x[1])
        cursor.execute("""
            SELECT data, horario_inicio, horario_fim, usuario
            FROM agendamentos
            WHERE sala_id = ?
            ORDER BY data, horario_inicio
        """, (sala_sel[0],))
        ags = cursor.fetchall()
        st.subheader(f"Agendamentos da Sala {sala_sel[1]}")
        if ags:
            for ag in ags:
                data_exib = datetime.datetime.strptime(ag[0], "%Y-%m-%d").strftime("%d-%m-%Y")
                st.write(f"📅 {data_exib} | ⏰ {ag[1]} - {ag[2]} | 👤 {ag[3]}")
        else:
            st.info("Nenhum agendamento para esta sala.")

    else:  # Semana
        hoje = datetime.date.today()
        ini0 = _inicio_da_semana(hoje)
        semanas = []
        for i in range(5):
            inicio = ini0 + datetime.timedelta(weeks=i)
            fim = inicio + datetime.timedelta(days=6)
            semanas.append((inicio, fim, f"Semana {'atual' if i==0 else '+'+str(i)} — {inicio.strftime('%d-%m-%Y')} a {fim.strftime('%d-%m-%Y')}"))

        escolha = st.selectbox("Selecione a semana", semanas, index=0, format_func=lambda x: x[2])
        inicio_semana, fim_semana, _ = escolha
        st.caption(f"Exibindo de {inicio_semana.strftime('%d-%m-%Y')} a {fim_semana.strftime('%d-%m-%Y')}")

        cursor.execute("""
            SELECT s.nome, a.data, a.horario_inicio, a.horario_fim, a.usuario
            FROM agendamentos a
            JOIN salas s ON a.sala_id = s.id
            WHERE a.data BETWEEN ? AND ?
            ORDER BY a.data, a.horario_inicio, s.nome
        """, (inicio_semana.strftime("%Y-%m-%d"), fim_semana.strftime("%Y-%m-%d")))
        ags = cursor.fetchall()

        if ags:
            for ag in ags:
                data_exib = datetime.datetime.strptime(ag[1], "%Y-%m-%d").strftime("%d-%m-%Y")
                st.write(f"🏢 {ag[0]} | 📅 {data_exib} | ⏰ {ag[2]} - {ag[3]} | 👤 {ag[4]}")
        else:
            st.info("Nenhum agendamento nesta semana selecionada.")
