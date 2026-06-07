from models.word import Word


class OutputWriter:
    def display(self, corrected_text: str, feedback: list):
        print("\nCorrected Text:", corrected_text)
        print("\nCorrections:")
        for word in feedback:
            if word.is_misspelled:
                print(f"  {word.original} → {word.corrected}")

    def export_report(self, filename: str, feedback: list):
        with open(filename, "w", encoding="utf-8") as f:
            for word in feedback:
                if word.is_misspelled:
                    f.write(f"{word.original} → {word.corrected}\n")
        print(f"\nReport saved as {filename}")
