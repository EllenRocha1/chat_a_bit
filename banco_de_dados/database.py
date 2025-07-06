import psycopg2
import bcrypt
from config.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

def conectar():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def criar_tabela_usuarios():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        );
    """)
    con.commit()
    cur.close()
    con.close()

def inserir_usuario(nome, usuario, senha):
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (nome, usuario, senha) VALUES (%s, %s, %s)",
                    (nome, usuario, senha))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except psycopg2.IntegrityError:
        conn.rollback()
        return False  # Usuário já existe
    except Exception as e:
        print("Erro ao inserir:", e)
        return False

def verificar_login(usuario, senha_digitada):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("SELECT senha FROM usuarios WHERE usuario = %s", (usuario,))
    resultado = cur.fetchone()

    cur.close()
    conn.close()

    if resultado:
        senha_hash = resultado[0]
        if bcrypt.checkpw(senha_digitada.encode(), senha_hash.encode()):
            return True
        else:
            return "senha_incorreta"
    return "usuario_nao_encontrado"
