from abc import ABC, abstractmethod

class ISpellService(ABC):
    @abstractmethod
    def check_word(self, word: str) -> bool:
        pass

    @abstractmethod
    def suggest(self, word: str) -> list:
        pass
