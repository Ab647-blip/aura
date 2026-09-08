from aura.core.web import clean, parse_results

PAGE = """
<a rel="nofollow" href="https://example.com/one" class='result-link'>First &amp; Best</a>
<td class='result-snippet'>A snippet about the <b>first</b> result.</td>
<a rel="nofollow" href="https://example.com/two" class='result-link'>Second</a>
"""


def test_clean_strips_tags_and_entities():
    assert clean("Live <b>Price</b> &amp; more") == "Live Price & more"


def test_clean_collapses_whitespace():
    assert clean("too    many\n  spaces") == "too many spaces"


def test_parse_pulls_title_snippet_url():
    title, snippet, url = parse_results(PAGE)[0]

    assert title == "First & Best"
    assert snippet == "A snippet about the first result."
    assert url == "https://example.com/one"


def test_result_without_snippet_does_not_borrow_one():
    results = parse_results(PAGE)

    assert len(results) == 2
    assert results[1][0] == "Second"
    assert results[1][1] == ""
