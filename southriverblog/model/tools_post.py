import re
import unicodedata
from pathlib import Path

import requests


def slugify(text: str) -> str:
    """
    Convert text to a URL-friendly slug.
    """
    # Normalize unicode characters (e.g., é -> e)
    text = unicodedata.normalize("NFKD", text)
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)
    # Remove all non-alphanumeric characters except hyphens
    text = re.sub(r"[^\w\-]", "", text)
    # Replace multiple hyphens with a single hyphen
    text = re.sub(r"-+", "-", text)
    # Remove leading/trailing hyphens
    text = text.strip("-")
    return text


def download_post(document_id: str) -> str:
    url = f"https://docs.google.com/document/d/{document_id}/export?format=md"
    response = requests.get(url)

    # Ensure UTF-8 encoding to preserve special characters
    response.encoding = "utf-8"
    markdown_content = response.text

    # Extract title from first H1 heading
    title_match = re.search(r"^#\s+(.+)$", markdown_content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    else:
        # Fallback: use document ID if no title found
        title = f"post_{document_id}"

    # Slugify the title for filename
    slug = slugify(title)

    if not Path("post_markdown").exists():
        Path("post_markdown").mkdir(parents=True, exist_ok=True)
    path_file = Path("post_markdown") / f"{slug}.md"

    with path_file.open("w", encoding="utf-8") as f:
        f.write(markdown_content)

    return path_file
