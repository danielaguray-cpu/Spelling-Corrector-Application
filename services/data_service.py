from interfaces.idata_service import IDataService


class DataService(IDataService):
    """Loads and manages the dictionary word set from a text file."""

    def __init__(self, dictionary_path: str = "dictionary.txt") -> None:
        try:
            with open(dictionary_path, "r", encoding="utf-8") as f:
                self._words: set[str] = {
                    line.strip().lower()
                    for line in f
                    if line.strip()
                }
        except OSError as exc:
            raise FileNotFoundError(
                f"Could not open dictionary file '{dictionary_path}': {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # IDataService interface
    # ------------------------------------------------------------------

    def add(self, item: str) -> None:
        """Add a word (lowercased) to the in-memory set."""
        self._words.add(item.lower())

    def update(self, item: str) -> None:
        """Replace a word entry — for a set this is equivalent to add."""
        self._words.add(item.lower())

    def delete(self, item_id: str) -> None:
        """Remove a word (lowercased) from the in-memory set if present."""
        self._words.discard(item_id.lower())

    def get_all(self) -> list[str]:
        """Return a sorted snapshot of the current word set."""
        return sorted(self._words)
