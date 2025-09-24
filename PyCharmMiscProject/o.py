import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import re
import os

# Define o nome do banco de dados
DB_NAME = "DBcliente.db"

# Lista em memória para salvar os cadastros
cadastros = []
menu_aberto = False
MENU_WIDTH = 0.4  # 40% da largura da janela


# ---- Funções de persistência e utilidades ----

def conectar_db():
    """Conecta-se ao banco de dados SQLite."""
    conn = sqlite3.connect(DB_NAME)
    return conn


def carregar_cadastros():
    """Carrega os dados de cadastro do banco de dados."""
    global cadastros
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS Cliente (cpf TEXT PRIMARY KEY, nome TEXT, telefone TEXT, gmail TEXT, data TEXT)")

    cursor.execute("SELECT * FROM Cliente")
    cadastros = [{"cpf": row[0], "nome": row[1], "telefone": row[2], "gmail": row[3], "data": row[4]} for row in
                 cursor.fetchall()]

    conn.close()


def salvar_cadastro_db(cadastro):
    """Salva um novo cadastro no banco de dados."""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Cliente (cpf, nome, telefone, gmail, data) VALUES (?, ?, ?, ?, ?)",
                       (cadastro['cpf'], cadastro['nome'], cadastro['telefone'], cadastro['gmail'], cadastro['data']))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro de Cadastro", "CPF já cadastrado.")
        return False
    finally:
        conn.close()


