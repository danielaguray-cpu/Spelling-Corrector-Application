class InputReader:
    def read_text(self):
        text = input("Enter text to check: ")
        if not text.strip():
            raise ValueError("Input cannot be empty.")
        return text
