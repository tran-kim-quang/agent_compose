from __future__ import annotations

from agent.analyze_context.analyzeAgent import run_analyze
from agent.research.researchAgent import run_research


def test_full_pipeline():
    """Test Research -> Analyze full pipeline"""
    print("=" * 80)
    print("TEST 1: Short-term stock news (1 day)")
    print("=" * 80)

    query1 = "Giá vàng hôm nay"
    research1 = run_research(query1, time_range="day")
    print(f"\n🔍 Research Result:\n{research1['answer']}\n")
    print(f"📚 Sources: {len(research1['sources'])} URLs\n")

    analysis1 = run_analyze(research1)
    print(f"\n📊 Analysis:\n{analysis1}\n")

    print("\n" + "=" * 80)
    print("TEST 2: Banking sector weekly trend")
    print("=" * 80)

    query2 = "Biến động cổ phiếu ngân hàng tuần qua"
    research2 = run_research(query2, time_range="week")
    print(f"\n🔍 Research Result:\n{research2['answer']}\n")
    print(f"📚 Sources: {len(research2['sources'])} URLs\n")

    analysis2 = run_analyze(research2)
    print(f"\n📊 Analysis:\n{analysis2}\n")

    print("\n" + "=" * 80)
    print("TEST 3: Monthly economic outlook")
    print("=" * 80)

    query3 = "Triển vọng kinh tế Việt Nam tháng này"
    research3 = run_research(query3, time_range="month")
    print(f"\n🔍 Research Result:\n{research3['answer']}\n")
    print(f"📚 Sources: {len(research3['sources'])} URLs\n")

    analysis3 = run_analyze(research3)
    print(f"\n📊 Analysis:\n{analysis3}\n")


def test_edge_cases():
    """Test edge cases"""
    print("=" * 80)
    print("EDGE CASE TEST: Empty sources")
    print("=" * 80)

    empty_result = {"answer": "Không tìm thấy thông tin liên quan.", "sources": []}
    analysis = run_analyze(empty_result)
    print(f"\n📊 Analysis:\n{analysis}\n")

    print("\n" + "=" * 80)
    print("EDGE CASE TEST: Many sources")
    print("=" * 80)

    many_sources_result = {
        "answer": "Thị trường chứng khoán biến động mạnh với nhiều yếu tố tác động.",
        "sources": [f"https://example.com/article{i}" for i in range(10)],
    }
    analysis = run_analyze(many_sources_result)
    print(f"\n📊 Analysis:\n{analysis}\n")


if __name__ == "__main__":
    print("\n🚀 Starting Full Pipeline Tests...\n")
    test_full_pipeline()

    print("\n🔧 Starting Edge Case Tests...\n")
    test_edge_cases()

    print("\n✅ All tests completed!")
