import socket
import threading
import json
from datetime import datetime
from banco_de_dados.database import listar_usuarios, salvar_mensagem_offline, carregar_mensagens_offline, salvar_mensagem_historico, carregar_historico_conversa

HOST = 'localhost'
PORTA = 5000
LOGIN_MARKER = ',entrou'
LOGOUT_MARKER = ',saiu'

servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor_socket.bind((HOST, PORTA))
servidor_socket.listen(10)

clientes_conectados = {}
clientes_lock = threading.Lock()

def broadcast(mensagem, conexao_excluida=None):
    mensagem_json = json.dumps(mensagem) + "\n"
    with clientes_lock:
        for usuario, dados_cliente in list(clientes_conectados.items()):
            if dados_cliente['conexao'] != conexao_excluida:
                try:
                    dados_cliente['conexao'].send(mensagem_json.encode('utf-8'))
                except:
                   pass

def remover_cliente(usuario):
    print(f"Tentando remover o cliente '{usuario}'...")
    with clientes_lock:
        if usuario in clientes_conectados:
            try:
                clientes_conectados[usuario]['conexao'].close()
            except:
                pass
            del clientes_conectados[usuario]
            print(f"Cliente '{usuario}' removido com sucesso.")
    
    broadcast({
        'tipo': 'status',
        'usuario': usuario,
        'status': 'offline',
    })

def lidar_com_mensagem(conexao, usuario, mensagem_str):
    try:
        dados = json.loads(mensagem_str)
        tipo_msg = dados.get('tipo')

        if tipo_msg == 'mensagem':
            destinatario = dados.get('para')
            conteudo = dados.get('conteudo')
            timestamp = dados.get('timestamp')

            salvar_mensagem_historico(usuario, destinatario, conteudo, timestamp)
            with clientes_lock:
                if destinatario in clientes_conectados:
                    clientes_conectados[destinatario]['conexao'].send((json.dumps(dados) + "\n").encode('utf-8'))
                else:
                    salvar_mensagem_offline(usuario, destinatario, conteudo)
        
        elif tipo_msg == 'digitando':
            destinatario = dados.get('para')
            if destinatario in clientes_conectados:
                with clientes_lock:
                    if destinatario in clientes_conectados:
                        clientes_conectados[destinatario]['conexao'].send((json.dumps(dados) + "\n").encode('utf-8'))
        
        elif tipo_msg == 'solicitacao':
            acao = dados.get('acao')
            if acao == 'historico':
                outro_usuario = dados.get('com')
                mensagens = carregar_historico_conversa(usuario, outro_usuario)
                resposta_historico = {
                    'tipo': 'historico_conversa',
                    'mensagens': [
                        {'remetente': rem, 'conteudo': cont, 'timestamp': ts} for rem, cont, ts in mensagens
                    ]
                }
                conexao.send((json.dumps(resposta_historico) + "\n").encode('utf-8'))

            elif acao == 'listar_usuarios':
                todos_usuarios = listar_usuarios()
                resposta = {
                    'tipo': 'lista_usuarios',
                    'usuarios': {
                        u: ('online' if u in clientes_conectados else 'offline')
                        for u in todos_usuarios
                        if u != usuario 
                    }
                }
                conexao.send((json.dumps(resposta) + "\n").encode('utf-8'))
    
    except json.JSONDecodeError:
        print(f"Mensagem JSON inválida recebida de {usuario}: {mensagem_str}")
    except Exception as e:
        print(f"Erro inesperado em lidar_com_mensagem para o usuário {usuario}: {e}")


def lidar_com_cliente(conexao):
    usuario = None
    buffer = ""
    try:
        while True:
            dados = conexao.recv(2048).decode('utf-8')
            if not dados:
                break  # Conexão fechada pelo cliente
            
            buffer += dados

            while '\n' in buffer:
                linha, buffer = buffer.split('\n', 1)
                if not linha.strip():
                    continue

                if not usuario:
                    try:
                        dados_login = json.loads(linha)
                        if dados_login.get('tipo') == 'login' and dados_login.get('usuario'):
                            usuario = dados_login.get('usuario')

                            with clientes_lock:
                                clientes_conectados[usuario] = {'conexao': conexao, 'status': 'online'}
                            print(f"Usuário '{usuario}' logado com sucesso de {conexao.getpeername()}.")
                            
                            mensagens_off = carregar_mensagens_offline(usuario)
                            for remetente, msg, timestamp in mensagens_off:
                                conexao.send((json.dumps({
                                    'tipo': 'mensagem', 'de': remetente, 'para': usuario,
                                    'conteudo': msg, 'timestamp': timestamp
                                }) + "\n").encode('utf-8'))

                            broadcast({'tipo': 'status', 'usuario': usuario, 'status': 'online'})
                        else:
                            print(f"Cliente enviou dados inválidos antes do login: {linha}. Desconectando.")
                            return 
                    except json.JSONDecodeError:
                        print(f"Cliente enviou JSON inválido antes do login: {linha}. Desconectando.")
                        return
                else:
                    lidar_com_mensagem(conexao, usuario, linha)

    except ConnectionResetError:
        print(f"Conexão com '{usuario or 'cliente desconhecido'}' foi redefinida.")
    except Exception as e:
        print(f"Erro inesperado na thread do cliente '{usuario}': {e}")
    finally:
        
        if usuario:
            remover_cliente(usuario)
        conexao.close()
        
print(f"Servidor iniciado em {HOST}:{PORTA}...")

while True:
    conexao_cliente, endereco = servidor_socket.accept()
    print(f"Nova conexão de {endereco}")
    thread = threading.Thread(target=lidar_com_cliente, args=(conexao_cliente,))
    thread.start()
