import tkinter as tk
from tkinter import messagebox
from spell_checker_module import SpellCheckerModule

class SpellingCorrectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spelling Corrector Application")
        self.root.geometry("650x650")
        self.root.configure(bg="#f0f4f8")

        self.spell_checker = SpellCheckerModule()

        # Title
        tk.Label(root, text="Spelling Corrector", bg="#f0f4f8",
                 font=("Segoe UI", 18, "bold")).pack(pady=10)

        # Input box
        tk.Label(root, text="Enter text:", bg="#f0f4f8",
                 font=("Segoe UI", 12)).pack(pady=5)
        self.entry = tk.Text(root, font=("Segoe UI", 12), height=6, width=70, wrap="word")
        self.entry.pack(pady=5)

        # Buttons
        tk.Button(root, text="Check Spelling", command=self.check_text,
                  bg="#0078D7", fg="white", font=("Segoe UI", 11, "bold")).pack(pady=10)

        tk.Button(root, text="Clear", command=self.clear_text,
                  bg="#d32f2f", fg="white", font=("Segoe UI", 11, "bold")).pack(pady=5)

        # Corrected text box
        tk.Label(root, text="Corrected text:", bg="#f0f4f8",
                 font=("Segoe UI", 12)).pack(pady=5)
        self.result_box = tk.Text(root, font=("Segoe UI", 12), height=6, width=70,
                                  state="disabled", wrap="word")
        self.result_box.pack(pady=5)

        # Feedback box (above suggestions)
        self.feedback_frame = tk.Frame(root, bg="#e8f5e9", bd=2, relief="groove")
        self.feedback_frame.pack(pady=10, fill="x", padx=20)
        self.feedback_label = tk.Label(self.feedback_frame, text="", bg="#e8f5e9",
                                       font=("Segoe UI", 12, "italic"), fg="green")
        self.feedback_label.pack(pady=5)

        # Suggestions box
        tk.Label(root, text="Suggestions:", bg="#f0f4f8",
                 font=("Segoe UI", 12)).pack(pady=5)
        self.suggestions_box = tk.Text(root, font=("Segoe UI", 11), height=6, width=70,
                                       state="disabled", wrap="word")
        self.suggestions_box.pack(pady=5)

    def check_text(self):
        text = self.entry.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Input Error", "Please enter text.")
            return

        words = text.split()
        corrected_words = []
        suggestions_output = []

        for word in words:
            correction = self.spell_checker.check_word(word)
            corrected_words.append(correction)
            if correction != word:
                suggestions = self.spell_checker.suggest(word)
                if suggestions:
                    suggestions_output.append(
                        f"{word} → {correction} (Suggestions: {', '.join(suggestions)})"
                    )

        corrected_text = " ".join(corrected_words)

        # Show corrected text
        self.result_box.config(state="normal")
        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, corrected_text)
        self.result_box.config(state="disabled")

        # Show feedback above suggestions
        if suggestions_output:
            self.feedback_label.config(
                text="Some words were corrected. See suggestions below.",
                fg="orange", bg="#fff3e0"
            )
        else:
            self.feedback_label.config(
                text="Great job! No spelling errors found.",
                fg="green", bg="#e8f5e9"
            )

        # Show suggestions
        self.suggestions_box.config(state="normal")
        self.suggestions_box.delete("1.0", tk.END)
        if suggestions_output:
            self.suggestions_box.insert(tk.END, "\n".join(suggestions_output))
        else:
            self.suggestions_box.insert(tk.END, "All words are spelled correctly ✅")
        self.suggestions_box.config(state="disabled")

    def clear_text(self):
        self.entry.delete("1.0", tk.END)
        self.result_box.config(state="normal")
        self.result_box.delete("1.0", tk.END)
        self.result_box.config(state="disabled")
        self.suggestions_box.config(state="normal")
        self.suggestions_box.delete("1.0", tk.END)
        self.suggestions_box.config(state="disabled")
        self.feedback_label.config(text="", bg="#e8f5e9")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpellingCorrectorApp(root)
    root.mainloop()
