# import socket
# import threading
# import json
# from datetime import datetime
# from banco_de_dados.database import listar_usuarios
# from utils.mensagens import alerta_personalizado

# HOST = 'localhost'
# PORT = 5000
# LOGIN_MARKER = ',entrou'
# LOGOUT_MARKER = ',saiu'

# class ChatClient:
#     def __init__(self, usuario, interface):
#         self.usuario = usuario
#         self.interface = interface
#         self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.conectado = False
#         self.destinatario_atual = None

#     def conectar(self):
#         try:
#             self.socket.connect((HOST, PORT))
#             self.socket.send(f"{self.usuario}{LOGIN_MARKER}".encode('utf-8'))
#             self.conectado = True
#             threading.Thread(target=self.receber_mensagens, daemon=True).start()
#             return True
#         except Exception as e:
#             print(f"Erro ao conectar: {e}")
#             return False

#     def solicitar_lista_usuarios(self):
#         if self.conectado:
#             mensagem = {
#                 'tipo': 'solicitacao',
#                 'acao': 'listar_usuarios',
#                 'usuario': self.usuario
#             }
#             try:
#                 self.socket.send(json.dumps(mensagem).encode('utf-8'))
#             except:
#                 pass

#     def receber_mensagens(self):
#         while self.conectado:
#             try:
#                 dados = self.socket.recv(2048).decode('utf-8')
#                 if not dados:
#                     break
#                 mensagem = json.loads(dados)
#                 self.processar_mensagem(mensagem)
#             except Exception as e:
#                 print(f"Erro ao receber mensagem: {e}")
#                 break

#     def processar_mensagem(self, mensagem):
#         if mensagem['tipo'] == 'mensagem':
#             self.interface.exibir_mensagem(
#                 mensagem['de'], mensagem['conteudo'], mensagem['timestamp'])
#         elif mensagem['tipo'] == 'status':
#             self.interface.atualizar_status_usuario(
#                 mensagem['usuario'], mensagem['status'])
#         elif mensagem['tipo'] == 'lista_usuarios':
#             self.interface.atualizar_lista_usuarios(mensagem['usuarios'])

#     def enviar_mensagem(self, destinatario, conteudo):
#         if not self.conectado:
#             alerta_personalizado("Erro", "Não conectado ao servidor")
#             return
#         mensagem = {
#             'tipo': 'mensagem',
#             'de': self.usuario,
#             'para': destinatario,
#             'conteudo': conteudo,
#             'timestamp': datetime.now().isoformat()
#         }
#         try:
#             self.socket.send(json.dumps(mensagem).encode('utf-8'))
#             self.interface.exibir_mensagem(self.usuario, conteudo, mensagem['timestamp'])
#         except Exception as e:
#             print(f"Erro ao enviar mensagem: {e}")

#     def selecionar_destinatario(self, nome):
#         self.destinatario_atual = nome

#     def desconectar(self):
#         if self.conectado:
#             try:
#                 self.socket.send(f"{self.usuario}{LOGOUT_MARKER}".encode('utf-8'))
#                 self.socket.close()
#             except:
#                 pass
#             self.conectado = False

import socket
import threading
import json
from datetime import datetime
from banco_de_dados.database import listar_usuarios
from utils.mensagens import alerta_personalizado

HOST = 'localhost'
PORT = 5000
LOGIN_MARKER = ',entrou'
LOGOUT_MARKER = ',saiu'

class ChatClient:
    def __init__(self, usuario, interface):
        self.usuario = usuario
        self.interface = interface
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conectado = False
        self.destinatario_atual = None
        self.buffer = ""

    def conectar(self):
        try:
            self.socket.connect((HOST, PORT))
            self.socket.send(f"{self.usuario}{LOGIN_MARKER}\n".encode('utf-8'))  # \n para login
            self.conectado = True
            threading.Thread(target=self.receber_mensagens, daemon=True).start()
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False

    def solicitar_lista_usuarios(self):
        if self.conectado:
            mensagem = {
                'tipo': 'solicitacao',
                'acao': 'listar_usuarios',
                'usuario': self.usuario
            }
            try:
                self.socket.send((json.dumps(mensagem) + "\n").encode('utf-8'))
            except:
                pass

    def receber_mensagens(self):
        buffer = ""
        while self.conectado:
            try:
                dados = self.socket.recv(2048).decode('utf-8')
                if not dados:
                    break
                buffer += dados
                while '\n' in buffer:
                    linha, buffer = buffer.split('\n', 1)
                    if not linha.strip():
                        continue
                    mensagem = json.loads(linha)
                    self.processar_mensagem(mensagem)
            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")
                break

    def processar_mensagem(self, mensagem):
        if mensagem['tipo'] == 'mensagem':
            self.interface.exibir_mensagem(
                mensagem['de'], mensagem['conteudo'], mensagem['timestamp'])
        elif mensagem['tipo'] == 'status':
            self.interface.atualizar_status_usuario(
                mensagem['usuario'], mensagem['status'])
            # self.solicitar_lista_usuarios()
        elif mensagem['tipo'] == 'lista_usuarios':
            self.interface.atualizar_lista_usuarios(mensagem['usuarios'])

    def enviar_mensagem(self, destinatario, conteudo):
        if not self.conectado:
            alerta_personalizado("Erro", "Não conectado ao servidor")
            return
        mensagem = {
            'tipo': 'mensagem',
            'de': self.usuario,
            'para': destinatario,
            'conteudo': conteudo,
            'timestamp': datetime.now().isoformat()
        }
        try:
            self.socket.send((json.dumps(mensagem) + "\n").encode('utf-8'))
            self.interface.exibir_mensagem(self.usuario, conteudo, mensagem['timestamp'])
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")

    def selecionar_destinatario(self, nome):
        if nome == self.destinatario_atual:
           return
       
        if self.conectado:
            mensagem = {
                'tipo': 'solicitacao',
                'acao': 'historico',
                'usuario': self.usuario,
                'com': nome
            }
            try:
                self.socket.send((json.dumps(mensagem) + "\n").encode('utf-8'))
            except:
                pass

    def desconectar(self):
        if self.conectado:
            try:
                self.socket.send(f"{self.usuario}{LOGOUT_MARKER}\n".encode('utf-8'))
                self.socket.close()
            except:
                pass
            self.conectado = False
