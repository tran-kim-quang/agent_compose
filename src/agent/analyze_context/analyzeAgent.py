from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from langgraph.graph.message import MessagesState

from agent.analyze_context.validation import run_all_validations
from agent.prompt_management.prompt_analyze import ANALYZE_SYSTEM_PROMPT

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

# Initialize LLM
llm = ChatGroq(
    model=MODEL_NAME,
    api_key=GROQ_API_KEY,
    temperature=0.3,  # Lower temperature for more consistent analysis
)


def call_analyze_llm(state: MessagesState):
    """Node to analyze research context"""
    msg = llm.invoke(state["messages"])
    return {"messages": [msg]}


# Build Graph
graph = StateGraph(MessagesState)
graph.add_node("analyze", call_analyze_llm)
graph.set_entry_point("analyze")
graph.add_edge("analyze", END)

# Compile
app = graph.compile()


def run_analyze(research_result: dict) -> str:
    """
    Analyze research results with validation and structured summary

    Args:
        research_result: Dict with 'answer' and 'sources' keys

    Returns:
        Analyzed summary string with validation warnings
    """
    answer = research_result.get("answer", "")
    sources = research_result.get("sources", [])

    # Run validation checks BEFORE sending to LLM
    validation_results = run_all_validations(research_result)

    # Build enhanced user message with validation context
    validation_context = ""
    if validation_results["warnings"]:
        validation_context = "\n⚠️ PRE-VALIDATION WARNINGS:\n"
        validation_context += "\n".join(
            f"- {w}" for w in validation_results["warnings"]
        )
        validation_context += "\n\n"

    user_msg = f"""Research Results:

Answer: {answer}

Sources ({len(sources)} URLs):
{chr(10).join(f"- {url}" for url in sources[:5])}
{"..." if len(sources) > 5 else ""}

{validation_context}Pre-calculated Data Quality: {validation_results['quality']}
Reason: {validation_results['quality_reason']}

Please analyze this research data following the CRITICAL RULES. Include citations for each key fact."""

    result = app.invoke(
        {
            "messages": [
                SystemMessage(content=ANALYZE_SYSTEM_PROMPT),
                ("user", user_msg),
            ],
        },
    )

    final_message = result["messages"][-1]
    return final_message.content


if __name__ == "__main__":
    # Test with sample data
    test_result = {
        "answer": "Kết quả nghiên cứu cho thấy biến động của mã chứng khoán ngành ngân hàng trong tuần qua là đa dạng và phong phú. Có những mã tăng giá mạnh mẽ như VRE, VHM, HDB, VCBS, PNC, trong khi những mã khác như BID giảm giá.",
        "sources": [
            "https://hanoimoi.vn/vic-va-co-phieu-ngan-hang-nang-do-thi-truong-ngay-30-12-728690.html",
            "https://cafef.vn/mot-co-phieu-ngan-hang-gan-tang-tran-trong-phien-giao-dich-cuoi-cung-cua-nam-2025-188251231164817637.chn",
        ],
    }

    analysis = run_analyze(test_result)
    print(analysis)
