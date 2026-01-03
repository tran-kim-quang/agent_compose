from __future__ import annotations

from datetime import datetime


def filter_short_content(sources: list[dict], min_length: int = 50) -> list[dict]:
    """
    Filter out sources with content shorter than minimum length

    Args:
        sources: List of dicts with 'content' and 'url' keys
        min_length: Minimum content length in characters

    Returns:
        Filtered list of sources
    """
    return [
        source
        for source in sources
        if source.get("content") and len(source["content"]) >= min_length
    ]


def deduplicate_sources(sources: list[dict], similarity_threshold: float = 0.95) -> list[dict]:
    """
    Remove duplicate or highly similar sources

    Args:
        sources: List of dicts with 'content' and 'url' keys
        similarity_threshold: Threshold for considering content as duplicate

    Returns:
        Deduplicated list of sources
    """
    if not sources:
        return []

    unique_sources = []
    seen_contents = []

    for source in sources:
        content = source.get("content", "").lower().strip()
        if not content:
            continue

        # Simple deduplication: check if exact match exists
        is_duplicate = False
        for seen in seen_contents:
            # Simple similarity: check if content is substring or very similar
            if content == seen or content in seen or seen in content:
                if len(content) > len(seen) * similarity_threshold or len(seen) > len(content) * similarity_threshold:
                    is_duplicate = True
                    break

        if not is_duplicate:
            unique_sources.append(source)
            seen_contents.append(content)

    return unique_sources


def reject_prediction_content(sources: list[dict]) -> list[dict]:
    """
    Filter out sources containing prediction/speculation keywords

    Args:
        sources: List of dicts with 'content' and 'url' keys

    Returns:
        Filtered list of sources without prediction content
    """
    prediction_keywords = [
        "dự đoán",
        "dự báo",
        "sẽ là",
        "có thể sẽ",
        "prediction",
        "forecast",
        "will be",
        "could be",
        "might be",
        "expected to be",
    ]

    filtered = []
    for source in sources:
        content = source.get("content", "").lower()
        # Check if content contains too many prediction keywords
        keyword_count = sum(1 for keyword in prediction_keywords if keyword in content)

        # Allow if less than 2 prediction keywords (some news legitimately mention predictions)
        if keyword_count < 2:
            filtered.append(source)

    return filtered


def validate_date_in_content(content: str, current_date: datetime = None) -> bool:
    """
    Check if dates mentioned in content are not in the future

    Args:
        content: Text content to check
        current_date: Current date (defaults to now)

    Returns:
        True if no future dates detected, False otherwise
    """
    if current_date is None:
        current_date = datetime.now()

    # Simple future date detection - look for years
    import re

    years = re.findall(r"\b(20\d{2})\b", content)
    for year_str in years:
        year = int(year_str)
        if year > current_date.year:
            return False
    return True


def preprocess_research_results(research_result: dict) -> dict:
    """
    Apply all preprocessing steps to research results

    Args:
        research_result: Dict with 'answer' and 'sources' keys

    Returns:
        Preprocessed research result with cleaned sources
    """
    # Extract sources from URLs if needed
    # Assuming research_result has sources as list of URLs or dicts
    sources = research_result.get("sources", [])

    # If sources are just URLs, convert to dict format
    if sources and isinstance(sources[0], str):
        sources = [{"url": url, "content": ""} for url in sources]

    # Apply filters
    sources = filter_short_content(sources)
    sources = reject_prediction_content(sources)
    sources = deduplicate_sources(sources)

    # Check if answer contains future dates
    answer = research_result.get("answer", "")
    has_future_dates = not validate_date_in_content(answer)

    return {
        "answer": answer,
        "sources": [s.get("url") for s in sources],  # Return URLs only
        "source_count": len(sources),
        "preprocessing_warnings": (
            ["⚠️ Detected potential future dates in content"] if has_future_dates else []
        ),
    }
