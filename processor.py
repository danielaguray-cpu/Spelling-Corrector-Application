import re
import string
from models.word import Word
from interfaces.ispell_service import ISpellService


class Processor:
    def __init__(self, spell_service: ISpellService = None):
        if spell_service is None:
            from services.spell_service import SpellService
            spell_service = SpellService()
        self.spell_service = spell_service

    def process_text(self, text: str) -> tuple:
        if not text or not text.strip():
            raise ValueError("Input cannot be empty.")
        tokens = text.split()
        feedback = []
        corrected_tokens = []
        for token in tokens:
            word = Word(token)
            # Strip leading/trailing punctuation for algorithm input
            clean = token.strip(string.punctuation)
            if clean:
                corrected = self.spell_service.check_word(clean)
                # Re-attach punctuation that was stripped
                prefix = token[:len(token) - len(token.lstrip(string.punctuation))]
                suffix = token[len(token.rstrip(string.punctuation)):]
                word.corrected = prefix + corrected + suffix
            else:
                word.corrected = token
            word.is_misspelled = word.original.lower() != word.corrected.lower()
            feedback.append(word)
            corrected_tokens.append(word.corrected)
        return " ".join(corrected_tokens), feedback
