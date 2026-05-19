from rag.query_intent import parse_query_intent


def test_sr_alias_resolves():
    intent = parse_query_intent("SR post orders")
    assert intent.community == "Sierra Ridge"


def test_sierra_partial_alias_resolves():
    intent = parse_query_intent("SIERRA kiosk rules")
    assert intent.community == "Sierra Ridge"


def test_glen_alias_resolves():
    intent = parse_query_intent("GLEN kiosk post orders")
    assert intent.community == "The Glen (Tamiment)"


def test_cbk_alias_resolves():
    intent = parse_query_intent("CBK concierge post orders")
    assert intent.community == "Clearbrook Main"


def test_mon_alias_resolves():
    intent = parse_query_intent("MON post orders for kiosk")
    assert intent.community == "Monterey"


def test_full_name_resolves():
    intent = parse_query_intent("post orders for Sierra Ridge kiosk")
    assert intent.community == "Sierra Ridge"


def test_no_community_for_global_query():
    intent = parse_query_intent("what is the default kiosk call flow")
    assert intent.community == "" or intent.community is None


def test_kiosk_scope_extracted():
    intent = parse_query_intent("SR post orders for kiosk")
    assert "kiosk" in (intent.scope_hint or "").lower()


def test_post_order_type_expected():
    intent = parse_query_intent("post orders for sierra ridge")
    assert "post_order" in (intent.expected_types or set())


def test_unknown_community_not_matched():
    intent = parse_query_intent("xyzzy unknown gate protocol")
    assert intent.community == "" or intent.community is None
