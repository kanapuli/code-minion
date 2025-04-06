import os
from os.path import isfile, relpath
from typing import Dict, List, Tuple

import git


class Repository:
    """Handles git repository operations and file retrieval"""

    def __init__(self, path: str) -> None:
        """Intializes with repository path"""
        self.path = path
        self._git_repo = None
        self._is_git_repo = os.path.isdir(os.path.join(self.path, ".git"))

        if self._is_git_repo:
            try:
                self._git_repo = git.Repo(self.path)
            except git.InvalidGitRepositoryError:
                self._is_git_repo = False

    @property
    def is_git_repo(self) -> bool:
        """Check if the directory is a git repository"""
        return self._is_git_repo

    def get_changed_files(self, base_revision: str = "HEAD~1") -> List[str]:
        """Get the list of changed files since the specified version"""
        if not self._is_git_repo:
            raise ValueError("Not a git repository")

        try:
            if self._git_repo is not None:
                diff = self._git_repo.git.diff("--name-only", base_revision)
                return [
                    os.path.join(self.path, file) for file in diff.split("\n") if file
                ]
            else:
                raise Exception(
                    "Expected _git_repo to be initialized for a valid git repo"
                )
        except git.GitCommandError as e:
            print(f"Git error: {e}")
            return []
        except Exception as e:
            print(f"Error: {e}")
            return []

    def get_file_content(self, file_path: str) -> Tuple[str, Dict[str, str]]:
        """Gets file contents and metadata"""

        abs_path = (
            file_path
            if os.path.isabs(file_path)
            else os.path.join(self.path, file_path)
        )

        if not os.path.isfile(abs_path):
            raise FileNotFoundError(f"File not found: {abs_path}")

        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            # Basic file stats
            stats = os.stat(abs_path)
            rel_path = os.path.relpath(abs_path, self.path)

            metadata = {
                "file_size": stats.st_size,
                "last_modified": stats.st_mtime,
                "relative_path": rel_path,
                "extension": os.path.splitext(abs_path)[1],
            }

            return content, metadata
        except Exception as e:
            print(f"Error reading file {abs_path}: {e}")
            raise
