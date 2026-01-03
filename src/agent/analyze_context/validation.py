from __future__ import annotations

import re
from datetime import datetime


def validate_future_dates(text: str, current_year: int = None) -> list[str]:
    """
    Detect mentions of future dates in text

    Args:
        text: Text to check
        current_year: Current year (defaults to now)

    Returns:
        List of warnings about future dates
    """
    if current_year is None:
        current_year = datetime.now().year

    warnings = []

    # Find year mentions
    years = re.findall(r"\b(20\d{2})\b", text)
    future_years = [int(y) for y in years if int(y) > current_year]

    if future_years:
        warnings.append(
            f"⚠️ Phát hiện ngày tương lai: {', '.join(map(str, set(future_years)))} "
            f"(hiện tại: {current_year}) - Có thể là dự đoán hoặc lỗi"
        )

    # Check for month/year patterns like "tháng 6/2026"
    future_month_year = re.findall(r"tháng\s+\d+[/\-](20\d{2})", text)
    for match in future_month_year:
        year = int(match)
        if year > current_year:
            warnings.append(
                f"⚠️ Phát hiện tháng/năm tương lai trong text - Kiểm tra tính chính xác"
            )
            break

    return warnings


def validate_numeric_claims(text: str) -> list[str]:
    """
    Check if numeric claims have proper units and context

    Args:
        text: Text to check

    Returns:
        List of warnings about vague numeric claims
    """
    warnings = []

    # Find standalone numbers without units (simplified check)
    # Look for patterns like "tăng 50" without unit
    vague_patterns = [
        r"tăng\s+\d+(?!\s*(triệu|nghìn|tỷ|%|điểm|đồng|USD))",
        r"giảm\s+\d+(?!\s*(triệu|nghìn|tỷ|%|điểm|đồng|USD))",
        r"đạt\s+\d+(?!\s*(triệu|nghìn|tỷ|%|điểm|đồng|USD))",
    ]

    for pattern in vague_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            warnings.append(
                "⚠️ Phát hiện số liệu thiếu đơn vị - Độ chính xác có thể thấp"
            )
            break

    return warnings


def detect_contradictions(answer: str) -> list[str]:
    """
    Detect potential contradictions in text

    Args:
        answer: Research answer text

    Returns:
        List of potential contradictions found
    """
    warnings = []

    # Simple contradiction detection: look for opposing words
    lower_text = answer.lower()

    opposing_pairs = [
        ("tăng", "giảm"),
        ("increase", "decrease"),
        ("cao", "thấp"),
        ("high", "low"),
        ("tích cực", "tiêu cực"),
        ("positive", "negative"),
    ]

    for word1, word2 in opposing_pairs:
        if word1 in lower_text and word2 in lower_text:
            # Check if they appear in different sentences (potential contradiction)
            sentences = re.split(r"[.!?]", answer)
            has_contradiction = False
            for i, sent in enumerate(sentences):
                sent_lower = sent.lower()
                if word1 in sent_lower:
                    # Check if opposite appears in nearby sentences
                    for j in range(max(0, i - 1), min(len(sentences), i + 2)):
                        if i != j and word2 in sentences[j].lower():
                            has_contradiction = True
                            break
                if has_contradiction:
                    break

            if has_contradiction:
                warnings.append(
                    f"⚠️ Phát hiện mâu thuẫn tiềm ẩn: văn bản chứa cả '{word1}' và '{word2}'"
                )
                break

    return warnings


def validate_source_quality(sources: list[str], answer: str) -> dict:
    """
    Assess overall source quality

    Args:
        sources: List of source URLs
        answer: Research answer text

    Returns:
        Dict with quality assessment
    """
    source_count = len(sources)

    # Quality factors
    has_numbers = bool(re.search(r"\d+", answer))
    has_units = bool(
        re.search(
            r"(triệu|nghìn|tỷ|%|điểm|đồng|USD|VND|lượng)", answer, re.IGNORECASE
        )
    )
    answer_length = len(answer)

    # Determine quality level
    if source_count >= 3 and has_numbers and has_units and answer_length > 100:
        quality = "HIGH"
        reason = f"Có {source_count} nguồn, dữ liệu cụ thể với đơn vị rõ ràng"
    elif source_count >= 2 and has_numbers:
        quality = "MEDIUM"
        reason = f"Có {source_count} nguồn, dữ liệu tương đối đầy đủ"
    else:
        quality = "LOW"
        reason = (
            f"Chỉ có {source_count} nguồn, "
            + (
                "thiếu dữ liệu cụ thể"
                if not has_numbers
                else "thiếu đơn vị rõ ràng"
            )
        )

    return {"quality": quality, "reason": reason}


def run_all_validations(research_result: dict) -> dict:
    """
    Run all validation checks on research result

    Args:
        research_result: Dict with 'answer' and 'sources' keys

    Returns:
        Dict with validation results and warnings
    """
    answer = research_result.get("answer", "")
    sources = research_result.get("sources", [])

    all_warnings = []

    # Date validation
    all_warnings.extend(validate_future_dates(answer))

    # Numeric validation
    all_warnings.extend(validate_numeric_claims(answer))

    # Contradiction detection
    all_warnings.extend(detect_contradictions(answer))

    # Source quality
    quality_assessment = validate_source_quality(sources, answer)

    return {
        "warnings": all_warnings,
        "quality": quality_assessment["quality"],
        "quality_reason": quality_assessment["reason"],
        "source_count": len(sources),
    }
