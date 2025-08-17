import streamlit as st
from database import get_connection
import datetime

def tela():
    st.title("Agendamento de Salas 📅")

    conn, cursor = get_connection()
    cursor.execute("SELECT id, nome, dias_disponiveis, horario_inicio, horario_fim FROM salas")
    salas = cursor.fetchall()
    if not salas:
        st.warning("Nenhuma sala cadastrada ainda.")
        return

    sala_escolhida = st.selectbox("Escolha uma sala:", salas, format_func=lambda x: x[1])
    sala_id = sala_escolhida[0]
    sala_nome = sala_escolhida[1]
    dias_disponiveis = sala_escolhida[2]
    horario_inicio_sala = sala_escolhida[3]
    horario_fim_sala = sala_escolhida[4]

    st.write(f"📌 Sala: **{sala_nome}**")
    st.write(f"🗓 Dias disponíveis: {dias_disponiveis}")
    st.write(f"⏰ Horário permitido: {horario_inicio_sala} às {horario_fim_sala}")

    data = st.date_input("Escolha a data", min_value=datetime.date.today())
    hora_inicio = st.time_input("Horário de Início")
    hora_fim = st.time_input("Horário de Fim")
    usuario = st.text_input("Seu nome")

    if st.button("Agendar Sala"):
        if hora_inicio >= hora_fim:
            st.error("O horário de início deve ser antes do horário de fim.")
            return
        if not usuario:
            st.error("Informe seu nome para agendar.")
            return

        cursor.execute("""
            SELECT * FROM agendamentos
            WHERE sala_id = ? AND data = ? 
            AND ((horario_inicio <= ? AND horario_fim > ?) 
            OR (horario_inicio < ? AND horario_fim >= ?))
        """, (sala_id, data.strftime("%Y-%m-%d"), str(hora_inicio), str(hora_inicio), str(hora_fim), str(hora_fim)))
        conflito = cursor.fetchall()

        if conflito:
            st.error("⚠️ Já existe um agendamento nesse horário.")
        else:
            cursor.execute("""
                INSERT INTO agendamentos (sala_id, data, horario_inicio, horario_fim, usuario)
                VALUES (?, ?, ?, ?, ?)
            """, (sala_id, data.strftime("%Y-%m-%d"), str(hora_inicio), str(hora_fim), usuario))
            conn.commit()
            st.success("✅ Agendamento realizado com sucesso!")

    st.subheader("📋 Agendamentos da Sala")
    cursor.execute("""
        SELECT data, horario_inicio, horario_fim, usuario
        FROM agendamentos
        WHERE sala_id = ? AND data >= ?
        ORDER BY data, horario_inicio
    """, (sala_id, datetime.date.today().strftime("%Y-%m-%d")))
    agendamentos = cursor.fetchall()

    if agendamentos:
        for ag in agendamentos:
            data_exib = datetime.datetime.strptime(ag[0], "%Y-%m-%d").strftime("%d-%m-%Y")
            st.write(f"📅 {data_exib} | ⏰ {ag[1]} - {ag[2]} | 👤 {ag[3]}")
    else:
        st.info("Nenhum agendamento futuro para esta sala.")
