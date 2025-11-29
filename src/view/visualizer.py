import sys
import os
import io
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText


class CompilerVisualizer:
    def __init__(self, master=None):
        self.master = master or tk.Tk()
        self.master.title("FunLang - Compilation Visualizer")

        # State for intermediates
        self.source_text = ""
        self.tokens = None
        self.ast = None
        self.semantic_result = None  # (is_valid, errors)
        self.cpp_code = None

        self._build_ui()

    def _build_ui(self):
        # Top controls
        top = tk.Frame(self.master)
        top.pack(fill="x", padx=6, pady=6)

        tk.Button(top, text="Load File", command=self.load_file).pack(side="left")
        tk.Button(top, text="Run Selected", command=self.run_selected).pack(
            side="left", padx=6
        )
        tk.Button(top, text="Run All", command=self.run_all).pack(side="left")
        tk.Button(top, text="Clear Outputs", command=self.clear_outputs).pack(
            side="left", padx=6
        )

        nav = tk.Frame(top)
        nav.pack(side="right")
        tk.Button(nav, text="Prev", command=self.prev_tab).pack(side="left")
        tk.Button(nav, text="Next", command=self.next_tab).pack(side="left", padx=4)

        # Main panes: left=source, right=tabs for steps
        main = tk.PanedWindow(self.master, sashrelief="raised")
        main.pack(fill="both", expand=True, padx=6, pady=6)

        left = tk.Frame(main)
        right = tk.Frame(main)
        main.add(left)
        main.add(right)

        tk.Label(left, text="Source").pack(anchor="w")
        self.src_editor = ScrolledText(left, width=60, height=40)
        self.src_editor.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill="both", expand=True)

        self.tabs = {}

        # lexing tab
        frame = tk.Frame(self.notebook)
        table = ttk.Treeview(
            frame, columns=("Token", "Lexeme", "Line", "Column"), show="headings"
        )
        table.heading("Token", text="Token")
        table.heading("Lexeme", text="Lexeme")
        table.heading("Line", text="Line")
        table.heading("Column", text="Column")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=vsb.set)
        table.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.notebook.add(frame, text="Lexing")
        self.tabs["Lexing"] = table

        frame = tk.Frame(self.notebook)
        parse_tree = ttk.Treeview(frame, columns=("Info",), show="tree")
        parse_tree.pack(side="left", fill="both", expand=True)
        parse_vsb = ttk.Scrollbar(frame, orient="vertical", command=parse_tree.yview)
        parse_tree.configure(yscrollcommand=parse_vsb.set)
        parse_vsb.pack(side="right", fill="y")
        self.notebook.add(frame, text="Parsing")
        self.tabs["Parsing"] = parse_tree

        for name in ("Semantic", "Codegen"):
            frame = tk.Frame(self.notebook)
            txt = ScrolledText(frame, wrap="word")
            txt.pack(fill="both", expand=True)
            txt.configure(state="disabled")
            self.notebook.add(frame, text=name)
            self.tabs[name] = txt

        codegen_frame = self.notebook.nametowidget(self.notebook.tabs()[-1])
        btn_frame = tk.Frame(codegen_frame)
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="Save C++", command=self.save_cpp).pack(
            side="left", padx=4, pady=4
        )

    def prev_tab(self):
        idx = self.notebook.index(self.notebook.select())
        if idx > 0:
            self.notebook.select(idx - 1)

    def next_tab(self):
        idx = self.notebook.index(self.notebook.select())
        if idx < len(self.notebook.tabs()) - 1:
            self.notebook.select(idx + 1)

    def load_file(self):
        p = filedialog.askopenfilename(
            filetypes=[("FunLang", "*.fun"), ("All files", "*")]
        )
        if not p:
            return
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = f.read()
            self.src_editor.delete("1.0", "end")
            self.src_editor.insert("1.0", data)
            self.clear_intermediates()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")

    def save_cpp(self):
        if not self.cpp_code:
            messagebox.showinfo(
                "Info", "No hay código C++ generado. Ejecute la fase Codegen primero."
            )
            return
        p = filedialog.asksaveasfilename(
            defaultextension=".cpp", filetypes=[("C++", "*.cpp"), ("All files", "*")]
        )
        if not p:
            return
        try:
            with open(p, "w", encoding="utf-8") as f:
                f.write(self.cpp_code)
            messagebox.showinfo("Saved", f"Código C++ guardado en:\n{p}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

    def run_selected(self):
        name = self.notebook.tab(self.notebook.select(), "text")
        try:
            if name == "Lexing":
                self.run_lexing()
            elif name == "Parsing":
                self.run_parsing()
            elif name == "Semantic":
                self.run_semantic()
            elif name == "Codegen":
                self.run_codegen()
        except Exception:
            tb = traceback.format_exc()
            self._set_tab_text(name, f"Unhandled exception:\n{tb}")

    def run_all(self):
        try:
            self.run_lexing()
            self.run_parsing()
            self.run_semantic()
            self.run_codegen()
        except Exception:
            messagebox.showerror(
                "Error",
                "Ocurrió un error durante 'Run All'. Revise las salidas de cada pestaña.",
            )

    def clear_outputs(self):
        self.clear_intermediates()
        for name in self.tabs:
            self._set_tab_text(name, "")
        for name, widget in self.tabs.items():
            if isinstance(widget, ttk.Treeview):
                for iid in widget.get_children():
                    widget.delete(iid)
            else:
                self._set_tab_text(name, "")

    def clear_intermediates(self):
        self.tokens = None
        self.ast = None
        self.semantic_result = None
        self.cpp_code = None

    def _populate_lexing_table(self, tokens_or_lines):
        table = self.tabs.get("Lexing")
        if not isinstance(table, ttk.Treeview):
            self._set_tab_text(
                "Lexing",
                (
                    tokens_or_lines
                    if isinstance(tokens_or_lines, str)
                    else "\n".join(map(str, tokens_or_lines))
                ),
            )
            return

        for iid in table.get_children():
            table.delete(iid)

        rows = []
        if isinstance(tokens_or_lines, str):
            lines = tokens_or_lines.splitlines()
            for line in lines:
                rows.append((line, "", "", ""))
        else:
            try:
                for t in tokens_or_lines:
                    if isinstance(t, (list, tuple)) and len(t) >= 4:
                        tok_type, tok_val, lineno, col = t[:4]
                        rows.append(
                            (str(tok_type), repr(tok_val), str(lineno), str(col))
                        )
                    else:
                        rows.append((str(t), "", "", ""))
            except Exception:
                rows = [(str(tokens_or_lines), "", "", "")]

        for vals in rows:
            table.insert("", "end", values=vals)

    def run_lexing(self):
        src = self.src_editor.get("1.0", "end").rstrip()
        self.source_text = src
        if not src.strip():
            self._set_tab_text(
                "Lexing", "(No source)\nLoad a file or paste source on the left."
            )
            return

        lexer = None
        try:
            from ..lexer import create_lexer as _create_lexer

            lexer = _create_lexer()
        except Exception:
            try:
                from src.lexer import create_lexer as _create_lexer

                lexer = _create_lexer()
            except Exception as e:
                self._set_tab_text("Lexing", f"Could not import lexer:\n{e}")
                return

        try:
            tokens = lexer.tokenize(src)
            self.tokens = tokens
            self._populate_lexing_table(tokens)
        except Exception as e:
            self._set_tab_text(
                "Lexing", f"Lexing error:\n{e}\n\n{traceback.format_exc()}"
            )

    def run_parsing(self):
        src = self.src_editor.get("1.0", "end").rstrip()
        if not src.strip():
            self._set_tab_text("Parsing", "(No source)")
            return

        try:
            from ..parser import create_parser as _create_parser
        except Exception:
            try:
                from src.parser import create_parser as _create_parser
            except Exception as e:
                self._set_tab_text("Parsing", f"Could not import parser:\n{e}\n{traceback.format_exc()}")
                return

        parser = None
        try:
            parser = _create_parser()
            ast = parser.parse(src)
            self.ast = ast
            if ast is None:
                self._set_tab_text(
                    "Parsing", "Parser returned None or failed to build AST"
                )
                return

            # Populate the parsing tree view
            try:
                self._populate_parsing_tree(ast)
                # switch to Parsing tab so user sees the tree
                for i in range(len(self.notebook.tabs())):
                    if self.notebook.tab(i, "text") == "Parsing":
                        self.notebook.select(i)
                        break
            except Exception as tree_err:
                # Fallback: try to print AST textually using ASTPrinter
                try:
                    try:
                        from ..ast_nodes import ASTPrinter
                    except Exception:
                        from src.ast_nodes import ASTPrinter

                    buf = io.StringIO()
                    import sys as _sys

                    old = _sys.stdout
                    _sys.stdout = buf
                    try:
                        p = ASTPrinter()
                        p.visit(ast)
                    finally:
                        _sys.stdout = old
                    text = buf.getvalue()
                    self._set_tab_text("Parsing", text or f"(AST printed nothing)\nTree error: {tree_err}")
                except Exception:
                    self._set_tab_text(
                        "Parsing",
                        f"(AST repr)\n{repr(ast)}\n\n(Tree error: {tree_err})\n(ASTPrinter also failed)\n{traceback.format_exc()}",
                    )
        except Exception as e:
            self._set_tab_text(
                "Parsing", f"Parsing error:\n{e}\n\n{traceback.format_exc()}"
            )

    def run_semantic(self):
        if self.ast is None:
            self.run_parsing()
        if self.ast is None:
            self._set_tab_text("Semantic", "No AST available. Run Parsing first.")
            return

        try:
            try:
                from ..semantic import create_analyzer as _create_analyzer
            except Exception:
                from src.semantic import create_analyzer as _create_analyzer
        except Exception as e:
            self._set_tab_text("Semantic", f"Could not import semantic analyzer:\n{e}")
            return

        try:
            analyzer = _create_analyzer()
            # analyze() returns bool, errors are in analyzer.errors
            is_valid = analyzer.analyze(self.ast)
            errors = getattr(analyzer, 'errors', [])
            self.semantic_result = (is_valid, errors)
            lines = [f"Valid: {is_valid}"]
            if not errors:
                lines.append("(No semantic errors)")
            else:
                for err in errors:
                    try:
                        lines.append(str(err))
                    except Exception:
                        lines.append(repr(err))
            self._set_tab_text("Semantic", "\n".join(lines))
        except Exception as e:
            self._set_tab_text(
                "Semantic", f"Semantic analysis error:\n{e}\n\n{traceback.format_exc()}"
            )

    def run_codegen(self):
        if self.ast is None:
            self.run_parsing()
        if self.ast is None:
            self._set_tab_text("Codegen", "No AST available. Run Parsing first.")
            return

        try:
            try:
                from ..codegen import create_generator as _create_generator
            except Exception:
                from src.codegen import create_generator as _create_generator
        except Exception as e:
            self._set_tab_text("Codegen", f"Could not import code generator:\n{e}")
            return

        try:
            gen = _create_generator()
            cpp = gen.generate(self.ast)
            self.cpp_code = cpp
            self._set_tab_text("Codegen", cpp or "(no cpp generated)")
        except Exception as e:
            self._set_tab_text(
                "Codegen", f"Codegen error:\n{e}\n\n{traceback.format_exc()}"
            )

    def _populate_parsing_tree(self, ast_root):
        tree = self.tabs.get("Parsing")
        if not isinstance(tree, ttk.Treeview):
            self._set_tab_text("Parsing", repr(ast_root))
            return

        for iid in tree.get_children():
            tree.delete(iid)

        ASTNode = None
        try:
            try:
                from ..ast_nodes import ASTNode as _ASTNode
            except Exception:
                from src.ast_nodes import ASTNode as _ASTNode
            ASTNode = _ASTNode
        except Exception:
            ASTNode = None

        def _insert(parent, name, node):
            if node is None:
                return tree.insert(parent, "end", text=f"{name}: None")

            if isinstance(node, (str, int, float, bool)):
                return tree.insert(parent, "end", text=f"{name}: {repr(node)}")
            
            if isinstance(node, (list, tuple)):
                nid = tree.insert(parent, "end", text=f"{name} [list]")
                for i, item in enumerate(node):
                    _insert(nid, f"[{i}]", item)
                return nid

            is_astnode = ASTNode is not None and isinstance(node, ASTNode)
            has_vars = hasattr(node, "__dict__")
            if is_astnode or has_vars:
                label = f"{name}: {node.__class__.__name__}"
                nid = tree.insert(parent, "end", text=label)
                try:
                    attrs = vars(node)
                except Exception:
                    attrs = {}

                for k, v in attrs.items():
                    if k.startswith("_"):
                        continue
                    if v is None or isinstance(v, (str, int, float, bool)):
                        tree.insert(nid, "end", text=f"{k}: {repr(v)}")
                    elif isinstance(v, (list, tuple)):
                        child = tree.insert(nid, "end", text=f"{k} [list]")
                        for i, item in enumerate(v):
                            _insert(child, f"[{i}]", item)
                    else:
                        _insert(nid, k, v)
                return nid

            return tree.insert(parent, "end", text=f"{name}: {repr(node)}")

        root_id = _insert(
            "",
            ast_root.__class__.__name__ if hasattr(ast_root, "__class__") else "AST",
            ast_root,
        )
        try:
            tree.item(root_id, open=True)
            for child in tree.get_children(root_id):
                tree.item(child, open=False)
        except Exception:
            pass

    def _set_tab_text(self, tab_name: str, text: str):
        txt = self.tabs.get(tab_name)
        if not txt:
            return
        if isinstance(txt, ttk.Treeview):
            for iid in txt.get_children():
                txt.delete(iid)
            if not text:
                return
            for line in str(text).splitlines():
                txt.insert("", "end", text=line)
            return

        txt.configure(state="normal")
        txt.delete("1.0", "end")
        txt.insert("1.0", text)
        txt.configure(state="disabled")


def main():
    if __name__ == "__main__":
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        repo_root = os.path.dirname(here)
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)

    root = tk.Tk()
    app = CompilerVisualizer(root)
    root.geometry("1200x750")
    root.mainloop()


if __name__ == "__main__":
    main()
