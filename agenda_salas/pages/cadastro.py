import streamlit as st
from database import get_connection
import datetime

DIAS_OPCOES = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

def _parse_time(txt: str) -> datetime.time:
    if isinstance(txt, datetime.time):
        return txt
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.datetime.strptime(txt, fmt).time()
        except Exception:
            continue
    return datetime.time(8, 0)

def _validar_horarios(h_ini: datetime.time, h_fim: datetime.time) -> bool:
    return h_ini < h_fim

def tela():
    st.title("Cadastro de Salas 🏢")

    senha = st.text_input("Digite a senha de administrador:", type="password")
    if senha != "admin123":
        if senha:
            st.error("Senha incorreta! ❌")
        return

    conn, cursor = get_connection()

    st.subheader("Nova Sala")
    with st.form("form_nova_sala", clear_on_submit=True):
        nome_sala = st.text_input("Nome da Sala")
        dias_semana = st.multiselect("Dias disponíveis", DIAS_OPCOES)
        horario_inicio = st.time_input("Horário de Início", datetime.time(8, 0), key="novo_inicio")
        horario_fim = st.time_input("Horário de Fim", datetime.time(18, 0), key="novo_fim")

        cadastrar = st.form_submit_button("Cadastrar Sala")
        if cadastrar:
            if not nome_sala or not dias_semana:
                st.error("Preencha todos os campos.")
            elif not _validar_horarios(horario_inicio, horario_fim):
                st.error("O horário de início deve ser antes do horário de fim.")
            else:
                cursor.execute("""
                    INSERT INTO salas (nome, dias_disponiveis, horario_inicio, horario_fim)
                    VALUES (?, ?, ?, ?)
                """, (nome_sala, ",".join(dias_semana), str(horario_inicio), str(horario_fim)))
                conn.commit()
                st.success(f"Sala '{nome_sala}' cadastrada com sucesso!")

    st.divider()
    st.subheader("Salas Cadastradas")

    if "editing_sala_id" not in st.session_state:
        st.session_state.editing_sala_id = None

    cursor.execute("SELECT id, nome, dias_disponiveis, horario_inicio, horario_fim FROM salas ORDER BY nome")
    salas = cursor.fetchall()

    if not salas:
        st.info("Nenhuma sala cadastrada ainda.")
        return

    for sala in salas:
        sala_id, nome, dias_txt, h_ini_txt, h_fim_txt = sala
        col1, col2, col3 = st.columns([6,1,1])
        with col1:
            st.write(f"**{nome}** — Dias: {dias_txt or '-'} | ⏰ {h_ini_txt} às {h_fim_txt}")
        with col2:
            if st.button("✏️ Editar", key=f"edit_{sala_id}"):
                st.session_state.editing_sala_id = sala_id
        with col3:
            if st.button("🗑 Excluir", key=f"del_{sala_id}"):
                cursor.execute("DELETE FROM salas WHERE id = ?", (sala_id,))
                conn.commit()
                st.warning(f"Sala '{nome}' excluída.")
                st.rerun()

    if st.session_state.editing_sala_id is not None:
        st.divider()
        st.subheader("Editar Sala")

        cursor.execute("SELECT id, nome, dias_disponiveis, horario_inicio, horario_fim FROM salas WHERE id = ?",
                       (st.session_state.editing_sala_id,))
        row = cursor.fetchone()
        if not row:
            st.error("Sala não encontrada.")
            st.session_state.editing_sala_id = None
            return

        sala_id, nome, dias_txt, h_ini_txt, h_fim_txt = row
        dias_pre = [d.strip() for d in (dias_txt or "").split(",") if d.strip()]

        with st.form(f"form_editar_{sala_id}"):
            novo_nome = st.text_input("Nome da Sala", value=nome, key=f"nome_edit_{sala_id}")
            novos_dias = st.multiselect("Dias disponíveis", DIAS_OPCOES, default=dias_pre, key=f"dias_edit_{sala_id}")
            novo_inicio = st.time_input("Horário de Início", value=_parse_time(h_ini_txt), key=f"ini_edit_{sala_id}")
            novo_fim = st.time_input("Horário de Fim", value=_parse_time(h_fim_txt), key=f"fim_edit_{sala_id}")

            c1, c2 = st.columns(2)
            salvar = c1.form_submit_button("💾 Salvar Alterações")
            cancelar = c2.form_submit_button("❌ Cancelar")

            if salvar:
                if not novo_nome or not novos_dias:
                    st.error("Preencha todos os campos.")
                elif not _validar_horarios(novo_inicio, novo_fim):
                    st.error("O horário de início deve ser antes do horário de fim.")
                else:
                    cursor.execute("""
                        UPDATE salas
                        SET nome = ?, dias_disponiveis = ?, horario_inicio = ?, horario_fim = ?
                        WHERE id = ?
                    """, (novo_nome, ",".join(novos_dias), str(novo_inicio), str(novo_fim), sala_id))
                    conn.commit()
                    st.success("Sala atualizada com sucesso!")
                    st.session_state.editing_sala_id = None
                    st.rerun()

            if cancelar:
                st.session_state.editing_sala_id = None
                st.info("Edição cancelada.")
                st.rerun()
