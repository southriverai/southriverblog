import json
import sys
from pathlib import Path

from southriverblog.model.tools_post import download_post


def update_manifest():
    """
    Update manifest.json to include all markdown files in post_markdown directory.
    Uses only filenames (e.g. "post.md") so the site can load post_markdown/<filename>.
    """
    manifest_path = Path("post_markdown") / "manifest.json"
    post_dir = Path("post_markdown")

    if not post_dir.exists():
        return

    # Collect filenames only so manifest works with static hosting (post_markdown/<name>)
    all_files = [f.name for f in post_dir.iterdir() if f.is_file() and f.suffix.lower() == ".md"]
    all_files.sort()

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {"files": all_files}
    with manifest_path.open("w", encoding="utf-8") as out:
        json.dump(manifest, out, indent=2)
    print(f"Updated manifest.json with {len(all_files)} files")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download posts and/or update manifest.")
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Only refresh manifest.json from post_markdown/*.md (no downloads).",
    )
    args = parser.parse_args()

    if args.manifest_only:
        update_manifest()
        sys.exit(0)

    document_ids = []
    document_ids.append("1DOQ6at_Ge8-zPbicYCqxx7cS3_bA_8dC_SRulZ-3Qoo")
    document_ids.append("1yiZzJee9BW_HECceGlxDo6JDm0PPdO7CQ30Cak7H1Ro")
    document_ids.append("1wcs4TomYZjJePAkcLroFtr_d_VKVW3rZXkb81c7VLDA")
    document_ids.append("1sdVTjVopYT-bKBhNCjK0Qc8PYZhKL7pa_qbuI6LG_R4")

    for document_id in document_ids:
        path = download_post(document_id)
        print(f"Downloaded: {path}")

    # Refresh manifest again after downloads in case new files were added
    update_manifest()
