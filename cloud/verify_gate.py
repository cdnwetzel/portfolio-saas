"""Pure logic for gating faithfulness verification on retrieval relevance.

When the top evidence chunk scores below a relevance threshold, skip verification
entirely — the retrieved chunks are too off-topic to make a faithfulness judgment
meaningful. This prevents false-positive flags on answers to off-topic (non-KB)
questions where Qdrant still returns its top-K nearest vectors, but they're
semantically unrelated to the query/answer domain.

Kept dependency-free and separate so it can be unit-tested without any I/O.
"""


def should_verify(top_score: float | None, threshold: float) -> bool:
    """True if the top retrieval score passes the relevance threshold.

    Args:
        top_score: The rerank score of the highest-scoring evidence chunk (0.0–0.08 range
                   for bge-reranker), or None/0.0 if no chunks were retrieved.
        threshold: Minimum score to consider evidence relevant enough to judge.
                   Calibrated empirically from golden_set.yaml distributions.

    Returns:
        False when top_score is None/missing or below threshold (skip verification).
        True when top_score meets or exceeds threshold (proceed with judge call).

    Example:
        >>> should_verify(0.06, 0.05)
        True
        >>> should_verify(0.02, 0.05)
        False
        >>> should_verify(None, 0.05)
        False
    """
    return top_score is not None and top_score >= threshold
