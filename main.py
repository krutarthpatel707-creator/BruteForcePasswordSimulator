import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading

from brute_force import brute_force_attack
from strength_checker import check_strength
from logger import save_result


# ----- Color palette (kept soft and low-contrast on purpose) -----
COLOR_BG = "#EEF1F7"          # app background
COLOR_HEADER = "#2F3B52"      # header bar
COLOR_HEADER_SUB = "#A9B4CC"  # header subtitle text
COLOR_CARD = "#FFFFFF"        # card panels
COLOR_BORDER = "#DDE3EE"      # card border
COLOR_TEXT = "#2E3648"        # primary text
COLOR_MUTED = "#7A8499"       # secondary text
COLOR_ACCENT = "#4C6FE0"      # primary accent (buttons)
COLOR_ACCENT_DARK = "#3C59C0" # accent hover/active
COLOR_CONSOLE_BG = "#F6F8FC"  # result text area
COLOR_CONSOLE_BORDER = "#E1E6F0"

STRENGTH_COLORS = {
    "Very Weak": "#D9534F",
    "Weak": "#E08E45",
    "Medium": "#D9B23C",
    "Strong": "#5CA86F",
    "Very Strong": "#2E8B57",
}


class BruteForceGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("Brute Force Simulator")
        self.root.geometry("640x620")
        self.root.minsize(560, 560)
        self.root.configure(bg=COLOR_BG)

        self.is_running = False

        self._build_styles()
        self._build_header()
        self._build_input_card()
        self._build_progress_card()
        self._build_results_card()

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------
    def _build_styles(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Accent.Horizontal.TProgressbar",
            troughcolor=COLOR_BORDER,
            background=COLOR_ACCENT,
            bordercolor=COLOR_BORDER,
            lightcolor=COLOR_ACCENT,
            darkcolor=COLOR_ACCENT,
            thickness=10,
        )

    def _card(self, parent):
        """A simple bordered 'card' container with consistent padding."""

        outer = tk.Frame(parent, bg=COLOR_BORDER)
        inner = tk.Frame(outer, bg=COLOR_CARD)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        return outer, inner

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    def _build_header(self):

        header = tk.Frame(self.root, bg=COLOR_HEADER, height=92)
        header.pack(fill="x", side="top")

        title = tk.Label(
            header,
            text="Brute Force Password Simulator",
            font=("Segoe UI", 19, "bold"),
            fg="#FFFFFF",
            bg=COLOR_HEADER,
        )
        title.pack(pady=(18, 2))

        subtitle = tk.Label(
            header,
            text="Educational demo \u00b7 see how quickly a weak password can be guessed",
            font=("Segoe UI", 10),
            fg=COLOR_HEADER_SUB,
            bg=COLOR_HEADER,
        )
        subtitle.pack(pady=(0, 16))

    # ------------------------------------------------------------------
    # Input + strength card
    # ------------------------------------------------------------------
    def _build_input_card(self):

        wrapper = tk.Frame(self.root, bg=COLOR_BG)
        wrapper.pack(fill="x", padx=24, pady=(20, 10))

        outer, card = self._card(wrapper)
        outer.pack(fill="x")

        content = tk.Frame(card, bg=COLOR_CARD)
        content.pack(fill="x", padx=20, pady=18)

        label = tk.Label(
            content,
            text="Password",
            font=("Segoe UI", 10, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_CARD,
        )
        label.grid(row=0, column=0, sticky="w", pady=(0, 6))

        entry_row = tk.Frame(content, bg=COLOR_CARD)
        entry_row.grid(row=1, column=0, sticky="ew")
        content.grid_columnconfigure(0, weight=1)

        self.password_entry = tk.Entry(
            entry_row,
            width=28,
            show="*",
            font=("Segoe UI", 12),
            fg=COLOR_TEXT,
            bg="#FBFCFE",
            relief="flat",
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_ACCENT,
            insertbackground=COLOR_TEXT,
        )
        self.password_entry.grid(row=0, column=0, sticky="ew", ipady=6, padx=(0, 10))
        entry_row.grid_columnconfigure(0, weight=1)

        self.password_entry.bind("<KeyRelease>", lambda e: self.show_strength())
        self.password_entry.bind("<Return>", lambda e: self.start_attack())

        check_button = self._make_button(
            entry_row,
            text="Check Strength",
            command=self.show_strength,
            primary=False,
        )
        check_button.grid(row=0, column=1, sticky="e")

        # Strength indicator row
        strength_row = tk.Frame(content, bg=COLOR_CARD)
        strength_row.grid(row=2, column=0, sticky="ew", pady=(14, 0))

        self.strength_caption = tk.Label(
            strength_row,
            text="Strength:",
            font=("Segoe UI", 9),
            fg=COLOR_MUTED,
            bg=COLOR_CARD,
        )
        self.strength_caption.pack(side="left")

        self.strength_label = tk.Label(
            strength_row,
            text="\u2014",
            font=("Segoe UI", 9, "bold"),
            fg=COLOR_MUTED,
            bg=COLOR_CARD,
        )
        self.strength_label.pack(side="left", padx=(6, 0))

        self.start_button = self._make_button(
            content,
            text="Start Simulation",
            command=self.start_attack,
            primary=True,
        )
        self.start_button.grid(row=3, column=0, sticky="ew", pady=(16, 0))

    def _make_button(self, parent, text, command, primary=True):

        bg = COLOR_ACCENT if primary else COLOR_CARD
        fg = "#FFFFFF" if primary else COLOR_TEXT
        active_bg = COLOR_ACCENT_DARK if primary else COLOR_BORDER
        border = COLOR_ACCENT if primary else COLOR_BORDER

        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10, "bold" if primary else "normal"),
            fg=fg,
            bg=bg,
            activeforeground=fg,
            activebackground=active_bg,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=border,
            cursor="hand2",
            padx=14,
            pady=8,
        )

        button.bind("<Enter>", lambda e: button.configure(bg=active_bg))
        button.bind("<Leave>", lambda e: button.configure(bg=bg))

        return button

    # ------------------------------------------------------------------
    # Progress card
    # ------------------------------------------------------------------
    def _build_progress_card(self):

        wrapper = tk.Frame(self.root, bg=COLOR_BG)
        wrapper.pack(fill="x", padx=24, pady=10)

        outer, card = self._card(wrapper)
        outer.pack(fill="x")

        content = tk.Frame(card, bg=COLOR_CARD)
        content.pack(fill="x", padx=20, pady=16)

        top_row = tk.Frame(content, bg=COLOR_CARD)
        top_row.pack(fill="x")

        status_label = tk.Label(
            top_row,
            text="Simulation Progress",
            font=("Segoe UI", 10, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_CARD,
        )
        status_label.pack(side="left")

        self.progress_label = tk.Label(
            top_row,
            text="Attempts: 0",
            font=("Segoe UI", 9),
            fg=COLOR_MUTED,
            bg=COLOR_CARD,
        )
        self.progress_label.pack(side="right")

        self.progress_bar = ttk.Progressbar(
            content,
            length=400,
            mode="indeterminate",
            style="Accent.Horizontal.TProgressbar",
        )
        self.progress_bar.pack(fill="x", pady=(12, 0))

    # ------------------------------------------------------------------
    # Results card
    # ------------------------------------------------------------------
    def _build_results_card(self):

        wrapper = tk.Frame(self.root, bg=COLOR_BG)
        wrapper.pack(fill="both", expand=True, padx=24, pady=(10, 24))

        outer, card = self._card(wrapper)
        outer.pack(fill="both", expand=True)

        content = tk.Frame(card, bg=COLOR_CARD)
        content.pack(fill="both", expand=True, padx=20, pady=16)

        results_label = tk.Label(
            content,
            text="Results",
            font=("Segoe UI", 10, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_CARD,
        )
        results_label.pack(anchor="w", pady=(0, 8))

        text_outer = tk.Frame(content, bg=COLOR_CONSOLE_BORDER)
        text_outer.pack(fill="both", expand=True)

        self.result_text = tk.Text(
            text_outer,
            height=10,
            font=("Consolas", 10),
            fg=COLOR_TEXT,
            bg=COLOR_CONSOLE_BG,
            relief="flat",
            wrap="word",
            padx=12,
            pady=10,
            highlightthickness=0,
        )
        self.result_text.pack(fill="both", expand=True, padx=1, pady=1)
        self.result_text.insert(
            tk.END,
            "Enter a password above and click \u201cStart Simulation\u201d to begin.",
        )
        self.result_text.configure(state="disabled")

    # ------------------------------------------------------------------
    # Behaviour (unchanged logic, only presentation updated)
    # ------------------------------------------------------------------
    def show_strength(self):

        password = self.password_entry.get()

        if not password:
            self.strength_label.config(text="\u2014", fg=COLOR_MUTED)
            return

        strength = check_strength(password)
        color = STRENGTH_COLORS.get(strength, COLOR_TEXT)

        self.strength_label.config(text=strength, fg=color)

    def update_attempts(self, attempts):

        self.progress_label.config(text=f"Attempts: {attempts:,}")
        self.root.update_idletasks()

    def _set_result_text(self, text):

        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.configure(state="disabled")

    def run_attack(self):

        password = self.password_entry.get()

        result = brute_force_attack(
            password,
            self.update_attempts
        )

        self.progress_bar.stop()
        self.is_running = False
        self.start_button.config(state="normal", text="Start Simulation")

        if result:

            save_result(
                result["password"],
                result["attempts"],
                result["time"]
            )

            self._set_result_text(
                "Password Found!\n\n"
                f"Password:  {result['password']}\n"
                f"Attempts:  {result['attempts']:,}\n"
                f"Time Taken: {result['time']} seconds\n\n"
                "Result saved to results.csv"
            )
        else:
            self._set_result_text(
                "No match found for the given password within the "
                "simulated character set."
            )

    def start_attack(self):

        if self.is_running:
            return

        password = self.password_entry.get()

        if not password:
            messagebox.showerror(
                "Error",
                "Please enter a password."
            )
            return

        self.is_running = True
        self.start_button.config(state="disabled", text="Running\u2026")
        self.progress_label.config(text="Attempts: 0")
        self._set_result_text("Running simulation, please wait\u2026")
        self.progress_bar.start(10)

        attack_thread = threading.Thread(
            target=self.run_attack,
            daemon=True,
        )

        attack_thread.start()


root = tk.Tk()
app = BruteForceGUI(root)
root.mainloop()
