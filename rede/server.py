# import socket 
# import threading
# import json
# from datetime import datetime

# informações do host do server 
# conectar com o servidor e escutar clientes
# para cada cliente conectado ele cria uma thread dedicada
# a cada cliente que se conecta ele muda o status (online, offline) vê se tem mensagens que foram recebidas offline
# esses clientes precisam estar em um dicionário composto por nome e endereço, assim o usuario pode procurar e se conectar pela interface 
# o servidor precisa saber quando o usuario está digitando
# tratamento de erro para possíveis desconexões

# import socket
# import threading
# import json
# from datetime import datetime
# from banco_de_dados.database import listar_usuarios, salvar_mensagem_offline, carregar_mensagens_offline

# HOST = 'localhost'
# PORTA = 5000
# LOGIN_MARKER = ',entrou'
# LOGOUT_MARKER = ',saiu'

# servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# servidor_socket.bind((HOST, PORTA))
# servidor_socket.listen(10)

# clientes_conectados = {}


# def broadcast(mensagem, conexao_excluida=None):
#     mensagem_json = json.dumps(mensagem)
#     for usuario, dados_cliente in clientes_conectados.items():
#         if dados_cliente['conexao'] != conexao_excluida:
#             try:
#                 dados_cliente['conexao'].send(mensagem_json.encode('utf-8'))
#             except:
#                 remover_cliente(usuario)

# def remover_cliente(usuario):
#     if usuario in clientes_conectados:
#         try:
#             clientes_conectados[usuario]['conexao'].close()
#         except:
#             pass
#         del clientes_conectados[usuario]
        
#         # Notificar outros usuários
#         broadcast({
#             'tipo': 'status',
#             'usuario': usuario,
#             'status': 'offline',
#             'timestamp': datetime.now().isoformat()
#         })

# def lidar_com_mensagem(conexao, usuario, mensagem):
#     try:
#         dados = json.loads(mensagem)
        
#         if dados['tipo'] == 'mensagem':
#             destinatario = dados['para']
#             if destinatario in clientes_conectados:
            
#                 clientes_conectados[destinatario]['conexao'].send(mensagem.encode('utf-8'))
#             else:
            
#                 salvar_mensagem_offline(usuario, destinatario, dados['conteudo'])
                
#         elif dados['tipo'] == 'digitando':
#             destinatario = dados['para']
#             if destinatario in clientes_conectados:
#                 clientes_conectados[destinatario]['conexao'].send(mensagem.encode('utf-8'))
#         elif dados['tipo'] == 'solicitacao' and dados['acao'] == 'listar_usuarios':
#             usuarios = listar_usuarios()
#             resposta = {
#                 'tipo': 'lista_usuarios',
#                 'usuarios': {
#                     usuario: ('online' if usuario in clientes_conectados else 'offline')
#                     for usuario in usuarios
#                     if usuario != dados['usuario']
#                 }
            
#         }
#         print(resposta)
#         conexao.send(json.dumps(resposta).encode('utf-8'))
                
#     except json.JSONDecodeError:
#         print(f"Mensagem inválida de {usuario}: {mensagem}")

# def lidar_com_cliente(conexao):
#     usuario = None
#     try:
#         while True:
#             dados = conexao.recv(2048).decode('utf-8')
#             if not dados:
#                 break
                
#             if LOGIN_MARKER in dados:
#                 usuario = dados.split(LOGIN_MARKER)[0]
#                 clientes_conectados[usuario] = {'conexao': conexao, 'status': 'online'}
                
#                 # Enviar mensagens offline pendentes
#                 mensagens = carregar_mensagens_offline(usuario)
#                 for remetente, msg, timestamp in mensagens:
#                     conexao.send(json.dumps({
#                         'tipo': 'mensagem',
#                         'de': remetente,
#                         'para': usuario,
#                         'conteudo': msg,
#                         'timestamp': timestamp
#                     }).encode('utf-8'))
                
#                 broadcast({
#                     'tipo': 'status',
#                     'usuario': usuario,
#                     'status': 'online',
#                     'timestamp': datetime.now().isoformat()
#                 }, conexao)
                
#             elif LOGOUT_MARKER in dados:
                
#                 usuario = dados.split(LOGOUT_MARKER)[0]
#                 break
                
#             else:
#                 lidar_com_mensagem(conexao, usuario, dados)
                
#     except ConnectionResetError:
#         pass
#     finally:
#         if usuario:
#             remover_cliente(usuario)
#         conexao.close()

# print(f"Servidor iniciado em {HOST}:{PORTA}...")

