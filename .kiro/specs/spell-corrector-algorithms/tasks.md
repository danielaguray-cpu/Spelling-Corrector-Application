# Implementation Plan: Spell Corrector Algorithms

## Overview

Fix the Spelling Corrector Application by implementing the complete service layer, all 10
spelling-correction algorithms from scratch, wiring dependency injection through the GUI and
CLI, aligning `output_writer.py` to the `Word`-object contract, and adding comprehensive
pytest + Hypothesis tests. No code should remain unreachable after these tasks are complete.

---

## Task Dependency Graph

```json
{
  "waves": [
    { "wave": 1, "tasks": ["1"] },
    { "wave": 2, "tasks": ["2"] },
    { "wave": 3, "tasks": ["3"] },
    { "wave": 4, "tasks": ["4"] },
    { "wave": 5, "tasks": ["5"] },
    { "wave": 6, "tasks": ["6", "7", "8", "9"] },
    { "wave": 7, "tasks": ["10"] },
    { "wave": 8, "tasks": ["11"] }
  ]
}
```

---

## Tasks

- [x] 1. Create `dictionary.txt` bundled word list
  - Create `dictionary.txt` in the project root containing ≥ 5 000 common English words, one
    word per line, all lowercase — this is the authoritative word source for all algorithms.
  - _Requirements: 2.4_

- [x] 2. Implement `services/data_service.py` — `DataService(IDataService)`
  - [x] 2.1 Implement `DataService` class
    - Create `services/data_service.py`.
    - `__init__` reads `dictionary.txt` (path configurable, default `"dictionary.txt"`);
      stores words in a `set[str]` (lowercase).
    - Implement `add(item)`, `update(item)`, `delete(item_id)`, `get_all()` as required by
      `IDataService`; `get_all()` returns a `list[str]` snapshot of the set.
    - Raise `FileNotFoundError` with a clear message if the file cannot be opened.
    - Update `services/__init__.py` to re-export `DataService`.
    - _Requirements: 2.4, 2.5_
  - [ ]* 2.2 Write unit tests for `DataService`
    - Test: dictionary loads without error when `dictionary.txt` exists (use a tmp file).
    - Test: `get_all()` returns a list of strings.
    - Test: `add` / `delete` / `update` mutate the set correctly.
    - Test: `FileNotFoundError` raised for a missing path.
    - Test: `IDataService` raises `TypeError` when instantiated directly.
    - _Requirements: 2.4, 2.5, 3.9_

