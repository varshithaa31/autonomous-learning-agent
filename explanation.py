from langchain_openai import ChatOpenAI

def feynman_explain(concept, context):
    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = f"Explain '{concept}' like I'm five using analogies based on: {context}"
    return llm.invoke(prompt).content