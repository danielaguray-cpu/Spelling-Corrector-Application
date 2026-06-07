# Bugfix Requirements Document

## Introduction

The Spelling Corrector Application has multiple structural and implementation defects that prevent it from running at all. The CLI entry point (`main.py`) crashes immediately because `processor.py` does not exist. The GUI (`app_gui.py`) bypasses the interface layer by directly importing `SpellCheckerModule`, breaking the intended dependency injection architecture. The `services/` layer is entirely empty — no concrete implementations of `ISpellService` or `IDataService` exist. The required suite of 10 spelling-correction algorithms (Levenshtein, Damerau-Levenshtein, BK-Tree, SymSpell, N-Gram/Jaccard, Double Metaphone, Noisy Channel/Bayesian, Viterbi, Beam Search, Hash Set Lookup) is completely absent, with `spell_checker_module.py` delegating all work to the third-party `pyspellchecker` library instead. The Hunspell dictionary file (`index.dic`) referenced in code is missing from the repository. `output_writer.py` iterates feedback as a `dict` but the structure returned by `Processor` (once created) may be incompatible. Finally, the `tests/` directory is empty despite the README claiming all pytest tests pass.

The fix must: create `processor.py`, implement all 10 algorithms in the service layer, wire `app_gui.py` through the interface, provide a bundled dictionary, align `output_writer.py` to the correct feedback structure, and add comprehensive pytest unit tests — so that both the CLI and GUI work correctly end-to-end.

---

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN `main.py` is executed THEN the system crashes with `ModuleNotFoundError: No module named 'processor'` because `processor.py` does not exist.

1.2 WHEN `app_gui.py` is launched THEN the system imports `SpellCheckerModule` directly, bypassing `ISpellService`, breaking the dependency-injection design and making the interface layer non-functional.

1.3 WHEN any spell-checking operation is requested THEN the system delegates entirely to `pyspellchecker` because `spell_checker_module.py` contains no custom algorithm implementations, ignoring the required suite of 10 algorithms.

1.4 WHEN `SpellCheckerModule.__init__` attempts to load the dictionary THEN the system raises a file-not-found exception because `index.dic` does not exist in the repository.

1.5 WHEN `services/` is imported THEN the system provides no concrete `ISpellService` or `IDataService` implementations because `services/__init__.py` is empty and no service modules exist.

1.6 WHEN the test suite is executed with `pytest -v` THEN the system reports zero tests collected because `tests/__init__.py` is empty and no test files exist.

1.7 WHEN `output_writer.py` iterates the `feedback` parameter THEN the system may raise `AttributeError` or produce incorrect output if `Processor.process_text` returns a list of `Word` objects rather than a plain `dict`.

---

### Expected Behavior (Correct)

2.1 WHEN `main.py` is executed THEN the system SHALL import and instantiate `Processor` from `processor.py` without error, and complete a full CLI spell-check cycle.

2.2 WHEN `app_gui.py` is launched THEN the system SHALL obtain its spell-checking functionality through the `ISpellService` interface (dependency injection), so that concrete algorithm implementations can be swapped without modifying the GUI.

2.3 WHEN a spell-checking operation is requested THEN the system SHALL execute all 10 required algorithms — Levenshtein Distance, Damerau-Levenshtein, BK-Tree, SymSpell, N-Gram Similarity (Jaccard), Double Metaphone, Noisy Channel Model (Bayesian), Viterbi Algorithm, Beam Search, and Hash Set Lookup — and aggregate their results to produce a correction and candidate suggestions.

2.4 WHEN `SpellCheckerModule` (or its service-layer replacement) initialises THEN the system SHALL load a bundled dictionary (plain word-list file present in the repository) without raising any file-not-found or I/O exception.

2.5 WHEN `services/` is imported THEN the system SHALL provide at least one concrete class that fully implements `ISpellService` (`check_word` and `suggest`) and at least one concrete class that fully implements `IDataService` (`add`, `update`, `delete`, `get_all`).

2.6 WHEN `pytest -v` is executed THEN the system SHALL run and pass unit tests covering each of the 10 algorithms individually, the service-layer `ISpellService` implementation, and the `Processor` class end-to-end.

2.7 WHEN `output_writer.display` and `output_writer.export_report` receive the feedback structure produced by `Processor.process_text` THEN the system SHALL iterate it correctly and display/write `original → corrected` lines without error.

---

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a correctly spelled word is passed to `check_word` THEN the system SHALL CONTINUE TO return the original word unchanged.

3.2 WHEN `suggest` is called with a correctly spelled word THEN the system SHALL CONTINUE TO return an empty list or a list containing only the word itself, with no spurious corrections.

3.3 WHEN `InputReader.read_text` receives non-empty input THEN the system SHALL CONTINUE TO return that text without modification.

3.4 WHEN `InputReader.read_text` receives empty or whitespace-only input THEN the system SHALL CONTINUE TO raise `ValueError("Input cannot be empty.")`.

3.5 WHEN the GUI "Clear" button is pressed THEN the system SHALL CONTINUE TO reset all text boxes and the feedback label to their initial empty state.

3.6 WHEN the GUI "Check Spelling" button is pressed with no input text THEN the system SHALL CONTINUE TO display the "Input Error" warning dialog.

3.7 WHEN `output_writer.export_report` is called with a valid filename and feedback THEN the system SHALL CONTINUE TO write the report file to disk and print a confirmation message.

3.8 WHEN `Word` objects are constructed THEN the system SHALL CONTINUE TO initialise `original` from the constructor argument, `corrected` as `None`, and `is_misspelled` as `False`.

3.9 WHEN the `ISpellService` and `IDataService` abstract interfaces are imported THEN the system SHALL CONTINUE TO raise `TypeError` if instantiated directly without implementing all abstract methods.
