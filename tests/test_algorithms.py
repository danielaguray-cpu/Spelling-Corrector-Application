"""
tests/test_algorithms.py
Tests for all 10 spelling-correction algorithms in services/spell_service.py
"""
import sys
import os

# Ensure project root is on sys.path so imports work from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from services.spell_service import (
    hash_lookup,
    levenshtein,
    damerau_levenshtein,
    BKTree,
    SymSpell,
    ngram_similarity,
    ngram_candidates,
    double_metaphone,
    phonetic_candidates,
    noisy_channel_score,
    noisy_channel_best,
    viterbi_correct,
    beam_search_correct,
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Hash Set Lookup
# ─────────────────────────────────────────────────────────────────────────────

class TestHashLookup:
    def test_present_word(self):
        assert hash_lookup("test", {"test", "word"}) is True

    def test_absent_word(self):
        assert hash_lookup("xyz", {"test"}) is False

    def test_case_insensitive(self):
        assert hash_lookup("Hello", {"hello"}) is True

    def test_empty_dict(self):
        assert hash_lookup("foo", set()) is False


# ─────────────────────────────────────────────────────────────────────────────
# 2. Levenshtein Distance
# ─────────────────────────────────────────────────────────────────────────────

class TestLevenshtein:
    def test_kitten_sitting(self):
        assert levenshtein("kitten", "sitting") == 3

    def test_empty_to_abc(self):
        assert levenshtein("", "abc") == 3

    def test_equal_strings(self):
        assert levenshtein("abc", "abc") == 0

    def test_single_substitution(self):
        assert levenshtein("cat", "bat") == 1

    def test_single_deletion(self):
        assert levenshtein("hello", "helo") == 1

    def test_single_insertion(self):
        assert levenshtein("helo", "hello") == 1

    def test_symmetry(self):
        assert levenshtein("abc", "xyz") == levenshtein("xyz", "abc")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Damerau-Levenshtein Distance
# ─────────────────────────────────────────────────────────────────────────────

class TestDamerauLevenshtein:
    def test_transposition_cost_1(self):
        # "ab" → "ba" is one transposition; plain lev would give 2
        assert damerau_levenshtein("ab", "ba") == 1

    def test_equal_strings(self):
        assert damerau_levenshtein("hello", "hello") == 0

    def test_dl_leq_lev_transposition(self):
        assert damerau_levenshtein("ab", "ba") <= levenshtein("ab", "ba")

    def test_dl_leq_lev_substitution(self):
        assert damerau_levenshtein("cat", "bat") <= levenshtein("cat", "bat")

    def test_dl_leq_lev_longer(self):
        assert damerau_levenshtein("algorithm", "altgorihm") <= levenshtein("algorithm", "altgorihm")

    def test_dl_leq_lev_empty(self):
        assert damerau_levenshtein("", "abc") <= levenshtein("", "abc")

    def test_single_substitution(self):
        assert damerau_levenshtein("cat", "cut") == 1

    def test_teh_the(self):
        # "teh" → "the" is a transposition — should cost 1
        assert damerau_levenshtein("teh", "the") == 1


# ─────────────────────────────────────────────────────────────────────────────
# 4. BK-Tree
# ─────────────────────────────────────────────────────────────────────────────

class TestBKTree:
    def setup_method(self):
        self.tree = BKTree()
        for w in ["hello", "world", "help", "held"]:
            self.tree.insert(w)

    def test_search_finds_close_match(self):
        results = self.tree.search("helo", 1)
        assert "hello" in results

    def test_search_exact_match(self):
        results = self.tree.search("hello", 0)
        assert "hello" in results

    def test_search_no_match_low_tolerance(self):
        results = self.tree.search("zzzzz", 1)
        assert results == []

    def test_search_tolerance_2(self):
        # "held" is at distance 2 from "hello": h-e-l-d vs h-e-l-l-o
        results = self.tree.search("hello", 2)
        assert "help" in results or "held" in results

    def test_duplicate_insert(self):
        # Duplicate inserts should not raise; the tree still works
        self.tree.insert("hello")
        results = self.tree.search("hello", 0)
        assert results.count("hello") == 1  # no duplication in results


# ─────────────────────────────────────────────────────────────────────────────
# 5. SymSpell
# ─────────────────────────────────────────────────────────────────────────────

class TestSymSpell:
    def setup_method(self):
        self.sym = SymSpell()
        self.sym.train(["spelling", "hello", "world", "help"])

    def test_lookup_one_delete(self):
        # "speling" is one delete away from "spelling"
        results = self.sym.lookup("speling")
        assert "spelling" in results

    def test_lookup_two_deletes(self):
        results = self.sym.lookup("speling", max_edit=2)
        assert "spelling" in results

    def test_lookup_exact_word(self):
        results = self.sym.lookup("hello")
        assert "hello" in results

    def test_lookup_no_candidates(self):
        sym2 = SymSpell()
        sym2.train(["abc"])
        # "zzzzz" very far from "abc"
        results = sym2.lookup("zzzzz")
        assert isinstance(results, list)


