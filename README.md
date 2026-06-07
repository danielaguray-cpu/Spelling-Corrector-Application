# Spelling Corrector Application

## Description
The Spelling Corrector Application is a desktop-based tool developed in Python that helps users identify and correct spelling errors in words, sentences, and paragraphs. The application uses advanced algorithms (SymSpell, Levenshtein distance, and n-gram context) with a 466,550-word dictionary to detect misspelled words and provide appropriate correction suggestions. It features a user-friendly graphical interface that makes spell checking simple and efficient.

---

## Features

### Feature 1: Input
Allows users to enter text that will be checked for spelling errors.

### Feature 2: Spelling Detection
Identifies misspelled words by comparing the entered text with the dictionary using SymSpell delete index and Levenshtein distance algorithms.

### Feature 3: Suggestion and Feedback
Provides correction suggestions, displays the corrected text, and gives feedback about the spelling check results using n-gram context scoring.

---

## Technologies Used

- Python 3.11+
- Tkinter (GUI)
- SymSpell Algorithm (Delete Index)
- Levenshtein Distance
- N-Gram Context Scoring
- Pytest (Unit Testing)
- 466,550-word Dictionary

---

## OOP Concepts Implemented

- Encapsulation - Data hiding within classes
- Polymorphism - Interface-based design (IDataService, ISpellService)
- Dependency Injection - Services are injected where needed
- Loose Coupling - Interfaces separate concerns
- Abstraction - Abstract base classes define contracts

---

## Project Structure

Spelling-Corrector-Application/
|
+-- interfaces/
|   +-- __init__.py
|   +-- idata_service.py
|   +-- ispell_service.py
|
+-- models/
|   +-- __init__.py
|   +-- word.py
|
+-- services/
|   +-- __init__.py
|   +-- spell_service.py
|
+-- tests/
|   +-- __init__.py
|   +-- test_spell_service.py
|   +-- test_algorithms.py
|   +-- test_processor.py
|
+-- app_gui.py
+-- main.py
+-- processor.py
+-- definitions.py
+-- dictionary.txt
+-- input_reader.py
+-- output_writer.py
+-- spell_checker_module.py
+-- README.md

---

## Installation

Prerequisites:
- Python 3.11 or higher
- pip (Python package manager)

Steps:

1. Clone the repository:
   git clone https://github.com/danielaguray-cpu/Spelling-Corrector-Application.git
   cd Spelling-Corrector-Application

2. Install dependencies:
   pip install pytest

3. Run the application:
   python main.py

---

## Running the Application

GUI Mode (Default):
   python main.py

---

## Running the Tests

   pytest -v

---

## Sample Usage

Input:
   the goverment is changing tac rules tomorow

Corrected Output:
   the government is changing tax rules tomorrow

Suggestions:
   goverment -> government
   tac -> tax
   tomorow -> tomorrow

Another Example:
   Input:  He stood in the centir of the room!
   Output: He stood in the center of the room!

---

## Algorithms Implemented

- SymSpell Delete Index - O(1) candidate generation for typos
- Levenshtein Distance - Edit distance calculation with early exit
- N-Gram (Bigram) Context Scoring - Resolves ambiguous corrections using context
- Bounded Levenshtein - Performance optimization for large dictionaries
- Hash Set Dictionary Lookup - O(1) correct word verification

---

## Sustainable Development Goal (SDG)

### SDG 4: Quality Education

This application supports SDG 4 by helping users improve their spelling, writing accuracy, and language skills. It serves as an educational tool that assists students and learners in producing error-free written content and developing better communication abilities.

---

## Testing

The application was tested using:

- Functional Testing
- User Interface Testing
- Manual Testing
- Error Handling Testing
- Automated Unit Testing using Pytest

All test cases passed successfully, confirming that the system functions correctly and reliably.

---

## Authors

- Daniela Guray
  GitHub: @danielaguray-cpu

- Clarice Febrero
  GitHub: @claricefebrero

- Maria Daphnie Gordola
  GitHub: @grdlmrdphn-cpu

---

In Partial Fulfillment of the Requirements for the Subject CC103 Computer Programming 2
Bachelor of Science in Information Technology at Sorsogon State University Bulan Campus.
Under the supervision of Professor John Mark Gabrentina.
