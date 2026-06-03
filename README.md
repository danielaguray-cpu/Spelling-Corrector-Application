# Spelling Corrector Application

## Description
The Spelling Corrector Application is a desktop-based tool developed in Python that helps users identify and correct spelling errors in words, sentences, and paragraphs. The application uses a Hunspell dictionary (index.dic and index.aff) to detect misspelled words and provide appropriate correction suggestions. It features a user-friendly graphical interface that makes spell checking simple and efficient.

---

## Features

### Feature 1: Input
Allows users to enter text that will be checked for spelling errors.

### Feature 2: Spelling Detection
Identifies misspelled words by comparing the entered text with the dictionary.

### Feature 3: Suggestion and Feedback
Provides correction suggestions, displays the corrected text, and gives feedback about the spelling check results.

---

## Technologies Used

- Python
- Tkinter (GUI)
- Hunspell Dictionary
- Pytest (Unit Testing)
- Object-Oriented Programming (OOP)

---

## OOP Concepts Implemented

- Encapsulation
- Polymorphism
- Dependency Injection
- Loose Coupling

---

## Project Structure

SpellingCorrector/
│
├── .idea/
│   ├── modules.xml
│   ├── spelling corrector application.iml
│   └── workspace.xml
│
├── .pytest_cache/
├── .vscode/
├── hunspell-master/
│
├── interfaces/
│   ├── init.py
│   ├── idata_service.py
│   └── ispell_service.py
│
├── models/
│   ├── init.py
│   └── word.py
│
├── services/
│   ├── init.py
│
├── tests/
│   ├── init.py
│
├── app_gui.py
├── custom_words.txt
├── input_reader.py
├── main.py
├── output_writer.py
└── spell_checker_module.py
---

## Installation

### 1. Download or Clone the Project

Place all project files inside a folder named:

text
SpellingCorrector

### 2. Install Required Libraries

pip install hunspell
pip install pytest

### 3. Add Dictionary Files

Place the following files in the project folder:

text
index.dic
index.aff

---

## Running the Application

Open a terminal in the project folder and run:

python main.py

---

## Running the Tests

Execute the following command:

pytest -v

Expected result:

text
========================
3 passed
========================

---

## Sample Usage

### Input

text
the goverment is changing tac rules tomorow

### Corrected Output

text
the government is changing tax rules tomorrow

### Suggestions

text
goverment → government
tac → tax
tomorow → tomorrow

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

## Developers

Developed as a course project for Object-Oriented Programming (OOP), applying software engineering principles and testing methodologies to create a reliable and user-friendly spelling correction system.
