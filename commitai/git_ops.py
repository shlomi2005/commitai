import subprocess
import sys


def get_staged_diff() -> str:
    result = subprocess.run(
        ["git", "diff", "--cached", "--stat", "--patch"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("❌ Not a git repository or git not found.", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def get_repo_context() -> dict:
    branch = subprocess.run(
        ["git", "branch", "--show-current"], capture_output=True, text=True
    ).stdout.strip()

    recent_commits = subprocess.run(
        ["git", "log", "--oneline", "-5"], capture_output=True, text=True
    ).stdout.strip()

    return {"branch": branch, "recent_commits": recent_commits}


def commit(message: str) -> bool:
    result = subprocess.run(["git", "commit", "-m", message])
    return result.returncode == 0


def is_git_repo() -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        capture_output=True,
    )
    return result.returncode == 0


def has_staged_changes() -> bool:
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        capture_output=True,
    )
    return result.returncode != 0
