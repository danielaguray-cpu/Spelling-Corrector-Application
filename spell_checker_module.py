import re
from spellchecker import SpellChecker

class SpellCheckerModule:
    def __init__(self):
        # Load pyspellchecker with your custom dictionary
        self.spell = SpellChecker()

        # Read words from your Hunspell .dic file
        try:
            with open("index.dic", "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip().split("/")[0]  # remove affix rules
                    if word:
                        self.spell.word_frequency.add(word.lower())
        except Exception as e:
            print(f"Error loading dictionary: {e}")

    def check_word(self, word):
        word_clean = re.sub(r'[^A-Za-z]', '', word)
        if not word_clean:
            return word
        correction = self.spell.correction(word_clean)
        return correction if correction else word

    def suggest(self, word):
        word_clean = re.sub(r'[^A-Za-z]', '', word)
        if not word_clean:
            return []
        suggestions = self.spell.candidates(word_clean)
        return list(suggestions) if suggestions else []
