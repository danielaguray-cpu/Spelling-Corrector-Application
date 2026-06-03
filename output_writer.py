class OutputWriter:
    def display(self, corrected_text, feedback):
        print("\nCorrected Text:", corrected_text)
        print("\nCorrections:")
        for original, corrected in feedback.items():
            print(f"{original} → {corrected}")

    def export_report(self, filename, feedback):
        with open(filename, "w") as file:
            for original, corrected in feedback.items():
                file.write(f"{original} → {corrected}\n")
        print(f"\nReport saved as {filename}")
