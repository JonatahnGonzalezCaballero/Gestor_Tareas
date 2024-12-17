import tkinter as tk
from tkinter import messagebox, Toplevel, Label
import json
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración de la base de datos
Base = declarative_base()
engine = create_engine('sqlite:///tasks.db')
Session = sessionmaker(bind=engine)
session = Session()

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)

Base.metadata.create_all(engine)

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Tareas")

        # Elementos de la interfaz
        self.title_label = tk.Label(root, text="Título de la tarea:")
        self.title_label.pack()

        self.title_entry = tk.Entry(root)
        self.title_entry.pack()

        self.description_label = tk.Label(root, text="Descripción de la tarea:")
        self.description_label.pack()

        self.description_entry = tk.Entry(root)
        self.description_entry.pack()

        self.add_button = tk.Button(root, text="Agregar Tarea", command=self.add_task)
        self.add_button.pack()

        self.task_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=50, height=15)
        self.task_listbox.pack()
        self.task_listbox.bind("<Double-1>", self.show_task_description)

        self.complete_button = tk.Button(root, text="Marcar como Completada", command=self.complete_task)
        self.complete_button.pack()

        self.delete_button = tk.Button(root, text="Eliminar Tarea", command=self.delete_task)
        self.delete_button.pack()

        self.save_button = tk.Button(root, text="Guardar Tareas", command=self.save_tasks)
        self.save_button.pack()

        self.load_button = tk.Button(root, text="Cargar Tareas", command=self.load_tasks)
        self.load_button.pack()

        self.refresh_task_list()

    def add_task(self):
        title = self.title_entry.get().strip()
        description = self.description_entry.get().strip()

        if not title:
            messagebox.showwarning("Error", "El título no puede estar vacío.")
            return

        new_task = Task(title=title, description=description)
        session.add(new_task)
        session.commit()

        self.title_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.refresh_task_list()

    def refresh_task_list(self):
        self.task_listbox.delete(0, tk.END)
        tasks = session.query(Task).all()
        for task in tasks:
            status = "[Completada]" if task.completed else "[Pendiente]"
            self.task_listbox.insert(tk.END, f"{task.id}: {status} {task.title}")

    def complete_task(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showwarning("Error", "Por favor, selecciona una tarea.")
            return

        task_id = int(self.task_listbox.get(selected[0]).split(":")[0])
        task = session.query(Task).get(task_id)
        task.completed = True
        session.commit()
        self.refresh_task_list()

    def delete_task(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showwarning("Error", "Por favor, selecciona una tarea.")
            return

        task_id = int(self.task_listbox.get(selected[0]).split(":")[0])
        task = session.query(Task).get(task_id)
        session.delete(task)
        session.commit()
        self.refresh_task_list()

    def save_tasks(self):
        tasks = session.query(Task).all()
        data = [
            {"id": task.id, "title": task.title, "description": task.description, "completed": task.completed}
            for task in tasks
        ]
        with open("tasks.json", "w") as file:
            json.dump(data, file)
        messagebox.showinfo("Éxito", "Tareas guardadas correctamente.")

    def load_tasks(self):
        try:
            with open("tasks.json", "r") as file:
                data = json.load(file)

            session.query(Task).delete()
            for item in data:
                task = Task(id=item["id"], title=item["title"], description=item["description"], completed=item["completed"])
                session.add(task)
            session.commit()
            self.refresh_task_list()
            messagebox.showinfo("Éxito", "Tareas cargadas correctamente.")
        except FileNotFoundError:
            messagebox.showerror("Error", "No se encontró el archivo tasks.json.")

    def show_task_description(self, event):
        selected = self.task_listbox.curselection()
        if not selected:
            return

        task_id = int(self.task_listbox.get(selected[0]).split(":")[0])
        task = session.query(Task).get(task_id)

        # Crear ventana emergente
        popup = Toplevel(self.root)
        popup.title(f"Descripción de la Tarea: {task.title}")

        description_label = Label(popup, text=f"Descripción:\n{task.description if task.description else 'Sin descripción.'}", wraplength=400)
        description_label.pack(pady=10, padx=10)

        close_button = tk.Button(popup, text="Cerrar", command=popup.destroy)
        close_button.pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()