from aura.core.retrieval import cosine, split_into_chunks


def test_cosine_identical():
    v = [0.1, 0.4, 0.9]

    assert cosine(v, v) == 1.0


def test_cosine_orthogonal():
    assert cosine([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_cosine_handles_zero_vector():
    assert cosine([0.0, 0.0], [1.0, 2.0]) == 0.0


def test_chunking_drops_headers():
    text = "Meeting notes\n\nWe agreed to hold the price steady until the end of the quarter."

    chunks = split_into_chunks(text)

    assert len(chunks) == 1
    assert chunks[0].startswith("We agreed")


def test_chunking_flattens_whitespace():
    text = "One line\nrunning on\nacross three lines with plenty of words in it."

    assert "\n" not in split_into_chunks(text)[0]
