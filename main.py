import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
from tavily import TavilyClient
import google.generativeai as genai

# Load API keys
load_dotenv()
TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

# Init clients
tavily = TavilyClient(api_key=TAVILY_API_KEY)
genai.configure(api_key=GOOGLE_API_KEY)
gemini = genai.GenerativeModel("gemini-2.5-pro")


# === Define State ===
class GraphState(TypedDict):
    messages: Annotated[list, add_messages]


# === Define Tavily Search Node ===
def tavily_search_node(state: GraphState) -> GraphState:
    question = state["messages"][-1].content
    results = tavily.search(query=question, search_depth="advanced", max_results=5)
    content = "\n\n".join(
        [f"{r['title']}:\n{r['content']}" for r in results["results"]]
    )
    return {"messages": [("system", content)]}



# === Define Gemini LLM Node ===
def gemini_node(state: GraphState) -> GraphState:
    user_question = state["messages"][0].content
    search_result = state["messages"][-1].content

    prompt = f"""You are a helpful assistant.
Answer based on the search results.

Question: {user_question}

Web Search Results:
{search_result}

Answer:"""

    response = gemini.generate_content(prompt)
    return {"messages": [("ai", response.text)]}



# === Build the Graph ===
builder = StateGraph(GraphState)

builder.add_node("search", tavily_search_node)
builder.add_node("gemini", gemini_node)

builder.set_entry_point("search")
builder.add_edge("search", "gemini")
builder.add_edge("gemini", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)


# === Run the graph ===
# === Run the graph ===
if __name__ == "__main__":
    user_question = input("Ask me something: ")
    result = graph.invoke(
        {"messages": [{"role": "user", "content": user_question}]},
        config={"thread_id": "news-thread"}
    )
    print("\n🔎 Answer from Gemini:\n")
    print(result["messages"][-1].content)


