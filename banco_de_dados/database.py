import psycopg2
import bcrypt
from config.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
import datetime

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
            CREATE TABLE IF NOT EXISTS mensagens_offline (
            id SERIAL PRIMARY KEY,
            remetente TEXT NOT NULL,
            destinatario TEXT NOT NULL,
            mensagem TEXT NOT NULL,
            timestamp TEXT NOT NULL
);
    """)
    con.commit()
    cur.close()
    con.close()
    
def criar_tabela_mensagens():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mensagens (
            id SERIAL PRIMARY KEY,
            remetente TEXT NOT NULL,
            destinatario TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conexao.commit()
    conexao.close()
    
def salvar_mensagem_historico(remetente, destinatario, conteudo, timestamp):
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute('''
            INSERT INTO mensagens (remetente, destinatario, conteudo, timestamp)
            VALUES (%s, %s, %s, %s)
        ''', (remetente, destinatario, conteudo, timestamp))
        conexao.commit()
        conexao.close()
    except Exception as e:
        print(f"Erro ao salvar mensagem no histórico: {e}")
        
def carregar_historico_conversa(usuario1, usuario2):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('''
        SELECT remetente, conteudo, timestamp FROM mensagens
        WHERE (remetente = %s AND destinatario = %s)
           OR (remetente = %s AND destinatario = %s)
        ORDER BY timestamp ASC
    ''', (usuario1, usuario2, usuario2, usuario1))
    mensagens = cursor.fetchall()
    conexao.close()
    return mensagens


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

# def salvar_mensagem_offline(remetente, destinatario, mensagem):
#     conn = conectar()
#     cur = conn.cursor()
#     cur.execute("""
#         INSERT INTO mensagens_offline (remetente, destinatario, mensagem, timestamp)
#         VALUES (%s, %s, %s, %s)
#     """, (remetente, destinatario, mensagem, datetime.now().isoformat()))
#     conn.commit()
#     cur.close()
#     conn.close()

# def carregar_mensagens_offline(usuario):
#     conn = conectar()
#     cur = conn.cursor()
#     cur.execute("SELECT remetente, mensagem, timestamp FROM mensagens_offline WHERE destinatario=%s", (usuario,))
#     mensagens = cur.fetchall()
#     cur.execute("DELETE FROM mensagens_offline WHERE destinatario=%s", (usuario,))
#     conn.commit()
#     cur.close()
#     conn.close()
#     return mensagens

def listar_usuarios():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT usuario FROM usuarios")
    usuarios = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return usuarios

def salvar_mensagem_offline(remetente, destinatario, mensagem):
    conn = conectar()
    cur = conn.cursor()
    timestamp = datetime.now().isoformat()
    try:
        cur.execute(
            "INSERT INTO mensagens_offline (remetente, destinatario, mensagem, timestamp) VALUES (%s, %s, %s, %s)",
            (remetente, destinatario, mensagem, timestamp)
        )
        conn.commit()
    except Exception as e:
        print(f"Erro ao salvar mensagem offline: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def carregar_mensagens_offline(usuario):
    conn = conectar()
    cur = conn.cursor()
    mensagens = []
    try:
        cur.execute(
            "SELECT remetente, mensagem, timestamp FROM mensagens_offline WHERE destinatario=%s",
            (usuario,)
        )
        mensagens = cur.fetchall()
        cur.execute(
            "DELETE FROM mensagens_offline WHERE destinatario=%s",
            (usuario,)
        )
        conn.commit()
    except Exception as e:
        print(f"Erro ao carregar mensagens offline: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    return mensagens