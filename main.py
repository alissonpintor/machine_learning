import tkinter as tk
from tkinter import messagebox
import sqlite3

class Task:
    def __init__(self, description, completed=False):
        self.description = description
        self.completed = completed

class TaskRepository:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                             (description text, completed integer)''')
        self.conn.commit()

    def add_task(self, task):
        self.cursor.execute("INSERT INTO tasks (description, completed) VALUES (?, ?)",
                            (task.description, task.completed))
        self.conn.commit()

    def delete_task(self, task_id):
        self.cursor.execute("DELETE FROM tasks WHERE rowid = ?",
                            (task_id,))
        self.conn.commit()

    def get_tasks(self):
        tasks = []
        for row in self.cursor.execute("SELECT rowid, description, completed FROM tasks ORDER BY rowid"):
            tasks.append(Task(row[1], row[2]))
        return tasks

    def mark_as_done(self, task_id):
        self.cursor.execute("UPDATE tasks SET completed = 1 WHERE rowid = ?",
                            (task_id,))
        self.conn.commit()

class TaskListController:
    def __init__(self, window, task_repository):
        self.window = window
        self.task_repository = task_repository

    def add_task(self):
        description = self.entry.get()
        if description:
            self.task_repository.add_task(Task(description))
            self.entry.delete(0, tk.END)
            self.show_tasks()

    def delete_task(self):
        task = self.task_list.get(tk.ACTIVE)
        if task:
            self.task_repository.delete_task(task[0])
            self.show_tasks()

    def show_tasks(self):
        self.task_list.delete(0, tk.END)
        for task in self.task_repository.get_tasks():
            line = (task.description, 'Feito' if task.completed else 'Pendente')
            self.task_list.insert(tk.END, line)

    def mark_as_done(self):
        task = self.task_list.get(tk.ACTIVE)
        if task:
            self.task_repository.mark_as_done(task[0])
            self.show_tasks()

if __name__ == '__main__':
    window = tk.Tk()
    window.title("To-Do List")

    task_repository = TaskRepository('tasks.db')
    task_repository.create_table()

    task_list_controller = TaskListController(window, task_repository)

    entry = tk.Entry(window, width=40)
    entry.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

    add_button = tk.Button(window, text="Add", command=task_list_controller.add_task)
    add_button.grid(row=1, column=0, padx=5, pady=5)

    done_button = tk.Button(window, text="Done", command=task_list_controller.mark_as_done)
    done_button.grid(row=1, column=1, padx=5, pady=5)

    delete_button = tk.Button(window, text="Delete", command=task_list_controller.delete_task)
    delete_button.grid(row=1, column=2, padx=5, pady=5)

    task_list = tk.Listbox(window, width=40)
    task_list.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    task_list_controller.show_tasks()

    window.mainloop()

