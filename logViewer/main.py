import os
import threading
import tkinter as tk
import boto3
from tkinter import ttk, messagebox, scrolledtext, filedialog
from botocore.exceptions import BotoCoreError, ClientError
from PIL import Image, ImageTk

from secrets.constants import LOCAL_DIR
from utils import sync_s3_files, file_text, file_text_doi
from pipeline import pipeline, insert_ip_info, extract_commands
from diagram_drawers import plot_all


class LogViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("logViewer")
        self.geometry("800x600")

        main_frame = tk.Frame(self)
        main_frame.pack(fill='both', expand=True)

        # Left side - file_frame
        # Scrollable left panel (file_frame)
        file_container = tk.Frame(main_frame, width=270, bg="lightgray", bd=2, relief="groove")
        file_container.pack(side='left', fill='y', padx=5, pady=5)
        file_container.pack_propagate(False)

        # Create canvas + scrollbar inside the container
        canvas = tk.Canvas(file_container, bg="lightgray", highlightthickness=0)
        scrollbar = ttk.Scrollbar(file_container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Actual scrollable frame
        self.file_frame = tk.Frame(canvas, bg="lightgray")
        self.file_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.file_frame, anchor="nw")

        self.add_directory_section("logs", "./logs", self.file_frame)
        self.add_directory_section("graphs", "./graphs", self.file_frame)

        # Right side - everything else
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side='left', fill='both', expand=True)

        try:
            self.s3 = boto3.client('s3')
        except Exception:
            self.s3 = None

        # Controls (refresh button + no_lines)
        controls_frame = tk.Frame(right_frame)
        controls_frame.pack(fill='x', padx=10, pady=5)

        # login logic
        self.login_button = ttk.Button(controls_frame, text='AWS Login', command=self.open_login_popup)
        self.login_button.pack(side='left', padx=5)

        # refresh button
        self.refresh_button = ttk.Button(controls_frame, text="Refresh logs", command=self.refresh_files)
        self.refresh_button.pack(side='left', padx=5)

        # pipeline button
        self.pipeline_button = ttk.Button(controls_frame, text="Do pipeline", command=self.call_pipeline)
        self.pipeline_button.pack(side='left', padx=5)

        # get ip button
        self.get_ip_button = ttk.Button(controls_frame, text="Get IP data", command=self.retrieve_ip_data)
        self.get_ip_button.pack(side='left', padx=5)

        # command extractor button
        self.command_extract_button = ttk.Button(controls_frame, text="Extract commands", command=self.get_commands)
        self.command_extract_button.pack(side='left', padx=5)

        # draw diagrams button
        self.draw_diagrams_button = ttk.Button(controls_frame, text="Draw diagrams", command=self.draw_diagrams)
        self.draw_diagrams_button.pack(side='left', padx=5)

        # for file listing
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

    def refresh_files(self):
        if self.s3 is None:
            self.open_login_popup()
            return

        # Create loading popup
        loading_popup = tk.Toplevel(self)
        loading_popup.title("Loading...")
        loading_popup.geometry("200x100")
        loading_popup.transient(self)
        loading_popup.grab_set()

        label = ttk.Label(loading_popup, text="Loading, please wait...")
        label.pack(expand=True, pady=20, padx=20)

        def worker():
            try:
                sync_s3_files(self.s3)
            except (BotoCoreError, ClientError, AttributeError) as e:
                self.after(0, lambda: messagebox.showerror("S3 Error", f"Failed to list files:\n{e}"))
            finally:
                # Close loading popup on main thread
                self.after(0, loading_popup.destroy)

        threading.Thread(target=worker, daemon=True).start()

    def call_pipeline(self):
        # Create loading popup
        loading_popup = tk.Toplevel(self)
        loading_popup.title("Loading...")
        loading_popup.geometry("200x100")
        loading_popup.transient(self)
        loading_popup.grab_set()

        label = ttk.Label(loading_popup, text="Processing data, please wait...")
        label.pack(expand=True, pady=20, padx=20)

        def worker():
            try:
                files = [f for f in os.listdir(LOCAL_DIR)
                         if os.path.isfile(os.path.join(LOCAL_DIR, f)) and not f.endswith('.etag') and f.find('ssh') != -1]

                pipeline(files)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Something wrong occurred during pipeline:\n{e}"))
            finally:
                self.after(0, loading_popup.destroy)

        threading.Thread(target=worker, daemon=True).start()

    def retrieve_ip_data(self):
        # Create loading popup
        loading_popup = tk.Toplevel(self)
        loading_popup.title("Loading...")
        loading_popup.geometry("200x100")
        loading_popup.transient(self)
        loading_popup.grab_set()

        label = ttk.Label(loading_popup, text="Extracting IP data, please wait...")
        label.pack(expand=True, pady=20, padx=20)

        def worker():
            try:
                insert_ip_info()
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Something wrong occurred during ip data extraction:\n{e}"))
            finally:
                self.after(0, loading_popup.destroy)

        threading.Thread(target=worker, daemon=True).start()

    def get_commands(self):
        # Create loading popup
        loading_popup = tk.Toplevel(self)
        loading_popup.title("Loading...")
        loading_popup.geometry("200x100")
        loading_popup.transient(self)
        loading_popup.grab_set()

        label = ttk.Label(loading_popup, text="Extracting commands, please wait...")
        label.pack(expand=True, pady=20, padx=20)

        def worker():
            try:
                extract_commands()
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Something wrong occurred command extraction:\n{e}"))
            finally:
                self.after(0, loading_popup.destroy)

        threading.Thread(target=worker, daemon=True).start()

    def draw_diagrams(self):
        # Create loading popup
        loading_popup = tk.Toplevel(self)
        loading_popup.title("Loading...")
        loading_popup.geometry("200x100")
        loading_popup.transient(self)
        loading_popup.grab_set()

        label = ttk.Label(loading_popup, text="Drawing diagrams, please wait...")
        label.pack(expand=True, pady=20, padx=20)

        def worker():
            try:
                plot_all()
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Something wrong occurred diagram drowing:\n{e}"))
            finally:
                self.after(0, loading_popup.destroy)

        threading.Thread(target=worker, daemon=True).start()

    def add_directory_section(self, name, path, parent):
        section_frame = tk.Frame(parent, bg="lightgray")
        section_frame.pack(fill='x', pady=5)

        collapsed = tk.BooleanVar(value=False)

        def toggle():
            if collapsed.get():
                collapsed.set(False)
                btn.config(text=f"{name} ▼")
                file_button_frame .pack(fill='x', padx=10)
            else:
                collapsed.set(True)
                btn.config(text=f"{name} ▶")
                file_button_frame .pack_forget()

        btn = ttk.Button(section_frame, text=f"{name} ▼", command=toggle)
        btn.pack(fill='x')

        file_button_frame = tk.Frame(section_frame, bg="lightgray")
        file_button_frame.pack(fill='x', padx=10)

        try:
            files = os.listdir(path)
            for f in files:
                if not f.endswith('.etag'):
                    file_path = os.path.join(path, f)
                    file_btn = ttk.Button(
                        file_button_frame,
                        text=f,
                        command=lambda fp=file_path: self.printFile(fp)
                    )
                    file_btn.pack(fill='x', pady=1)
        except Exception as e:
            error_label = tk.Label(file_button_frame, text=f"Error: {e}", bg="lightgray", fg="red")
            error_label.pack()

    def printFile(self, path):
        ext = os.path.splitext(path)[1].lower()

        # destroy old notebook tabs
        for tab_id in self.notebook.tabs():
            self.notebook.forget(tab_id)

        tab = ttk.Frame(self.notebook)

        if ext == '.png':
            img = Image.open(path)
            img.thumbnail((self.notebook.winfo_width(), self.notebook.winfo_height()), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            label = tk.Label(tab, image=photo)
            label.image = photo
            label.pack(expand=True, fill='both')

        else:
            # Show text content
            content = file_text_doi(path)
            text_area = scrolledtext.ScrolledText(tab, wrap=tk.WORD, font=("Consolas", 10))
            text_area.insert(tk.END, content)
            text_area.pack(expand=True, fill='both')

        self.notebook.add(tab, text=os.path.basename(path))

    def open_login_popup(self):
        popup = tk.Toplevel()
        popup.title("AWS Keys Input")
        popup.geometry("400x400")
        popup.grab_set()

        ttk.Label(popup, text="AWS keys:").pack(pady=(20, 5))

        text_area = scrolledtext.ScrolledText(popup, width=40, height=10, font=("Consolas", 12))
        text_area.pack(pady=5, padx=10, fill='both', expand=True)

        def do_login():
            content = text_area.get("1.0", tk.END).strip()
            # Save to file or further processing here
            try:
                with open(r"C:\Users\andre\.aws\credentials", "w", encoding="utf-8") as f:
                    f.write(content)
                self.s3 = boto3.client('s3')
                print("File saved successfully.")
            except Exception as e:
                print(f"Error saving file: {e}")
            popup.destroy()

        login_btn = ttk.Button(popup, text="Login", command=do_login)
        login_btn.pack(pady=20)


if __name__ == "__main__":
    app = LogViewer()
    app.mainloop()
