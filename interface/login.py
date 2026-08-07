import customtkinter as ctk 
from PIL import Image, ImageTk
from banco_de_dados.database import inserir_usuario, verificar_login
from utils.mensagens import alerta_personalizado
from interface.chat import abrir_chat
import bcrypt
from utils.path import resource_path
from utils.theme import get_colors, toggle_theme, register_theme_callback

def criar_tela_login(app):
    widgets_login = {}

    def atualizar_cores_login():
        c = get_colors()
        if "btn_entrar" in widgets_login:
            widgets_login["btn_entrar"].configure(fg_color=c["tertiary"], hover_color=c["primary"], text_color=c["primary"])
        if "btn_cadastre" in widgets_login:
            widgets_login["btn_cadastre"].configure(fg_color=c["secondary"], hover_color=c["tertiary"])
        if "btn_tema" in widgets_login:
            widgets_login["btn_tema"].configure(fg_color=c["primary"], text_color="#FFFFFF")
        for lbl in widgets_login.get("labels", []):
            lbl.configure(text_color=c["text"])

    register_theme_callback(atualizar_cores_login)

    def abrir_cadastro():
        app.withdraw()
        cadastro = ctk.CTkToplevel(app)
        cadastro.title("Cadastro")
        cadastro.geometry("500x600")
        
        c = get_colors()
        cadastro.configure(fg_color=c["bg"])

        imagem_fundo_cadastro = Image.open(resource_path("assets/chat_a_bit_cadastro_fundo.png"))
        imagem_fundo_cadastro = imagem_fundo_cadastro.resize((500, 600))
        imagem_fundo_cadastro_tk = ImageTk.PhotoImage(imagem_fundo_cadastro)

        fundo = ctk.CTkLabel(cadastro, image=imagem_fundo_cadastro_tk, text="")
        fundo.place(x=0, y=0, relwidth=1, relheight=1)
        fundo.image = imagem_fundo_cadastro_tk

        frame_cadastro = ctk.CTkFrame(cadastro, fg_color="transparent")
        frame_cadastro.place(relx=0.5, rely=0.6, anchor="center")

        font_padrao = ctk.CTkFont(size=14)
        campos = [("Nome:", 0), ("usuário:", 1), ("Senha:", 2), ("Confirmar Senha:", 3)]
        entradas = {}
        
        labels_cad = []
        for texto, linha in campos:
            label = ctk.CTkLabel(frame_cadastro, text=texto, font=font_padrao, text_color=c["text"])
            label.grid(row=linha, column=0, padx=10, pady=10, sticky="e")
            labels_cad.append(label)
            entry = ctk.CTkEntry(frame_cadastro, width=250, font=font_padrao, show="*" if "Senha" in texto else "")
            entry.grid(row=linha, column=1, padx=10, pady=10)
            entradas[texto] = entry

        def cadastrar_usuario():
            nome = entradas["Nome:"].get()
            usuario = entradas["usuário:"].get()
            senha = entradas["Senha:"].get()
            confirmar = entradas["Confirmar Senha:"].get()

            if not nome or not usuario or not senha:
                alerta_personalizado("Erro", "Preencha todos os campos.")
                return
            if senha != confirmar:
                alerta_personalizado("Erro", "Senhas não conferem.")
                return
            senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
            sucesso = inserir_usuario(nome, usuario, senha_hash)
            if sucesso:
                alerta_personalizado("Sucesso", "Cadastro realizado!")
                cadastro.destroy()
                app.deiconify()
            else:
                alerta_personalizado("Erro", "Usuário já existe ou erro no cadastro.")

        btn_cad = ctk.CTkButton(frame_cadastro, text="Cadastrar", width=200, corner_radius=10, fg_color=c["tertiary"],
                      hover_color=c["primary"], text_color=c["primary"], font=ctk.CTkFont(size=15, weight="bold"),
                      command=cadastrar_usuario)
        btn_cad.grid(row=4, column=0, columnspan=2, pady=(20, 10))

        btn_voltar = ctk.CTkButton(frame_cadastro, text="Voltar", width=100, corner_radius=10, fg_color=c["secondary"],
                      hover_color=c["tertiary"], command=lambda: [cadastro.destroy(), app.deiconify()])
        btn_voltar.grid(row=5, column=0, columnspan=2, pady=(0, 20))
        
        def atualizar_cores_cadastro():
            c2 = get_colors()
            cadastro.configure(fg_color=c2["bg"])
            btn_cad.configure(fg_color=c2["tertiary"], hover_color=c2["primary"], text_color=c2["primary"])
            btn_voltar.configure(fg_color=c2["secondary"], hover_color=c2["tertiary"])
            for l in labels_cad:
                l.configure(text_color=c2["text"])
                
        register_theme_callback(atualizar_cores_cadastro)

    def fazer_login():
        usuario = entrada_usuario.get()
        senha = entrada_senha.get()
        if not usuario or not senha:
            alerta_personalizado("Erro", "Preencha usuário e senha.")
            return
        try:
            resultado = verificar_login(usuario, senha)
            if resultado == True:
                alerta_personalizado("Sucesso", f"Bem-vindo(a), {usuario}!")
                app.withdraw()
                abrir_chat(app, usuario)
            elif resultado == "senha_incorreta":
                alerta_personalizado("Erro", "Senha incorreta.")
            elif resultado == "usuario_nao_encontrado":
                alerta_personalizado("Erro", "Usuário não encontrado.")
            else:
                alerta_personalizado("Erro", "Erro ao tentar fazer login.")
        except Exception as e:
            alerta_personalizado("Erro", f"Erro ao tentar fazer login: {e}")

    imagem_logo = Image.open(resource_path("assets/chat_a_bit_login_fundo.png")).resize((540, 540))
    imagem_logo_fundo_tk = ImageTk.PhotoImage(imagem_logo)

    fundo_label = ctk.CTkLabel(app, image=imagem_logo_fundo_tk, text="")
    fundo_label.place(x=0, y=0, relwidth=1, relheight=1)

    btn_tema = ctk.CTkButton(app, text="Mudar Tema", width=100, corner_radius=10, command=toggle_theme)
    btn_tema.place(x=10, y=10)
    widgets_login["btn_tema"] = btn_tema

    frame = ctk.CTkFrame(app, fg_color="transparent")
    frame.place(relx=0.5, rely=0.6, anchor="center")

    lbl1 = ctk.CTkLabel(frame, text="Usuário:")
    lbl1.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="e")
    entrada_usuario = ctk.CTkEntry(frame, width=200)
    entrada_usuario.grid(row=0, column=1, padx=10, pady=(20, 10))

    lbl2 = ctk.CTkLabel(frame, text="Senha:")
    lbl2.grid(row=1, column=0, padx=10, pady=10, sticky="e")
    entrada_senha = ctk.CTkEntry(frame, show="*", width=200)
    entrada_senha.grid(row=1, column=1, padx=10, pady=10)

    btn_entrar = ctk.CTkButton(frame, text="Entrar", width=200, corner_radius=10, command=fazer_login)
    btn_entrar.grid(row=2, column=0, columnspan=2, pady=(20, 20))
    widgets_login["btn_entrar"] = btn_entrar

    lbl3 = ctk.CTkLabel(frame, text="Não tem uma conta?")
    lbl3.grid(row=3, column=0, columnspan=2, pady=(10, 5))

    btn_cadastre = ctk.CTkButton(frame, text="Cadastre-se", width=150, corner_radius=10, command=abrir_cadastro)
    btn_cadastre.grid(row=4, column=0, columnspan=2, pady=(0, 20))
    widgets_login["btn_cadastre"] = btn_cadastre
    
    widgets_login["labels"] = [lbl1, lbl2, lbl3]
    
    atualizar_cores_login()
