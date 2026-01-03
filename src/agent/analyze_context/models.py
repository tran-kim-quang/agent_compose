from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class KeyFact(BaseModel):
    """A key fact with its source"""

    fact: str = Field(description="The factual statement")
    source: str = Field(description="URL source or 'Không có nguồn cụ thể'")
    confidence: str = Field(
        description="Confidence level: high/medium/low", default="medium"
    )


class AnalysisResult(BaseModel):
    """Structured output for financial analysis"""

    warnings: list[str] = Field(
        default_factory=list,
        description="List of warnings: future dates, contradictions, vague claims",
    )

    summary: str = Field(description="2-3 sentence objective summary")

    key_facts: list[KeyFact] = Field(
        description="3-5 key facts with sources", min_items=1, max_items=5
    )

    contradictions: Optional[str] = Field(
        default="Không phát hiện",
        description="Description of contradictions found or 'Không phát hiện'",
    )

    data_quality: str = Field(
        description="Data quality assessment: HIGH/MEDIUM/LOW"
    )

    data_quality_reason: str = Field(
        description="Explanation for data quality rating"
    )

    source_count: int = Field(description="Number of sources analyzed")

    reasoning: str = Field(
        description="Chain-of-thought explanation of confidence level"
    )

    def to_markdown(self) -> str:
        """Convert to markdown format for display"""
        output = ["📊 PHÂN TÍCH TÀI CHÍNH\n"]

        if self.warnings:
            output.append("⚠️ Cảnh báo:")
            for warning in self.warnings:
                output.append(f"- {warning}")
            output.append("")

        output.append("Tóm tắt:")
        output.append(f"{self.summary}\n")

        output.append("Điểm chính:")
        for fact in self.key_facts:
            output.append(f"• {fact.fact} - [Source: {fact.source}]")
        output.append("")

        output.append("Mâu thuẫn phát hiện:")
        output.append(f"{self.contradictions}\n")

        output.append(
            f"Chất lượng dữ liệu: {self.data_quality}"
        )
        output.append(f"Lý do: {self.data_quality_reason}\n")

        output.append(f"Nguồn: {self.source_count} URLs\n")

        output.append("---")
        output.append("REASONING (Chain-of-Thought):")
        output.append(f"{self.reasoning}")

        return "\n".join(output)
