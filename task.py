import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os
import threading
import time
from datetime import datetime
import requests

CURRENT_VERSION = "1.0.0"
VERSION_URL = "https://raw.githubusercontent.com/tanawin2544/TasksProgram/main/version.txt"
UPDATE_URL = "https://drive.google.com/uc?export=download&id=1HJwuQwIVA8godaeE2p1t1d6nbO3YU96s"

TASKS_FILE = 'tasks.json'

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("320x400")
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(False)
        self.root.attributes('-topmost', True)
        self.root.iconbitmap("icon.ico")  # ไอคอนที่จะแสดงบน Taskbar
        self.root.title("To-Do Widget")   # ต้องมี title ด้วย ถึงจะโชว์ใน Taskbar


        # ✅ ICON
        try:
            self.root.iconbitmap("icon.ico")  # ต้องมีไฟล์ icon.ico ในโฟลเดอร์เดียวกัน
        except:
            pass  # ไม่ทำอะไรถ้าไม่มี icon

        # ✅ CUSTOM TITLE BAR
        self.title_bar = tk.Frame(root, bg="#2c3e50", relief='raised', bd=0, height=28)
        self.title_bar.pack(fill='x')
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)

        self.title_label = tk.Label(self.title_bar, text="📝 To-Do Widget", bg="#2c3e50", fg="white", font=("Kanit", 10))
        self.title_label.pack(side='left', padx=10)

        self.btn_close = tk.Button(self.title_bar, text='✖', command=self.save_and_exit,
                                   bg="#e74c3c", fg='white', bd=0, font=("Arial", 10, "bold"))
        self.btn_close.pack(side='right', padx=5)

        # ✅ TASK ZONE
        self.task_frame = tk.Frame(root, bg="white")
        self.task_frame.pack(fill='both', expand=True)

        self.task_list = []
        self.task_vars = []

        self.load_tasks()

        self.btn_add = tk.Button(root, text="+ Add Task", command=self.add_task)
        self.btn_add.pack(fill='x')

        self.root.protocol("WM_DELETE_WINDOW", self.save_and_exit)

        threading.Thread(target=self.check_reminders, daemon=True).start()
        threading.Thread(target=self.check_for_update, daemon=True).start()

    # ===== MOVE WINDOW =====
    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = self.root.winfo_pointerx() - self._x
        y = self.root.winfo_pointery() - self._y
        self.root.geometry(f'+{x}+{y}')

    # ===== LOAD / SAVE TASKS =====
    def load_tasks(self):
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r') as f:
                self.task_list = json.load(f)
        for task in self.task_list:
            self.create_task(task['text'], task['done'], task.get("reminder"))

    def save_and_exit(self):
        self.task_list = []
        for chk, var, time_label in self.task_vars:
            self.task_list.append({
                "text": chk.cget("text"),
                "done": var.get(),
                "reminder": time_label.cget("text") if time_label else ""
            })
        with open(TASKS_FILE, 'w') as f:
            json.dump(self.task_list, f)
        self.root.destroy()

    # ===== ADD TASK =====
    def add_task(self):
        text = simpledialog.askstring("New Task", "Enter your task:")
        if text:
            reminder = simpledialog.askstring("Reminder", "Enter reminder time (HH:MM 24hr), or leave blank:")
            self.task_list.append({"text": text, "done": False, "reminder": reminder})
            self.create_task(text, False, reminder)

    def create_task(self, text, done=False, reminder=None):
        frame = tk.Frame(self.task_frame, bg="white")
        frame.pack(fill='x', padx=5, pady=3)

        var = tk.BooleanVar(value=done)
        chk = tk.Checkbutton(frame, text=text, variable=var, bg="white", anchor='w')
        chk.pack(side='left', fill='x', expand=True)

        time_label = None
        if reminder:
            time_label = tk.Label(frame, text=reminder, fg='blue', bg="white")
            time_label.pack(side='right')

        self.task_vars.append((chk, var, time_label))

    # ===== REMINDER CHECK =====
    def check_reminders(self):
        while True:
            now = datetime.now().strftime("%H:%M")
            for chk, var, time_label in self.task_vars:
                if time_label and not var.get():
                    task_time = time_label.cget("text")
                    if task_time == now:
                        messagebox.showinfo("Reminder", f"Task: {chk.cget('text')}")
                        time.sleep(60)
            time.sleep(10)

    # ===== UPDATE CHECK =====
    def check_for_update(self):
    try:
        r = requests.get(VERSION_URL, timeout=5)
        latest_version = r.text.strip()
        if latest_version != CURRENT_VERSION:
            answer = messagebox.askyesno("🔄 Update Available", f"New version {latest_version} available. Download now?")
            if answer:
                self.download_update()
    except Exception as e:
        print(f"Update check failed: {e}")

def download_update(self):
    try:
        r = requests.get(UPDATE_URL, stream=True)
        with open("task_latest.exe", "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        messagebox.showinfo("✅ Downloaded", "task_latest.exe is downloaded.\nPlease run the new version manually.")
    except Exception as e:
        messagebox.showerror("❌ Error", f"Download failed:\n{e}")


# ===== RUN =====
if __name__ == '__main__':
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
