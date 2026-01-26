import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()
search = TavilySearch(max_results=2) 

def gather_context(main_topic: str, checkpoint_title: str):
    query = f"In-depth educational explanation of {checkpoint_title} for {main_topic}"
    try:
        results = search.invoke(query)
        context_text = "\n\n".join([r['content'][:1000] for r in results])
        return context_text if context_text.strip() else "No data found."
    except Exception as e:
        return f"Search Error: {str(e)}"