# ─────────────────────────────────────────────────────────────────────────────
# 6. N-Gram Similarity (Jaccard)
# ─────────────────────────────────────────────────────────────────────────────

class TestNgramSimilarity:
    def test_identical(self):
        assert ngram_similarity("hello", "hello") == 1.0

    def test_range(self):
        s = ngram_similarity("cat", "dog")
        assert 0.0 <= s <= 1.0

    def test_similar_words_higher_than_dissimilar(self):
        sim_close = ngram_similarity("spelling", "speling")
        sim_far = ngram_similarity("spelling", "xyz")
        assert sim_close > sim_far

    def test_empty_string(self):
        # Should not raise; result is between 0 and 1
        s = ngram_similarity("", "hello")
        assert 0.0 <= s <= 1.0

    def test_ngram_candidates_sorted(self):
        dictionary = ["spelling", "hello", "world", "speling", "cat"]
        results = ngram_candidates("spelling", dictionary)
        # spelling should be first (identical)
        assert results[0] == "spelling"


# ─────────────────────────────────────────────────────────────────────────────
# 7. Double Metaphone
# ─────────────────────────────────────────────────────────────────────────────

class TestDoubleMetaphone:
    def test_smith_smyth_same_primary(self):
        assert double_metaphone("Smith")[0] == double_metaphone("Smyth")[0]

    def test_empty_string(self):
        assert double_metaphone("")[0] == ""

    def test_returns_tuple(self):
        result = double_metaphone("hello")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_codes_are_strings(self):
        p, s = double_metaphone("world")
        assert isinstance(p, str)
        assert isinstance(s, str)

    def test_known_phonetic_equivalents(self):
        # "phone" and "fone" should share a primary code (F)
        p1 = double_metaphone("phone")[0]
        p2 = double_metaphone("fone")[0]
        assert p1 == p2

    def test_no_crash_on_various_inputs(self):
        words = ["knight", "gnome", "psychology", "xylophone", "czar", "tsunami"]
        for w in words:
            result = double_metaphone(w)
            assert isinstance(result, tuple)


# ─────────────────────────────────────────────────────────────────────────────
# 8. Noisy Channel Model
# ─────────────────────────────────────────────────────────────────────────────

class TestNoisyChannel:
    def test_identical_is_one(self):
        assert noisy_channel_score("the", "the") == 1.0

    def test_close_beats_distant(self):
        assert noisy_channel_score("teh", "the") > noisy_channel_score("teh", "xyz")

    def test_best_returns_string(self):
        result = noisy_channel_best("teh", ["the", "ten", "tea"])
        assert isinstance(result, str)
        assert result in ["the", "ten", "tea"]

    def test_best_empty_candidates(self):
        assert noisy_channel_best("teh", []) == "teh"

    def test_score_range(self):
        s = noisy_channel_score("hello", "world")
        assert 0.0 < s <= 1.0


# ─────────────────────────────────────────────────────────────────────────────
# 9. Viterbi
# ─────────────────────────────────────────────────────────────────────────────

class TestViterbi:
    def test_matches_noisy_channel(self):
        word = "teh"
        candidates = ["the", "ten", "tea"]
        assert viterbi_correct(word, candidates) == noisy_channel_best(word, candidates)

    def test_empty_candidates_returns_word(self):
        assert viterbi_correct("foo", []) == "foo"

    def test_single_candidate(self):
        assert viterbi_correct("helo", ["hello"]) == "hello"

    def test_returns_string(self):
        result = viterbi_correct("speling", ["spelling", "speaking", "spilling"])
        assert isinstance(result, str)


# ─────────────────────────────────────────────────────────────────────────────
# 10. Beam Search
# ─────────────────────────────────────────────────────────────────────────────

class TestBeamSearch:
    def test_already_correct(self):
        dictionary = {"hello", "world", "help"}
        assert beam_search_correct("hello", dictionary) == "hello"

    def test_helo_corrects_to_hello(self):
        dictionary = {"hello", "world", "help"}
        # Both "hello" (insert l) and "help" (substitute o→p) are distance-1
        # corrections. The beam search must return one of them.
        result = beam_search_correct("helo", dictionary)
        assert result in {"hello", "help"}

    def test_returns_string(self):
        dictionary = {"hello", "world"}
        result = beam_search_correct("worrld", dictionary)
        assert isinstance(result, str)

    def test_no_match_terminates(self):
        # Should terminate gracefully even with no plausible match
        dictionary = {"abc"}
        result = beam_search_correct("zzzzzzzzz", dictionary)
        assert isinstance(result, str)
