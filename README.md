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

---

## OOP Concepts Implemented

### This project demonstrates core Object-Oriented Programming Principles:

- Encapsulation 
- Polymorphism
- Dependency Injection
- Loose Coupling
- Abstraction: 

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
│   ├── __init__.py  
│   ├── idata_service.py  
│   └── ispell_service.py  
│  
├── models/  
│   ├── __init__.py  
│   └── word.py  
│  
├── services/  
│   ├── __init__.py  
│  
├── tests/  
│   ├── __init__.py  
│  
├── app_gui.py  
├── custom_words.txt  
├── input_reader.py  
├── main.py  
├── output_writer.py  
└── spell_checker_module.py  

---

## Running the Application

Open a terminal in the project folder and run:

python main.py

---

## Running the Tests

Execute the following command:

pytest -v

---

## Sample Usage

### Input

text: the goverment is changing tac rules tomorow

### Corrected Output

text: the government is changing tax rules tomorrow

### Suggestions

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

## Authors

- **Daniela Guray**  
  GitHub: [@danielaguray-cpu](https://github.com/danielaguray-cpu)

- **Clarice Febrero**  
  GitHub: [@claricefebrero](https://github.com/claricefebrero)

- **Maria Daphnie Gordola**  
  GitHub: [@grdlmrdphn-cpu](https://github.com/grdlmrdphn-cpu)

---

In Partial Fulfillment of the Requirements for the Subject **CC103 Computer Programming 2**  
Bachelor of Science in Information Technology  Under the Course of Bachelor of Science in Information Technology at Sorsogon State University Bulan Campus. With the supervision of **Professor John Mark Gabrentina**

---



