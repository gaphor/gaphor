from gaphor.babel import extract_gaphor


def test_babel(test_models):
    with (test_models / "test-model.gaphor").open(encoding="utf-8") as model:
        texts = list(extract_gaphor(model, (), (), None))

    assert (None, "gettext", "Element", []) in texts
