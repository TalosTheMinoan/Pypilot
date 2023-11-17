import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk, simpledialog

class SimpleIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Python IDE")

        # Update Log
        self.update_log_text = """
        Update Log:
        - Added a popup for Update Log on startup.
        - Replaced tk.Text with tk.scrolledtext.ScrolledText for better navigation.
        - Added Help menu with a link to Python documentation.
        - Added a Run Code menu to execute Python code.
        - Added Clear Console menu to clear the console.
        - Improved the GUI with better styling.
        - Implemented user settings for font size.
        - Added the ability to open new code tabs.
        """
        self.show_update_log_notification()

        # User Settings
        self.font_size = tk.StringVar()
        self.font_size.set("12")

        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand="yes", fill="both")

        # Initial code tab
        self.add_code_tab()

        # Menu Bar
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.add_code_tab)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.destroy)

        # Run Menu
        run_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Code", command=self.run_code)

        # Edit Menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)

        # Console Menu
        console_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Console", menu=console_menu)
        console_menu.add_command(label="Clear Console", command=self.clear_console)
        console_menu.add_checkbutton(label="Show Console", command=self.toggle_console)

        # Settings Menu
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="User Settings", command=self.show_user_settings)

        # Help Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.open_documentation)

    def add_code_tab(self):
        # Text Editor
        text_editor = scrolledtext.ScrolledText(self.notebook, wrap="word", undo=True, font=("Courier New", int(self.font_size.get())))
        text_editor.pack(expand="yes", fill="both")
        self.notebook.add(text_editor, text=f"Untitled {self.notebook.index(tk.END)}")

        # Console
        console = scrolledtext.ScrolledText(self.notebook, wrap="word", height=10, state=tk.DISABLED, font=("Courier New", int(self.font_size.get())))
        console.pack(expand="yes", fill="both")
        console.insert(tk.END, f"Python Console {self.notebook.index(tk.END)}\n")
        self.notebook.add(console, text="Console")

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                text_editor = self.notebook.select().children["!scrolledtext"]
                text_editor.delete(1.0, tk.END)
                text_editor.insert(tk.END, content)

    def save_file(self):
        text_editor = self.notebook.select().children["!scrolledtext"]
        # If the file is already saved, overwrite it
        if hasattr(text_editor, "file_path"):
            with open(text_editor.file_path, "w") as file:
                file.write(text_editor.get(1.0, tk.END))
        # If the file is not saved yet, use Save As
        else:
            self.save_as_file()

    def save_as_file(self):
        text_editor = self.notebook.select().children["!scrolledtext"]
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                   filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(text_editor.get(1.0, tk.END))
                text_editor.file_path = file_path
                # Update the tab name with the file name
                self.notebook.tab(self.notebook.select(), text=file_path)

    def run_code(self):
        text_editor = self.notebook.select().children["!scrolledtext"]
        code = text_editor.get(1.0, tk.END)
        console = self.notebook.select().children["!scrolledtext"]
        result = self.run_python_code(code)
        console.config(state=tk.NORMAL)
        console.insert(tk.END, f"\nOutput:\n{result}\n")
        console.config(state=tk.DISABLED)

    def run_python_code(self, code):
        try:
            result = subprocess.check_output(["python", "-c", code], stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as e:
            result = e.output
        return result

    def open_documentation(self):
        webbrowser.open("https://docs.python.org/3/")

    def show_update_log_notification(self):
        messagebox.showinfo("Update Log", self.update_log_text)

    def clear_console(self):
        console = self.notebook.select().children["!scrolledtext"]
        console.config(state=tk.NORMAL)
        console.delete(1.0, tk.END)
        console.insert(tk.END, f"Python Console {self.notebook.index(tk.END)}\n")
        console.config(state=tk.DISABLED)

    def toggle_console(self):
        console = self.notebook.select().children["!scrolledtext"]
        current_state = console.cget("state")
        new_state = tk.NORMAL if current_state == tk.DISABLED else tk.DISABLED
        console.config(state=new_state)

    def show_user_settings(self):
        font_size = simpledialog.askinteger("User Settings", "Enter font size:", parent=self.root, initialvalue=int(self.font_size.get()))
        if font_size is not None:
            self.font_size.set(str(font_size))
            self.apply_user_settings()

    def apply_user_settings(self):
        for tab_id in self.notebook.tabs():
            tab = self.notebook.nametowidget(tab_id)
            text_editor = tab.children["!scrolledtext"]
            console = self.notebook.tab(tab, "text") == "Console" and tab.children["!scrolledtext"]
            text_editor.configure(font=("Courier New", int(self.font_size.get())))
            if console:
                console.configure(font=("Courier New", int(self.font_size.get())))

    def undo(self):
        text_editor = self.notebook.select().children["!scrolledtext"]
        text_editor.event_generate("<<Undo>>")

    def redo(self):
        text_editor = self.notebook.select().children["!scrolledtext"]
        text_editor.event_generate("<<Redo>>")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleIDE(root)
    root.mainloop()
