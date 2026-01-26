from langchain_openai import ChatOpenAI
import json

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def generate_learning_path(topic: str):
    """
    Generates a structured list of 3-5 specific checkpoints for a given topic.
    """
    prompt = f"""
    You are an expert curriculum designer. 
    Topic: {topic}
    
    Task: Create a logical learning path consisting of 3 to 5 specific sub-topics (checkpoints).
    Rules:
    1. Each checkpoint must be a specific milestone for mastering {topic}.
    2. Format the output ONLY as a valid Python list of strings.
    3. Example: ["Introduction to {topic}", "Core Mechanics of {topic}", "Advanced Applications"]
    """
    
    try:
        response = llm.invoke(prompt)
        # Using eval safely or parsing since we expect a list format string
        path = eval(response.content.strip())
        if isinstance(path, list):
            return path
        return [f"Introduction to {topic}", f"Intermediate {topic}", f"Advanced {topic}"]
    except Exception:
        # Fallback if LLM output isn't a clean list
        return [f"Basics of {topic}", f"Applications of {topic}", f"Future of {topic}"]