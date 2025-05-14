import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os
import threading
import time
from datetime import datetime
import requests
import subprocess
import sys

CURRENT_VERSION = "1.0.3"
VERSION_URL = "https://raw.githubusercontent.com/tanawin2544/TasksProgram/refs/heads/main/version.txt"
UPDATE_URL = "https://drive.google.com/uc?export=download&id=1Av8bKGocJkSE5RQItgbFrPF3JiaubJqw"

TASKS_FILE = 'tasks.json'

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("320x400")
        self.root.attributes('-topmost', True)
        self.root.title("To-Do Widget")

        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

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
            downloaded_file = f"task_update_v{int(time.time())}.exe"
            final_filename = "task.exe"

            r = requests.get(UPDATE_URL, stream=True)
            with open(downloaded_file, "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)

            messagebox.showinfo("✅ Downloaded", "Update downloaded. Replacing old version...")

            # ✅ สร้าง .bat สำหรับลบตัวเก่า + เปลี่ยนชื่อ + เปิดใหม่
            script_name = "update_runner.bat"
            with open(script_name, "w") as bat:
                bat.write(f"""@echo off
timeout /t 1 >nul
del "{os.path.basename(sys.argv[0])}" >nul
rename "{downloaded_file}" "{final_filename}"
start "" "{final_filename}"
del "%~f0"
""")

            # ✅ รัน .bat
            subprocess.Popen([script_name], shell=True)

            # ✅ ปิดโปรแกรมเก่า
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("❌ Error", f"Download failed:\n{e}")

# ===== RUN =====
if __name__ == '__main__':
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
