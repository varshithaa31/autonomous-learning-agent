from typing import List, TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from context import gather_context

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

class AgentState(TypedDict):
    topic: str
    context: str
    explanation: str
    feynman_text: str 
    questions: str
    is_feynman: bool 

def gather_info_node(state: AgentState):
    material = gather_context(state["topic"], "comprehensive technical breakdown")
    # Fix: Truncate to stay within Groq TPM limits
    return {"context": material[:10000]}

def explain_node(state: AgentState):
    topic = state["topic"]
    if state.get("is_feynman"):
        prompt = f"Explain '{topic}' using the Feynman Technique. Provide a 500-word immersive story-based analogy and 3 real-world examples."
        return {"feynman_text": llm.invoke(prompt).content}
    else:
        prompt = f"Provide a detailed academic deep-dive into '{topic}' (700 words). Include technical definitions, core principles, and 4 industrial use cases. Context: {state['context'][:4000]}"
        return {"explanation": llm.invoke(prompt).content}

def generate_mcq_node(state: AgentState):
    source = state.get('feynman_text') if state.get('is_feynman') else state.get('explanation')
    prompt = f"Based on this text: {source}. Generate 3 challenging MCQs. Format: Q: [Text] A) [Opt] B) [Opt] C) [Opt] Answer: [Letter]"
    return {"questions": llm.invoke(prompt).content}

workflow = StateGraph(AgentState)
workflow.add_node("gather_info", gather_info_node)
workflow.add_node("explain", explain_node)
workflow.add_node("generate_mcqs", generate_mcq_node)

workflow.set_entry_point("gather_info")
workflow.add_edge("gather_info", "explain")
workflow.add_edge("explain", "generate_mcqs") 
workflow.add_edge("generate_mcqs", END)

learning_graph = workflow.compile()