"""Tests for backend/retrieval/rrf.py."""

from backend.retrieval.models import SearchResult
from backend.retrieval.rrf import reciprocal_rank_fusion


def _make_result(chunk_id: str, score: float = 1.0) -> SearchResult:
    return SearchResult(
        chunk_id=chunk_id,
        content=f"Content for {chunk_id}",
        source_url="https://example.com",
        document_title="Test Doc",
        section_title="Section",
        score=score,
    )


class TestReciprocalRankFusion:
    def test_no_duplicates_in_output(self):
        a = [_make_result("c1"), _make_result("c2"), _make_result("c3")]
        b = [_make_result("c2"), _make_result("c3"), _make_result("c4")]
        result = reciprocal_rank_fusion(a, b)
        ids = [r.chunk_id for r in result]
        assert len(ids) == len(set(ids))

    def test_union_of_both_lists(self):
        a = [_make_result("c1"), _make_result("c2")]
        b = [_make_result("c3"), _make_result("c4")]
        result = reciprocal_rank_fusion(a, b)
        assert {r.chunk_id for r in result} == {"c1", "c2", "c3", "c4"}

    def test_sorted_by_fused_score_descending(self):
        a = [_make_result("c1"), _make_result("c2"), _make_result("c3")]
        b = [_make_result("c1"), _make_result("c3"), _make_result("c4")]
        result = reciprocal_rank_fusion(a, b)
        scores = [r.score for r in result]
        assert scores == sorted(scores, reverse=True)

    def test_overlap_boosts_score(self):
        # c1 appears rank-1 in both lists → highest fused score
        a = [_make_result("c1"), _make_result("c2")]
        b = [_make_result("c1"), _make_result("c3")]
        result = reciprocal_rank_fusion(a, b)
        assert result[0].chunk_id == "c1"

    def test_known_rrf_scores(self):
        # With k=60: score(c1) = 1/61 + 1/61 ≈ 0.03279
        #            score(c2) = 1/62                ≈ 0.01613
        #            score(c3) =        1/62         ≈ 0.01613
        a = [_make_result("c1"), _make_result("c2")]
        b = [_make_result("c1"), _make_result("c3")]
        result = reciprocal_rank_fusion(a, b, k=60)
        by_id = {r.chunk_id: r.score for r in result}
        assert abs(by_id["c1"] - (1 / 61 + 1 / 61)) < 1e-9
        assert abs(by_id["c2"] - (1 / 62)) < 1e-9
        assert abs(by_id["c3"] - (1 / 62)) < 1e-9

    def test_score_field_is_fused_not_original(self):
        a = [_make_result("c1", score=0.99)]
        b = [_make_result("c1", score=0.50)]
        result = reciprocal_rank_fusion(a, b, k=60)
        # Original scores were 0.99 and 0.50; fused should be ~0.0328
        assert result[0].score < 0.1

    def test_empty_lists_return_empty(self):
        assert reciprocal_rank_fusion([], []) == []

    def test_one_empty_list(self):
        a = [_make_result("c1"), _make_result("c2")]
        result = reciprocal_rank_fusion(a, [])
        assert len(result) == 2
        assert result[0].chunk_id == "c1"

    def test_metadata_preserved(self):
        a = [_make_result("c1")]
        b = []
        result = reciprocal_rank_fusion(a, b)
        assert result[0].content == "Content for c1"
        assert result[0].source_url == "https://example.com"
