import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import pywhatkit as kit
import json
import os

class OrdemServicoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ordem de Serviço")
        self.root.geometry("600x400")

        self.tipo_label = tk.Label(root, text="Tipo:")
        self.tipo_label.pack()
        self.tipo_combobox = ttk.Combobox(root, values=["Orçamento", "Serviço"])
        self.tipo_combobox.pack()

        self.nome_label = tk.Label(root, text="Nome do Cliente:")
        self.nome_label.pack()
        self.nome_entry = tk.Entry(root, width=50)
        self.nome_entry.pack()
        self.nome_entry.bind("<FocusOut>", self.formatar_entrada)

        self.servico_label = tk.Label(root, text="Serviço Realizado:")
        self.servico_label.pack()
        self.servico_entry = tk.Entry(root, width=50)
        self.servico_entry.pack()
        self.servico_entry.bind("<FocusOut>", self.formatar_entrada)

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

        self.buscar_button = tk.Button(root, text="Buscar Ordem/Orçamento", command=self.abrir_busca)
        self.buscar_button.pack()

        self.ordem_servico_counter = self.ler_contador()
        self.orcamentos = self.carregar_orcamentos()  # Carregar os orçamentos salvos
        self.ordem_selecionada = None

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

    def salvar_orcamentos(self):
        with open("orcamentos.json", "w") as file:
            json.dump(self.orcamentos, file)

    def carregar_orcamentos(self):
        if os.path.exists("orcamentos.json"):
            with open("orcamentos.json", "r") as file:
                return json.load(file)
        return []

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

        if self.ordem_selecionada:
            numero_ordem = self.ordem_selecionada['numero']
        else:
            numero_ordem = self.ordem_servico_counter
            self.atualizar_contador()

        mensagem = (
            f"Olá {nome}, segue sua {tipo.lower()} #{numero_ordem}: {servico}, Realizado em {data_formatada}, "
            f"no valor de R${valor}, LFLINFORMÁTICA, ##."
        )

        if self.ordem_selecionada:
            # Atualiza o orçamento existente para serviço
            self.ordem_selecionada.update({
                "tipo": tipo,
                "nome": nome,
                "servico": servico,
                "data": data_formatada,
                "valor": valor,
                "telefone": telefone
            })
        else:
            # Cria uma nova ordem de serviço ou orçamento
            self.orcamentos.append({
                "numero": numero_ordem,
                "tipo": tipo,
                "nome": nome,
                "servico": servico,
                "data": data_formatada,
                "valor": valor,
                "telefone": telefone
            })
        
        self.salvar_orcamentos()

        try:
            kit.sendwhatmsg_instantly(f"+{telefone}", mensagem, wait_time=8, tab_close=True, close_time=1)
            messagebox.showinfo("Sucesso", "Ordem gerada e enviada com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao enviar mensagem pelo WhatsApp: {e}")

        self.ordem_selecionada = None

    def abrir_busca(self):
        self.busca_window = tk.Toplevel(self.root)
        self.busca_window.title("Buscar Ordem/Orçamento")
        self.busca_window.geometry("600x400")

        self.busca_entry = tk.Entry(self.busca_window, width=50)
        self.busca_entry.pack()

        self.buscar_button = tk.Button(self.busca_window, text="Buscar", command=self.buscar_orcamento)
        self.buscar_button.pack()

        self.resultados_listbox = tk.Listbox(self.busca_window, width=80)
        self.resultados_listbox.pack()

        self.selecionar_button = tk.Button(self.busca_window, text="Selecionar", command=self.selecionar_orcamento)
        self.selecionar_button.pack()

    def buscar_orcamento(self):
        termo_busca = self.busca_entry.get().lower()
        self.resultados_listbox.delete(0, tk.END)
        for orcamento in self.orcamentos:
            if termo_busca in orcamento['nome'].lower() or termo_busca in orcamento['servico'].lower():
                self.resultados_listbox.insert(tk.END, f"#{orcamento['numero']} - {orcamento['nome']} - {orcamento['servico']} - {orcamento['valor']} - {orcamento['data']}")

    def selecionar_orcamento(self):
        selected_index = self.resultados_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Erro", "Selecione um orçamento para editar.")
            return

        selected_text = self.resultados_listbox.get(selected_index)
        numero_ordem = int(selected_text.split(" ")[0][1:])

        for orcamento in self.orcamentos:
            if orcamento['numero'] == numero_ordem:
                self.tipo_combobox.set(orcamento['tipo'])
                self.nome_entry.delete(0, tk.END)
                self.nome_entry.insert(0, orcamento['nome'])
                self.servico_entry.delete(0, tk.END)
                self.servico_entry.insert(0, orcamento['servico'])
                self.data_entry.delete(0, tk.END)
                self.data_entry.insert(0, orcamento['data'].replace("/", ""))
                self.valor_entry.delete(0, tk.END)
                self.valor_entry.insert(0, orcamento['valor'])
                self.telefone_entry.delete(0, tk.END)
                self.telefone_entry.insert(0, orcamento['telefone'])
                self.ordem_selecionada = orcamento

        self.busca_window.destroy()

    def formatar_entrada(self, event):
        widget = event.widget
        texto = widget.get()
        if texto:
            texto_formatado = texto.title()
            widget.delete(0, tk.END)
            widget.insert(0, texto_formatado)

if __name__ == "__main__":
    root = tk.Tk()
    app = OrdemServicoApp(root)
    root.mainloop()








