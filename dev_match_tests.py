from match_policy import (
    AUTO_MATCH_STATUS,
    PRINTING_TIE_STATUS,
    UNKNOWN_STATUS,
    decide_local_match,
    describe_decision,
    resolve_printing_tie_with_visual
)


def card(card_id, name, set_code, number, score):
    return {
        "id": card_id,
        "name": name,
        "set": set_code,
        "collector_number": number,
        "score": score
    }


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected}, got {actual}")


def test_policy():
    _, _, status = decide_local_match([])
    assert_equal(status, UNKNOWN_STATUS, "empty match list rejects")

    low = [card("a", "Quick Study", "sos", "65", 650)]
    _, _, status = decide_local_match(low)
    assert_equal(status, UNKNOWN_STATUS, "low score rejects")

    tied = [
        card("a", "Fear, Fire, Foes!", "ltr", "125", 2500),
        card("b", "Fear, Fire, Foes!", "ltr", "576", 2500)
    ]
    _, _, status = decide_local_match(tied)
    assert_equal(status, PRINTING_TIE_STATUS, "close printings reject")
    explanation = describe_decision(tied, status, ocr_text="")
    assert_equal(
        explanation[0],
        "rejected: same card text matches multiple close printings",
        "printing tie explanation"
    )

    clear = [
        card("a", "Fear, Fire, Foes!", "ltr", "125", 3600),
        card("b", "Fear, Fire, Foes!", "ltr", "576", 2100)
    ]
    selected, _, status = decide_local_match(clear)
    assert_equal(status, AUTO_MATCH_STATUS, "clear print auto matches")
    assert_equal(selected["collector_number"], "125", "selected clear print")

    visual = resolve_printing_tie_with_visual(
        tied,
        [
            {"id": "a", "distance": 5},
            {"id": "b", "distance": 14}
        ]
    )
    assert_equal(
        visual["collector_number"],
        "125",
        "strong visual tie-break selects print"
    )

    visual = resolve_printing_tie_with_visual(
        tied,
        [
            {"id": "a", "distance": 5},
            {"id": "b", "distance": 7}
        ]
    )
    assert_equal(visual, None, "weak visual gap still rejects")


if __name__ == "__main__":
    test_policy()
    print("dev_match_tests: OK")
