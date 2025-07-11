import customtkinter as ctk
from PIL import Image
# Importe CTkImage para um melhor dimensionamento de imagem e para remover os avisos
from customtkinter import CTkImage 
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

    caminho_cursor = os.path.abspath("assets/cursor.cur").replace("\\", "/")
    chat.configure(cursor=f"@{caminho_cursor}")

    chat.timer_digitando = None

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

    barra_superior = ctk.CTkFrame(chat, height=40, fg_color=roxo)
    barra_superior.pack(side="top", fill="x")

    try:
        imagem_logo_ctk = CTkImage(
            light_image=Image.open("assets/chat_a_bit_logo.png"),
            dark_image=Image.open("assets/chat_a_bit_logo.png"),
            size=(70, 50)
        )
        label_logo = ctk.CTkLabel(barra_superior, image=imagem_logo_ctk, text="")
        label_logo.pack(side="left", padx=10, pady=5)
    except Exception as e:
        print(f"Erro ao carregar imagem do logo: {e}")

    ctk.CTkButton(barra_superior, text="Sair", width=70, height=30, fg_color=amarelo,
                  text_color=roxo, hover_color=rosa_escuro, command=fechar_janela).pack(side="right", padx=10, pady=5)

    ctk.CTkButton(barra_superior, text="Conta", width=70, height=30, fg_color=amarelo,
                  text_color=roxo, hover_color=rosa_escuro).pack(side="right", padx=10, pady=5)

    corpo = ctk.CTkFrame(chat, fg_color="transparent")
    corpo.pack(fill="both", expand=True)

    barra_lateral = ctk.CTkFrame(corpo, width=250, fg_color=rosa_escuro)
    barra_lateral.pack(side="left", fill="y")

    entrada_busca = ctk.CTkEntry(barra_lateral, placeholder_text="Procurar usuário...", height=30)
    entrada_busca.pack(padx=10, pady=10, fill="x")

    lista_usuarios = ctk.CTkScrollableFrame(barra_lateral, fg_color="#F6C6FA")
    lista_usuarios.pack(padx=10, pady=(0, 10), fill="both", expand=True)

    frame_chat = ctk.CTkFrame(corpo, fg_color="#1e1e1e")
    frame_chat.pack(side="left", fill="both", expand=True)

    mensagens_frame = ctk.CTkScrollableFrame(frame_chat, fg_color="#2e2e2e")
    mensagens_frame.pack(padx=10, pady=(10, 5), fill="both", expand=True)

    indicador_digitando_label = ctk.CTkLabel(frame_chat, text="", font=ctk.CTkFont(size=12, slant="italic"))
    indicador_digitando_label.pack(side="bottom", anchor="w", padx=10)

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

    def tratar_desconexao_inesperada():
        """Callback para quando o servidor cai. Alerta o usuário e desabilita a UI."""
        alerta_personalizado("Conexão Perdida", "A conexão com o servidor foi encerrada.")
        entrada_mensagem.configure(state="disabled")
        # O último widget no frame inferior é o botão "Enviar"
        campo_inferior.winfo_children()[-1].configure(state="disabled")

    def limpar_mensagens():
        """Remove todas as mensagens da tela para carregar um novo histórico."""
        for widget in mensagens_frame.winfo_children():
            widget.destroy()

    def mostrar_indicador_digitando(remetente):
        """Mostra o indicador 'digitando...' e o esconde após um tempo."""
        if chat.timer_digitando:
            chat.after_cancel(chat.timer_digitando)
        
        indicador_digitando_label.configure(text=f"{remetente} está digitando...")
        
        chat.timer_digitando = chat.after(2000, lambda: indicador_digitando_label.configure(text=""))

    def exibir_mensagem(remetente, conteudo, timestamp):
        """Exibe uma única mensagem na tela, formatada para o remetente ou destinatário."""
        def atualizar():
            try:
                hora = datetime.fromisoformat(timestamp).strftime("%H:%M")
            except (ValueError, TypeError):
                hora = "agora" # Fallback para timestamps inválidos

            frame_msg = ctk.CTkFrame(mensagens_frame, fg_color="transparent")
            
            if remetente == usuario:
                frame_msg.pack(anchor="e", pady=2, padx=(50, 5))
                texto = f"{conteudo} ({hora})"
                label = ctk.CTkLabel(frame_msg, text=texto, wraplength=400,
                                     justify="right", fg_color=roxo, corner_radius=10,
                                     text_color="white", padx=10, pady=5)
                label.pack(side="right")
            else:
                frame_msg.pack(anchor="w", pady=2, padx=(5, 50))
                texto = f"{remetente}: {conteudo} ({hora})"
                label = ctk.CTkLabel(frame_msg, text=texto, wraplength=400,
                                     justify="left", fg_color="#3A3A3A", corner_radius=10,
                                     text_color="white", padx=10, pady=5)
                label.pack(side="left")
            
            # Força a rolagem para o final para ver a mensagem mais recente
            mensagens_frame._parent_canvas.yview_moveto(1.0)
        
        chat.after(0, atualizar)

    def atualizar_status_usuario(usuario_nome, status):
        """Atualiza o ícone de status (online/offline) de um usuário na lista."""
        for widget in lista_usuarios.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                # O botão é o primeiro filho do frame da linha
                btn = widget.winfo_children()[0]
                if isinstance(btn, ctk.CTkButton) and btn.cget("text") == usuario_nome:
                    # O label de status é o segundo filho
                    status_label = widget.winfo_children()[1]
                    status_label.configure(text_color="#227522" if status == "online" else "#B31B1B")
                    break

    def atualizar_lista_usuarios(lista):
        """Reconstrói a lista de usuários na barra lateral."""
        limpar_mensagens() # Limpa a conversa atual ao atualizar a lista
        for widget in lista_usuarios.winfo_children():
            widget.destroy()

        for nome, status in lista.items():
            if nome == usuario:
                continue
            
            status_cor = "#227522" if status == "online" else "#B31B1B"
            linha = ctk.CTkFrame(lista_usuarios, fg_color="transparent")
            linha.pack(fill="x", pady=2)
            
            btn = ctk.CTkButton(linha, text=nome, text_color=roxo, anchor="w",
                                fg_color="transparent", hover_color="#E8A0F0",
                                command=lambda n=nome: cliente.selecionar_destinatario(n))
            btn.pack(side="left", padx=5, fill="x", expand=True)
            
            ctk.CTkLabel(linha, text="•", text_color=status_cor,
                         font=ctk.CTkFont(size=24)).pack(side="right", padx=5)

    # Botão de Enviar
    ctk.CTkButton(campo_inferior, text="Enviar", fg_color=amarelo,
                  text_color=roxo, hover_color=roxo, width=100,
                  command=enviar_mensagem).pack(side="right")
    
    entrada_mensagem.bind("<Return>", lambda event: enviar_mensagem())
    
    entrada_mensagem.bind("<KeyRelease>", lambda event: cliente.enviar_status_digitando())

    chat.exibir_mensagem = exibir_mensagem
    chat.atualizar_status_usuario = atualizar_status_usuario
    chat.atualizar_lista_usuarios = atualizar_lista_usuarios
    chat.limpar_mensagens = limpar_mensagens
    chat.mostrar_indicador_digitando = mostrar_indicador_digitando
    chat.tratar_desconexao_inesperada = tratar_desconexao_inesperada
    
    cliente.solicitar_lista_usuarios()
    chat.after(100, lambda: entrada_mensagem.focus_set())