import socket
import threading
import json
from datetime import datetime
from utils.mensagens import alerta_personalizado

HOST = 'localhost'
PORT = 5000

class ChatClient:
    def __init__(self, usuario, interface):
        self.usuario = usuario
        self.interface = interface
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conectado = False
        self.destinatario_atual = None
    
    def conectar(self):
        try:
            self.socket.connect((HOST, PORT))
            login_msg = {'tipo': 'login', 'usuario': self.usuario}
            self.socket.send((json.dumps(login_msg) + "\n").encode('utf-8'))
            self.conectado = True
            
            thread_recebimento = threading.Thread(target=self.receber_mensagens, daemon=True)
            thread_recebimento.start()
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False

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

            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
                print(f"Conexão perdida com o servidor: {e}")
                break
            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON: {e} - Dados recebidos: '{linha}'")
                continue
            except Exception as e:
                print(f"Erro inesperado ao receber mensagem: {e}")
                break
        
        if self.conectado:
            print("Notificando a interface sobre a desconexão inesperada.")
            self.interface.after(0, self.interface.tratar_desconexao_inesperada)
        
        self.conectado = False
        print("Thread de recebimento de mensagens encerrada.")

    def processar_mensagem(self, mensagem):
        tipo_msg = mensagem.get('tipo')
        
        if tipo_msg == 'mensagem':
            remetente = mensagem.get('de')
            if remetente == self.destinatario_atual or remetente == self.usuario:
                self.interface.exibir_mensagem(
                    mensagem.get('de'), mensagem.get('conteudo'), mensagem.get('timestamp')
                )
        
        elif tipo_msg == 'status':
            self.interface.atualizar_status_usuario(mensagem.get('usuario'), mensagem.get('status'))
        
        elif tipo_msg == 'lista_usuarios':
            self.interface.atualizar_lista_usuarios(mensagem.get('usuarios'))
        
        elif tipo_msg == 'historico_conversa':
            for msg in mensagem.get('mensagens', []):
                self.interface.exibir_mensagem(msg['remetente'], msg['conteudo'], msg['timestamp'])

        elif tipo_msg == 'digitando':
            remetente = mensagem.get('de')
            if remetente == self.destinatario_atual:
                self.interface.after(0, lambda r=remetente: self.interface.mostrar_indicador_digitando(r))

    def enviar_mensagem(self, destinatario, conteudo):
        if not self.conectado:
            alerta_personalizado("Erro", "Não conectado ao servidor")
            return
            
        timestamp_atual = datetime.now().isoformat()
        mensagem = {
            'tipo': 'mensagem', 'de': self.usuario, 'para': destinatario,
            'conteudo': conteudo, 'timestamp': timestamp_atual
        }
        try:
            self.socket.send((json.dumps(mensagem) + "\n").encode('utf-8'))
            self.interface.exibir_mensagem(self.usuario, conteudo, timestamp_atual)
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")

    def selecionar_destinatario(self, nome):
        if nome == self.destinatario_atual:
            return

        self.destinatario_atual = nome
        self.interface.after(0, self.interface.limpar_mensagens)
        
        if self.conectado:
            mensagem = {
                'tipo': 'solicitacao', 'acao': 'historico',
                'usuario': self.usuario, 'com': nome
            }
            try:
                self.socket.send((json.dumps(mensagem) + "\n").encode('utf-8'))
            except Exception as e:
                print(f"Erro ao solicitar histórico: {e}")

    def solicitar_lista_usuarios(self):
        if self.conectado:
            mensagem = {
                'tipo': 'solicitacao', 'acao': 'listar_usuarios', 'usuario': self.usuario
            }
            try:
                self.socket.send((json.dumps(mensagem) + "\n").encode('utf-8'))
            except Exception as e:
                print(f"Erro ao solicitar lista de usuários: {e}")

    def enviar_status_digitando(self):
        if not self.conectado or not self.destinatario_atual:
            return
        
        mensagem = {
            'tipo': 'digitando', 'de': self.usuario, 'para': self.destinatario_atual
        }
        try:
            self.socket.send((json.dumps(mensagem) + "\n").encode('utf-8'))
        except Exception as e:
            print(f"Erro ao enviar status 'digitando': {e}")

    def desconectar(self):
        if self.conectado:
            self.conectado = False
            try:
                logout_msg = {'tipo': 'logout'}
                self.socket.send((json.dumps(logout_msg) + "\n").encode('utf-8'))
                self.socket.shutdown(socket.SHUT_RDWR)
            except Exception as e:
                print(f"Erro ao enviar logout (socket já fechado?): {e}")
            finally:
                self.socket.close()