class Word:
    def __init__(self, original: str):
        self.original = original
        self.corrected = None
        self.is_misspelled = False
