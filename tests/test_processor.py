"""
tests/test_processor.py
End-to-end tests for the Processor class.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from models.word import Word
from processor import Processor


class _StubSpellService:
    """Trivial spell service: returns the word unchanged, no corrections."""

    def check_word(self, word: str) -> str:
        return word

    def suggest(self, word: str) -> list:
        return []


class _CorrectingSpellService:
    """Spell service that always 'corrects' 'teh' → 'the'."""

    _MAP = {"teh": "the", "helo": "hello"}

    def check_word(self, word: str) -> str:
        return self._MAP.get(word.lower(), word)

    def suggest(self, word: str) -> list:
        c = self._MAP.get(word.lower())
        return [c] if c else []


@pytest.fixture
def stub_processor():
    return Processor(spell_service=_StubSpellService())


@pytest.fixture
def correcting_processor():
    return Processor(spell_service=_CorrectingSpellService())


class TestProcessorValidation:
    def test_empty_string_raises(self, stub_processor):
        with pytest.raises(ValueError):
            stub_processor.process_text("")

    def test_whitespace_only_raises(self, stub_processor):
        with pytest.raises(ValueError):
            stub_processor.process_text("   ")

    def test_none_raises(self, stub_processor):
        with pytest.raises((ValueError, AttributeError)):
            stub_processor.process_text(None)


class TestProcessorReturnType:
    def test_returns_tuple(self, stub_processor):
        result = stub_processor.process_text("hello world")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_corrected_text_is_string(self, stub_processor):
        corrected_text, _ = stub_processor.process_text("hello world")
        assert isinstance(corrected_text, str)

    def test_feedback_is_list(self, stub_processor):
        _, feedback = stub_processor.process_text("hello world")
        assert isinstance(feedback, list)

    def test_feedback_length_matches_tokens(self, stub_processor):
        text = "one two three four"
        _, feedback = stub_processor.process_text(text)
        assert len(feedback) == len(text.split())

    def test_single_word(self, stub_processor):
        corrected, feedback = stub_processor.process_text("hello")
        assert len(feedback) == 1
        assert corrected == "hello"


class TestWordModel:
    def test_word_constructor_original(self):
        w = Word("test")
        assert w.original == "test"

    def test_word_constructor_corrected_is_none(self):
        w = Word("test")
        assert w.corrected is None

    def test_word_constructor_is_misspelled_false(self):
        w = Word("test")
        assert w.is_misspelled is False

    def test_word_corrected_attribute_settable(self):
        w = Word("teh")
        w.corrected = "the"
        assert w.corrected == "the"


class TestProcessorCorrections:
    def test_misspelled_word_flagged(self, correcting_processor):
        _, feedback = correcting_processor.process_text("teh")
        assert feedback[0].is_misspelled is True

    def test_correct_word_not_flagged(self, correcting_processor):
        _, feedback = correcting_processor.process_text("the")
        assert feedback[0].is_misspelled is False

    def test_corrected_text_updated(self, correcting_processor):
        corrected, _ = correcting_processor.process_text("teh world")
        assert corrected == "the world"

    def test_original_preserved_in_feedback(self, correcting_processor):
        _, feedback = correcting_processor.process_text("teh")
        assert feedback[0].original == "teh"
