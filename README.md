# Spelling Corrector Application

## 📖 Description
The Spelling Corrector Application is a standalone Python project designed to help users efficiently detect and correct spelling errors in digital text.  
It operates entirely offline using the **Hunspell dictionary system**, ensuring reliable performance without requiring internet connectivity.  
The application emphasizes simplicity, usability, and accessibility, with a clean graphical interface and structured Input → Process → Output workflow.

Through this tool, users can improve writing accuracy, minimize typographical mistakes, and enhance communication quality in academic, professional, and personal tasks.

---

## 🎯 Rationale
This project was proposed to address common difficulties in producing error‑free written text:
- Frequent spelling mistakes and typographical errors
- Reliance on online tools that require internet access
- Time‑consuming manual proofreading

By automating spelling detection and correction, the application saves time, improves clarity, and boosts productivity.

---

## 🗂 Project Structure
SpellingCorrector/
│
├── interfaces/  
├── models/  
├── services/  
├── tests/  
├── main.py  
├── spell_checker_module.py  
├── app_gui.py  
└── output_writer.py  

---

## ⚙️ Features
- **Text Input** – Enter words, sentences, or paragraphs for checking  
- **Spelling Detection** – Identify misspelled words using Hunspell  
- **Suggestions & Feedback** – Provide correction recommendations  
- **Output Writer** – Save corrected text and reports to `.txt` files  
- **Offline Capability** – Works without internet connection  
- **Automated Testing** – Pytest unit tests for reliability  

---

## 🛠 OOP & SOLID Principles
- **Encapsulation** – Private attributes and controlled access  
- **Abstraction** – Interfaces for dictionary and correction services  
- **Polymorphism** – Flexible suggestion algorithms  
- **Modularity** – Clear separation into models, services, interfaces, UI, and tests  
- **SOLID** – Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion  

---

## 🌍 Sustainable Development Goal (SDG)
Supports **SDG 4: Quality Education** by improving spelling accuracy, literacy, and communication skills for learners and professionals.

---

## ▶️ How to Run
1. Install dependencies:
   ```bash
   pip install pytest hunspell
