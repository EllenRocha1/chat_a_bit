# Chat a Bit

Chat a Bit é uma aplicação de mensagens instantâneas baseada em arquitetura **cliente-servidor**, desenvolvida como projeto acadêmico para a disciplina de **Redes de Computadores** da **UFRPE**.  
O sistema utiliza **sockets TCP** para comunicação em tempo real, com autenticação segura, persistência em banco de dados e interface gráfica desktop.

---

## Tecnologias Utilizadas

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-4169E1?logo=postgresql&logoColor=white)
![Sockets](https://img.shields.io/badge/TCP%20Sockets-Networking-blue)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-GUI-darkgreen)
![PyInstaller](https://img.shields.io/badge/PyInstaller-Build-lightgrey)
![bcrypt](https://img.shields.io/badge/bcrypt-Security-critical)

---

## Funcionalidades

- **Comunicação em tempo real**  
  Troca de mensagens instantâneas entre usuários conectados via sockets TCP.

- **Cadastro e autenticação segura**  
  Senhas criptografadas utilizando a biblioteca `bcrypt`.

- **Persistência de dados**  
  Armazenamento de usuários e histórico de mensagens em banco de dados PostgreSQL.

- **Indicadores de status**  
  Visualização de usuários online/offline e indicação visual de digitação.

- **Interface gráfica customizada**  
  Desenvolvida com CustomTkinter, incluindo cursores personalizados e notificações internas.

- **Distribuição portátil**  
  Geração de executável único (.exe) com Splash Screen integrada via PyInstaller.

---

## Demonstração da Interface

### Tela de Login
![Tela de Login](./login.png)

### Tela de Cadastro
![Tela de Cadastro](./cadastro.png)

### Chat Principal
![Chat Principal](./conversa.png)

---

## Estrutura do Projeto

```plaintext
chat_a_bit/
├── assets/             # Recursos visuais (ícones, imagens, cursores)
├── banco_de_dados/     # Scripts de criação e conexão com PostgreSQL
├── config/             # Arquivos de configuração do sistema
├── interface/          # Janelas e componentes da interface gráfica
├── rede/               # Implementação de sockets (cliente e servidor)
├── utils/              # Funções auxiliares e tratamento de caminhos
└── main.py             # Ponto de entrada da aplicação cliente
