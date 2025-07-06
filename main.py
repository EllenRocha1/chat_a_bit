import customtkinter as ctk
from interface.login import criar_tela_login

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.title("Chat a Bit")
    app.geometry("500x600")

    criar_tela_login(app)

    app.mainloop()