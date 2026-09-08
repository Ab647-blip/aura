from __future__ import annotations

import html
import re

import httpx

ENDPOINT = "https://lite.duckduckgo.com/lite/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Aura)"}

LINK = re.compile(r"<a rel=\"nofollow\" href=\"([^\"]+)\"[^>]*class=['\"]result-link['\"]>(.*?)</a>", re.S)
SNIPPET = re.compile(r"class=['\"]result-snippet['\"]>(.*?)</td>", re.S)
TAGS = re.compile(r"<[^>]+>")


class SearchError(Exception):
    "Raised when the search request fails."


def clean(fragment: str) -> str:
    return " ".join(html.unescape(TAGS.sub("", fragment)).split())


def parse_results(page: str) -> list[tuple[str, str, str]]:
    links = list(LINK.finditer(page))
    results = []

    for position, match in enumerate(links):
        stop = links[position + 1].start() if position + 1 < len(links) else len(page)
        snippet = SNIPPET.search(page, match.end(), stop)

        results.append(
            (
                clean(match.group(2)),
                clean(snippet.group(1)) if snippet else "",
                match.group(1),
            )
        )

    return results


def web_search(query: str, k: int = 4) -> str:
    """Top web results as plain text for the model to read and answer from."""

    try:
        response = httpx.post(
            ENDPOINT,
            data={"q": query},
            headers=HEADERS,
            timeout=15,
            follow_redirects=True,
        )
        response.raise_for_status()
        response.encoding = "utf-8"
    except httpx.HTTPError as e:
        raise SearchError(f"search request failed: {e}") from e

    results = parse_results(response.text)

    if not results:
        return f"No web results for: {query}"

    return "\n\n".join(
        f"{title}\n{snippet}\n{url}" for title, snippet, url in results[:k] if title
    )
