import os
import glob

REPO_URL = "https://github.com/vinceliuice/MacTahoe-gtk-theme"

# Default location for cloning
DEFAULT_REPO_DIR = os.path.expanduser("~/.local/share/MacTahoe-gtk-theme")

# Common locations where the repo might already exist
_SEARCH_PATHS = [
    DEFAULT_REPO_DIR,
    os.path.expanduser("~/Documents/Customs/MacTahoe-gtk-theme"),
    os.path.expanduser("~/MacTahoe-gtk-theme"),
    os.path.expanduser("~/Downloads/MacTahoe-gtk-theme"),
]

# Theme install directory
THEME_DIR = os.path.expanduser("~/.themes")


def find_repo_dir():
    """
    Search for the MacTahoe repo in known locations.
    Returns the first path that contains install.sh, or DEFAULT_REPO_DIR as fallback.
    """
    for path in _SEARCH_PATHS:
        if os.path.isfile(os.path.join(path, "install.sh")):
            return path
    return DEFAULT_REPO_DIR


def is_theme_installed():
    """Check if any MacTahoe theme variant is installed in ~/.themes."""
    pattern = os.path.join(THEME_DIR, "MacTahoe-*")
    return len(glob.glob(pattern)) > 0


def get_installed_themes():
    """Return a list of installed MacTahoe theme variant names."""
    pattern = os.path.join(THEME_DIR, "MacTahoe-*")
    return [os.path.basename(p) for p in sorted(glob.glob(pattern))]


# Resolve the actual repo dir at import time
REPO_DIR = find_repo_dir()
