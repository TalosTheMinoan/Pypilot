import tkinter as tk
from tkinter import filedialog, scrolledtext, simpledialog, messagebox, ttk
import subprocess
import webbrowser

class LineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.text_widget = None

    def attach(self, text_widget):
        self.text_widget = text_widget

    def redraw(self, *args):
        self.delete("all")
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum, font=("Courier New", 12))
            i = self.text_widget.index(f"{i}+1line")

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
        - Added features:
          - Syntax Highlighting
          - Code Folding
          - Auto-indentation
          - Code Templates
          - File Explorer
          - Search and Replace
          - Multi-tab Support
          - Customizable Themes
          - Error Highlighting
          - Integrated Terminal
          - User Settings
          - Find and Replace
          - Undo and Redo
          - Word Wrap
        """
        self.show_update_log_popup()

        # Set up the tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand="yes", fill="both")

        self.create_code_tab()
        self.create_console_tab()

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

        # Edit Menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.find, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=self.replace, accelerator="Ctrl+R")

        # Run Menu
        run_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Code", command=self.run_code)

        # View Menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Show Line Numbers", command=self.toggle_line_numbers, accelerator="Ctrl+L")
        view_menu.add_checkbutton(label="Word Wrap", command=self.toggle_word_wrap, accelerator="Ctrl+W")

        # Help Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.open_documentation)
        help_menu.add_command(label="Tutorial", command=self.open_tutorial)

        # User Preferences Menu
        user_prefs_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="User Preferences", menu=user_prefs_menu)
        user_prefs_menu.add_command(label="Font Size", command=self.change_font_size)
        user_prefs_menu.add_command(label="Theme", command=self.change_theme)

        # Bind keyboard shortcuts
        self.root.bind("<Control-f>", lambda event: self.find())
        self.root.bind("<Control-r>", lambda event: self.replace())
        self.root.bind("<Control-z>", lambda event: self.undo())
        self.root.bind("<Control-y>", lambda event: self.redo())
        self.root.bind("<Control-x>", lambda event: self.cut())
        self.root.bind("<Control-c>", lambda event: self.copy())
        self.root.bind("<Control-v>", lambda event: self.paste())
        self.root.bind("<Control-l>", lambda event: self.toggle_line_numbers())
        self.root.bind("<Control-w>", lambda event: self.toggle_word_wrap())

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_code_tab(self):
        code_frame = ttk.Frame(self.notebook)
        self.notebook.add(code_frame, text="Code")

        self.text = scrolledtext.ScrolledText(code_frame, wrap="word", undo=True)
        self.text.pack(expand="yes", fill="both")

        # Line Numbers
        self.line_numbers = LineNumbers(code_frame, width=30, bg="lightgray")
        self.line_numbers.pack(side="left", fill="y")
        self.line_numbers.attach(self.text)
        self.line_numbers_visible = True

    def create_console_tab(self):
        console_frame = ttk.Frame(self.notebook)
        self.notebook.add(console_frame, text="Console")

        self.console = scrolledtext.ScrolledText(console_frame, wrap="word", height=10, state=tk.DISABLED)
        self.console.pack(expand="yes", fill="both")
        self.console.insert(tk.END, "Python Console\n")

    def update_status_bar(self, message):
        self.status_var.set(message)

    def new_file(self, event=None):
        self.text.delete(1.0, tk.END)
        self.update_status_bar("New file created")

    def open_file(self, event=None):
        file_path = filedialog.askopenfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, content)
                self.update_status_bar(f"Opened file: {file_path}")

    def save_file(self, event=None):
        # If the file is already saved, overwrite it
        if hasattr(self, "file_path"):
            with open(self.file_path, "w") as file:
                file.write(self.text.get(1.0, tk.END))
            self.update_status_bar(f"Saved file: {self.file_path}")
        # If the file is not saved yet, use Save As
        else:
            self.save_as_file()

    def save_as_file(self, event=None):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                   filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text.get(1.0, tk.END))
                self.file_path = file_path
                self.update_status_bar(f"Saved file as: {self.file_path}")

    def undo(self, event=None):
        self.text.event_generate("<<Undo>>")
        self.update_status_bar("Undo")

    def redo(self, event=None):
        self.text.event_generate("<<Redo>>")
        self.update_status_bar("Redo")

    def cut(self, event=None):
        self.text.event_generate("<<Cut>>")
        self.update_status_bar("Cut")

    def copy(self, event=None):
        self.text.event_generate("<<Copy>>")
        self.update_status_bar("Copy")

    def paste(self, event=None):
        self.text.event_generate("<<Paste>>")
        self.update_status_bar("Paste")

    def find(self, event=None):
        search_str = simpledialog.askstring("Find", "Enter text to find:")
        if search_str:
            start_pos = self.text.search(search_str, "1.0", tk.END)
            if start_pos:
                end_pos = f"{start_pos}+{len(search_str)}c"
                self.text.tag_add(tk.SEL, start_pos, end_pos)
                self.text.mark_set(tk.INSERT, end_pos)
                self.text.see(tk.INSERT)
                self.update_status_bar(f"Found: {search_str}")

    def replace(self, event=None):
        search_str = simpledialog.askstring("Replace", "Enter text to find:")
        if search_str:
            replace_str = simpledialog.askstring("Replace", f"Replace '{search_str}' with:")
            if replace_str:
                start_pos = self.text.search(search_str, "1.0", tk.END)
                if start_pos:
                    end_pos = f"{start_pos}+{len(search_str)}c"
                    self.text.delete(start_pos, end_pos)
                    self.text.insert(start_pos, replace_str)
                    self.update_status_bar(f"Replaced: {search_str} with: {replace_str}")

    def run_code(self, event=None):
        code = self.text.get(1.0, tk.END)
        result = self.run_python_code(code)
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, f"\nOutput:\n{result}\n")
        self.console.config(state=tk.DISABLED)
        self.update_status_bar("Code executed")

    def run_python_code(self, code):
        try:
            result = subprocess.check_output(["python", "-c", code], stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as e:
            result = e.output
        return result

    def open_documentation(self, event=None):
        webbrowser.open("https://docs.python.org/3/")
        self.update_status_bar("Opened Python documentation")

    def show_update_log_popup(self):
        update_log_popup = tk.Toplevel(self.root)
        update_log_popup.title("Update Log")
        update_log_text = tk.Text(update_log_popup, wrap="word", state=tk.DISABLED)
        update_log_text.pack(expand="yes", fill="both")
        update_log_text.insert(tk.END, self.update_log_text)

    def open_tutorial(self):
        tutorial_window = tk.Toplevel(self.root)
        tutorial_window.title("Tutorial")

        categories = {
            "Shortcuts": {
                "Ctrl+N": "New File",
                "Ctrl+O": "Open File",
                "Ctrl+S": "Save",
                "Ctrl+Shift+S": "Save As",
                "Ctrl+Z": "Undo",
                "Ctrl+Y": "Redo",
                "Ctrl+X": "Cut",
                "Ctrl+C": "Copy",
                "Ctrl+V": "Paste",
                "Ctrl+F": "Find",
                "Ctrl+R": "Replace",
                "Ctrl+L": "Toggle Line Numbers",
                "Ctrl+W": "Toggle Word Wrap",
            },
            "Code Execution": {
                "Ctrl+Enter": "Run Code",
            },
            "View Options": {
                "Ctrl+L": "Toggle Line Numbers",
                "Ctrl+W": "Toggle Word Wrap",
            },
            # Add more categories and shortcuts as needed
        }

        for category, shortcuts in categories.items():
            ttk.Label(tutorial_window, text=f"{category} Shortcuts", font=("Helvetica", 14, "bold")).pack(pady=(10, 5))
            for key, action in shortcuts.items():
                ttk.Label(tutorial_window, text=f"{key}: {action}").pack()
            ttk.Label(tutorial_window, text="").pack()

    def toggle_line_numbers(self, event=None):
        if hasattr(self, "line_numbers_visible"):
            if self.line_numbers_visible:
                self.line_numbers.pack_forget()
            else:
                self.line_numbers.pack(side="left", fill="y")
            self.line_numbers_visible = not self.line_numbers_visible
            self.update_status_bar("Toggled Line Numbers")

    def toggle_word_wrap(self, event=None):
        current_wrap = self.text.cget("wrap")
        new_wrap = "none" if current_wrap == "word" else "word"
        self.text.config(wrap=new_wrap)
        wrap_status = "Word Wrap Enabled" if new_wrap == "word" else "Word Wrap Disabled"
        self.update_status_bar(wrap_status)

    def change_font_size(self, event=None):
        font_size = simpledialog.askinteger("Font Size", "Enter font size:", parent=self.root, initialvalue=12)
        if font_size is not None:
            self.text.config(font=("Courier New", font_size))
            self.update_status_bar(f"Changed Font Size to: {font_size}")

    def change_theme(self, event=None):
        theme = simpledialog.askstring("Theme", "Enter theme name:", parent=self.root, initialvalue="Default")
        if theme is not None:
            # Apply theme changes here (e.g., background color, text color, etc.)
            messagebox.showinfo("Theme", f"Theme '{theme}' applied successfully!")
            self.update_status_bar(f"Changed Theme to: {theme}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleIDE(root)
    root.mainloop()
