#!/usr/bin/env python3
"""
Commit all changes with an AI-generated message, add the generate-pages tag, and push.

Requires OPENAI_API_KEY in the environment for AI commit messages.
Falls back to a simple message if the API is unavailable.
"""
import argparse
import os
import subprocess
import sys

GENERATE_PAGES_TAG = "generate-pages"


def run(cmd: list[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    result = subprocess.run(
        cmd,
        check=check,
        capture_output=capture,
        text=True,
    )
    return result


def git_add_all() -> None:
    """Stage all changes."""
    print("Staging all changes (git add .)...")
    run(["git", "add", "."])


def has_staged_changes() -> bool:
    """Return True if there are staged changes."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        capture_output=True,
        check=False,
    )
    return result.returncode != 0


def get_staged_diff() -> str:
    """Return the staged diff (for commit message generation)."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--stat"],
        capture_output=True,
        text=True,
        check=False,
    )
    stat = result.stdout or ""
    result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True,
        check=False,
    )
    diff = result.stdout or ""
    # Truncate very large diffs to avoid token limits
    max_chars = 8000
    if len(diff) > max_chars:
        diff = diff[:max_chars] + "\n\n... (diff truncated)"
    return f"{stat}\n\n{diff}"


def generate_commit_message_with_ai(diff_text: str, api_key: str | None) -> str | None:
    """Use OpenAI to generate a short commit message from the staged diff."""
    if not api_key or not diff_text.strip():
        return None
    try:
        from openai import OpenAI  # pyright: ignore[reportMissingImports]

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helper that writes concise git commit messages. "
                        "Reply with a single short line (under 72 characters), "
                        "no quotes, no prefix like 'Commit:'. Use imperative mood."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Generate a commit message for these staged changes:\n\n{diff_text}",
                },
            ],
            max_tokens=100,
        )
        msg = (response.choices[0].message.content or "").strip().strip("\"'")
        if msg:
            return msg
        else:
            return None
    except Exception as e:
        print(f"AI commit message failed ({e}), using fallback.", file=sys.stderr)
        return None


MAX_PATHS_IN_FALLBACK = 3


def get_fallback_commit_message() -> str:
    """Fallback message based on git status."""
    result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True,
        text=True,
        check=False,
    )
    lines = (result.stdout or "").strip().splitlines()
    if not lines:
        return "Update repository"
    # Simple heuristic: mention first few changed paths
    parts = []
    for line in lines[:5]:
        path = line.split()[-1] if line.split() else ""
        if path and path not in parts:
            parts.append(path)
    summary = ", ".join(parts[:MAX_PATHS_IN_FALLBACK])
    if len(lines) > MAX_PATHS_IN_FALLBACK:
        summary += ", ..."
    return f"Update: {summary}"


def git_commit(message: str) -> None:
    """Create commit with the given message."""
    print(f"Committing: {message}")
    run(["git", "commit", "-m", message])


def git_tag(tag_name: str, force: bool = True) -> None:
    """Create or update the tag (e.g. for triggering generate-pages)."""
    print(f"Adding tag '{tag_name}'...")
    cmd = ["git", "tag", "-f", tag_name] if force else ["git", "tag", tag_name]
    run(cmd)


def git_push(with_tags: bool = True) -> None:
    """Push current branch and tags."""
    print("Pushing branch...")
    run(["git", "push"])
    if with_tags:
        print("Pushing tags...")
        run(["git", "push", "--tags"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage all changes, commit with AI-generated message, add generate-pages tag, push.")
    parser.add_argument(
        "--tag",
        default=GENERATE_PAGES_TAG,
        help=f"Tag to create/update (default: {GENERATE_PAGES_TAG})",
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Skip AI and use a simple fallback commit message",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print what would be done; do not run git commands",
    )
    args = parser.parse_args()

    if args.dry_run:
        print("Dry run: would run git add ., commit, tag, push.")
        return 0

    git_add_all()

    if not has_staged_changes():
        print("No changes to commit.")
        return 0

    staged = get_staged_diff()

    if args.no_ai:
        message = get_fallback_commit_message()
    else:
        api_key = os.environ.get("OPENAI_API_KEY")
        message = generate_commit_message_with_ai(staged, api_key)
        if not message:
            message = get_fallback_commit_message()

    git_commit(message)
    git_tag(args.tag)
    git_push()

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
