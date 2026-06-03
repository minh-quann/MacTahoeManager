"""
Version checker for MacTahoe GTK Theme.
Compares local git commit hash with the remote repository
to determine if updates are available.
"""

import subprocess
import threading
from enum import Enum


class UpdateStatus(Enum):
    """Possible states of an update check."""
    UP_TO_DATE = "up_to_date"
    UPDATE_AVAILABLE = "update_available"
    ERROR = "error"
    CHECKING = "checking"
    NOT_CLONED = "not_cloned"


class VersionInfo:
    """Holds version information for the local and remote repository."""
    def __init__(self):
        self.local_hash = ""
        self.local_short_hash = ""
        self.local_date = ""
        self.local_message = ""
        self.remote_hash = ""
        self.remote_short_hash = ""
        self.remote_date = ""
        self.remote_message = ""
        self.commits_behind = 0
        self.status = UpdateStatus.CHECKING


def get_local_commit_info(repo_dir):
    """Get the latest commit info from the local repository."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H|%h|%ci|%s"],
            cwd=repo_dir, capture_output=True, text=True, check=True
        )
        parts = result.stdout.strip().split("|", 3)
        if len(parts) == 4:
            return parts[0], parts[1], parts[2], parts[3]
    except Exception:
        pass
    return "", "", "", ""


def get_remote_commit_info(repo_dir):
    """Fetch and get the latest commit info from the remote repository."""
    try:
        # Fetch latest info from remote without merging
        subprocess.run(
            ["git", "fetch", "origin", "main"],
            cwd=repo_dir, capture_output=True, text=True, check=True
        )
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H|%h|%ci|%s", "origin/main"],
            cwd=repo_dir, capture_output=True, text=True, check=True
        )
        parts = result.stdout.strip().split("|", 3)
        if len(parts) == 4:
            return parts[0], parts[1], parts[2], parts[3]
    except Exception:
        pass
    return "", "", "", ""


def get_commits_behind(repo_dir):
    """Count how many commits the local branch is behind the remote."""
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD..origin/main"],
            cwd=repo_dir, capture_output=True, text=True, check=True
        )
        return int(result.stdout.strip())
    except Exception:
        return 0


def check_version(repo_dir, callback):
    """
    Check for updates asynchronously.
    Calls callback(VersionInfo) on completion.
    """
    def _check():
        info = VersionInfo()
        try:
            local = get_local_commit_info(repo_dir)
            info.local_hash = local[0]
            info.local_short_hash = local[1]
            info.local_date = local[2]
            info.local_message = local[3]

            remote = get_remote_commit_info(repo_dir)
            info.remote_hash = remote[0]
            info.remote_short_hash = remote[1]
            info.remote_date = remote[2]
            info.remote_message = remote[3]

            info.commits_behind = get_commits_behind(repo_dir)

            if info.local_hash == info.remote_hash:
                info.status = UpdateStatus.UP_TO_DATE
            else:
                info.status = UpdateStatus.UPDATE_AVAILABLE
        except Exception:
            info.status = UpdateStatus.ERROR

        callback(info)

    threading.Thread(target=_check, daemon=True).start()


def pull_and_get_changelog(repo_dir):
    """
    Pull latest changes and return a list of new commit messages.
    Returns (success: bool, messages: list[str], error: str).
    """
    try:
        # Get current HEAD before pulling
        old_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_dir, capture_output=True, text=True, check=True
        ).stdout.strip()

        # Pull latest
        subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=repo_dir, capture_output=True, text=True, check=True
        )

        # Get new HEAD
        new_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_dir, capture_output=True, text=True, check=True
        ).stdout.strip()

        # Get changelog between old and new HEAD
        changelog = []
        if old_head != new_head:
            result = subprocess.run(
                ["git", "log", "--oneline", f"{old_head}..{new_head}"],
                cwd=repo_dir, capture_output=True, text=True, check=True
            )
            changelog = [
                line.strip() for line in result.stdout.strip().split("\n")
                if line.strip()
            ]

        return True, changelog, ""
    except Exception as e:
        return False, [], str(e)
