import sys
import tkinter as tk
from tkinter import messagebox

from input_reader import InputReader
from output_writer import OutputWriter
from processor import Processor
from services.spell_service import SpellService
from definitions import get_definition


# ── Tooltip helper ────────────────────────────────────────────────────────────

class _Tooltip:
    """Lightweight tooltip shown near a widget on hover."""

    def __init__(self, widget, text_func):
        self._widget = widget
        self._text_func = text_func
        self._tip_window = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event=None):
        text = self._text_func()
        if not text or self._tip_window:
            return
        x = self._widget.winfo_rootx() + 20
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4
        self._tip_window = tw = tk.Toplevel(self._widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(
            tw,
            text=text,
            justify="left",
            background="#ffffff",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9),
            wraplength=260,
            padx=6,
            pady=4,
        ).pack()

    def _hide(self, event=None):
        if self._tip_window:
            self._tip_window.destroy()
            self._tip_window = None


# ── GUI application ───────────────────────────────────────────────────────────

class SpellingCorrectorApp:
    def __init__(self, root, spell_service=None):
        self.root = root
        self.root.title("Running... Spelling_Corrector.exe")
        self.root.geometry("620x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#f4f4f4")

        if spell_service is None:
            spell_service = SpellService()
        self.spell_service = spell_service

        # list of dicts: {original, corrected, suggestions}
        # Using dicts + index for reliable click-replace (avoids text-match bugs)
        self._word_corrections = []

        # ── Title ──────────────────────────────────────────────────────
        tk.Label(root, text="Spelling Corrector", bg="#f0f4f8",
                 font=("Segoe UI", 18, "bold")).pack(pady=(8, 2))

        # ── Input box ──────────────────────────────────────────────────
        tk.Label(root, text="Enter text:", bg="#f0f4f8",
                 font=("Segoe UI", 12)).pack(pady=(4, 1))
        self.entry = tk.Text(root, font=("Segoe UI", 11), height=4, width=68, wrap="word")
        self.entry.pack(pady=(0, 4), padx=16)

        # ── Buttons ────────────────────────────────────────────────────
        btn_frame = tk.Frame(root, bg="#f0f4f8")
        btn_frame.pack(pady=(2, 4))
        tk.Button(btn_frame, text="Check Spelling", command=self.check_text,
                  bg="#0078D7", fg="white", font=("Segoe UI", 11, "bold"),
                  padx=14, pady=3).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Clear", command=self.clear_text,
                  bg="#d32f2f", fg="white", font=("Segoe UI", 11, "bold"),
                  padx=14, pady=3).pack(side="left", padx=6)

        # ── Corrected text box ─────────────────────────────────────────
        tk.Label(root, text="Corrected text:", bg="#f0f4f8",
                 font=("Segoe UI", 12)).pack(pady=(4, 1))
        self.result_box = tk.Text(root, font=("Segoe UI", 11), height=4, width=68,
                                  state="disabled", wrap="word")
        self.result_box.tag_config("correct", foreground="#2e7d32")
        self.result_box.tag_config("error", foreground="#d32f2f")
        self.result_box.pack(pady=(0, 4), padx=16)

        # ── Feedback banner ────────────────────────────────────────────
        self.feedback_frame = tk.Frame(root, bg="#e8f5e9", bd=2, relief="groove")
        self.feedback_frame.pack(pady=(2, 2), fill="x", padx=16)
        self.feedback_label = tk.Label(self.feedback_frame, text="", bg="#e8f5e9",
                                       font=("Segoe UI", 11, "italic"), fg="green")
        self.feedback_label.pack(pady=3)

        # ── Suggestions label ──────────────────────────────────────────
        tk.Label(root, text="Suggestions:", bg="#f0f4f8",
                 font=("Segoe UI", 12)).pack(pady=(4, 1))

        # ── Scrollable suggestions area ────────────────────────────────
        suggestions_container = tk.Frame(root, bg="#f0f4f8")
        suggestions_container.pack(pady=(0, 8), fill="x", padx=16)

        self._suggestions_scrollbar = tk.Scrollbar(suggestions_container, orient="vertical")
        self._suggestions_scrollbar.pack(side="right", fill="y")

        self._suggestions_canvas = tk.Canvas(
            suggestions_container,
            bg="white",
            height=130,
            yscrollcommand=self._suggestions_scrollbar.set,
            highlightthickness=1,
            highlightbackground="#cccccc",
        )
        self._suggestions_canvas.pack(side="left", fill="both", expand=True)
        self._suggestions_scrollbar.config(command=self._suggestions_canvas.yview)

        self.suggestions_frame = tk.Frame(self._suggestions_canvas, bg="white")
        self._canvas_window = self._suggestions_canvas.create_window(
            (0, 0), window=self.suggestions_frame, anchor="nw"
        )

        self.suggestions_frame.bind("<Configure>", self._on_frame_configure)
        self._suggestions_canvas.bind("<Configure>", self._on_canvas_configure)
        self._suggestions_canvas.bind("<Enter>", self._bind_mousewheel)
        self._suggestions_canvas.bind("<Leave>", self._unbind_mousewheel)

    # ── Scroll helpers ─────────────────────────────────────────────────

    def _on_frame_configure(self, event=None):
        self._suggestions_canvas.configure(
            scrollregion=self._suggestions_canvas.bbox("all")
        )

    def _on_canvas_configure(self, event):
        self._suggestions_canvas.itemconfig(self._canvas_window, width=event.width)

    def _bind_mousewheel(self, event):
        self._suggestions_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self._suggestions_canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self._suggestions_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ── Result-box coloring ────────────────────────────────────────────

    def _render_result_box(self):
        """Re-render result_box with green (correct) / red (changed) color tags."""
        self.result_box.config(state="normal")
        self.result_box.delete("1.0", tk.END)
        for i, entry in enumerate(self._word_corrections):
            if i > 0:
                self.result_box.insert(tk.END, " ")
            original = entry["original"]
            corrected = entry["corrected"]
            tag = "error" if corrected.lower() != original.lower() else "correct"
            self.result_box.insert(tk.END, corrected, tag)
        self.result_box.config(state="disabled")

    # ── Suggestion panel ───────────────────────────────────────────────

    def _rebuild_suggestions_panel(self):
        """Clear and repopulate the scrollable suggestions frame."""
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()

        has_errors = any(
            e["corrected"].lower() != e["original"].lower()
            for e in self._word_corrections
        )

        if not has_errors:
            tk.Label(
                self.suggestions_frame,
                text="All words you've put are correct \u2705",
                bg="white",
                font=("Segoe UI", 11),
                fg="#2e7d32",
            ).pack(anchor="w", padx=8, pady=4)
            return

        for idx, entry in enumerate(self._word_corrections):
            original = entry["original"]
            corrected = entry["corrected"]
            suggestions = entry["suggestions"]

            # Only show rows for words that were changed
            if corrected.lower() == original.lower():
                continue

            row = tk.Frame(self.suggestions_frame, bg="white")
            row.pack(anchor="w", fill="x", padx=6, pady=2)

            # Show original → label
            tk.Label(
                row,
                text=f"{original}  \u2192  ",
                bg="white",
                font=("Segoe UI", 11),
                fg="#333333",
            ).pack(side="left")

            # Deduplicate: auto-correction first, then all suggestions
            seen = []
            if corrected not in seen:
                seen.append(corrected)
            for s in suggestions:
                if s not in seen:
                    seen.append(s)

            for suggestion in seen:
                btn = tk.Button(
                    row,
                    text=suggestion,
                    bg="white",
                    fg="#0078D7",
                    font=("Segoe UI", 11, "underline"),
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                    activeforeground="#005a9e",
                    activebackground="#e3f0fb",
                    # KEY FIX: bind by index, not by text — avoids stale-match bug
                    command=lambda i=idx, sug=suggestion: self._apply_suggestion(i, sug),
                )
                btn.pack(side="left", padx=2)
                tip_word = suggestion
                _Tooltip(btn, lambda w=tip_word: get_definition(w))

    # ── Apply suggestion  (index-based — no text-match bug) ───────────

    def _apply_suggestion(self, word_index: int, clicked_suggestion: str):
        """Replace the corrected word at word_index with clicked_suggestion."""
        self._word_corrections[word_index]["corrected"] = clicked_suggestion
        # Mark as correct if the user picked back the original word
        original = self._word_corrections[word_index]["original"]
        self._word_corrections[word_index]["is_corrected"] = (
            clicked_suggestion.lower() != original.lower()
        )
        self._render_result_box()
        self._rebuild_suggestions_panel()

    # ── check_text ────────────────────────────────────────────────────

    def check_text(self):
        text = self.entry.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Input Error", "Please enter text.")
            return

        words = text.split()
        self._word_corrections = []
        has_errors = False

        for word in words:
            corrected = self.spell_service.check_word(word)
            changed = corrected.lower() != word.lower()
            suggestions = self.spell_service.suggest(word) if changed else []
            self._word_corrections.append({
                "original":   word,
                "corrected":  corrected,
                "suggestions": suggestions,
                "is_corrected": changed,
            })
            if changed:
                has_errors = True

        self._render_result_box()

        if has_errors:
            self.feedback_label.config(
                text="Some words were corrected. See suggestions below.",
                fg="orange",
                bg="#fff3e0",
            )
            self.feedback_frame.config(bg="#fff3e0")
        else:
            self.feedback_label.config(
                text="All words you've put are correct \u2705",
                fg="green",
                bg="#e8f5e9",
            )
            self.feedback_frame.config(bg="#e8f5e9")

        self._rebuild_suggestions_panel()

    # ── clear_text ────────────────────────────────────────────────────

    def clear_text(self):
        self.entry.delete("1.0", tk.END)
        self.result_box.config(state="normal")
        self.result_box.delete("1.0", tk.END)
        self.result_box.config(state="disabled")
        self.feedback_label.config(text="", bg="#e8f5e9")
        self.feedback_frame.config(bg="#e8f5e9")
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()
        self._word_corrections = []
        self._suggestions_canvas.yview_moveto(0)


# ── CLI entry point ───────────────────────────────────────────────────────────

def run_cli():
    reader = InputReader()
    writer = OutputWriter()
    processor = Processor()
    try:
        text = reader.read_text()
        corrected, feedback = processor.process_text(text)
        writer.display(corrected, feedback)
        writer.export_report("report.txt", feedback)
    except ValueError as e:
        print("Error:", e)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_cli()
    else:
        root = tk.Tk()
        SpellingCorrectorApp(root)
        root.mainloop()
