import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
from tavily import TavilyClient
import google.generativeai as genai


# Load environment variables
load_dotenv()
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
LANGSMITH_API_KEY = os.environ.get("LANGSMITH_API_KEY")



# Initialize clients
tavily = TavilyClient(api_key=TAVILY_API_KEY)
genai.configure(api_key=GOOGLE_API_KEY)
gemini = genai.GenerativeModel("gemini-2.0-flash") 


# LangGraph State Definition
# ==========================
class GraphState(TypedDict):
    messages: Annotated[list, add_messages]


# Node 1: Tavily Search
# ==========================
def search_tech_news(state: GraphState) -> GraphState:
    results = tavily.search(
        query="Top stock market news today",
        search_depth="advanced",
        max_results=5
    )

    combined_content = "\n\n".join(
        [f"{r['title']}:\n{r['content']}" for r in results["results"]]
    )

    return {"messages": [{"role": "system", "content": combined_content}]}


# ==========================
# Node 2: Summarize one topic
# ==========================
def summarize_one_topic(state: GraphState) -> GraphState:
    all_news = state["messages"][-1].content


    prompt = f"""
You are a professional finaical analyst .

From the following stock news articles, choose the most interesting and trending one.

Summarize it in 2-3 sentences for a professional audience:
Return only the summary.
{all_news}
"""

    response = gemini.generate_content(prompt)
    return {"messages": [{"role": "assistant", "content": response.text.strip()}]}

# ==========================
# Node 3: Create LinkedIn Post
# ==========================
def linkedin_post_node(state: GraphState) -> GraphState:
    summary = state["messages"][-1].content


    prompt = f"""
Write a professional LinkedIn post based on this stock news topic summary:

"{summary}"

Instructions:
- Use a professional yet engaging tone
- Include 2-3 relevant emojis
- Add popular LinkedIn hashtags for reach (5-8 max)
- Encourage engagement (e.g., ask a question or opinion)

Return only the post content.
"""

    response = gemini.generate_content(prompt)
    return {"messages": [{"role": "assistant", "content": response.text.strip()}]}


# ==========================
# Build LangGraph
# ==========================
builder = StateGraph(GraphState)

builder.add_node("search_news", search_tech_news)
builder.add_node("summarize_topic", summarize_one_topic)
builder.add_node("linkedin_post", linkedin_post_node)

builder.set_entry_point("search_news")
builder.add_edge("search_news", "summarize_topic")
builder.add_edge("summarize_topic", "linkedin_post")
builder.add_edge("linkedin_post", END)

graph = builder.compile()



# ==========================
# Run the Graph
# ==========================
if __name__ == "__main__":
    print("🔍 Fetching trending tech news and generating LinkedIn post...\n")
    output = graph.invoke({"messages": []})

    final_post = output["messages"][-1].content

    print("✅ Done! Here’s your LinkedIn post:\n")
    print("=" * 60)
    print(final_post)
    print("=" * 60)