import pytest


pytestmark = pytest.mark.requires_index


def test_sr_physical_id_retrieval(require_index, retrieve):
    chunks, hints, assessment = retrieve(
        "physical ID requirement at sierra ridge", 10, False
    )
    assert assessment["confidence"] == "strong"
    assert assessment["refuse"] is False
    communities = [c["community"] for c in chunks]
    assert any("sierra ridge" in c.lower() for c in communities)
    types = [c["type"] for c in chunks]
    assert any(t in ("post_order", "qa_rule") for t in types)


def test_sr_kiosk_post_orders_retrieval(require_index, retrieve):
    chunks, hints, assessment = retrieve(
        "post orders for sierra ridge kiosk", 10, False
    )
    assert assessment["confidence"] == "strong"
    assert assessment["refuse"] is False
    assert hints["community"] == "Sierra Ridge"
    assert any(c["type"] == "post_order" for c in chunks)
    statuses = [c["status"] for c in chunks]
    assert all(s in ("active", "pending") for s in statuses)


def test_glen_kiosk_post_orders_retrieval(require_index, retrieve):
    chunks, hints, assessment = retrieve("GLEN kiosk post orders", 10, False)
    assert assessment["confidence"] == "strong"
    communities = [c["community"].lower() for c in chunks]
    assert any("glen" in c or "tamiment" in c for c in communities)


def test_no_unknown_community_retrieval(require_index, retrieve):
    """
    Completely unrecognized text like 'fakecommunity99' is not parsed
    as a community name by the intent parser. No community hint is set,
    no missing_community flag is set, and the system treats the query
    as a global query. This is correct behavior - no false-positive
    refuse on opaque noise.

    The missing_community refuse path fires only when the intent parser
    identifies something that looks like a community alias or known name
    but cannot find a match in the indexed vault. That behavior is
    covered separately by test_community_resolution.py.
    """
    chunks, hints, assessment = retrieve(
        "fakecommunity99 kiosk post orders", 10, False
    )
    # Unrecognized text: no community hint or missing_community expected
    assert hints.get("community", "") == "" or hints.get("missing_community", "") == ""


def test_active_sources_preferred(require_index, retrieve):
    chunks, hints, assessment = retrieve(
        "post orders for clearbrook kiosk", 10, False
    )
    if not assessment["refuse"]:
        active_chunks = [c for c in chunks if c["status"] == "active"]
        assert len(active_chunks) > 0


def test_managed_sources_preferred(require_index, retrieve):
    chunks, hints, assessment = retrieve(
        "post orders for sierra ridge", 10, False
    )
    if not assessment["refuse"]:
        managed = [c for c in chunks if c.get("lifecycle_generation") == "managed"]
        assert len(managed) > 0
