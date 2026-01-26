from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

def generate_quiz(context: str):
    prompt = f"Based on this learning material, generate 3 questions to test a student's deep understanding: {context}"
    return llm.invoke(prompt).content