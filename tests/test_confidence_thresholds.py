import pytest


@pytest.mark.requires_index
def test_xyzzy_nonsense_refuses(require_index, retrieve):
    """
    Nonsense queries must not return strong confidence.
    This validates the minimum_raw_distance_floor fix from Phase 4.23.0.
    A query with no semantically relevant vault content must refuse.
    """
    chunks, hints, assessment = retrieve(
        "xyzzy unknown community gate protocol", 10, False
    )
    assert assessment["refuse"] is True, (
        f"Expected refuse=True for nonsense query, got confidence="
        f"{assessment['confidence']}, reason={assessment['reason']}"
    )


@pytest.mark.requires_index
def test_random_gibberish_refuses(require_index, retrieve):
    chunks, hints, assessment = retrieve(
        "asdfghjkl qwerty zxcvbnm poiuyt", 10, False
    )
    assert assessment["refuse"] is True


@pytest.mark.requires_index
def test_real_query_does_not_refuse(require_index, retrieve):
    """
    A real operational query must not be over-refused by the floor.
    """
    chunks, hints, assessment = retrieve(
        "what are the post orders for sierra ridge kiosk", 10, False
    )
    assert assessment["refuse"] is False, (
        f"Real operational query was incorrectly refused: "
        f"confidence={assessment['confidence']}, reason={assessment['reason']}"
    )


@pytest.mark.requires_index
def test_call_flow_query_does_not_refuse(require_index, retrieve):
    chunks, hints, assessment = retrieve("kiosk call flow for the glen", 10, False)
    assert assessment["refuse"] is False


def test_weak_confidence_for_no_chunks():
    """Unit test - no ChromaDB needed."""
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from rag.retrieval import retrieval_assessment

    result = retrieval_assessment(
        chunks=[],
        hints={"community": "", "missing_community": "", "expected_types": set()},
        threshold=0.95,
        primary_workflow_default_threshold=1.1,
        is_default_query=False,
        config={},
    )
    assert result["confidence"] == "none"
    assert result["refuse"] is True
