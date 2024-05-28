import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import pywhatkit as kit

class OrdemServicoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ordem de Serviço")
        self.root.geometry("400x400")

        self.tipo_label = tk.Label(root, text="Tipo:")
        self.tipo_label.pack()
        self.tipo_combobox = ttk.Combobox(root, values=["Orçamento", "Serviço"])
        self.tipo_combobox.pack()

        self.nome_label = tk.Label(root, text="Nome do Cliente:")
        self.nome_label.pack()
        self.nome_entry = tk.Entry(root, width=50)
        self.nome_entry.pack()

        self.servico_label = tk.Label(root, text="Serviço Realizado:")
        self.servico_label.pack()
        self.servico_entry = tk.Entry(root, width=50)
        self.servico_entry.pack()

        self.data_label = tk.Label(root, text="Data (ddmmaaaa):")
        self.data_label.pack()
        self.data_entry = tk.Entry(root, width=50)
        self.data_entry.pack()
        self.preencher_data_atual()  

        self.valor_label = tk.Label(root, text="Valor:")
        self.valor_label.pack()
        self.valor_entry = tk.Entry(root, width=50)
        self.valor_entry.pack()

        self.telefone_label = tk.Label(root, text="Telefone (com DDD, sem +):")
        self.telefone_label.pack()
        self.telefone_entry = tk.Entry(root, width=50)
        self.telefone_entry.pack()

        self.gerar_button = tk.Button(root, text="Gerar Ordem", command=self.gerar_ordem)
        self.gerar_button.pack()

        self.ordem_servico_counter = self.ler_contador()

    def preencher_data_atual(self):
        data_atual = datetime.now().strftime("%d%m%Y")
        self.data_entry.insert(0, data_atual)

    def ler_contador(self):
        try:
            with open("ordem_servico_counter.txt", "r") as file:
                return int(file.read())
        except FileNotFoundError:
            return 2650  # Valor padrão se o arquivo não existir

    def atualizar_contador(self):
        self.ordem_servico_counter += 1
        with open("ordem_servico_counter.txt", "w") as file:
            file.write(str(self.ordem_servico_counter))

    def gerar_ordem(self):
        tipo = self.tipo_combobox.get()
        nome = self.nome_entry.get()
        servico = self.servico_entry.get()
        data = self.data_entry.get()
        valor = self.valor_entry.get()
        telefone = self.telefone_entry.get()

        if not tipo or not nome or not servico or not data or not valor or not telefone:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return

        if len(data) != 8 or not data.isdigit():
            messagebox.showerror("Erro", "Data inválida! Use o formato ddmmaaaa.")
            return

        try:
            data_formatada = datetime.strptime(data, "%d%m%Y").strftime("%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Erro", "Data inválida! Use o formato ddmmaaaa.")
            return

        numero_ordem = self.ordem_servico_counter
        self.atualizar_contador()

        if tipo == "Orçamento":
            mensagem = f"Olá {nome}, segue seu orçamento #{numero_ordem}: {servico} realizado em {data_formatada}, no valor de R${valor}, LFLINFORMÁTICA, ##."
        elif tipo == "Serviço":
            mensagem = f"Olá {nome}, segue sua ordem de serviço #{numero_ordem}: {servico} realizado em {data_formatada}, no valor de R${valor}, LFLINFORMÁTICA, ##."

        try:
            kit.sendwhatmsg_instantly(f"+{telefone}", mensagem, wait_time=20, tab_close=True, close_time=5)
            messagebox.showinfo("Sucesso", "Ordem gerada e enviada com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao enviar mensagem pelo WhatsApp: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = OrdemServicoApp(root)
    root.mainloop()










