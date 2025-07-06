# import customtkinter as ctk
# from PIL import Image, ImageTk
# import os

# def abrir_chat(app, usuario):
#     amarelo = "#ffdf61"
#     roxo = "#402456"
#     rosa_escuro = "#b20f55"

#     chat = ctk.CTkToplevel(app)
#     chat.title("Chat a Bit")
#     chat.geometry("1000x700")

#     caminho_cursor = os.path.abspath("assets/cursor.cur").replace("\\", "/")
#     chat.configure(cursor=f"@{caminho_cursor}")

#     barra_superior = ctk.CTkFrame(chat, height=40, fg_color=roxo)
#     barra_superior.pack(side="top", fill="x")

#     imagem_logo = Image.open("assets/chat_a_bit_logo.png")
#     imagem_logo_pequena = imagem_logo.resize((70, 50))
#     imagem_logo_tk = ImageTk.PhotoImage(imagem_logo_pequena)

#     label_logo = ctk.CTkLabel(barra_superior, image=imagem_logo_tk, text="")
#     label_logo.image = imagem_logo_tk 
#     label_logo.pack(side="left", padx=10, pady=5)

#     ctk.CTkButton(barra_superior, text="Sair", width=70, height=30, fg_color=amarelo,
#                 text_color=roxo, hover_color=rosa_escuro).pack(side="right", padx=10, pady=5)
    
#     ctk.CTkButton(barra_superior, text="Conta", width=70, height=30, fg_color=amarelo,
#                 text_color=roxo, hover_color=rosa_escuro).pack(side="right", padx=10, pady=5)


#     corpo = ctk.CTkFrame(chat, fg_color="transparent")
#     corpo.pack(fill="both", expand=True)

#     barra_lateral = ctk.CTkFrame(corpo, width=250, fg_color=rosa_escuro)
#     barra_lateral.pack(side="left", fill="y")
#     ctk.CTkEntry(barra_lateral, placeholder_text="Procurar usuário...", height=30).pack(padx=10, pady=10, fill="x")

#     lista_usuarios = ctk.CTkScrollableFrame(barra_lateral, fg_color="#F6C6FA")
#     lista_usuarios.pack(padx=10, pady=(0, 10), fill="both", expand=True)

#     for nome, status in [("maria", True), ("joao", False), ("ana", True)]:
#         status_cor = "#227522" if status else "#B31B1B"
#         linha = ctk.CTkFrame(lista_usuarios, fg_color="transparent")
#         linha.pack(fill="x", pady=5)
#         ctk.CTkLabel(linha, text=nome, text_color=roxo, anchor="w").pack(side="left", padx=5)
#         ctk.CTkLabel(linha, text="•", text_color=status_cor, font=ctk.CTkFont(size=24)).pack(side="right", padx=5)
    
#     frame_chat = ctk.CTkFrame(corpo, fg_color="#1e1e1e")
#     frame_chat.pack(side="left", fill="both", expand=True)

#     mensagens_frame = ctk.CTkScrollableFrame(frame_chat, fg_color="#2e2e2e")
#     mensagens_frame.pack(padx=10, pady=(10, 5), fill="both", expand=True)
#     ctk.CTkLabel(mensagens_frame, text=f"", anchor="w").pack(fill="x", padx=5, pady=2)

#     campo_inferior = ctk.CTkFrame(frame_chat, fg_color="transparent")
#     campo_inferior.pack(padx=10, pady=10, fill="x")
#     ctk.CTkEntry(campo_inferior, placeholder_text="Digite sua mensagem...", height=35).pack(side="left", fill="x", expand=True, padx=(0, 10))
#     ctk.CTkButton(campo_inferior, text="Enviar", fg_color=amarelo, text_color=roxo,
#                   hover_color=roxo, width=100).pack(side="right")

import customtkinter as ctk
from PIL import Image, ImageTk
import os
from datetime import datetime
from rede.client import ChatClient
from utils.mensagens import alerta_personalizado


