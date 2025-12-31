import os
import json

from langchain.tools import tool

from tavily import TavilyClient


from dotenv import load_dotenv

load_dotenv()
tavily_api = os.getenv("TAVILY_API_KEY")

class TavilySearch:
    """
    Research tool with fintech topic
    """
    def __init__(self):
        self.api_key = tavily_api
        if not self.api_key:
            raise ValueError("Missing Tavily API key.")
    def search(self, query: str, time_range: str) -> str:
        tavily_client = TavilyClient(api_key=self.api_key)
        response = tavily_client.search(
            query=query,
            # topic="finance",
            time_range=time_range,
            mmax_results=3,
        )
        # Extract results with proper Unicode handling
        results = response.get("results", [])
        context = [{"url": r.get("url"), "content": r.get("content")} for r in results]
        return json.dumps(context, ensure_ascii=False, indent=2)


@tool
def research(query: str, time_range: str) -> str:
    """
    Get a query and search for relevant financial information.
    :input query: Description
    :input time_range: Time range of the research (e.g., day, week, month, year)
    :return: Results of the research
    """
    research_tool = TavilySearch()
    return research_tool.search(query, time_range)