- [x] 3. Implement the 10 spell-correction algorithm functions in `services/spell_service.py`
  - [x] 3.1 Implement Hash Set Lookup
    - Create `services/spell_service.py`.
    - Implement `hash_lookup(word: str, dictionary: set) -> bool`.
    - _Requirements: 2.3 (Hash Set Lookup)_
  - [ ]* 3.2 Write property test for Hash Set Lookup
    - **Property 5: Hash Set Lookup round-trip**
    - **Validates: Requirements 2.3, 2.4**
    - Use Hypothesis: for any word added to the set, `hash_lookup` returns `True`; for any
      word not in the set, returns `False`.
    - _Requirements: 2.3_
  - [x] 3.3 Implement Levenshtein Distance
    - Implement `levenshtein(a: str, b: str) -> int` using bottom-up DP.
    - _Requirements: 2.3 (Levenshtein)_
  - [ ]* 3.4 Write property tests for Levenshtein Distance
    - **Property 2: Levenshtein metric axioms**
    - **Validates: Requirements 2.3**
    - Reflexivity, symmetry, triangle inequality, non-negativity; use Hypothesis text strategy.
    - Unit tests: `("kitten","sitting")==3`, `("","abc")==3`, `("abc","abc")==0`.
    - _Requirements: 2.3_
  - [x] 3.5 Implement Damerau-Levenshtein Distance
    - Implement `damerau_levenshtein(a: str, b: str) -> int` (restricted DL, transpositions
      allowed).
    - _Requirements: 2.3 (Damerau-Levenshtein)_
  - [ ]* 3.6 Write property test for Damerau-Levenshtein
    - **Property 3: Damerau-Levenshtein is bounded by Levenshtein**
    - **Validates: Requirements 2.3**
    - Use Hypothesis: for any `a`, `b`, `damerau_levenshtein(a,b) <= levenshtein(a,b)`.
    - Unit test: `("ab","ba")` — DL==1, Lev==2.
    - _Requirements: 2.3_
  - [x] 3.7 Implement N-Gram Similarity (Jaccard)
    - Implement `ngram_similarity(a: str, b: str, n: int = 2) -> float`.
    - Implement `ngram_candidates(word: str, dictionary: list, n: int = 2) -> list[str]`
      returning words sorted by descending Jaccard similarity.
    - _Requirements: 2.3 (N-Gram)_
  - [ ]* 3.8 Write property tests for N-Gram Similarity
    - **Property 4: N-gram Jaccard similarity range and reflexivity**
    - **Validates: Requirements 2.3**
    - Range `[0.0, 1.0]` for any two strings; `ngram_similarity(s, s) == 1.0` for any
      non-empty `s`; use Hypothesis text strategy.
    - _Requirements: 2.3_
  - [x] 3.9 Implement BK-Tree
    - Implement `BKTree` class with `insert(word)` and `search(word, tolerance) -> list[str]`
      using Levenshtein as the metric.
    - _Requirements: 2.3 (BK-Tree)_
  - [ ]* 3.10 Write unit tests for BK-Tree
    - Build from a small known vocabulary; assert `search("helo", 1)` returns `"hello"`;
      search with tolerance 0 on exact word returns that word; empty tree search returns `[]`.
    - _Requirements: 2.3_
  - [x] 3.11 Implement SymSpell
    - Implement `SymSpell` class with `train(dictionary: list)` and
      `lookup(word: str, max_edit: int = 2) -> list[str]`.
    - Pre-compute delete variants up to depth `max_edit`; store in `dict[str, set[str]]`.
    - _Requirements: 2.3 (SymSpell)_
  - [ ]* 3.12 Write unit tests for SymSpell
    - Train on a small vocabulary; test `lookup("speling")` returns `"spelling"` or similar;
      test exact-match lookup; test word beyond max_edit returns empty.
    - _Requirements: 2.3_
  - [x] 3.13 Implement Double Metaphone
    - Implement `double_metaphone(word: str) -> tuple[str, str]` returning (primary,
      secondary) phonetic codes using the standard Philips rule table in pure Python.
    - Implement `phonetic_candidates(word: str, dictionary: list) -> list[str]`.
    - _Requirements: 2.3 (Double Metaphone)_
  - [ ]* 3.14 Write unit tests for Double Metaphone
    - Known equivalences: `double_metaphone("Smith")[0] == double_metaphone("Smyth")[0]`;
      `double_metaphone("")[0] == ""`.
    - _Requirements: 2.3_
  - [x] 3.15 Implement Noisy Channel Model (Bayesian)
    - Implement `noisy_channel_score(observed: str, candidate: str) -> float` returning
      `exp(-levenshtein(observed, candidate))`.
    - Implement `noisy_channel_best(word: str, candidates: list[str]) -> str`.
    - _Requirements: 2.3 (Noisy Channel)_
  - [ ]* 3.16 Write unit tests for Noisy Channel
    - For `observed="teh"`, given `["the", "ten", "tea"]`, assert `"the"` scores highest;
      assert identical word scores `1.0`.
    - _Requirements: 2.3_
  - [x] 3.17 Implement Viterbi Algorithm
    - Implement `viterbi_correct(word: str, candidates: list[str]) -> str` structured as a
      Viterbi lattice over a one-step "hidden state = correct word" model.
    - _Requirements: 2.3 (Viterbi)_
  - [ ]* 3.18 Write unit tests for Viterbi
    - Assert Viterbi returns same winner as Noisy Channel for matching candidate sets.
    - _Requirements: 2.3_
  - [x] 3.19 Implement Beam Search
    - Implement `beam_search_correct(word: str, dictionary: set, beam_width: int = 5) -> str`
      using iterative single-character edits; terminate when a beam member is in the dictionary.
    - _Requirements: 2.3 (Beam Search)_
  - [ ]* 3.20 Write unit tests for Beam Search
    - Assert `beam_search_correct("helo", vocab)` returns `"hello"` for vocab with `"hello"`;
      already-correct word returns itself; no close match terminates gracefully.
    - _Requirements: 2.3_

