import customtkinter as ctk 
from PIL import Image, ImageTk

ctk.set_appearance_mode("dark")

amarelo = "#ffdf61"
roxo = "#402456"
rosa_escuro = "#b20f55"

app = ctk.CTk()

app.title('Chat a Bit')
app.geometry('500x600')

def abrir_cadastro():
    app.withdraw()
    cadastro = ctk.CTkToplevel(app)
    cadastro.title("Cadastro")
    cadastro.geometry("500x600")

    # Fundo com imagem
    imagem_fundo_cadastro = Image.open("assets/chat_a_bit_cadastro_fundo.png")
    imagem_fundo_cadastro = imagem_fundo_cadastro.resize((500, 600))
    imagem_fundo_cadastro_tk = ImageTk.PhotoImage(imagem_fundo_cadastro)

    fundo = ctk.CTkLabel(cadastro, image=imagem_fundo_cadastro_tk, text="")
    fundo.place(x=0, y=0, relwidth=1, relheight=1)
    fundo.image = imagem_fundo_cadastro_tk  # manter referência

    frame_cadastro = ctk.CTkFrame(cadastro, fg_color="transparent")
    frame_cadastro.place(relx=0.5, rely=0.6, anchor="center")

    font_padrao = ctk.CTkFont(size=14)

    campos = [("Nome:", 0), ("usuário:", 1), ("Senha:", 2), ("Confirmar Senha:", 3)]
    entradas = {}

    for texto, linha in campos:
        label = ctk.CTkLabel(frame_cadastro, text=texto, font=font_padrao)
        label.grid(row=linha, column=0, padx=10, pady=10, sticky="e")

        entry = ctk.CTkEntry(frame_cadastro, width=250, font=font_padrao, show="*" if "Senha" in texto else "")
        entry.grid(row=linha, column=1, padx=10, pady=10)
        entradas[texto] = entry

    botao_confirmar = ctk.CTkButton(frame_cadastro, text="Cadastrar", width=200,
                                    corner_radius=10, fg_color=amarelo, hover_color=roxo,
                                    text_color=roxo, font=ctk.CTkFont(size=15, weight="bold"))
    botao_confirmar.grid(row=4, column=0, columnspan=2, pady=(20, 10))

    botao_voltar = ctk.CTkButton(frame_cadastro, text="Voltar", width=100,
                                 corner_radius=10, fg_color=rosa_escuro, hover_color=amarelo,
                                 command=cadastro.destroy)
    botao_voltar.grid(row=5, column=0, columnspan=2, pady=(0, 20))


imagem_logo = Image.open("assets/chat_a_bit_login_fundo.png")
imagem_logo_fundo = imagem_logo.resize((540, 540))
imagem_logo_fundo_tk = ImageTk.PhotoImage(imagem_logo_fundo)

fundo_label = ctk.CTkLabel(app, image=imagem_logo_fundo_tk, text="")
fundo_label.place(x=0, y=0, relwidth=1, relheight=1)

frame = ctk.CTkFrame(app, fg_color="transparent")
frame.place(relx=0.5, rely=0.6, anchor="center")

campo_usuario = ctk.CTkLabel(frame, text="Usuário:")
campo_usuario.grid(row=0, column=0, padx=10, pady=(20, 10), sticky="e")

entrada_usuario = ctk.CTkEntry(frame, width=200)
entrada_usuario.grid(row=0, column=1, padx=10, pady=(20, 10))

campo_senha = ctk.CTkLabel(frame, text="Senha:")
campo_senha.grid(row=1, column=0, padx=10, pady=10, sticky="e")

entrada_senha = ctk.CTkEntry(frame, show="*", width=200)
entrada_senha.grid(row=1, column=1, padx=10, pady=10)

botao_login = ctk.CTkButton(frame, text="Entrar", width=200, corner_radius=10, fg_color=amarelo, hover_color= roxo, text_color= roxo)
botao_login.grid(row=2, column=0, columnspan=2, padx=10, pady=(20, 20))

campo_cadastre = ctk.CTkLabel(frame, text="Não tem uma conta?")
campo_cadastre.grid(row=3, column=0, columnspan=2, pady=(10, 5))

botao_cadastre = ctk.CTkButton(frame, text="Cadastre-se", width=150, corner_radius=10, fg_color=rosa_escuro, hover_color=amarelo, command=abrir_cadastro)      
botao_cadastre.grid(row=4, column=0, columnspan=2, pady=(0, 20))


app.mainloop()