def excluir_cadastro_db(cpf):
    """Exclui um cadastro do banco de dados."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Cliente WHERE cpf=?", (cpf,))
    conn.commit()
    conn.close()


def limitar_tamanho(entry_text, limite):
    """Limita o número de caracteres em um campo de entrada."""
    if len(entry_text.get()) > limite:
        entry_text.set(entry_text.get()[:limite])


def formatar_data(event=None):
    """Formata a data automaticamente (DD/MM/AAAA)."""
    digits = "".join(ch for ch in data_var.get() if ch.isdigit())[:8]
    if len(digits) <= 2:
        fmt = digits
    elif len(digits) <= 4:
        fmt = f"{digits[:2]}/{digits[2:]}"
    else:
        fmt = f"{digits[:2]}/{digits[2:4]}/{digits[4:]}"
    data_var.set(fmt)
    data_entry.icursor(tk.END)


def formatar_cpf(event=None):
    """Formata o CPF automaticamente (###.###.###-##)."""
    digits = "".join(ch for ch in cpf_var.get() if ch.isdigit())[:11]
    if len(digits) <= 3:
        fmt = digits
    elif len(digits) <= 6:
        fmt = f"{digits[:3]}.{digits[3:]}"
    elif len(digits) <= 9:
        fmt = f"{digits[:3]}.{digits[3:6]}.{digits[6:]}"
    else:
        fmt = f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    cpf_var.set(fmt)
    cpf_entry.icursor(tk.END)


def formatar_telefone(event=None):
    """Formata o telefone automaticamente ((##) #####-####)."""
    digits = "".join(ch for ch in tel_var.get() if ch.isdigit())[:11]
    if len(digits) <= 2:
        fmt = f"({digits}"
    elif len(digits) <= 7:
        fmt = f"({digits[:2]}) {digits[2:]}"
    else:
        fmt = f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    tel_var.set(fmt)
    tel_entry.icursor(tk.END)


def validar_cpf_checksum(cpf):
    """Verifica se o CPF é estruturalmente válido usando o algoritmo de checksum."""
    cpf = re.sub(r'[^0-9]', '', cpf)

    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False

    # Valida o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cpf[9]) != digito1:
        return False

    # Valida o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    if int(cpf[10]) != digito2:
        return False

    return True


def validar_dados():
    """Valida os dados de entrada antes de salvar."""
    cpf = cpf_var.get()
    nome = nome_var.get().strip()
    telefone = tel_var.get().strip()
    gmail = gmail_var.get().strip()
    data = data_var.get().strip()

    if not nome:
        messagebox.showerror("Erro de validação", "O campo 'Nome' é obrigatório.")
        return False

    if not validar_cpf_checksum(cpf):
        messagebox.showerror("Erro de validação", "CPF inválido. Verifique o número digitado.")
        return False

    if not re.match(r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}", telefone):
        messagebox.showerror("Erro de validação", "Telefone inválido. Formato esperado: (99) 99999-9999.")
        return False

    if not re.match(r"[^@]+@[^@]+\.[^@]+", gmail):
        messagebox.showerror("Erro de validação", "Gmail inválido.")
        return False

    if not re.match(r"\d{2}/\d{2}/\d{4}", data):
        messagebox.showerror("Erro de validação", "Data inválida. Use o formato dd/mm/aaaa.")
        return False

    return True


def salvar():
    """Valida e salva o cadastro, atualizando o banco de dados e a interface."""
    if not validar_dados():
        return

    cadastro = {
        "cpf": re.sub(r'[^0-9]', '', cpf_var.get()),
        "nome": nome_var.get(),
        "telefone": re.sub(r'[^0-9]', '', tel_var.get()),
        "gmail": gmail_var.get(),
        "data": data_var.get()
    }

    if salvar_cadastro_db(cadastro):
        messagebox.showinfo("Cadastro realizado", f"Informações de {cadastro['nome']} salvas com sucesso!")

        # Limpa os campos após salvar
        cpf_var.set("")
        nome_var.set("")
        tel_var.set("")
        gmail_var.set("")
        data_var.set("")


def excluir_cadastro(cadastro_para_excluir):
    """Exclui um cadastro e atualiza a interface."""
    if messagebox.askyesno("Confirmar exclusão",
                           f"Tem certeza que deseja excluir o cadastro de {cadastro_para_excluir['nome']}?"):
        excluir_cadastro_db(cadastro_para_excluir['cpf'])
        mostrar_historico()
        messagebox.showinfo("Exclusão", "Cadastro excluído com sucesso!")


def mostrar_detalhes(cadastro_selecionado):
    """Cria uma nova aba com os detalhes do cadastro selecionado."""
    # Cria uma nova aba e a seleciona
    details_frame = tk.Frame(notebook, bg="#2c3e50")
    notebook.add(details_frame, text=cadastro_selecionado['nome'])
    notebook.select(details_frame)

    details_inner_frame = tk.Frame(details_frame, bg="#34495e", padx=20, pady=20, relief="solid", bd=1,
                                   highlightbackground="#3498db", highlightthickness=2)
    details_inner_frame.pack(padx=20, pady=20)

    # Adiciona um botão de voltar
    back_btn = tk.Button(details_inner_frame, text="Voltar", font=("Segoe UI", 11, "bold"),
                         bg="#3498db", fg="white", relief="flat", cursor="hand2",
                         command=lambda: notebook.select(0))  # Volta para a primeira aba
    back_btn.pack(pady=10)

    # Botão de excluir com ícone de lixeira
    delete_btn = tk.Button(details_inner_frame, text="🗑️ Excluir", font=("Segoe UI", 11, "bold"),
                           bg="#e74c3c", fg="white", relief="flat", cursor="hand2",
                           command=lambda: excluir_cadastro(cadastro_selecionado))
    delete_btn.pack(pady=10)

    # Exibe as informações do cadastro de forma organizada
    info_dict = {
        "CPF": cadastro_selecionado['cpf'],
        "Nome": cadastro_selecionado['nome'],
        "Telefone": cadastro_selecionado['telefone'],
        "Gmail": cadastro_selecionado['gmail'],
        "Data de Nascimento": cadastro_selecionado['data']
    }

    for key, value in info_dict.items():
        info_frame = tk.Frame(details_inner_frame, bg="#34495e")
        info_frame.pack(fill="x", pady=5)
        tk.Label(info_frame, text=f"{key}:", font=("Segoe UI", 11, "bold"), bg="#34495e", fg="white", anchor="w").pack(
            side="left", padx=(0, 10))
        tk.Label(info_frame, text=value, font=("Segoe UI", 11), bg="#34495e", fg="white", anchor="w").pack(side="left",
                                                                                                           fill="x",
                                                                                                           expand=True)


def mostrar_historico():
    """Exibe a lista de cadastros no painel lateral."""
    carregar_cadastros()
    # Oculta o menu principal e mostra a lista de histórico
    main_menu_frame.pack_forget()
    history_frame.pack(fill="both", expand=True)

    # Limpa o notebook para recriar as abas
    for tab in notebook.tabs():
        notebook.forget(tab)

    # Cria a primeira aba de histórico
    history_list_frame = tk.Frame(notebook, bg="#2c3e50")
    notebook.add(history_list_frame, text="Histórico")

    # Adiciona a barra de pesquisa
    search_var.set("")  # Limpa o campo de pesquisa
    search_frame = tk.Frame(history_list_frame, bg="#2c3e50", highlightbackground="#2c3e50", highlightthickness=1)
    search_frame.pack(fill="x", padx=10, pady=5)

    search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Segoe UI", 11), relief="flat", bd=0,
                            bg="#4f6176", fg="white")
    search_entry.pack(fill="x", padx=5, ipady=5)
    search_var.trace("w", lambda *args: filtrar_cadastros())

    tk.Frame(search_frame, height=1, bg="#2c3e50").pack(fill="x")  # Adiciona a linha cinza

    # Frame para a lista de botões
    list_frame = tk.Frame(history_list_frame, bg="#2c3e50")
    list_frame.pack(fill="both", expand=True)

    def filtrar_cadastros():
        termo = search_var.get().lower()
        for widget in list_frame.winfo_children():
            widget.destroy()

        # Exibe os cadastros filtrados
        cadastros_filtrados = [c for c in sorted(cadastros, key=lambda x: x['nome'].lower()) if
                               termo in c['nome'].lower()]

        if not cadastros_filtrados:
            tk.Label(list_frame, text="Nenhum cadastro encontrado.",
                     bg="#2c3e50", fg="white", font=("Segoe UI", 11)).pack(pady=20)
        else:
            for cadastro in cadastros_filtrados:
                btn = tk.Button(list_frame, text=cadastro['nome'], font=("Segoe UI", 11, "bold"),
                                bg="#34495e", fg="white", relief="flat", anchor="w", cursor="hand2",
                                activebackground="#2a3847", activeforeground="white",
                                command=lambda c=cadastro: mostrar_detalhes(c))
                btn.pack(fill="x", padx=10, pady=5)

    filtrar_cadastros()  # Chama a função para exibir a lista inicial

    notebook.select(0)  # Seleciona a primeira aba


