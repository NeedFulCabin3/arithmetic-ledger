import math
import tkinter as tk


class ExtendedCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator with History")
        self.root.geometry("360x480")
        self.root.resizable(False, False)
        self.root.configure(bg="#f4f4f4")

        self.expression = ""
        self.history = []
        self.show_history = False

        # Main Container Layout (Main Calculator + Collapsible History Panel)
        self.container = tk.Frame(self.root, bg="#f4f4f4")
        self.container.pack(fill=tk.BOTH, expand=True)

        self.calc_frame = tk.Frame(self.container, bg="#f4f4f4")
        self.calc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Setup Display Screen & History Toggle Button
        top_bar = tk.Frame(self.calc_frame, bg="#f4f4f4")
        top_bar.pack(fill=tk.X, pady=(5, 0))

        self.history_btn = tk.Button(
            top_bar,
            text="📜 History",
            font=("Arial", 9, "bold"),
            bg="#8e44ad",
            fg="#ffffff",
            bd=0,
            command=self._toggle_history_panel,
        )
        self.history_btn.pack(side=tk.RIGHT, padx=5)

        self.display = tk.Entry(
            self.calc_frame,
            font=("Arial", 20),
            bg="#ffffff",
            fg="#333333",
            bd=8,
            relief=tk.FLAT,
            justify="right",
        )
        self.display.pack(fill=tk.X, padx=5, pady=10, ipady=10)

        # Grid frame for buttons
        self.grid_frame = tk.Frame(self.calc_frame, bg="#f4f4f4")
        self.grid_frame.pack(fill=tk.BOTH, expand=True)

        # Button Map: (Text, Row, Column, [ColumnSpan])
        buttons = [
            ("C", 0, 0), ("⌫", 0, 1), ("%", 0, 2), ("/", 0, 3),
            ("√", 1, 0), ("x²", 1, 1), ("x^y", 1, 2), ("*", 1, 3),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("-", 2, 3),
            ("4", 3, 0), ("5", 3, 1), ("6", 3, 2), ("+", 3, 3),
            ("1", 4, 0), ("2", 4, 1), ("3", 4, 2), ("=", 4, 3, 1, 2),
            ("0", 5, 0, 2), (".", 5, 2)
        ]

        self._create_buttons(buttons)
        self._setup_history_panel()

        self.root.bind("<Key>", self._on_key_press)

    def _create_buttons(self, buttons):
        """Generates layout grid for digits and math operators."""
        for btn in buttons:
            text, row, col = btn[0], btn[1], btn[2]
            colspan = btn[3] if len(btn) >= 4 else 1
            rowspan = btn[4] if len(btn) == 5 else 1

            bg_color = "#e0e0e0"
            fg_color = "#000000"
            if text in ["/", "*", "-", "+", "="]:
                bg_color = "#4a90e2"
                fg_color = "#ffffff"
            elif text in ["C", "⌫", "%"]:
                bg_color = "#d9534f"
                fg_color = "#ffffff"
            elif text in ["√", "x²", "x^y"]:
                bg_color = "#34495e"
                fg_color = "#ffffff"

            button = tk.Button(
                self.grid_frame,
                text=text,
                font=("Arial", 12, "bold"),
                bg=bg_color,
                fg=fg_color,
                bd=0,
                activebackground="#cccccc",
                command=lambda val=text: self._handle_click(val),
            )
            button.grid(
                row=row,
                column=col,
                columnspan=colspan,
                rowspan=rowspan,
                padx=2,
                pady=2,
                sticky="nsew",
            )

        for i in range(6):
            self.grid_frame.grid_rowconfigure(i, weight=1)
        for j in range(4):
            self.grid_frame.grid_columnconfigure(j, weight=1)

    def _setup_history_panel(self):
        """Prepares the collapsible side panel for history log."""
        self.history_frame = tk.Frame(self.container, bg="#ffffff", width=200)

        title = tk.Label(
            self.history_frame,
            text="History",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            fg="#333333",
        )
        title.pack(fill=tk.X, pady=5)

        self.history_listbox = tk.Listbox(
            self.history_frame,
            font=("Arial", 10),
            bd=0,
            selectbackground="#4a90e2",
        )
        self.history_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.history_listbox.bind("<<ListboxSelect>>", self._on_history_select)

        clear_btn = tk.Button(
            self.history_frame,
            text="Clear History",
            font=("Arial", 9),
            bg="#e74c3c",
            fg="#ffffff",
            bd=0,
            command=self._clear_history,
        )
        clear_btn.pack(fill=tk.X, padx=5, pady=5)

    def _toggle_history_panel(self):
        """Expands or collapses the history side panel."""
        if self.show_history:
            self.history_frame.pack_forget()
            self.root.geometry("360x480")
            self.show_history = False
        else:
            self.history_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)
            self.root.geometry("560x480")
            self.show_history = True

    def _handle_click(self, char):
        """Processes input logic for normal keys and special math functions."""
        if char == "C":
            self.expression = ""
            self._update_display()
        elif char == "⌫":
            self.expression = self.expression[:-1]
            self._update_display()
        elif char == "=":
            self._evaluate_expression()
        elif char == "x²":
            self._apply_unary_math(lambda x: x ** 2, "({})^2")
        elif char == "√":
            self._apply_unary_math(lambda x: math.sqrt(x), "√({})")
        elif char == "x^y":
            self.expression += "**"
            self._update_display()
        else:
            self.expression += str(char)
            self._update_display()

    def _apply_unary_math(self, func, label_fmt):
        """Executes operations on the current result directly (e.g., √ or x²)."""
        if not self.expression:
            return
        try:
            val = float(
                eval(self.expression.replace("%", "/100"), {"__builtins__": None}, {})
            )
            result = func(val)
            if result.is_integer():
                result = int(result)

            display_expr = label_fmt.format(self.expression)
            self.history.append(f"{display_expr} = {result}")
            self._sync_history_ui()

            self.expression = str(result)
            self._update_display()
        except Exception:
            self._update_display("Error")
            self.expression = ""

    def _update_display(self, text=None):
        self.display.delete(0, tk.END)
        self.display.insert(0, text if text is not None else self.expression)

    def _evaluate_expression(self):
        if not self.expression:
            return

        try:
            raw_expr = self.expression
            sanitized_expr = raw_expr.replace("%", "/100")
            result = eval(sanitized_expr, {"__builtins__": None}, {})

            if isinstance(result, float) and result.is_integer():
                result = int(result)

            # Record calculation into history log
            history_entry = f"{raw_expr.replace('**', '^')} = {result}"
            self.history.append(history_entry)
            self._sync_history_ui()

            self.expression = str(result)
            self._update_display()
        except ZeroDivisionError:
            self._update_display("Error: Div by 0")
            self.expression = ""
        except Exception:
            self._update_display("Syntax Error")
            self.expression = ""

    def _sync_history_ui(self):
        self.history_listbox.delete(0, tk.END)
        for entry in reversed(self.history):
            self.history_listbox.insert(tk.END, entry)

    def _clear_history(self):
        self.history.clear()
        self.history_listbox.delete(0, tk.END)

    def _on_history_select(self, event):
        """Loads selected historical calculation result back onto display."""
        selection = self.history_listbox.curselection()
        if selection:
            item = self.history_listbox.get(selection[0])
            # Parse result value after the '=' character
            result_val = item.split("=")[-1].strip()
            self.expression = result_val
            self._update_display()

    def _on_key_press(self, event):
        key = event.char
        keysym = event.keysym

        if keysym in ("Return", "KP_Enter"):
            self._handle_click("=")
        elif keysym == "BackSpace":
            self._handle_click("⌫")
        elif keysym == "Escape":
            self._handle_click("C")
        elif key in "0123456789.+-*/%^":
            if key == "^":
                self._handle_click("x^y")
            else:
                self._handle_click(key)


if __name__ == "__main__":
    root = tk.Tk()
    app = ExtendedCalculator(root)
    root.mainloop()
