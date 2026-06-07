import re
import string
from services.spell_service import SpellService


class SpellCheckerModule:
    """Thin wrapper that delegates to SpellService.
    Kept for backward compatibility.
    """

    def __init__(self):
        self.service = SpellService()

    def check_word(self, word: str) -> str:
        return self.service.check_word(word)

    def suggest(self, word: str) -> list:
        return self.service.suggest(word)
