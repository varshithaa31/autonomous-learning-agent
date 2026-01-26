from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def evaluate_mcqs(questions: str, user_answers: str, context: str):
    """
    Evaluates MCQ selections against the lesson content.
    """
    prompt = f"""
    Context: {context}
    Questions: {questions}
    User Selections: {user_answers}
    
    Task: Grade these MCQs based ONLY on the provided Context. 
    1. Identify the correct answer for each question based on the context.
    2. Compare it to the User Selection.
    3. Calculate a percentage score (0-100).
    
    Return ONLY the numerical integer (e.g., 75).
    """
    try:
        response = llm.invoke(prompt)
        score = int(''.join(filter(str.isdigit, response.content)))
        return score
    except Exception:
        return 0