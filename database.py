import sqlite3

def get_connection():
    conn = sqlite3.connect("salas.db", check_same_thread=False)
    cursor = conn.cursor()

    # Tabela de salas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS salas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        dias_disponiveis TEXT NOT NULL,
        horario_inicio TEXT NOT NULL,
        horario_fim TEXT NOT NULL
    )
    """)

    # Tabela de agendamentos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sala_id INTEGER NOT NULL,
        data DATE NOT NULL,
        horario_inicio TEXT NOT NULL,
        horario_fim TEXT NOT NULL,
        usuario TEXT NOT NULL,
        FOREIGN KEY(sala_id) REFERENCES salas(id)
    )
    """)

    conn.commit()
    return conn, cursor
