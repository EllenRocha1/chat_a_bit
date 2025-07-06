import customtkinter as ctk
from PIL import Image, ImageTk

def abrir_chat(app, usuario):
    amarelo = "#ffdf61"
    roxo = "#402456"
    rosa_escuro = "#b20f55"

    chat = ctk.CTkToplevel(app)
    chat.title("Chat a Bit")
    chat.geometry("1000x700")

    barra_superior = ctk.CTkFrame(chat, height=40, fg_color=roxo)
    barra_superior.pack(side="top", fill="x")

    imagem_logo = Image.open("assets/chat_a_bit_logo.png")
    imagem_logo_pequena = imagem_logo.resize((70, 50))
    imagem_logo_tk = ImageTk.PhotoImage(imagem_logo_pequena)

    label_logo = ctk.CTkLabel(barra_superior, image=imagem_logo_tk, text="")
    label_logo.image = imagem_logo_tk 
    label_logo.pack(side="left", padx=10, pady=5)

    ctk.CTkButton(barra_superior, text="Sair", width=70, height=30, fg_color=amarelo,
                text_color=roxo, hover_color=rosa_escuro).pack(side="right", padx=10, pady=5)
    
    ctk.CTkButton(barra_superior, text="Conta", width=70, height=30, fg_color=amarelo,
                text_color=roxo, hover_color=rosa_escuro).pack(side="right", padx=10, pady=5)


    corpo = ctk.CTkFrame(chat, fg_color="transparent")
    corpo.pack(fill="both", expand=True)

    barra_lateral = ctk.CTkFrame(corpo, width=250, fg_color=rosa_escuro)
    barra_lateral.pack(side="left", fill="y")
    ctk.CTkEntry(barra_lateral, placeholder_text="Procurar usuário...", height=30).pack(padx=10, pady=10, fill="x")

    lista_usuarios = ctk.CTkScrollableFrame(barra_lateral, fg_color="#F6C6FA")
    lista_usuarios.pack(padx=10, pady=(0, 10), fill="both", expand=True)

    for nome, status in [("maria", True), ("joao", False), ("ana", True)]:
        status_cor = "#227522" if status else "#B31B1B"
        linha = ctk.CTkFrame(lista_usuarios, fg_color="transparent")
        linha.pack(fill="x", pady=5)
        ctk.CTkLabel(linha, text=nome, text_color=roxo, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(linha, text="•", text_color=status_cor, font=ctk.CTkFont(size=24)).pack(side="right", padx=5)
    
    frame_chat = ctk.CTkFrame(corpo, fg_color="#1e1e1e")
    frame_chat.pack(side="left", fill="both", expand=True)

    mensagens_frame = ctk.CTkScrollableFrame(frame_chat, fg_color="#2e2e2e")
    mensagens_frame.pack(padx=10, pady=(10, 5), fill="both", expand=True)
    ctk.CTkLabel(mensagens_frame, text=f"", anchor="w").pack(fill="x", padx=5, pady=2)

    campo_inferior = ctk.CTkFrame(frame_chat, fg_color="transparent")
    campo_inferior.pack(padx=10, pady=10, fill="x")
    ctk.CTkEntry(campo_inferior, placeholder_text="Digite sua mensagem...", height=35).pack(side="left", fill="x", expand=True, padx=(0, 10))
    ctk.CTkButton(campo_inferior, text="Enviar", fg_color=amarelo, text_color=roxo,
                  hover_color=roxo, width=100).pack(side="right")