- [x] 4. Checkpoint — all algorithm unit and property tests pass
  - Run `pytest tests/test_algorithms.py -v`. Ensure all tests pass.
  - Ask the user if any questions arise before continuing.

- [x] 5. Implement `SpellService(ISpellService)` in `services/spell_service.py`
  - [x] 5.1 Implement `SpellService` class
    - `__init__` accepts a `DataService` instance (default: `DataService()`); builds BK-Tree
      and SymSpell index from `data_service.get_all()`.
    - `check_word(word: str) -> str`: short-circuit on `hash_lookup`; collect candidates from
      BK-Tree + SymSpell + N-Gram + Double Metaphone + Beam Search; rank with DL + Noisy
      Channel; return the top-ranked candidate.
    - `suggest(word: str) -> list[str]`: return top-5 ranked candidates; return `[]` for
      in-dictionary words.
    - Handle punctuation-only and empty-string inputs (return token unchanged).
    - Update `services/__init__.py` to re-export `SpellService`.
    - _Requirements: 2.3, 2.5_
  - [ ]* 5.2 Write property tests for `SpellService`
    - **Property 1: Dictionary word identity (check_word invariant)**
    - **Validates: Requirements 3.1**
    - Use Hypothesis + a small `DataService` from a fixture word list; for any word in that
      list, `check_word(word) == word`.
    - **Property 10: suggest returns list for any input**
    - **Validates: Requirements 3.2**
    - For any string, `suggest(word)` returns a `list` of non-empty strings.
    - _Requirements: 2.3, 2.5, 3.1, 3.2_
  - [ ]* 5.3 Write unit tests for `SpellService`
    - Correctly spelled word returns itself.
    - Known misspelling returns expected correction.
    - `suggest` returns empty list for in-dictionary word.
    - `ISpellService` raises `TypeError` when instantiated directly.
    - _Requirements: 2.5, 3.1, 3.2, 3.9_

- [x] 6. Fix `output_writer.py` to consume `list[Word]`
  - [x] 6.1 Update `OutputWriter.display` and `OutputWriter.export_report`
    - Change both methods to accept `feedback: list[Word]`.
    - Iterate with `for word in feedback` and format `f"{word.original} → {word.corrected}"`.
    - Import `Word` from `models.word`.
    - _Requirements: 2.7, 3.7_
  - [ ]* 6.2 Write property tests for `OutputWriter`
    - **Property 6: OutputWriter formats any list of Word objects correctly**
    - **Validates: Requirements 2.7, 3.7**
    - Use Hypothesis `builds(Word, text(...))` + `lists(...)`: for any `list[Word]`, `display`
      does not raise; `export_report` writes one line per `Word` matching
      `"original → corrected"`.
    - _Requirements: 2.7, 3.7_

