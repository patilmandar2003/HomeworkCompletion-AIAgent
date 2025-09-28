import base64
from typing import List, TypedDict, Annotated, Optional, Dict, Any
from langchain_ollama import OllamaLLM
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
import pypdf
import asyncio
from IPython.display import Image, display

# PATH to reference material and homework questions
reference_material_path = "./boy_who_lived.pdf"
homework_questions_path = "./questions.pdf"
# Defining Agent's State
class AgentState(TypedDict, total=False):
    homework_questions: Optional[str]   # Input file provided with questions, contains path
    homework_content: Optional[str]
    reference_material: Optional[str]   # Input file provided to refer, contains path
    reference_material_content: Optional[str]
    homework_draft: Optional[str]
    # messages: Annotated[list[AnyMessage], add_messages]
    subject: Optional[str]     # Subject of homework
    # messages: List[Dict[str, Any]]  # Track converstation with LLM for analysis

# Defining LLM
model = OllamaLLM(
    model="phi3:mini",
    temperature=0
)

async def load_pages(loader: PyPDFLoader) -> List[Document]:
    """
    Loads pdf and extracts content and metadata 
    """
    pages=[]    # Stores content and metadata

    async for page in loader.alazy_load():
        pages.append(page)

    return pages

def read_material(state: AgentState):
    """
    Model reads provided reference material
    
    - reference_material: PATH to reference material pdf.
    - material_loader: loads the pdf in PyPDFLoader
    - material_pages: stores pages content and metadata

    Returns:
    - reference_material_content: Only page content of reference material and not metadata
    """

    print("Reading reference material...")

    material_loader = PyPDFLoader((state["reference_material"])) # Loads pdf

    material_pages = asyncio.run(load_pages(material_loader))      

    return {
        "reference_material_content": material_pages[0].page_content
    }

def read_questions(state: AgentState):
    """
    Model reads the homework questions.

    - homework_questions: PATH to homework pdf.
    - homework_loader: loads the pdf in PyPDFLoader
    - homework_pages: stores page content and metadata
    
    Returns:
    - homework_content: returns only content of homework pdf.
    """

    print("Reading homework questions...")

    homework_loader = PyPDFLoader((state["homework_questions"]))
    
    homework_pages = asyncio.run(load_pages(homework_loader))

    return {
        "homework_content": homework_pages[0].page_content
    }

def draft_homework(state: AgentState):
    """
    Reads and understands reference material and homework questions and drafts solutions.

    - reference_content: Content of reference material.
    - homework_questions: Questions of homework.

    Returns:
    - subject: The subject of the homework. [English, Mathematics, Science, etc.]
    - homework_draft: Draft of the homework
    """

    print("Drafting homework...")
    
    reference_content = state['reference_material_content']
    homework_questions = state['homework_content']

    prompt = f"""
    As a homework completion LLM.
    Tasks:
    1. Read and understand the reference material 
    2. Identify the subject of the homework
    3. Read and understand homework questions
    4. Answer homework questions based on reference material


    Reference material: {reference_content}
    Homework questions: {homework_questions}

    Output format:
    Subject: (The subject of homework. [English, Mathematics, Science])
    Question: (Question from homework_questions extracted from pdf. Do not add or reframe questions.)
    Answer: (Answer to the question.)
    """

    # Call the LLM
    messages = [HumanMessage(content=prompt)]
    response = model.invoke(messages)

    # Logic to parse the response and identify the subject
    response_text = response.lower()
    subject = None
    if "subject:" in response_text:
        subject_line = response_text.split("subject:")[1].split("\n")[0].strip()
        # keep only first word (one-word subject)
        subject = subject_line.split()[0]

    return {
        "subject": subject,
        "homework_draft": response
    }

def print_homework(state: AgentState):
    """
    Print homework 
    
    -homework_draft: Draft prepared by LLM.
    """

    homework_draft = state["homework_draft"]

    print("\n" + "="*50)
    print(f"{homework_draft}")
    print("="*50 + "\n")

    return {}

# Creating Stategraph and defining edges
# Create graph
homework_graph = StateGraph(AgentState)

# Add nodes
homework_graph.add_node("read_material", read_material)
homework_graph.add_node("read_questions", read_questions)
homework_graph.add_node("draft_homework", draft_homework)
homework_graph.add_node("print_homework", print_homework)

# Add edges
homework_graph.add_edge(START, "read_material")     # Start edge
homework_graph.add_edge("read_material", "read_questions")
homework_graph.add_edge("read_questions", "draft_homework")
homework_graph.add_edge("draft_homework", "print_homework")
homework_graph.add_edge("print_homework", END)     # End edge

# Compile the graph
compiled_graph = homework_graph.compile()

# Invoke graph
homework_response = compiled_graph.invoke({
    "homework_questions": homework_questions_path,
    "homework_content": None,
    "reference_material": reference_material_path ,  # Input file provided to refer, contains path
    "reference_material_content": None,
    "homework_draft": None,
    "subject": None    # Subject of homework
})
