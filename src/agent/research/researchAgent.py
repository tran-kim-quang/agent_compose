from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from agent.prompt_management.prompt_research import RESEARCH_SYSTEM_PROMPT
from agent.research.tools.research_news import research

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
# Bind Tool
llm = ChatGroq(
    model=MODEL_NAME,
    api_key=GROQ_API_KEY,
    model_kwargs={"tool_choice": "auto"},
)
llm_with_tools = llm.bind_tools([research])


def call_llm(state: MessagesState):
    """Node LLM"""
    msg = llm_with_tools.invoke(state["messages"])
    return {"messages": [msg]}


# Buld Graph
graph = StateGraph(MessagesState)
graph.add_node("llm", call_llm)
graph.add_node("tools", ToolNode([research]))

# If need to call tool, go to tools node
graph.add_conditional_edges("llm", tools_condition)
graph.add_edge("tools", "llm")
graph.set_entry_point("llm")
graph.add_edge("llm", END)

# Compile
app = graph.compile()


def run_research(query: str, time_range: str | None = None):
    """Call agent function"""
    user_msg = f"Query: {query}"
    if time_range:
        user_msg += f"\nTime range: {time_range}"

    result = app.invoke(
        {
            "messages": [
                SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
                ("user", user_msg),
            ],
        },
    )

    tool_messages = []
    for msg in result["messages"]:
        if isinstance(msg, ToolMessage):
            tool_messages.append(msg)
    final_message = result["messages"][-1]

    # Parse URLs
    urls = []
    for tool_msg in tool_messages:
        try:
            data = json.loads(tool_msg.content)
            urls.extend([item.get("url") for item in data if item.get("url")])
        except Exception as e:
            print(f"Parse error: {e}")

    return {
        "answer": final_message.content,
        "sources": urls,
    }


if __name__ == "__main__":
    result = run_research("giá vàng những ngày gần đây")
    print(result)
