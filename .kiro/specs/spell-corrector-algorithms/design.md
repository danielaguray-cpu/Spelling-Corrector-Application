# Design Document — Spell Corrector Algorithms (Bugfix)

## Overview

This document describes the design for fixing the Spelling Corrector Application so that both
the CLI entry point (`main.py`) and the GUI (`app_gui.py`) work correctly end-to-end. The fix
introduces a concrete service layer, implements all 10 spell-correction algorithms from scratch
(no `pyspellchecker` dependency for algorithm logic), provides a bundled word-list dictionary,
aligns `output_writer.py` to consume `Word` objects, and adds comprehensive pytest coverage.

The architecture follows a clean dependency-injection pattern already implied by the `interfaces/`
layer: `Processor` and `app_gui.py` depend on `ISpellService` and `IDataService` abstractions;
concrete implementations live in `services/`.

---

## Glossary

- **ISpellService** — Abstract base class defining `check_word(word) -> str` and `suggest(word) -> list[str]`
- **IDataService** — Abstract base class defining `add`, `update`, `delete`, `get_all`
- **SpellService** — Concrete `ISpellService` implementation running all 10 algorithms
- **DataService** — Concrete `IDataService` implementation loading `dictionary.txt`
- **Processor** — Orchestrates CLI text flow: tokenise → check → assemble `Word` feedback
- **Word** — Data model holding `original`, `corrected`, and `is_misspelled` fields
- **BK-Tree** — Metric-space tree for efficient edit-distance nearest-neighbour queries
- **SymSpell** — Symmetric-delete lookup algorithm for fast candidate retrieval
- **Double Metaphone** — Phonetic encoding algorithm for sound-alike matching
- **Noisy Channel Model** — Bayesian correction: `P(correction | observed) ∝ P(observed | correction) × P(correction)`
- **Viterbi** — Dynamic-programming sequence decoder used for single-word correction lattice
- **Beam Search** — Best-first search over edit-step space keeping top-K candidates

---

## Bug Details

The application has seven distinct defects that collectively prevent it from running at all:

1. **Missing `processor.py`** — `main.py` imports `from processor import Processor` but the file
   does not exist, causing an immediate `ModuleNotFoundError` on every CLI launch.

2. **Broken dependency injection in `app_gui.py`** — `SpellingCorrectorApp` directly instantiates
   `SpellCheckerModule` rather than accepting an `ISpellService`, making the interface layer a
   dead code path.

3. **Empty `services/` layer** — `services/__init__.py` is empty; no `spell_service.py` or
   `data_service.py` exists, so `ISpellService` and `IDataService` have no concrete implementations.

4. **All algorithm logic delegated to `pyspellchecker`** — `spell_checker_module.py` calls
   `SpellChecker()` from the third-party library; none of the 10 required algorithms
   (Levenshtein, Damerau-Levenshtein, BK-Tree, SymSpell, N-Gram, Double Metaphone,
   Noisy Channel, Viterbi, Beam Search, Hash Set Lookup) are implemented anywhere in the codebase.

5. **Missing dictionary file** — `SpellCheckerModule.__init__` opens `index.dic` which does not
   exist in the repository, raising a file-not-found exception even when `pyspellchecker` is
   available.

6. **`output_writer.py` expects a `dict` but will receive `list[Word]`** — both `display` and
   `export_report` call `.items()` on the `feedback` parameter; once `Processor` returns a
   `list[Word]` this raises `AttributeError`.

7. **Empty `tests/` directory** — the README claims all pytest tests pass, but no test files
   exist; `pytest -v` collects zero tests.

---

## Expected Behavior

After the fix is applied:

- `python main.py` completes a full CLI spell-check cycle without import errors.
- `python app_gui.py` launches the GUI; spell-checking is routed through `ISpellService`.
- All 10 algorithms execute for every correction request and aggregate results via voting.
- `SpellService` and `DataService` instantiate cleanly, loading `dictionary.txt` from disk.
- `OutputWriter.display` and `OutputWriter.export_report` correctly iterate a `list[Word]` and
  produce `"original → corrected"` lines.
- `pytest -v` collects and passes tests in `test_algorithms.py`, `test_spell_service.py`, and
  `test_processor.py` covering each algorithm, the service layer, and end-to-end flow.
- All regression behaviours documented in `bugfix.md` section 3 are preserved.

---

## Hypothesized Root Cause

