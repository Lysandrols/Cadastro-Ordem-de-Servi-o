import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import pywhatkit as kit
import json
import os

# Informações de Versão
__version__ = "0.1.0"

class OrdemServicoApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Ordem de Serviço - Versão {__version__}")
        self.root.geometry("700x500")

        # Estilos
        self.estilo = ttk.Style()
        self.estilo.theme_use('clam')
        self.estilo.configure("TLabel", font=("Helvetica", 10))
        self.estilo.configure("TButton", font=("Helvetica", 10), padding=10)
        self.estilo.configure("TEntry", font=("Helvetica", 10), padding=10)
        self.estilo.configure("TCombobox", font=("Helvetica", 10))

        # Widgets
        self.tipo_label = ttk.Label(root, text="Tipo:")
        self.tipo_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.tipo_combobox = ttk.Combobox(root, values=["Orçamento", "Ordem de Serviço"])
        self.tipo_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.nome_label = ttk.Label(root, text="Nome do Cliente:")
        self.nome_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.nome_entry = ttk.Entry(root)
        self.nome_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.nome_entry.bind("<FocusOut>", self.formatar_entrada)

        self.servico_label = ttk.Label(root, text="Serviço Realizado:")
        self.servico_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.servico_button = ttk.Button(root, text="Selecionar Serviços", command=self.selecionar_servicos)
        self.servico_button.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        self.data_label = ttk.Label(root, text="Data (ddmmaaaa):")
        self.data_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.data_entry = ttk.Entry(root)
        self.data_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        self.preencher_data_atual()

        self.valor_label = ttk.Label(root, text="Valor Total:")
        self.valor_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.valor_entry = ttk.Entry(root, state='readonly')
        self.valor_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

        self.telefone_label = ttk.Label(root, text="Telefone (com DDD, sem +):")
        self.telefone_label.grid(row=5, column=0, padx=10, pady=10, sticky="w")
        self.telefone_entry = ttk.Entry(root)
        self.telefone_entry.grid(row=5, column=1, padx=10, pady=10, sticky="ew")

        self.gerar_button = ttk.Button(root, text="Gerar Ordem", command=self.gerar_ordem)
        self.gerar_button.grid(row=6, column=0, columnspan=2, pady=10)

        self.buscar_button = ttk.Button(root, text="Buscar Ordem/Orçamento", command=self.abrir_busca)
        self.buscar_button.grid(row=7, column=0, columnspan=2, pady=10)

        self.desenvolvido_label = ttk.Label(root, text="Desenvolvido por Lysandro Luiz", anchor='w')
        self.desenvolvido_label.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Configurar layout de colunas
        root.columnconfigure(1, weight=1)

        self.ordem_servico_counter = self.ler_contador()
        self.orcamentos = self.carregar_orcamentos()
        self.ordem_selecionada = None
        self.servicos_selecionados = []

    def preencher_data_atual(self):
        data_atual = datetime.now().strftime("%d%m%Y")
        self.data_entry.insert(0, data_atual)

    def ler_contador(self):
        try:
            with open("ordem_servico_counter.txt", "r") as file:
                return int(file.read())
        except FileNotFoundError:
            return 2650

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

    def selecionar_servicos(self):
        self.servicos_window = tk.Toplevel(self.root)
        self.servicos_window.title("Selecionar Serviços")
        self.servicos_window.geometry("450x800")

        self.servicos_var = {}
        self.servicos_valor = {}
        servicos = ["Limpeza", "Formatação", "Formatação com Backup", "Troca de peças", "Reparo de Placa Mãe", "Configuração", "Instalação de programas", "Acesso remoto", "Montagem e configuração", "Recuperação de arquivos",]

        for servico in servicos:
            frame = ttk.Frame(self.servicos_window)
            frame.pack(fill='x', padx=10, pady=5)

            var = tk.BooleanVar()
            chk = ttk.Checkbutton(frame, text=servico, variable=var)
            chk.pack(side='left')

            valor_entry = ttk.Entry(frame, width=10)
            valor_entry.pack(side='right')
            valor_entry.insert(0, "0.00")

            self.servicos_var[servico] = var
            self.servicos_valor[servico] = valor_entry

        self.outro_servico_frames = []

        self.outro_servico_frame = ttk.Frame(self.servicos_window)
        self.outro_servico_frame.pack(fill='x', padx=10, pady=5)

        self.adicionar_servico_button = ttk.Button(self.outro_servico_frame, text="Adicionar Outro Serviço", command=self.adicionar_outro_servico)
        self.adicionar_servico_button.pack(side='left')

        self.salvar_servicos_button = ttk.Button(self.servicos_window, text="Salvar", command=self.salvar_servicos_selecionados)
        self.salvar_servicos_button.pack(pady=10)

    def adicionar_outro_servico(self):
        frame = ttk.Frame(self.servicos_window)
        frame.pack(fill='x', padx=10, pady=5)
        self.outro_servico_frames.append(frame)

        outro_servico_entry = ttk.Entry(frame, width=30)
        outro_servico_entry.pack(side='left', padx=5)

        outro_valor_entry = ttk.Entry(frame, width=10)
        outro_valor_entry.pack(side='left')
        outro_valor_entry.insert(0, "0.00")

        remover_button = ttk.Button(frame, text="Remover", command=lambda f=frame: self.remover_outro_servico(f))
        remover_button.pack(side='left', padx=5)

    def remover_outro_servico(self, frame):
        self.outro_servico_frames.remove(frame)
        frame.destroy()

    def salvar_servicos_selecionados(self):
        self.servicos_selecionados = []
        valor_total = 0.0
        for servico, var in self.servicos_var.items():
            if var.get():
                valor = self.servicos_valor[servico].get()
                try:
                    valor = float(valor)
                except ValueError:
                    messagebox.showerror("Erro", f"Valor inválido para o serviço: {servico}")
                    return
                self.servicos_selecionados.append((servico, valor))
                valor_total += valor

        for frame in self.outro_servico_frames:
            outro_servico_entry = frame.winfo_children()[0]
            outro_valor_entry = frame.winfo_children()[1]
            outro_servico = outro_servico_entry.get().strip()
            if outro_servico:
                outro_valor = outro_valor_entry.get()
                try:
                    outro_valor = float(outro_valor)
                except ValueError:
                    messagebox.showerror("Erro", "Valor inválido para o outro serviço.")
                    return
                self.servicos_selecionados.append((outro_servico, outro_valor))
                valor_total += outro_valor

        self.valor_entry.config(state='normal')
        self.valor_entry.delete(0, tk.END)
        self.valor_entry.insert(0, f"{valor_total:.2f}")
        self.valor_entry.config(state='readonly')

        self.servicos_window.destroy()

    def gerar_ordem(self):
        tipo = self.tipo_combobox.get()
        nome = self.nome_entry.get()
        servico = ", ".join([f"{s[0]} (R${s[1]:.2f})" for s in self.servicos_selecionados])
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
            f"Olá {nome},\n"
            f"Segue {tipo.lower()} OS#{numero_ordem}:\n"
            f"{servico}\n"
            f"Realizado em {data_formatada},\n"
            f"No valor total de R${valor},\n"
            f"LFLINFORMÁTICA,\n" 
            f"Agradecemos a sua preferência."
        )

        if self.ordem_selecionada:
            self.ordem_selecionada.update({
                "tipo": tipo,
                "nome": nome,
                "servico": servico,
                "data": data_formatada,
                "valor": valor,
                "telefone": telefone
            })
        else:
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
            kit.sendwhatmsg_instantly(f"+{telefone}", mensagem, wait_time=10, tab_close=False, close_time=0)
            messagebox.showinfo("Sucesso", "Ordem gerada e enviada com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao enviar mensagem pelo WhatsApp: {e}")

        self.ordem_selecionada = None

    def abrir_busca(self):
        self.busca_window = tk.Toplevel(self.root)
        self.busca_window.title("Buscar Ordem/Orçamento")
        self.busca_window.geometry("600x400")

        self.busca_entry = ttk.Entry(self.busca_window, width=50)
        self.busca_entry.pack(padx=10, pady=10)

        self.buscar_button = ttk.Button(self.busca_window, text="Buscar", command=self.buscar_orcamento)
        self.buscar_button.pack(padx=10, pady=10)

        self.resultados_listbox = tk.Listbox(self.busca_window, width=80)
        self.resultados_listbox.pack(padx=10, pady=10)

        self.selecionar_button = ttk.Button(self.busca_window, text="Selecionar", command=self.selecionar_orcamento)
        self.selecionar_button.pack(padx=10, pady=10)

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
                self.data_entry.delete(0, tk.END)
                self.data_entry.insert(0, orcamento['data'].replace("/", ""))
                self.valor_entry.config(state='normal')
                self.valor_entry.delete(0, tk.END)
                self.valor_entry.insert(0, orcamento['valor'])
                self.valor_entry.config(state='readonly')
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
