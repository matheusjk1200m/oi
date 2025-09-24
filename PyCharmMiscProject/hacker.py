import tkinter as tk
from PIL import Image, ImageTk
import time, threading, random

# ===== CONFIGURAÇÃO DA JANELA =====
root = tk.Tk()
root.attributes("-fullscreen", True)
root.configure(bg="black")
root.title("Hacker Style")
root.bind("<Escape>", lambda e: root.destroy())  # sair com ESC

# ===== CANVAS PRINCIPAL =====
canvas = tk.Canvas(root, bg="black", highlightthickness=0)
canvas.pack(fill="both", expand=True)
largura = root.winfo_screenwidth()
altura = root.winfo_screenheight()

# ===== IMAGEM DE FUNDO =====
# Use o arquivo fundo.png
img_original = Image.open("fundo.png").resize((largura, altura), Image.LANCZOS)

# Fade-in suave da imagem
def fade_in():
    for alpha in range(0, 101, 2):        # 0 a 100% de opacidade
        img = img_original.copy()
        img.putalpha(int(alpha * 2.55))   # converte % para 0–255
        bg = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor="nw", image=bg, tags="bg")
        canvas.lower("bg")                # garante que fique atrás do texto
        canvas.image = bg
        time.sleep(0.05)
        root.update()

# ===== LOGS EM ESTILO TERMINAL =====
texto = tk.Text(canvas, bg="black", fg="#00FF00",
                insertbackground="#00FF00",
                font=("Consolas", 14), wrap="word",
                borderwidth=0, highlightthickness=0)
texto.place(relx=0.02, rely=0.05, relwidth=0.96, relheight=0.9)

mensagens_fixas = [
    "[INFO] Iniciando protocolo seguro TLS...",
    "[WARN] Porta 22 aberta – estabelecendo túnel SSH...",
    "[INFO] Download de dados criptografados concluído."
]

def gerar_log_aleatorio():
    ip = ".".join(str(random.randint(0,255)) for _ in range(4))
    return f"[OK] Conexão {ip} pacote {random.randint(20,900)}KB"

def escrever_texto(msg, delay=0.02):
    for ch in msg + "\n":
        texto.insert(tk.END, ch)
        texto.see(tk.END)
        texto.update()
        time.sleep(delay)

def logs():
    for m in mensagens_fixas:
        escrever_texto(m, 0.03)
        time.sleep(0.7)
    while True:
        escrever_texto(gerar_log_aleatorio(), 0.01)
        time.sleep(random.uniform(0.3, 1.0))

# ===== EXECUÇÃO =====
threading.Thread(target=fade_in, daemon=True).start()
threading.Thread(target=logs, daemon=True).start()

root.mainloop()
