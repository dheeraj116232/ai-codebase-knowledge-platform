import os
import shutil
import stat
from git import Repo
from urllib.parse import urlparse

REPOS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "repos")

def get_repo_name(github_url: str) -> str:
    """Extract 'owner_repo' from a GitHub URL for use as a folder name."""
    path = urlparse(github_url).path.strip("/")
    path = path.replace(".git", "")
    return path.replace("/", "_")

def _handle_remove_error(func, path, exc_info):
    """Error handler for shutil.rmtree to handle permission errors on Windows.
    
    Git repositories often have read-only files that need permission changes
    before they can be deleted, especially on Windows.
    """
    if not os.access(path, os.W_OK):
        # Add write permissions and retry
        os.chmod(path, stat.S_IWUSR | stat.S_IRUSR | stat.S_IXUSR)
        func(path)
    else:
        raise exc_info[1]

def clone_repository(github_url: str) -> dict:
    repo_name = get_repo_name(github_url)
    local_path = os.path.join(REPOS_DIR, repo_name)

    # If already cloned, remove it first (simplest approach for now)
    if os.path.exists(local_path):
        shutil.rmtree(local_path, onerror=_handle_remove_error)

    os.makedirs(REPOS_DIR, exist_ok=True)

    try:
        Repo.clone_from(github_url, local_path)
    except Exception as e:
        raise RuntimeError(f"Failed to clone repository: {e}")

    return {
        "repo_name": repo_name,
        "local_path": local_path,
        "status": "cloned"
    }