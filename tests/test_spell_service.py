"""
tests/test_spell_service.py
Tests for SpellService using a small in-memory mock DataService.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from services.spell_service import SpellService


class _MockDataService:
    """Minimal in-memory DataService for testing."""

    _WORDS = [
        "the", "hello", "world", "spelling", "correct", "test",
        "help", "held", "belt", "melt", "felt", "ten", "tea",
        "there", "their", "then", "them", "they", "this", "that",
    ]

    def get_all(self) -> list:
        return list(self._WORDS)

    def add(self, item): self._WORDS.append(item.lower())
    def update(self, item): pass
    def delete(self, item_id): pass


@pytest.fixture
def service():
    return SpellService(data_service=_MockDataService())


class TestSpellServiceCheckWord:
    def test_dictionary_word_unchanged(self, service):
        assert service.check_word("the") == "the"

    def test_dictionary_word_hello(self, service):
        assert service.check_word("hello") == "hello"

    def test_check_word_teh_returns_the(self, service):
        result = service.check_word("teh")
        # "teh" is one transposition away from "the"
        assert result == "the"

    def test_check_word_helo_corrects(self, service):
        result = service.check_word("helo")
        assert result in {"hello", "help", "held"}

    def test_check_word_empty_string(self, service):
        # Empty or punctuation-only should not crash
        result = service.check_word("")
        assert isinstance(result, str)

    def test_check_word_returns_string(self, service):
        assert isinstance(service.check_word("speling"), str)

    def test_check_word_punctuation_only(self, service):
        result = service.check_word("...")
        assert isinstance(result, str)


class TestSpellServiceSuggest:
    def test_in_dict_word_returns_empty(self, service):
        assert service.suggest("the") == []

    def test_suggest_returns_list(self, service):
        result = service.suggest("teh")
        assert isinstance(result, list)

    def test_suggest_not_empty_for_misspelled(self, service):
        result = service.suggest("teh")
        assert len(result) > 0

    def test_suggest_max_five(self, service):
        result = service.suggest("speling")
        assert len(result) <= 5

    def test_suggest_returns_strings(self, service):
        result = service.suggest("helo")
        for item in result:
            assert isinstance(item, str)
