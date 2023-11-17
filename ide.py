import tkinter as tk
from tkinter import filedialog, scrolledtext
import subprocess
import webbrowser

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
        """
        self.show_update_log_popup()

        self.text = scrolledtext.ScrolledText(self.root, wrap="word", undo=True)
        self.text.pack(expand="yes", fill="both")

        # Console
        self.console = scrolledtext.ScrolledText(self.root, wrap="word", height=10, state=tk.DISABLED)
        self.console.pack(expand="yes", fill="both")
        self.console.insert(tk.END, "Python Console\n")

        # Menu Bar
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.destroy)

        # Run Menu
        run_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Code", command=self.run_code)

        # Help Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.open_documentation)

    def new_file(self):
        self.text.delete(1.0, tk.END)

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, content)

    def save_file(self):
        # If the file is already saved, overwrite it
        if hasattr(self, "file_path"):
            with open(self.file_path, "w") as file:
                file.write(self.text.get(1.0, tk.END))
        # If the file is not saved yet, use Save As
        else:
            self.save_as_file()

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                   filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text.get(1.0, tk.END))
                self.file_path = file_path

    def run_code(self):
        code = self.text.get(1.0, tk.END)
        result = self.run_python_code(code)
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, f"\nOutput:\n{result}\n")
        self.console.config(state=tk.DISABLED)

    def run_python_code(self, code):
        try:
            result = subprocess.check_output(["python", "-c", code], stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as e:
            result = e.output
        return result

    def open_documentation(self):
        webbrowser.open("https://docs.python.org/3/")

    def show_update_log_popup(self):
        update_log_popup = tk.Toplevel(self.root)
        update_log_popup.title("Update Log")
        update_log_text = tk.Text(update_log_popup, wrap="word", state=tk.DISABLED)
        update_log_text.pack(expand="yes", fill="both")
        update_log_text.insert(tk.END, self.update_log_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleIDE(root)
    root.mainloop()
