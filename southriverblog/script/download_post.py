import os
import re
import requests
import unicodedata

def slugify(text: str) -> str:
    """
    Convert text to a URL-friendly slug.
    """
    # Normalize unicode characters (e.g., é -> e)
    text = unicodedata.normalize('NFKD', text)
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Remove all non-alphanumeric characters except hyphens
    text = re.sub(r'[^\w\-]', '', text)
    # Replace multiple hyphens with a single hyphen
    text = re.sub(r'-+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text

def download_post(document_id: str) -> str:
    url = f"https://docs.google.com/document/d/{document_id}/export?format=md"
    response = requests.get(url)
    
    # Ensure UTF-8 encoding to preserve special characters
    response.encoding = 'utf-8'
    markdown_content = response.text
    
    # Extract title from first H1 heading
    title_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    else:
        # Fallback: use document ID if no title found
        title = f"post_{document_id}"
    
    # Slugify the title for filename
    slug = slugify(title)
    
    if not os.path.exists("post_markdown"):
        os.makedirs("post_markdown")
    path_file = os.path.join("post_markdown", f"{slug}.md")

    with open(path_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    return path_file

if __name__ == "__main__":
    document_ids = []
    document_ids.append("1DOQ6at_Ge8-zPbicYCqxx7cS3_bA_8dC_SRulZ-3Qoo")
    document_ids.append("1yiZzJee9BW_HECceGlxDo6JDm0PPdO7CQ30Cak7H1Ro")
    
    for document_id in document_ids:
        path = download_post(document_id)
        print(f"Downloaded: {path}")