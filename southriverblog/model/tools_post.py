import io
import re
import unicodedata
import zipfile
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


def _img_order_from_html(html: str) -> list[str]:
    """Extract image filenames in document order from HTML img src='images/...'."""
    return re.findall(r'src="images/([^"]+)"', html)


def _sanitize_doc_id_for_path(document_id: str) -> str:
    """Replace underscores with hyphens so URLs don't trigger markdown emphasis parsing."""
    return document_id.replace("_", "-")


def _download_zip_images(document_id: str, images_dir: Path) -> dict[str, str]:
    """
    Download zip export, extract images to images/{sanitized_doc_id}/.
    Uses HTML to determine image order (markdown image1 = first img in doc, etc.).
    Returns mapping of image ref (e.g. image1) -> filename (e.g. image3.png).
    """
    url = f"https://docs.google.com/document/d/{document_id}/export?format=zip"
    response = requests.get(url)
    response.raise_for_status()

    safe_id = _sanitize_doc_id_for_path(document_id)
    out_dir = images_dir / safe_id
    out_dir.mkdir(parents=True, exist_ok=True)
    ref_to_file: dict[str, str] = {}
    image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
    html_img_order: list[str] = []
    zip_content = response.content

    with zipfile.ZipFile(io.BytesIO(zip_content), "r") as zf:
        # Find HTML file and extract image order
        for name in zf.namelist():
            if name.lower().endswith(".html"):
                html = zf.read(name).decode("utf-8", errors="replace")
                html_img_order = _img_order_from_html(html)
                break

        # Extract images
        for name in zf.namelist():
            if name.endswith("/"):
                continue
            if name.startswith("images/"):
                img_name = name.split("/", 1)[1]
            else:
                if Path(name).suffix.lower() not in image_extensions:
                    continue
                img_name = Path(name).name
            (out_dir / img_name).write_bytes(zf.read(name))

        # Build ref_to_file from HTML order: image1 -> first img, image2 -> second, etc.
        for i, filename in enumerate(html_img_order, start=1):
            ref_to_file[f"image{i}"] = filename

    return ref_to_file


def _rewrite_markdown_image_refs(markdown: str, document_id: str, ref_to_file: dict[str, str]) -> str:
    """Replace [imageN]: <data:...> definitions with paths to images/{safe_id}/imageN.ext.
    Uses hyphenated doc_id in path to avoid underscores being parsed as markdown emphasis."""

    def repl(m: re.Match[str]) -> str:
        ref = m.group(1)
        filename = ref_to_file.get(ref, f"{ref}.png")
        safe_id = _sanitize_doc_id_for_path(document_id)
        url = f"images/{safe_id}/{filename}"
        return f"[{ref}]: {url}"

    return re.sub(r"\[(image\d+)\]:\s*<[^>]+>", repl, markdown)


def download_post(document_id: str) -> tuple[Path, bool, bool]:
    """
    Download a Google Doc as markdown and save to post_markdown.
    Also downloads zip export and extracts images to images/{document_id}/.

    Returns:
        Tuple of (path, is_new, content_changed)
        - is_new: True if the file did not exist before
        - content_changed: True if file was new or existing content differed from downloaded content
    """
    url = f"https://docs.google.com/document/d/{document_id}/export?format=md"
    response = requests.get(url)

    # Ensure UTF-8 encoding to preserve special characters
    response.encoding = "utf-8"
    markdown_content = response.text

    # Download zip and extract images to images/{document_id}/
    images_dir = Path("images")
    try:
        ref_to_file = _download_zip_images(document_id, images_dir)
        if ref_to_file:
            markdown_content = _rewrite_markdown_image_refs(markdown_content, document_id, ref_to_file)
    except requests.RequestException:
        pass  # Keep original markdown (with base64) if zip download fails

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

    is_new = not path_file.exists()
    existing_content = path_file.read_text(encoding="utf-8") if path_file.exists() else ""
    content_changed = is_new or existing_content != markdown_content

    with path_file.open("w", encoding="utf-8") as f:
        f.write(markdown_content)

    return (path_file, is_new, content_changed)