# while True:
#     conexao_cliente, endereco = servidor_socket.accept()
#     print(f"Nova conexão de {endereco}")
#     thread = threading.Thread(target=lidar_com_cliente, args=(conexao_cliente,))
#     thread.start()

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

def broadcast(mensagem, conexao_excluida=None):
    mensagem_json = json.dumps(mensagem) + "\n"
    for usuario, dados_cliente in list(clientes_conectados.items()):
        if dados_cliente['conexao'] != conexao_excluida:
            try:
                dados_cliente['conexao'].send(mensagem_json.encode('utf-8'))
            except:
                remover_cliente(usuario)

def remover_cliente(usuario):
    if usuario in clientes_conectados:
        try:
            clientes_conectados[usuario]['conexao'].close()
        except:
            pass
        del clientes_conectados[usuario]
        broadcast({
            'tipo': 'status',
            'usuario': usuario,
            'status': 'offline',
            'timestamp': datetime.now().isoformat()
        })

def lidar_com_mensagem(conexao, usuario, mensagem):
    try:
        dados = json.loads(mensagem)
        
        if dados['tipo'] == 'mensagem':
            destinatario = dados['para']
            salvar_mensagem_historico(usuario, destinatario, dados['conteudo'], dados['timestamp'])
            if destinatario in clientes_conectados:
                clientes_conectados[destinatario]['conexao'].send((mensagem + "\n").encode('utf-8'))
            else:
                salvar_mensagem_offline(usuario, destinatario, dados['conteudo'])
                
        elif dados['tipo'] == 'digitando':
            destinatario = dados['para']
            if destinatario in clientes_conectados:
                clientes_conectados[destinatario]['conexao'].send((mensagem + "\n").encode('utf-8'))
        
        elif dados['tipo'] == 'solicitacao' and dados['acao'] == 'historico':
            mensagens = carregar_historico_conversa(dados['usuario'], dados['com'])
            for remetente, conteudo, timestamp in mensagens:
                conexao.send((json.dumps({
                    'tipo': 'mensagem',
                    'de': remetente,
                    'para': dados['usuario'],
                    'conteudo': conteudo,
                    'timestamp': timestamp
                }) + "\n").encode('utf-8'))

                
        elif dados['tipo'] == 'solicitacao' and dados['acao'] == 'listar_usuarios':
            usuarios = listar_usuarios()
            resposta = {
                'tipo': 'lista_usuarios',
                'usuarios': {
                    usuario: ('online' if usuario in clientes_conectados else 'offline')
                    for usuario in usuarios
                    if usuario != dados['usuario']
                }
            }
            conexao.send((json.dumps(resposta) + "\n").encode('utf-8'))
                
    except json.JSONDecodeError:
        print(f"Mensagem inválida de {usuario}: {mensagem}")

def lidar_com_cliente(conexao):
    usuario = None
    buffer = ""
    try:
        while True:
            dados = conexao.recv(2048).decode('utf-8')
            if not dados:
                break
            buffer += dados
            while '\n' in buffer:
                linha, buffer = buffer.split('\n', 1)
                if not linha.strip():
                    continue
                if LOGIN_MARKER in linha:
                    usuario = linha.split(LOGIN_MARKER)[0]
                    clientes_conectados[usuario] = {'conexao': conexao, 'status': 'online'}
                    
                    mensagens = carregar_mensagens_offline(usuario)
                    for remetente, msg, timestamp in mensagens:
                        conexao.send((json.dumps({
                            'tipo': 'mensagem',
                            'de': remetente,
                            'para': usuario,
                            'conteudo': msg,
                            'timestamp': timestamp
                        }) + "\n").encode('utf-8'))
                    
                    broadcast({
                        'tipo': 'status',
                        'usuario': usuario,
                        'status': 'online',
                        'timestamp': datetime.now().isoformat()
                    }, conexao)
                
                
                    for nome, dados in clientes_conectados.items():
                        try:
                            usuarios = listar_usuarios()
                            resposta = {
                                'tipo': 'lista_usuarios',
                                'usuarios': {
                                    u: ('online' if u in clientes_conectados else 'offline')
                                    for u in usuarios
                                    if u != nome
                                }
                            }
                            dados['conexao'].send((json.dumps(resposta) + "\n").encode('utf-8'))
                        except Exception as e:
                            print(f"Erro ao enviar lista atualizada para {nome}: {e}")
                
                    
                elif LOGOUT_MARKER in linha:
                    usuario = linha.split(LOGOUT_MARKER)[0]
                    break
                else:
                    lidar_com_mensagem(conexao, usuario, linha)
    except ConnectionResetError:
        pass
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