def voltar_menu():
    """Volta para o menu principal do painel lateral."""
    history_frame.pack_forget()
    main_menu_frame.pack(fill="both", expand=True)


def fechar_menu():
    """Fecha o menu lateral."""
    global menu_aberto
    menu_frame.place_forget()
    canvas.place(relx=0, rely=0, relwidth=1, relheight=1, y=40)
    menu_aberto = False


def toggle_menu():
    """Abre ou fecha o menu lateral."""
    global menu_aberto
    if menu_aberto:
        fechar_menu()
    else:
        # Abre o menu no lado direito
        menu_frame.place(relx=1 - MENU_WIDTH, rely=0, relheight=1, relwidth=MENU_WIDTH)
        # Redimensiona o canvas para caber ao lado do menu
        canvas.place(relx=0, rely=0, relwidth=1 - MENU_WIDTH, relheight=1, y=40)
        main_menu_frame.pack(fill="both", expand=True)
        menu_aberto = True


def novo_cadastro():
    """Abre a tela de novo cadastro (fecha o menu lateral)."""
    fechar_menu()
    messagebox.showinfo("Novo Cadastro", "Você pode agora preencher um novo cadastro na tela principal.")


# ---- Janela principal ----
root = tk.Tk()
root.title("Cadastro de Cliente")
root.geometry("1024x768")  # Define a janela para um formato de retângulo deitado
root.configure(bg="#34495e")  # Cor de fundo mais escura

# Carrega os dados existentes ao iniciar a aplicação
carregar_cadastros()

fonte_label = ("Segoe UI", 11, "bold")
fonte_entry = ("Segoe UI", 11)

cpf_var = tk.StringVar()
nome_var = tk.StringVar()
tel_var = tk.StringVar()
gmail_var = tk.StringVar()
data_var = tk.StringVar()
search_var = tk.StringVar()  # Variável para a barra de pesquisa

# Cria um frame para o cabeçalho onde o botão estará
header_frame = tk.Frame(root, bg="#34495e", height=40)
header_frame.pack(side="top", fill="x")

# Botão de menu
plus_btn = tk.Button(header_frame, text="☰", font=("Segoe UI", 14, "bold"),
                     bg="#2c3e50", fg="white", relief="flat",
                     command=toggle_menu, cursor="hand2")
plus_btn.place(relx=1.0, x=-10, y=5, anchor="ne")

# ---- SCROLL ----
canvas = tk.Canvas(root, bg="#34495e", highlightthickness=0)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#34495e")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="n", width=900)
canvas.configure(yscrollcommand=scrollbar.set)

canvas.place(relx=0, rely=0, relwidth=1, relheight=1, y=40)
scrollbar.pack(side="right", fill="y")


def on_mouse_wheel(event):
    """Permite o scroll com a roda do mouse."""
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