The application was designed with a layered, interface-driven architecture
(`interfaces/ → services/ → processor/GUI`) but the service-layer implementation was never
written. The placeholder `SpellCheckerModule` was added as a temporary shortcut that
delegated everything to `pyspellchecker`, bypassing the intended architecture. Over time:

- `processor.py` was never created, leaving `main.py` broken.
- `services/` was never populated, leaving `ISpellService` and `IDataService` as dead interfaces.
- The dictionary file (`index.dic`) was never committed, so even the pyspellchecker path fails.
- `output_writer.py` was written to a `dict`-based feedback contract that was later superseded
  by the `Word` model but never updated.
- Tests were planned but never written.

The root cause is incomplete implementation of the service layer after the interface skeleton
was established.

---

## Fix Implementation

### Architecture

```
main.py / app_gui.py
       │
       ▼
  Processor                   ← new file; orchestrates CLI flow
       │ uses ISpellService
       ▼
services/spell_service.py     ← SpellService(ISpellService)
       │ uses IDataService
       ▼
services/data_service.py      ← DataService(IDataService) — loads dictionary.txt
       │
       ▼
dictionary.txt                ← bundled plain-text word list (one word per line)
```

`app_gui.py` is refactored so that `SpellingCorrectorApp.__init__` accepts an `ISpellService`
parameter (default: `SpellService()`). This keeps the GUI decoupled from algorithm details.

`output_writer.py` is aligned to iterate a `list[Word]` instead of a `dict`.

### Components and Interfaces

#### Existing Interfaces (unchanged)

```python
# interfaces/ispell_service.py
class ISpellService(ABC):
    def check_word(self, word: str) -> str: ...   # returns corrected word
    def suggest(self, word: str) -> list[str]: ... # returns candidate list
```

```python
# interfaces/idata_service.py
class IDataService(ABC):
    def add(self, item): ...
    def update(self, item): ...
    def delete(self, item_id): ...
    def get_all(self) -> list: ...
```

#### New / Fixed Components

| File | Class | Responsibility |
|------|-------|---------------|
| `services/data_service.py` | `DataService(IDataService)` | Loads `dictionary.txt`; stores words in a `set` for O(1) lookup; implements `add/update/delete/get_all` |
| `services/spell_service.py` | `SpellService(ISpellService)` | Holds a `DataService`; runs all 10 algorithms; returns best correction via voting |
| `processor.py` | `Processor` | Tokenises input text; calls `SpellService`; constructs `Word` objects; returns `(corrected_text, feedback)` |
| `app_gui.py` | `SpellingCorrectorApp` | Accepts `ISpellService` via DI; delegates `check_word` / `suggest` calls |
| `output_writer.py` | `OutputWriter` | Iterates `list[Word]`; formats `word.original → word.corrected` lines |
| `spell_checker_module.py` | `SpellCheckerModule` | Thin façade; delegates to `SpellService`; no longer uses `pyspellchecker` |
| `dictionary.txt` | — | Bundled word list (~10 000 common English words, one per line) |

### Data Models

#### Word (existing — unchanged)

```python
class Word:
    original: str       # token as extracted from input
    corrected: str|None # best correction found; None if not yet processed
    is_misspelled: bool # True when original != corrected after processing
```

#### Feedback structure (new contract)

`Processor.process_text(text: str) -> tuple[str, list[Word]]`

- `str` — the fully corrected sentence (words joined by space)
- `list[Word]` — one `Word` per token; `corrected` and `is_misspelled` populated

`OutputWriter` consumes `list[Word]` directly.

### Algorithm Design

All 10 algorithms are implemented as pure Python functions/classes with no external
spell-checking library dependency. They share the dictionary `set[str]` supplied by
`DataService`.

#### 1. Hash Set Lookup (O(1) Dictionary Check)

The simplest algorithm. A word is considered correct if it exists in the dictionary set.
Used as a short-circuit: if `word.lower()` is in the set, return it immediately without
running the distance-based algorithms.

```
is_correct(word) := word.lower() in dictionary_set
```

#### 2. Levenshtein Distance

Classic dynamic-programming edit distance (insertions, deletions, substitutions).
For a query word `q`, scan all dictionary candidates whose length is within ±2 of `|q|`
and return the one(s) with minimum distance.

```
lev(a, b):
  dp[i][j] = edit distance between a[:i] and b[:j]
  transitions: insertion (+1), deletion (+1), substitution (+0 or +1)
```

**Properties:**
- `lev(a,a) == 0`
- `lev(a,b) == lev(b,a)` (symmetric)
- `lev(a,c) <= lev(a,b) + lev(b,c)` (triangle inequality)

