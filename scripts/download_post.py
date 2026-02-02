import json
from pathlib import Path

from southriverblog.model.tools_post import download_post


def update_manifest():
    """
    Update manifest.json to include all markdown files in post_markdown directory.
    """
    manifest_path = Path("post_markdown") / "manifest.json"

    # Get all markdown files in the directory
    if Path("post_markdown").exists():
        all_files = [f for f in Path("post_markdown").iterdir() if f.endswith(".md") and f.is_file()]
        # Sort alphabetically for consistent ordering
        all_files.sort()

        # Write manifest.json
        manifest = {"files": all_files}
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"Updated manifest.json with {len(all_files)} files")


if __name__ == "__main__":
    document_ids = []
    document_ids.append("1DOQ6at_Ge8-zPbicYCqxx7cS3_bA_8dC_SRulZ-3Qoo")
    document_ids.append("1yiZzJee9BW_HECceGlxDo6JDm0PPdO7CQ30Cak7H1Ro")
    document_ids.append("1wcs4TomYZjJePAkcLroFtr_d_VKVW3rZXkb81c7VLDA")
    document_ids.append("1sdVTjVopYT-bKBhNCjK0Qc8PYZhKL7pa_qbuI6LG_R4")

    for document_id in document_ids:
        path = download_post(document_id)
        print(f"Downloaded: {path}")

    # Update manifest.json after all downloads are complete
    update_manifest()
