# 📝 Homework Assistant with LangGraph & Ollama  

An AI-powered agent that assists students in completing homework using **available reference documents** and **homework question PDFs**.  

The agent takes:  
1. A **reference material PDF** (study material).  
2. A **questions PDF** (homework questions).  

It then:  
- Reads the reference material.  
- Reads the homework questions.  
- Drafts answers based on the reference material.  
- Prints the completed homework draft with subject detection.  

---

## 📂 Project Structure  

.
├── main.py # Main script with graph workflow
├── boy_who_lived.pdf # Reference material (example)
├── questions.pdf # Homework questions (example)
├── README.md # Project documentation
└── venv/ # Virtual environment (optional)


---

## ⚙️ Installation  

1. Clone the repository and enter the project directory:  
   ```bash
   git clone <your-repo-url>
   cd agentpractice

2. Create and activate a virtual environment:
python3 -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows

3. Install dependencies
pip install langchain langchain-community langgraph langchain-ollama pypdf

4. Install and run Ollama (if not installed):
You can change the LLM by making chanes in code. This agent uses **phi3:mini**.

Note: Yet to add more features.
