import tkinter as tk
from tkinter import messagebox
from dataclasses import dataclass
from enum import Enum
import sqlite3

class Prioridade(Enum):
    BAIXA = 1
    MEDIA = 2
    ALTA = 3

@dataclass
class Tarefa:
    id: int
    nome: str
    prioridade: Prioridade
    concluida: bool

class TarefaRepository:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tarefas(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                prioridade INTEGER,
                concluida INTEGER
            )
        """)
        self.conn.commit()

    def get_all(self):
        self.cursor.execute("SELECT * FROM tarefas")
        return [Tarefa(*t) for t in self.cursor.fetchall()]

    def add(self, tarefa):
        self.cursor.execute("INSERT INTO tarefas(nome, prioridade, concluida) VALUES(?,?,?)",
            (tarefa.nome, tarefa.prioridade.value, tarefa.concluida))
        self.conn.commit()

    def update(self, tarefa):
        self.cursor.execute("UPDATE tarefas SET nome=?, prioridade=?, concluida=? WHERE id=?",
            (tarefa.nome, tarefa.prioridade.value, tarefa.concluida, tarefa.id))
        self.conn.commit()

    def delete(self, tarefa_id):
        self.cursor.execute("DELETE FROM tarefas WHERE id=?", (tarefa_id,))
        self.conn.commit()

class TarefaService:
    def __init__(self, repo):
        self.repo = repo

    def get_all(self):
        return self.repo.get_all()

    def add(self, tarefa):
        self.repo.add(tarefa)

    def update(self, tarefa):
        self.repo.update(tarefa)

    def delete(self, tarefa_id):
        self.repo.delete(tarefa_id)

class TarefaUI:
    def __init__(self, master, service):
        self.master = master
        self.service = service
        self.tarefas = tk.Listbox(self.master)
        self.tarefas.pack()
        self.entry_nome = tk.Entry(self.master)
        self.entry_nome.pack()
        self.button_add = tk.Button(self.master, text="Adicionar", command=self.adicionar_tarefa)
        self.button_add.pack()
        self.button_update = tk.Button(self.master, text="Atualizar", command=self.atualizar_tarefa)
        self.button_update.pack()
        self.button_delete = tk.Button(self.master, text="Excluir", command=self.excluir_tarefa)
        self.button_delete.pack()
        self.atualizar_lista()

    def adicionar_tarefa(self):
        nome = self.entry_nome.get()
        tarefa = Tarefa(None, nome, Prioridade.MEDIA, False)
        self.service.add(tarefa)
        self.entry_nome.delete(0, tk.END)
        self.atualizar_lista()

    def atualizar_tarefa(self):
        tarefa_id = self.tarefas.curselection()
        if tarefa_id:
            tarefa = self.service.get_all()[tarefa_id[0]]
            tarefa.nome = self.entry_nome.get()
            self.service.update(tarefa)
            self.entry_nome.delete(0, tk.END)
            self.atualizar_lista()

    def excluir_tarefa(self):
        tarefa_id = self.tarefas.curselection()
        if tarefa_id:
            self.service.delete(tarefa_id[0])
            self.atualizar_lista()

    def atualizar_lista(self):
        self.tarefas.delete(0, tk.END)
        for t in self.service.get_all():
            self.tarefas.insert(tk.END, t.nome)

root = tk.Tk()
repo = TarefaRepository("tarefas.db")
service = TarefaService(repo)
ui = TarefaUI(root, service)
root.mainloop()