- [x] 7. Create `processor.py` — `Processor` class
  - [x] 7.1 Implement `Processor` class
    - Create `processor.py` in the project root.
    - `__init__` accepts an optional `ISpellService` (default: `SpellService()`).
    - `process_text(text: str) -> tuple[str, list[Word]]`:
      - Raise `ValueError("Input cannot be empty.")` for empty/whitespace-only text.
      - Tokenise with `text.split()`; strip leading/trailing punctuation from each token
        for algorithm input while preserving original token in `Word.original`.
      - Call `spell_service.check_word(clean_token)`; set `word.corrected` and
        `word.is_misspelled = (word.original.lower() != word.corrected.lower())`.
      - Return `(" ".join(corrected_tokens), feedback_list)`.
    - _Requirements: 2.1, 2.3, 2.7_
  - [ ]* 7.2 Write property tests for `Processor`
    - **Property 9: Processor.process_text output structure**
    - **Validates: Requirements 2.1, 2.3, 2.7**
    - Use Hypothesis: for any non-empty text string, `process_text` returns `(str, list[Word])`
      with `len(feedback) == len(text.split())`.
    - **Property 7: Word constructor invariants**
    - **Validates: Requirements 3.8**
    - For any string `s`, `Word(s).original==s`, `.corrected is None`, `.is_misspelled==False`.
    - _Requirements: 2.1, 2.7, 3.8_
  - [ ]* 7.3 Write property test for `InputReader`
    - **Property 8: InputReader rejects all-whitespace input**
    - **Validates: Requirements 3.4**
    - Use Hypothesis `text(alphabet=" \t\n", min_size=1)`: `InputReader().read_text()` always
      raises `ValueError` (patch `builtins.input`).
    - _Requirements: 3.4_
  - [ ]* 7.4 Write unit tests for `Processor`
    - `process_text` on empty string raises `ValueError`.
    - `process_text` on a correctly-spelled sentence returns the same sentence.
    - `process_text` on a known misspelling returns corrected word and `is_misspelled=True`.
    - `process_text` returns exactly one `Word` per whitespace-separated token.
    - _Requirements: 2.1, 3.3, 3.4_

- [ ] 8. Merge `app_gui.py` into `main.py` and fix dependency injection
  - Move the full `SpellingCorrectorApp` Tkinter class into `main.py`, keeping the same visual design.
  - Refactor `SpellingCorrectorApp.__init__` to accept `spell_service: ISpellService = None`; default to `SpellService()` if `None`.
  - Remove direct `SpellCheckerModule` import; replace `self.spell_checker.*` calls with `self.spell_service.check_word(word)` and `self.spell_service.suggest(word)`.
  - Keep the CLI `Processor`-based path inside `main()` function in the same `main.py` file; add a `--gui` flag (or default to GUI if no stdin args) so both modes work from one entry point.
  - Delete `app_gui.py` after merging.
  - _Requirements: 2.1, 2.2, 3.5, 3.6_

- [x] 9. Refactor `spell_checker_module.py` to delegate to `SpellService`
  - Remove `pyspellchecker` import and all `index.dic` loading logic.
  - `__init__` instantiates `SpellService()` internally.
  - `check_word` and `suggest` delegate to `self.service.check_word` / `self.service.suggest`.
  - _Requirements: 2.3_

- [ ] 10. Verify `main.py` end-to-end wiring (no source changes expected)
  - Confirm `main.py` imports `Processor` correctly — no changes needed once `processor.py`
    exists.
  - Trace the call chain manually in code review: `InputReader → Processor → SpellService
    → OutputWriter`.
  - _Requirements: 2.1_

- [x] 11. Final checkpoint — full test suite passes
  - Run `pytest -v` and confirm all tests in `tests/test_algorithms.py`,
    `tests/test_spell_service.py`, and `tests/test_processor.py` pass with zero failures.
  - Ensure all tests pass. Ask the user if any questions arise.
  - _Requirements: 2.6_

---

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP.
- Every property test must include the tag comment
  `# Feature: spell-corrector-algorithms, Property N: <property_text>` directly above each
  `@given` decorated test function.
- Apply `@settings(max_examples=100)` to all Hypothesis tests to satisfy the 100-iteration
  minimum.
- `dictionary.txt` is the single source of truth; `DataService` owns loading it — never
  hardcode word lists in algorithm code.
- `services/__init__.py` should re-export `SpellService` and `DataService` for clean imports.
- The `pyspellchecker` library dependency can be removed from `requirements.txt` once tasks 5
  and 9 are complete.
