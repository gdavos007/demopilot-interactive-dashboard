"""Extract main documentation body text from saved HTML pages."""

from __future__ import annotations

import re
from bs4 import BeautifulSoup, Tag

NOISE_TAGS = frozenset(
    {
        "script",
        "style",
        "noscript",
        "svg",
        "iframe",
        "nav",
        "footer",
        "header",
        "aside",
        "form",
    }
)

NOISE_SELECTORS = (
    "[aria-hidden='true']",
    ".cookie",
    ".cookies",
    "#cookie",
    "#onetrust-banner-sdk",
    ".onetrust-pc-dark-filter",
    ".skip-link",
    ".skip-to-main",
    "[class*='cookie-banner']",
    "[class*='CookieBanner']",
    "[id*='cookie']",
    ".global-header",
    ".global-nav",
    ".site-header",
    ".site-footer",
    ".sidebar",
    ".doc-sidebar",
    ".table-of-contents",
    ".toc",
    ".breadcrumbs",
    ".breadcrumb",
)

MAIN_CONTENT_SELECTORS = (
    ".doc-as-code-renderer",
    ".document-rendered",
    ".post-document",
    "main",
    "article",
    "[role='main']",
    ".documentation-content",
    "#content",
    ".content",
)


def _normalize_whitespace(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _text_length(element: Tag) -> int:
    return len(_normalize_whitespace(element.get_text(" ", strip=True)))


def _link_density(element: Tag) -> float:
    text_len = max(_text_length(element), 1)
    link_text = sum(len(link.get_text(strip=True)) for link in element.find_all("a"))
    return link_text / text_len


def _remove_noise(soup: BeautifulSoup) -> None:
    for tag_name in NOISE_TAGS:
        for element in soup.find_all(tag_name):
            element.decompose()

    for selector in NOISE_SELECTORS:
        for element in soup.select(selector):
            element.decompose()


def _score_content_block(element: Tag) -> float:
    text = _normalize_whitespace(element.get_text(" ", strip=True))
    if len(text) < 200:
        return 0.0

    tag_count = max(len(element.find_all(True)), 1)
    text_to_tag_ratio = len(text) / tag_count

    class_str = " ".join(element.get("class", [])).lower()
    id_str = (element.get("id") or "").lower()
    semantic_bonus = 0.0
    for token in ("document", "content", "article", "post", "main", "doc"):
        if token in class_str or token in id_str:
            semantic_bonus += 250.0

    if element.name in {"main", "article"}:
        semantic_bonus += 500.0

    link_penalty = _link_density(element) * 400.0

    return (len(text) * 0.6) + (text_to_tag_ratio * 40.0) + semantic_bonus - link_penalty


def _prune_in_content_chrome(element: Tag) -> None:
    for selector in (
        ".doc-sidebar",
        ".table-of-contents",
        ".toc",
        ".breadcrumbs",
        ".breadcrumb",
        ".print-to-pdf",
        "[class*='breadcrumb']",
    ):
        for child in element.select(selector):
            child.decompose()


def _find_best_content_block(soup: BeautifulSoup) -> Tag | None:
    for selector in MAIN_CONTENT_SELECTORS:
        for element in soup.select(selector):
            if _text_length(element) >= 200:
                return element

    candidates: list[tuple[float, Tag]] = []
    for element in soup.find_all(["main", "article", "section", "div"]):
        score = _score_content_block(element)
        if score > 0:
            candidates.append((score, element))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)

    best_score, best_element = candidates[0]
    for score, element in candidates[1:6]:
        if best_element in element.parents and score >= best_score * 0.85:
            best_element = element
            break

    return best_element


def extract_main_text(html: str) -> str:
    """
    Strip headers, footers, sidebars, and cookie banners; return main body text.
    """
    soup = BeautifulSoup(html, "html.parser")
    _remove_noise(soup)

    title = soup.title.get_text(strip=True) if soup.title else ""
    content_block = _find_best_content_block(soup)

    if content_block is not None:
        _prune_in_content_chrome(content_block)
        body_text = _normalize_whitespace(content_block.get_text("\n", strip=True))
    else:
        body_text = _normalize_whitespace(soup.get_text("\n", strip=True))

    if title and title not in body_text[: len(title) + 20]:
        return f"{title}\n\n{body_text}".strip()

    return body_text
