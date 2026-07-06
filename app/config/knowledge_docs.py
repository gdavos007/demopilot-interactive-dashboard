"""CrowdStrike knowledge-base sources for DemoPilot demo questions."""

from typing import TypedDict


class KnowledgeDoc(TypedDict):
    question: str
    url: str


def dropbox_direct_url(url: str) -> str:
    """Use dl=1 so Dropbox serves HTML content for scraping."""
    if "dropbox.com" not in url:
        return url
    if "dl=0" in url:
        return url.replace("dl=0", "dl=1")
    if "dl=1" in url:
        return url
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}dl=1"


CROWDSTRIKE_KNOWLEDGE_DOCS: list[KnowledgeDoc] = [
    {
        "question": "What platforms and operating systems are supported (Windows, macOS, Linux)?",
        "url": dropbox_direct_url(
            "https://www.dropbox.com/scl/fi/6vqtrsctqe4lhmws6yqor/"
            "What-platforms-and-operating-systems-are-supported-Windows-macOS-Linux.html"
            "?rlkey=to1auaoubjv7b6lq11fxhv23f&st=z7di85pe&dl=0"
        ),
    },
    {
        "question": "Is there API access for custom integrations?",
        "url": dropbox_direct_url(
            "https://www.dropbox.com/scl/fi/g1mpptbr0fv95q9s6bam3/"
            "Is-there-API-access-for-custom-integrations.html"
            "?rlkey=7ad9dh5z95uf87hoxwpatgsy7&st=1suzljrb&dl=0"
        ),
    },
    {
        "question": (
            "What automated response actions are available "
            "(e.g., quarantine, kill process, isolate host)?"
        ),
        "url": dropbox_direct_url(
            "https://www.dropbox.com/scl/fi/ums676ep8d8ft0lb8qud5/"
            "What-automated-response-actions-are-available-e.g.-quarantine-kill-process-isolate-host.html"
            "?rlkey=z6f5j16qrpqv25vi72vpiqjq9&st=wpw0bn1q&dl=0"
        ),
    },
    {
        "question": "How can I look for removed malware?",
        "url": dropbox_direct_url(
            "https://www.dropbox.com/scl/fi/2dfoyahdbt9zrv7l23aom/"
            "How-can-I-look-for-removed-malware.html"
            "?rlkey=q731eb1q7h45kw96d7tcik3i1&st=8fruq4gs&e=1&dl=0"
        ),
    },
]

CROWDSTRIKE_FALLBACK_ANSWERS: dict[str, str] = {}