#### 3. Damerau-Levenshtein Distance

Extends Levenshtein with transposition of adjacent characters (cost 1).
`dl_distance(a, b) <= lev_distance(a, b)` always.

#### 4. BK-Tree

Metric-space tree built over the dictionary using Levenshtein distance as the metric.
Supports efficient nearest-neighbour queries:
`search(word, tolerance=2)` returns all dictionary words within edit distance 2 of `word`.

Build: insert each dictionary word; each node stores `{distance: child_node}`.

#### 5. SymSpell

Symmetric-delete algorithm: pre-compute all deletes of each dictionary word up to
edit distance 2. Store as `delete_hash: {derived_form -> set[original_words]}`.
For a query, generate all deletes of the query up to depth 2 and look up in the hash;
the real edit distance is computed only for candidates found this way.

#### 6. N-Gram Similarity (Jaccard)

Tokenise both strings into character n-grams (n=2, bigrams by default).
Jaccard similarity: `|A ∩ B| / |A ∪ B|`.
Return the dictionary word with the highest Jaccard similarity to the query.

**Properties:**
- Result in `[0.0, 1.0]`
- `jaccard(s, s) == 1.0` for any non-empty string

#### 7. Double Metaphone

Phonetic encoding algorithm. Each word is encoded to a primary (and optional secondary)
phonetic key. Implemented as a pure-Python translation of the Lawrence Philips algorithm
(standard rule table — no external library). Dictionary words are indexed by their metaphone
key. Candidates with a matching phonetic key are returned as suggestions.

#### 8. Noisy Channel Model (Bayesian)

`P(correction | observed) ∝ P(observed | correction) × P(correction)`

- `P(correction)` — unigram frequency from dictionary (uniform if no frequency data)
- `P(observed | correction)` — approximated by `exp(-lev_distance(observed, correction))`

Select the correction maximising the posterior over the candidate set (from BK-Tree or
SymSpell candidates).

#### 9. Viterbi Algorithm

Applied to single-word correction. The "hidden state" is the correct word; the "observation"
is the misspelled form. Transition model: edit distance-based probability. Emission:
character-level confusion probability (uniform approximation). Over a small candidate set
this reduces to Bayesian selection but is structured as a Viterbi lattice for extensibility
to sequence decoding.

#### 10. Beam Search

Beam search over the edit-step space. Starting from the observed word, iteratively generate
candidate edits (single-character insertions, deletions, substitutions, transpositions) and
keep the top-K beams (default K=5) at each step. Terminate when a beam matches a dictionary
word. Complements Levenshtein by exploring the correction space without exhaustive enumeration.

#### Algorithm Aggregation (Voting)

`SpellService.check_word(word)`:
1. If `HashSetLookup.is_correct(word)` → return `word` immediately.
2. Collect candidate lists from: BK-Tree, SymSpell, N-Gram, Double Metaphone, Beam Search.
3. Score each unique candidate with Levenshtein, Damerau-Levenshtein, Noisy Channel.
4. Rank by weighted score; return the top candidate as the correction.

`SpellService.suggest(word)`:
- Return the top-5 ranked candidates from the aggregation step.

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions
of a system — essentially, a formal statement about what the system should do. Properties
serve as the bridge between human-readable specifications and machine-verifiable correctness
guarantees.*

### Property 1: Dictionary word identity (check_word invariant)

*For any* word drawn from the loaded dictionary, `check_word(word)` SHALL return `word`
unchanged (case-insensitive comparison on the returned value).

**Validates: Requirements 3.1**

### Property 2: Levenshtein metric axioms

*For any* two strings `a` and `b`:
- `lev(a, a) == 0` (reflexivity)
- `lev(a, b) == lev(b, a)` (symmetry)
- `lev(a, c) <= lev(a, b) + lev(b, c)` for any third string `c` (triangle inequality)
- `lev(a, b) >= 0` (non-negativity)

**Validates: Requirements 2.3**

### Property 3: Damerau-Levenshtein is bounded by Levenshtein

*For any* two strings `a` and `b`, `dl_distance(a, b) <= lev_distance(a, b)`.

**Validates: Requirements 2.3**

### Property 4: N-gram Jaccard similarity range and reflexivity

*For any* two non-empty strings `a` and `b`:
- `0.0 <= jaccard(a, b) <= 1.0`
- `jaccard(s, s) == 1.0` for any non-empty string `s`

**Validates: Requirements 2.3**

