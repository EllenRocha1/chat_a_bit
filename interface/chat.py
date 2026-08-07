import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage 
from datetime import datetime
from rede.client import ChatClient
from utils.mensagens import alerta_personalizado
from utils.path import resource_path
from utils.theme import get_colors, toggle_theme, register_theme_callback, unregister_theme_callback

def abrir_chat(app, usuario):
    chat = ctk.CTkToplevel(app)
    chat.title(f"Chat a Bit - {usuario}")
    chat.geometry("1000x700")
    chat.resizable(False, False)

    caminho_cursor = resource_path("assets/cursor.cur").replace("\\", "/")
    chat.configure(cursor=f"@{caminho_cursor}")

    chat.timer_digitando = None

    cliente = ChatClient(usuario, chat)
    chat.cliente = cliente

    if not cliente.conectar():
        alerta_personalizado("Erro", "Não foi possível conectar ao servidor.")
        chat.destroy()
        return

    def fechar_janela():
        unregister_theme_callback(atualizar_cores_chat)
        cliente.desconectar()
        chat.destroy()

    chat.protocol("WM_DELETE_WINDOW", fechar_janela)

    c = get_colors()
    
    barra_superior = ctk.CTkFrame(chat, height=40, fg_color=c["primary"])
    barra_superior.pack(side="top", fill="x")

    try:
        imagem_logo_ctk = CTkImage(
            light_image=Image.open(resource_path("assets/chat_a_bit_logo.png")),
            dark_image=Image.open(resource_path("assets/chat_a_bit_logo.png")),
            size=(70, 50)
        )
        label_logo = ctk.CTkLabel(barra_superior, image=imagem_logo_ctk, text="")
        label_logo.pack(side="left", padx=10, pady=5)
    except Exception as e:
        print(f"Erro ao carregar imagem do logo: {e}")

    btn_sair = ctk.CTkButton(barra_superior, text="Sair", width=70, height=30, fg_color=c["tertiary"],
                  text_color=c["primary"], hover_color=c["secondary"], command=fechar_janela)
    btn_sair.pack(side="right", padx=10, pady=5)
    
    btn_tema = ctk.CTkButton(barra_superior, text="Tema", width=70, height=30, command=toggle_theme)
    btn_tema.pack(side="right", padx=10, pady=5)

    corpo = ctk.CTkFrame(chat, fg_color="transparent")
    corpo.pack(fill="both", expand=True)

    barra_lateral = ctk.CTkFrame(corpo, width=250, fg_color=c["secondary"])
    barra_lateral.pack(side="left", fill="y")

    entrada_busca = ctk.CTkEntry(barra_lateral, placeholder_text="Procurar usuário...", height=30)
    entrada_busca.pack(padx=10, pady=10, fill="x")

    lista_usuarios = ctk.CTkScrollableFrame(barra_lateral, fg_color=c["user_list_bg"])
    lista_usuarios.pack(padx=10, pady=(0, 10), fill="both", expand=True)

    frame_chat = ctk.CTkFrame(corpo, fg_color=c["bg"])
    frame_chat.pack(side="left", fill="both", expand=True)

    mensagens_frame = ctk.CTkScrollableFrame(frame_chat, fg_color=c["bg_frame"])
    mensagens_frame.pack(padx=10, pady=(10, 5), fill="both", expand=True)

    indicador_digitando_label = ctk.CTkLabel(frame_chat, text="", font=ctk.CTkFont(size=12, slant="italic"))
    indicador_digitando_label.pack(side="bottom", anchor="w", padx=10)

    campo_inferior = ctk.CTkFrame(frame_chat, fg_color="transparent")
    campo_inferior.pack(padx=10, pady=10, fill="x")

    entrada_mensagem = ctk.CTkEntry(campo_inferior, placeholder_text="Digite sua mensagem...", height=35)
    entrada_mensagem.pack(side="left", fill="x", expand=True, padx=(0, 10))

    btn_enviar = ctk.CTkButton(campo_inferior, text="Enviar", fg_color=c["tertiary"],
                  text_color=c["primary"], hover_color=c["primary"], width=100)
    btn_enviar.pack(side="right")
    
    # Lista de bolhas para atualizar
    bolhas_mensagens = []
    
    def atualizar_cores_chat():
        cores = get_colors()
        chat.configure(fg_color=cores["bg"])
        barra_superior.configure(fg_color=cores["primary"])
        btn_sair.configure(fg_color=cores["tertiary"], text_color=cores["primary"], hover_color=cores["secondary"])
        btn_tema.configure(fg_color=cores["tertiary"], text_color=cores["primary"], hover_color=cores["secondary"])
        barra_lateral.configure(fg_color=cores["secondary"])
        lista_usuarios.configure(fg_color=cores["user_list_bg"])
        frame_chat.configure(fg_color=cores["bg"])
        mensagens_frame.configure(fg_color=cores["bg_frame"])
        btn_enviar.configure(fg_color=cores["tertiary"], text_color=cores["primary"], hover_color=cores["primary"])
        indicador_digitando_label.configure(text_color=cores["text_secondary"])
        
        # update bolhas
        for (label, eh_remetente) in bolhas_mensagens:
            if eh_remetente:
                label.configure(fg_color=cores["primary"], text_color="#FFFFFF")
            else:
                label.configure(fg_color=cores["message_bg"], text_color=cores["text"])
                
        # update users
        if hasattr(cliente, 'lista_usuarios_conhecidos'):
            atualizar_lista_usuarios(cliente.lista_usuarios_conhecidos)

    register_theme_callback(atualizar_cores_chat)

    def enviar_mensagem():
        mensagem = entrada_mensagem.get().strip()
        if not cliente.destinatario_atual:
            alerta_personalizado("Aviso", "Selecione um usuário para conversar")
            return
        if mensagem:
            cliente.enviar_mensagem(cliente.destinatario_atual, mensagem)
            entrada_mensagem.delete(0, 'end')
            
    btn_enviar.configure(command=enviar_mensagem)

    def tratar_desconexao_inesperada():
        alerta_personalizado("Conexão Perdida", "A conexão com o servidor foi encerrada.")
        entrada_mensagem.configure(state="disabled")
        btn_enviar.configure(state="disabled")

    def limpar_mensagens():
        for widget in mensagens_frame.winfo_children():
            widget.destroy()
        bolhas_mensagens.clear()

    def mostrar_indicador_digitando(remetente):
        if chat.timer_digitando:
            chat.after_cancel(chat.timer_digitando)
        indicador_digitando_label.configure(text=f"{remetente} está digitando...")
        chat.timer_digitando = chat.after(2000, lambda: indicador_digitando_label.configure(text=""))

    def exibir_mensagem(remetente, conteudo, timestamp):
        def atualizar():
            try:
                hora = datetime.fromisoformat(timestamp).strftime("%H:%M")
            except (ValueError, TypeError):
                hora = "agora"

            cores = get_colors()
            frame_msg = ctk.CTkFrame(mensagens_frame, fg_color="transparent")
            
            eh_remetente = (remetente == usuario)
            
            if eh_remetente:
                frame_msg.pack(anchor="e", pady=2, padx=(50, 5))
                texto = f"{conteudo} ({hora})"
                label = ctk.CTkLabel(frame_msg, text=texto, wraplength=400,
                                     justify="right", fg_color=cores["primary"], corner_radius=10,
                                     text_color="white", padx=10, pady=5)
                label.pack(side="right")
            else:
                frame_msg.pack(anchor="w", pady=2, padx=(5, 50))
                texto = f"{remetente}: {conteudo} ({hora})"
                label = ctk.CTkLabel(frame_msg, text=texto, wraplength=400,
                                     justify="left", fg_color=cores["message_bg"], corner_radius=10,
                                     text_color=cores["text"], padx=10, pady=5)
                label.pack(side="left")
            
            bolhas_mensagens.append((label, eh_remetente))
            mensagens_frame._parent_canvas.yview_moveto(1.0)
        
        chat.after(0, atualizar)

    def atualizar_status_usuario(usuario_nome, status):
        cores = get_colors()
        cor_status = cores["status_online"] if status == "online" else cores["status_offline"]
        for widget in lista_usuarios.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                btn = widget.winfo_children()[0]
                if isinstance(btn, ctk.CTkButton) and btn.cget("text") == usuario_nome:
                    status_label = widget.winfo_children()[1]
                    status_label.configure(text_color=cor_status)
                    break

    def atualizar_lista_usuarios(lista):
        if not hasattr(cliente, 'lista_usuarios_conhecidos'):
            cliente.lista_usuarios_conhecidos = lista
        else:
            cliente.lista_usuarios_conhecidos.update(lista)
            
        limpar_mensagens()
        for widget in lista_usuarios.winfo_children():
            widget.destroy()

        cores = get_colors()
        for nome, status in lista.items():
            if nome == usuario:
                continue
            
            status_cor = cores["status_online"] if status == "online" else cores["status_offline"]
            linha = ctk.CTkFrame(lista_usuarios, fg_color="transparent")
            linha.pack(fill="x", pady=2)
            
            btn = ctk.CTkButton(linha, text=nome, text_color=cores["primary"], anchor="w",
                                fg_color="transparent", hover_color="#E8A0F0",
                                command=lambda n=nome: cliente.selecionar_destinatario(n))
            btn.pack(side="left", padx=5, fill="x", expand=True)
            
            ctk.CTkLabel(linha, text="•", text_color=status_cor,
                         font=ctk.CTkFont(size=24)).pack(side="right", padx=5)

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