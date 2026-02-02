import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

from southriverblog.model.tools_post import download_post


def _parse_file_entry(entry) -> tuple[str, str | None, str | None]:
    """Extract (filename, created_at, updated_at) from manifest entry (string or dict)."""
    if isinstance(entry, str):
        return (entry, None, None)
    filename = entry.get("filename", "")
    return (filename, entry.get("created_at"), entry.get("updated_at"))


def update_manifest(downloaded_updates=None):
    """
    Update manifest.json to include all markdown files in post_markdown directory.

    Each file has created_at and updated_at (ISO 8601 UTC).
    - New file: both set to now.
    - Re-downloaded with different content: updated_at set to now, created_at preserved.
    - Other files: preserve existing metadata, or use file mtime if missing.

    downloaded_updates: list of dicts {"filename": str, "is_new": bool, "content_changed": bool}
    """
    manifest_path = Path("post_markdown") / "manifest.json"
    post_dir = Path("post_markdown")

    if not post_dir.exists():
        return

    # Load existing manifest to preserve created_at/updated_at
    existing_by_filename = {}
    if manifest_path.exists():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            for entry in data.get("files", []):
                fn, ca, ua = _parse_file_entry(entry)
                if fn:
                    existing_by_filename[fn] = {"created_at": ca, "updated_at": ua}
        except (json.JSONDecodeError, OSError):
            pass

    # Build lookup of download results
    download_info = {}
    if downloaded_updates:
        for d in downloaded_updates:
            fn = d.get("filename")
            if fn:
                download_info[fn] = d

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    all_files = [f.name for f in post_dir.iterdir() if f.is_file() and f.suffix.lower() == ".md"]
    all_files.sort()

    files_with_meta = []
    for filename in all_files:
        info = download_info.get(filename)
        existing = existing_by_filename.get(filename)
        path_file = post_dir / filename

        if info:
            # We just downloaded this file
            if info.get("is_new"):
                created_at = now
                updated_at = now
            elif info.get("content_changed"):
                created_at = (existing or {}).get("created_at") or now
                updated_at = now
            else:
                created_at = (existing or {}).get("created_at") or now
                updated_at = (existing or {}).get("updated_at") or now
        elif existing and (existing.get("created_at") or existing.get("updated_at")):
            # Keep existing metadata
            created_at = existing.get("created_at")
            updated_at = existing.get("updated_at")
            # Fallback to mtime if either missing
            if not created_at or not updated_at:
                mtime = datetime.fromtimestamp(path_file.stat().st_mtime, tz=timezone.utc)
                mtime_str = mtime.strftime("%Y-%m-%dT%H:%M:%SZ")
                created_at = created_at or mtime_str
                updated_at = updated_at or mtime_str
        else:
            # New to manifest (e.g. manually added) - use file mtime
            mtime = datetime.fromtimestamp(path_file.stat().st_mtime, tz=timezone.utc)
            mtime_str = mtime.strftime("%Y-%m-%dT%H:%M:%SZ")
            created_at = mtime_str
            updated_at = mtime_str

        files_with_meta.append(
            {
                "filename": filename,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {"files": files_with_meta}
    with manifest_path.open("w", encoding="utf-8") as out:
        json.dump(manifest, out, indent=2)
    print(f"Updated manifest.json with {len(files_with_meta)} files")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download posts and/or update manifest.")
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Only refresh manifest.json from post_markdown/*.md (no downloads).",
    )
    parser.add_argument(
        "--zip-inspect",
        action="store_true",
        help="Download zip export for first doc, extract to post_zip_export/, and list contents.",
    )
    args = parser.parse_args()

    if args.zip_inspect:
        import io
        import zipfile

        document_id = "1DOQ6at_Ge8-zPbicYCqxx7cS3_bA_8dC_SRulZ-3Qoo"
        url = f"https://docs.google.com/document/d/{document_id}/export?format=zip"
        print(f"Downloading zip from {url}...")
        response = requests.get(url)
        response.raise_for_status()
        out_dir = Path("post_zip_export")
        out_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(response.content), "r") as zf:
            zf.extractall(out_dir)
            print(f"Extracted to {out_dir.absolute()}/")
            print("Contents:")
            for name in sorted(zf.namelist()):
                info = zf.getinfo(name)
                size = f"{info.file_size} bytes" if not info.is_dir() else "(dir)"
                print(f"  {name} {size}")
        sys.exit(0)

    if args.manifest_only:
        update_manifest()
        sys.exit(0)

    document_ids = []
    document_ids.append("1DOQ6at_Ge8-zPbicYCqxx7cS3_bA_8dC_SRulZ-3Qoo")
    document_ids.append("1yiZzJee9BW_HECceGlxDo6JDm0PPdO7CQ30Cak7H1Ro")
    document_ids.append("1wcs4TomYZjJePAkcLroFtr_d_VKVW3rZXkb81c7VLDA")
    document_ids.append("1sdVTjVopYT-bKBhNCjK0Qc8PYZhKL7pa_qbuI6LG_R4")

    downloaded_updates = []
    for document_id in document_ids:
        path, is_new, content_changed = download_post(document_id)
        print(f"Downloaded: {path}" + (" (new)" if is_new else " (updated)" if content_changed else ""))
        downloaded_updates.append(
            {
                "filename": path.name,
                "is_new": is_new,
                "content_changed": content_changed,
            }
        )

    update_manifest(downloaded_updates)