### Property 5: Hash Set Lookup round-trip

*For any* word added to the dictionary set, `HashSetLookup.is_correct(word)` SHALL return
`True`; for any word not added, it SHALL return `False`.

**Validates: Requirements 2.3, 2.4**

### Property 6: OutputWriter formats any list of Word objects correctly

*For any* list of `Word` objects (with arbitrary `original` and `corrected` strings),
`OutputWriter.display` and `OutputWriter.export_report` SHALL NOT raise an exception and
SHALL produce output lines of the form `"{word.original} → {word.corrected}"` for each
word in the list.

**Validates: Requirements 2.7, 3.7**

### Property 7: Word constructor invariants

*For any* string `s`, `Word(s)` SHALL satisfy: `word.original == s`, `word.corrected is None`,
`word.is_misspelled == False`.

**Validates: Requirements 3.8**

### Property 8: InputReader rejects all-whitespace input

*For any* string composed entirely of whitespace characters (spaces, tabs, newlines),
`InputReader.read_text()` SHALL raise `ValueError`.

**Validates: Requirements 3.4**

### Property 9: Processor.process_text output structure

*For any* non-empty text string, `Processor.process_text(text)` SHALL return a tuple
`(corrected_str, feedback_list)` where `corrected_str` is a non-empty string and
`feedback_list` is a list of `Word` objects whose length equals the number of
whitespace-separated tokens in the original text.

**Validates: Requirements 2.1, 2.3, 2.7**

### Property 10: suggest returns list for any input

*For any* string `word`, `SpellService.suggest(word)` SHALL return a `list` (possibly empty),
and every element in the list SHALL be a non-empty string.

**Validates: Requirements 3.2**

---

## Error Handling

| Scenario | Handling |
|----------|---------|
| `dictionary.txt` missing | `DataService.__init__` raises `FileNotFoundError` with a descriptive message; caught at startup to print a clear error |
| `check_word` receives empty string | Strip and return `""` without algorithm invocation |
| `check_word` receives punctuation-only token | Return token unchanged |
| BK-Tree search on empty dictionary | Return empty candidate list |
| SymSpell pre-computation on very long words (>50 chars) | Skip pre-computation; fall back to direct Levenshtein |
| `Processor.process_text` receives empty/whitespace text | Raise `ValueError("Input cannot be empty.")` |
| `OutputWriter.export_report` encounters I/O error | Propagate `IOError`; caller handles |

---

## Testing Strategy

### Dual Testing Approach

Unit tests handle specific examples, edge cases, and error conditions. Property-based tests
verify universal invariants across many generated inputs. Both are required.

**Property-based testing library:** `hypothesis` (Python)
- Minimum 100 iterations per property test (Hypothesis default strategy is ≥100 examples)
- Each property test references its design property via a comment tag

**Tag format:** `# Feature: spell-corrector-algorithms, Property N: <property_text>`

### Test Files

| File | Coverage |
|------|---------|
| `tests/test_algorithms.py` | Each of the 10 algorithms individually; Properties 2, 3, 4, 5 |
| `tests/test_spell_service.py` | `SpellService` full interface; Properties 1, 10 |
| `tests/test_processor.py` | `Processor` end-to-end; Properties 6, 7, 8, 9 |

### Unit Test Focus Areas

- Levenshtein: known pairs (`("kitten","sitting") == 3`, `("","abc") == 3`)
- Damerau-Levenshtein: transposition case (`("ab","ba") == 1` vs lev `== 2`)
- BK-Tree: build with small vocabulary, search returns correct neighbours
- SymSpell: pre-compute and query known misspellings
- N-Gram: empty-string edge cases, single-char strings
- Double Metaphone: known phonetic equivalences (e.g. "Smith" == "Smyth")
- Noisy Channel: correct word gets higher probability than random string
- Viterbi: single best path matches Noisy Channel winner for small candidate sets
- Beam Search: terminates and returns a dictionary word for simple single-edit errors
- Hash Set: correct and incorrect words; case insensitivity

### Property Test Generators

- **Arbitrary strings:** `hypothesis.strategies.text(alphabet=string.ascii_lowercase, min_size=1)`
- **Word pairs:** two independent `text()` draws
- **Word lists:** `lists(text(...), min_size=1, max_size=20)`
- **Whitespace-only strings:** `text(alphabet=" \t\n", min_size=1)`
- **Word objects:** `builds(Word, text(min_size=1))`
- **Feedback lists:** `lists(builds(Word, text(min_size=1)), min_size=1)`
