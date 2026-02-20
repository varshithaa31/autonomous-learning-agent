import os
import re
from typing import TypedDict, List
from dotenv import load_dotenv  # Ensure this is imported
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

# --- THIS LINE IS THE FIX ---
load_dotenv() 

class AgentState(TypedDict):
    topic: str
    explanation: str
    feynman_text: str
    quiz_data: List[dict]
    attempt_count: int
    error: str

# Use groq_api_key as the parameter name
llm = ChatGroq(
    model="llama-3.1-8b-instant", 
    groq_api_key=os.getenv("GROQ_API_KEY") 
)

def learning_engine(state: AgentState):
    topic = state.get("topic", "")
    attempt = state.get("attempt_count", 1)
    try:
        tech_resp = llm.invoke(f"Provide a rigorous technical breakdown of {topic} focusing on architecture and mechanisms.")
        f_prompt = (
            f"Topic: {topic}\n"
            f"Technical Context: {tech_resp.content[:1000]}\n\n"
            f"Task: Provide a DETAILED Feynman explanation for a 10-year-old.\n"
            "Requirements:\n"
            "1. Start with a vivid, relatable real-world analogy.\n"
            "2. Map every complex part of the technical breakdown to a part of your analogy.\n"
            "3. Use detailed descriptions of 'why' things happen.\n"
            "4. NO bullet points. Explain it as a continuous, engaging story.\n"
            "5. Avoid jargon. Use plain English."
        )
        feynman_resp = llm.invoke(f_prompt)
        parsed_questions = []
        for _ in range(3): 
            quiz_prompt = (
                f"Generate EXACTLY 5 unique MCQs for '{topic}'. Attempt: {attempt}. "
                "Format: Q: [Question]\nA) [Opt]\nB) [Opt]\nC) [Opt]\nAnswer: [Letter]\nExplanation: [Detailed explanation]\n\n"
            )
            quiz_resp = llm.invoke(quiz_prompt)
            blocks = re.split(r'Q[:\d\s.]+', quiz_resp.content)
            current_batch = []
            for block in blocks:
                if not block.strip(): continue
                lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
                ans_match = re.search(r'Answer:\s*([A-C])', block, re.I)
                exp_match = re.search(r'Explanation:\s*(.*)', block, re.I | re.S)
                opts = [l for l in lines if re.match(r'^[A-C][\).]', l)]
                if len(opts) >= 3 and ans_match:
                    current_batch.append({
                        "q": lines[0], "opts": opts[:3], "a": ans_match.group(1).upper(),
                        "exp": exp_match.group(1).strip() if exp_match else "Correct choice."
                    })
            if len(current_batch) >= 5:
                parsed_questions = current_batch[:5]
                break
        return {
            "topic": topic, "explanation": tech_resp.content, "feynman_text": feynman_resp.content,
            "quiz_data": parsed_questions, "attempt_count": attempt, "error": ""
        }
    except Exception as e:
        return {"error": str(e), "topic": topic}

workflow = StateGraph(AgentState)
workflow.add_node("process", learning_engine)
workflow.set_entry_point("process")
workflow.add_edge("process", END)
learning_graph = workflow.compile()