canvas.bind_all("<MouseWheel>", on_mouse_wheel)


def criar_campo(label, var, limite=None, bind_func=None):
    """Cria um campo de entrada com rótulo e binding opcional."""
    bloco = tk.Frame(scrollable_frame, bg="#34495e", padx=15, pady=15,
                     highlightbackground="#bdc3c7", highlightthickness=1,
                     highlightcolor="#2980b9")
    bloco.pack(fill="x", pady=10, padx=40)

    tk.Label(bloco, text=label, font=fonte_label, bg="#34495e", fg="white", anchor="w").pack(anchor="w")

    entry = tk.Entry(bloco, textvariable=var, font=fonte_entry,
                     relief="flat", bd=0, bg="#4f6176", fg="white", insertbackground="white")
    entry.pack(fill="x", pady=(8, 0), ipady=6)

    tk.Frame(bloco, height=1, bg="#2c3e50").pack(fill="x")  # Adiciona a linha cinza

    # Adiciona um marcador visual para o foco
    def on_focus_in(event):
        bloco.config(highlightbackground="#3498db", highlightthickness=2)

    def on_focus_out(event):
        bloco.config(highlightbackground="#2c3e50", highlightthickness=1)

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

    if limite:
        var.trace("w", lambda *args: limitar_tamanho(var, limite))
    if bind_func:
        entry.bind("<KeyRelease>", bind_func)

    return entry


# Campos com formatação e validação melhoradas
cpf_entry = criar_campo("CPF", cpf_var, limite=14, bind_func=formatar_cpf)
criar_campo("Nome completo", nome_var, limite=250)
tel_entry = criar_campo("Telefone/Contato", tel_var, limite=15, bind_func=formatar_telefone)
criar_campo("Gmail", gmail_var, limite=100)
data_entry = criar_campo("Data de Nascimento (dd/mm/aaaa)", data_var, bind_func=formatar_data)

# Botão salvar (agora dentro do frame rolável)
btn = tk.Button(scrollable_frame,
                text="Salvar informações",
                command=salvar,
                font=("Segoe UI", 12, "bold"),
                bg="#3498db", fg="white",
                relief="flat",
                activebackground="#2980b9",
                activeforeground="white",
                height=2,
                cursor="hand2")
btn.pack(fill="x", padx=40, pady=20)

# ---- Painel Lateral (Histórico) ----
menu_frame = tk.Frame(root, bg="#2c3e50", highlightbackground="#3498db", highlightthickness=2)
menu_frame.place_forget()

# Botão de fechar menu
close_menu_btn = tk.Button(menu_frame, text="X", font=("Segoe UI", 14, "bold"),
                           bg="#2c3e50", fg="#e74c3c", relief="flat",
                           activebackground="#1a242f", activeforeground="#c0392b",
                           command=fechar_menu, cursor="hand2")
close_menu_btn.place(relx=1.0, x=-10, y=5, anchor="ne")

# Frames para o menu principal e a lista de histórico
main_menu_frame = tk.Frame(menu_frame, bg="#2c3e50")
history_frame = tk.Frame(menu_frame, bg="#2c3e50")

# Botões do menu principal
tk.Button(main_menu_frame, text="🔎 Histórico", font=("Segoe UI", 11, "bold"),
          bg="#34495e", fg="white", relief="flat", activebackground="#2a3847", activeforeground="white",
          command=mostrar_historico, cursor="hand2").pack(pady=10)

tk.Button(main_menu_frame, text="➕ Novo Cadastro", font=("Segoe UI", 11, "bold"),
          bg="#34495e", fg="white", relief="flat", activebackground="#2a3847", activeforeground="white",
          command=novo_cadastro, cursor="hand2").pack(pady=10)

tk.Button(history_frame, text="🔙 Voltar ao Menu", font=("Segoe UI", 11, "bold"),
          bg="#34495e", fg="white", relief="flat", activebackground="#2a3847", activeforeground="white",
          command=voltar_menu, cursor="hand2").pack(pady=10, padx=10, anchor="w")

# Notebook para abas (histórico e detalhes) dentro do history_frame
style = ttk.Style()
style.theme_use('default')
style.configure("TNotebook", background="#2c3e50", borderwidth=0)
style.configure("TNotebook.Tab", background="#34495e", foreground="white", padding=[10, 5])
style.map("TNotebook.Tab", background=[("selected", "#2c3e50")], foreground=[("selected", "#3498db")])

notebook = ttk.Notebook(history_frame)
notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

root.mainloop()