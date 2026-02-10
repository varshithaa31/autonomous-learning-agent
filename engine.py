import os
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

# 1. Load environment variables from .env file
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

class AgentState(TypedDict):
    topic: str
    explanation: str
    feynman_text: str
    questions: str

# 2. Initialize LLM correctly using the variable
llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    groq_api_key=api_key  # This fetches the key from your .env
)

def explain_node(state: AgentState):
    topic = state["topic"]
    
    academic_prompt = f"Provide a technical, structured academic breakdown of '{topic}'."
    
    feynman_prompt = (
        f"Explain '{topic}' using a deep, detailed analogy. "
        f"Break it down into specific roles (e.g., The Clerk, The Manager). "
        f"Describe how these parts interact step-by-step and relate them to the topic."
    )
    
    quiz_prompt = f"Generate 5 unique MCQs for '{topic}'. Format: Q: [Text] A) [Opt] B) [Opt] C) [Opt] Answer: [Letter]"
    
    return {
        "explanation": llm.invoke(academic_prompt).content,
        "feynman_text": llm.invoke(feynman_prompt).content,
        "questions": llm.invoke(quiz_prompt).content
    }

workflow = StateGraph(AgentState)
workflow.add_node("explain", explain_node)
workflow.set_entry_point("explain")
workflow.add_edge("explain", END)
learning_graph = workflow.compile()