def abrir_chat(app, usuario):
    amarelo = "#ffdf61"
    roxo = "#402456"
    rosa_escuro = "#b20f55"

    chat = ctk.CTkToplevel(app)
    chat.title(f"Chat a Bit - {usuario}")
    chat.geometry("1000x700")
    chat.resizable(False, False)

    # Cursor personalizado
    caminho_cursor = os.path.abspath("assets/cursor.cur").replace("\\", "/")
    chat.configure(cursor=f"@{caminho_cursor}")

    # Variáveis de estado
    chat.mensagens_widgets = []
    chat.status_usuarios = {}

    # Conecta lógica do cliente
    cliente = ChatClient(usuario, chat)
    chat.cliente = cliente

    if not cliente.conectar():
        alerta_personalizado("Erro", "Não foi possível conectar ao servidor.")
        chat.destroy()
        return

    def fechar_janela():
        cliente.desconectar()
        chat.destroy()

    chat.protocol("WM_DELETE_WINDOW", fechar_janela)

    # Topo
    barra_superior = ctk.CTkFrame(chat, height=40, fg_color=roxo)
    barra_superior.pack(side="top", fill="x")

    try:
        imagem_logo = Image.open("assets/chat_a_bit_logo.png")
        imagem_logo_pequena = imagem_logo.resize((70, 50))
        imagem_logo_tk = ImageTk.PhotoImage(imagem_logo_pequena)
        label_logo = ctk.CTkLabel(barra_superior, image=imagem_logo_tk, text="")
        label_logo.image = imagem_logo_tk
        label_logo.pack(side="left", padx=10, pady=5)
    except:
        pass

    ctk.CTkButton(barra_superior, text="Sair", width=70, height=30, fg_color=amarelo,
                  text_color=roxo, hover_color=rosa_escuro, command=fechar_janela).pack(side="right", padx=10, pady=5)

    ctk.CTkButton(barra_superior, text="Conta", width=70, height=30, fg_color=amarelo,
                  text_color=roxo, hover_color=rosa_escuro).pack(side="right", padx=10, pady=5)

    corpo = ctk.CTkFrame(chat, fg_color="transparent")
    corpo.pack(fill="both", expand=True)

    # Barra lateral
    barra_lateral = ctk.CTkFrame(corpo, width=250, fg_color=rosa_escuro)
    barra_lateral.pack(side="left", fill="y")

    entrada_busca = ctk.CTkEntry(barra_lateral, placeholder_text="Procurar usuário...", height=30)
    entrada_busca.pack(padx=10, pady=10, fill="x")

    lista_usuarios = ctk.CTkScrollableFrame(barra_lateral, fg_color="#F6C6FA")
    lista_usuarios.pack(padx=10, pady=(0, 10), fill="both", expand=True)

    # Área de conversa
    frame_chat = ctk.CTkFrame(corpo, fg_color="#1e1e1e")
    frame_chat.pack(side="left", fill="both", expand=True)

    mensagens_frame = ctk.CTkScrollableFrame(frame_chat, fg_color="#2e2e2e")
    mensagens_frame.pack(padx=10, pady=(10, 5), fill="both", expand=True)

    campo_inferior = ctk.CTkFrame(frame_chat, fg_color="transparent")
    campo_inferior.pack(padx=10, pady=10, fill="x")

    entrada_mensagem = ctk.CTkEntry(campo_inferior, placeholder_text="Digite sua mensagem...", height=35)
    entrada_mensagem.pack(side="left", fill="x", expand=True, padx=(0, 10))

    def enviar_mensagem():
        mensagem = entrada_mensagem.get().strip()
        if not cliente.destinatario_atual:
            alerta_personalizado("Aviso", "Selecione um usuário para conversar")
            return
        if mensagem:
            cliente.enviar_mensagem(cliente.destinatario_atual, mensagem)
            entrada_mensagem.delete(0, 'end')

    ctk.CTkButton(campo_inferior, text="Enviar", fg_color=amarelo,
                  text_color=roxo, hover_color=roxo, width=100,
                  command=enviar_mensagem).pack(side="right")

    entrada_mensagem.bind("<Return>", lambda event: enviar_mensagem())

    # Métodos chamados pelo cliente
    # def exibir_mensagem(remetente, conteudo, timestamp):
    #     hora = datetime.fromisoformat(timestamp).strftime("%H:%M")
    #     frame_msg = ctk.CTkFrame(mensagens_frame, fg_color="transparent")
    #     if remetente == usuario:
    #         frame_msg.pack(anchor="e", pady=2)
    #         texto = f"{conteudo} ({hora})"
    #         label = ctk.CTkLabel(frame_msg, text=texto, wraplength=400,
    #                               justify="right", fg_color=roxo, corner_radius=10,
    #                               text_color="white", padx=10, pady=5)
    #         label.pack(side="right")
    #     else:
    #         frame_msg.pack(anchor="w", pady=2)
    #         texto = f"{remetente}: {conteudo} ({hora})"
    #         label = ctk.CTkLabel(frame_msg, text=texto, wraplength=400,
    #                               justify="left", fg_color="#3A3A3A", corner_radius=10,
    #                               text_color="white", padx=10, pady=5)
    #         label.pack(side="left")
    #     mensagens_frame._parent_canvas.yview_moveto(1.0)

    def exibir_mensagem(remetente, conteudo, timestamp):
        def atualizar():
            hora = datetime.fromisoformat(timestamp).strftime("%H:%M")
            frame_msg = ctk.CTkFrame(mensagens_frame, fg_color="transparent")
            if remetente == usuario:
                frame_msg.pack(anchor="e", pady=2)
                texto = f"{conteudo} ({hora})"
                label = ctk.CTkLabel(frame_msg, text=texto, wraplength=400,
                                    justify="right", fg_color=roxo, corner_radius=10,
                                    text_color="white", padx=10, pady=5)
                label.pack(side="right")
            else:
                frame_msg.pack(anchor="w", pady=2)
                texto = f"{remetente}: {conteudo} ({hora})"
                label = ctk.CTkLabel(frame_msg, text=texto, wraplength=400,
                                    justify="left", fg_color="#3A3A3A", corner_radius=10,
                                    text_color="white", padx=10, pady=5)
                label.pack(side="left")
            mensagens_frame._parent_canvas.yview_moveto(1.0)
        chat.after(0, atualizar)

    def atualizar_status_usuario(usuario_nome, status):
        chat.status_usuarios[usuario_nome] = status
        for widget in lista_usuarios.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkButton) and child.cget("text") == usuario_nome:
                        for sibling in widget.winfo_children():
                            if isinstance(sibling, ctk.CTkLabel) and sibling.cget("text") == "•":
                                sibling.configure(text_color="#227522" if status == "online" else "#B31B1B")

    def atualizar_lista_usuarios(lista):
        for widget in lista_usuarios.winfo_children():
            widget.destroy()
        for nome, status in lista.items():
            if nome == usuario:
                continue
            status_cor = "#227522" if status == "online" else "#B31B1B"
            linha = ctk.CTkFrame(lista_usuarios, fg_color="transparent")
            linha.pack(fill="x", pady=5)
            btn = ctk.CTkButton(linha, text=nome, text_color=roxo, anchor="w",
                                fg_color="transparent", hover_color="#E8A0F0",
                                command=lambda n=nome: cliente.selecionar_destinatario(n))
            btn.pack(side="left", padx=5, fill="x", expand=True)
            ctk.CTkLabel(linha, text="•", text_color=status_cor,
                         font=ctk.CTkFont(size=24)).pack(side="right", padx=5)

    # Disponibiliza os métodos para o cliente
    chat.exibir_mensagem = exibir_mensagem
    chat.atualizar_status_usuario = atualizar_status_usuario
    chat.atualizar_lista_usuarios = atualizar_lista_usuarios

    # Solicita a lista de usuários
    cliente.solicitar_lista_usuarios()

    chat.after(100, lambda: entrada_mensagem.focus_set())
