import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk, simpledialog
from pygments import highlight
from pygments.lexers import HtmlLexer, CssLexer, JavascriptLexer
from pygments.token import Keyword, Name, String, Comment, Text
import webbrowser
import os
import tempfile

class SimpleIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Simple IDE")
        self.root.geometry("800x600")
        self.create_menu()
        self.create_text_area()
        self.create_language_selector()
        self.set_dark_theme()
        self.current_language = 'HTML'
        self.file_path = None
        self.autocomplete_list = {
            'JavaScript': ['function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'return', 'document', 'getElementById', 'querySelector'],
            'CSS': ['color', 'background', 'margin', 'padding', 'border', 'display', 'flex', 'grid', 'position', 'width', 'height'],
            'HTML': ['div', 'span', 'a', 'p', 'h1', 'h2', 'h3', 'ul', 'li', 'img']
        }
        self.create_status_bar()

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        file_menu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        edit_menu = tk.Menu(menu)
        menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Find", command=self.find_text)
        edit_menu.add_command(label="Replace", command=self.replace_text)
        edit_menu.add_separator()
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)

        run_menu = tk.Menu(menu)
        menu.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run JavaScript", command=self.run_javascript)
        run_menu.add_command(label="Run HTML", command=self.run_html)

    def create_text_area(self):
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Consolas", 12))
        self.text_area.pack(expand=True, fill='both')
        self.text_area.bind("<KeyRelease>", self.highlight_syntax)
        self.text_area.bind("<KeyRelease>", self.update_status_bar)
        self.text_area.bind("<Key>", self.autocomplete)

    def create_language_selector(self):
        self.language_var = tk.StringVar(value='HTML')
        language_frame = tk.Frame(self.root)
        language_frame.pack(fill=tk.X)
        language_label = tk.Label(language_frame, text="Select Language:")
        language_label.pack(side=tk.LEFT, padx=5)
        language_selector = ttk.Combobox(language_frame, textvariable=self.language_var, 
                                           values=['HTML', 'CSS', 'JavaScript'])
        language_selector.pack(side=tk.LEFT, padx=5)
        language_selector.bind("<<ComboboxSelected>>", self.change_language)

    def create_status_bar(self):
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def set_dark_theme(self):
        self.text_area.config(bg="#282a36", fg="#f8f8f2", insertbackground='white')

    def highlight_syntax(self, event=None):
        code = self.text_area.get("1.0", tk.END)
        self.text_area.tag_remove("keyword", "1.0", tk.END)
        self.text_area.tag_remove("string", "1.0", tk.END)
        self.text_area.tag_remove("comment", "1.0", tk.END)

        lexer = self.get_lexer()
        tokens = lexer.get_tokens(code)

        for token_type, token_string in tokens:
            start_index = self.text_area.index("1.0 + %d chars" % len(token_string))
            end_index = self.text_area.index("1.0 + %d chars" % (len(token_string) + len(token_string)))
            if token_type in (Keyword, Name):
                self.text_area.tag_add("keyword", start_index, end_index)
            elif token_type in (String,):
                self.text_area.tag_add("string", start_index, end_index)
            elif token_type in (Comment,):
                self.text_area.tag_add("comment", start_index, end_index)

        self.text_area.tag_config("keyword", foreground="#66d9ef")  # Cyan
        self.text_area.tag_config("comment", foreground="#6272a4")  # Gray

    def get_lexer(self):
        if self.current_language == 'HTML':
            return HtmlLexer()
        elif self.current_language == 'CSS':
            return CssLexer()
        elif self.current_language == 'JavaScript':
            return JavascriptLexer()
        return HtmlLexer()

    def change_language(self, event):
        self.current_language = self.language_var.get()
        self.highlight_syntax()

    def save_file(self):
        if not self.file_path:
            self.file_path = filedialog.asksaveasfilename(defaultextension=".html",
                                                           filetypes=[("HTML files", "*.html"),
                                                                      ("CSS files", "*.css"),
                                                                      ("JavaScript files", "*.js"),
                                                                      ("All files", "*.*")])
        if self.file_path:
            try:
                with open(self.file_path, "w", encoding='utf-8') as f:
                    f.write(self.text_area.get("1.0", tk.END))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def open_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("HTML files", "*.html"),
                                                                ("CSS files", "*.css"),
                                                                ("JavaScript files", "*.js"),
                                                                ("All files", "*.*")])
        if self.file_path:
            encoding = simpledialog.askstring("Input", "Enter encoding (e.g., utf-8, cp1251):", initialvalue="utf-8")
            if not encoding:
                encoding = "utf-8"  # Default encoding
            try:
                with open(self.file_path, "r", encoding=encoding) as f:
                    code = f.read()
                    self.text_area.delete("1.0", tk.END)
                    self.text_area.insert(tk.END, code)
                    self.language_var.set(self.file_path.split('.')[-1].upper())
                    self.change_language(None)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")

    def run_javascript(self):
        html_content = self.text_area.get("1.0", tk.END)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_file:
            temp_file.write(f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Run JavaScript</title>
            </head>
            <body>
                <script>
                {html_content}
                </script>
            </body>
            </html>
            """.encode('utf-8'))
            temp_file_path = temp_file.name
            
        webbrowser.open(f"file://{os.path.abspath(temp_file_path)}")

    def run_html(self):
        html_content = self.text_area.get("1.0", tk.END)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_file:
            temp_file.write(html_content.encode('utf-8'))
            temp_file_path = temp_file.name
            
        webbrowser.open(f"file://{os.path.abspath(temp_file_path)}")

    def autocomplete(self, event):
        if event.char == '.':
            self.show_autocomplete()
        elif event.keysym == "BackSpace":
            self.hide_autocomplete()
        elif event.keysym == "Return":
            self.hide_autocomplete()

    def hide_autocomplete(self):
        if hasattr(self, 'suggestion_window'):
            self.suggestion_window.destroy()

    def show_autocomplete(self):
        current_word = self.get_current_word()
        if current_word:
            suggestions = [word for word in self.autocomplete_list[self.current_language] if word.startswith(current_word)]
            if suggestions:
                self.show_suggestions(suggestions)

    def get_current_word(self):
        cursor_index = self.text_area.index(tk.INSERT)
        line = self.text_area.get(f"{cursor_index.split('.')[0]}.0", cursor_index)
        return line.split()[-1] if line else ""

    def show_suggestions(self, suggestions):
        # Создаем новое окно для подсказок
        self.suggestion_window = tk.Toplevel(self.root)
        self.suggestion_window.wm_title("Suggestions")
        self.suggestion_window.geometry("200x100")
        self.suggestion_listbox = tk.Listbox(self.suggestion_window)
        self.suggestion_listbox.pack(fill=tk.BOTH, expand=True)

        for suggestion in suggestions:
            self.suggestion_listbox.insert(tk.END, suggestion)

        self.suggestion_listbox.bind("<Double-Button-1>", self.insert_suggestion)
        self.suggestion_listbox.bind("<Return>", self.insert_suggestion)
        self.suggestion_window.transient(self.root)
        self.suggestion_window.grab_set()

    def insert_suggestion(self, event):
        selected = self.suggestion_listbox.curselection()
        if selected:
            suggestion = self.suggestion_listbox.get(selected[0])
            cursor_index = self.text_area.index(tk.INSERT)
            line_start = f"{cursor_index.split('.')[0]}.0"
            line_end = cursor_index
            self.text_area.delete(line_start, line_end)
            self.text_area.insert(line_start, suggestion + " ")
            self.suggestion_window.destroy()

    def update_status_bar(self, event=None):
        line, column = self.text_area.index(tk.INSERT).split('.')
        self.status_bar.config(text=f"Line: {line}, Column: {column}")

    def find_text(self):
        find_window = tk.Toplevel(self.root)
        find_window.title("Find")
        tk.Label(find_window, text="Find:").grid(row=0, column=0)
        find_entry = tk.Entry(find_window)
        find_entry.grid(row=0, column=1)
        tk.Button(find_window, text="Find", command=lambda: self.perform_find(find_entry.get())).grid(row=0, column=2)

    def perform_find(self, text):
        start_index = self.text_area.search(text, "1.0", tk.END)
        if start_index:
            end_index = f"{start_index}+{len(text)}c"
            self.text_area.tag_add("highlight", start_index, end_index)
            self.text_area.mark_set("insert", end_index)
            self.text_area.see("insert")
            self.text_area.tag_config("highlight", background="yellow")
        else:
            messagebox.showinfo("Find", "Text not found.")

    def replace_text(self):
        replace_window = tk.Toplevel(self.root)
        replace_window.title("Replace")
        tk.Label(replace_window, text="Find:").grid(row=0, column=0)
        find_entry = tk.Entry(replace_window)
        find_entry.grid(row=0, column=1)
        tk.Label(replace_window, text="Replace with:").grid(row=1, column=0)
        replace_entry = tk.Entry(replace_window)
        replace_entry.grid(row=1, column=1)
        tk.Button(replace_window, text="Replace", command=lambda: self.perform_replace(find_entry.get(), replace_entry.get())).grid(row=2, column=1)

    def perform_replace(self, find_text, replace_text):
        content = self.text_area.get("1.0", tk.END)
        new_content = content.replace(find_text, replace_text)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", new_content)

    def undo(self):
        try:
            self.text_area.edit_undo()
        except Exception as e:
            messagebox.showerror("Error", f"Undo failed: {e}")

    def redo(self):
        try:
            self.text_area.edit_redo()
        except Exception as e:
            messagebox.showerror("Error", f"Redo failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    ide = SimpleIDE(root)
    root.mainloop()


