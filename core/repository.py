import fnmatch
import os
from os.path import isfile, relpath
from typing import Dict, List, Tuple

import git
from git.repo import base

from core.models import AnalysisContext


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

    def get_diff_content(self, file_path: str, base_revision: str = "HEAD~1") -> str:
        """Get the diff of a specific file"""
        if not self._git_repo:
            raise ValueError("Not a git repository")

        rel_path = os.path.relpath(self.path, file_path)

        try:
            return self._git_repo.git.diff(base_revision, rel_path)
        except git.CommandError as e:
            print(f"Git error getting diff in {rel_path}: {e}")
            return ""

    def find_files(self, context: AnalysisContext) -> List[str]:
        """Find files to analyse based on context"""
        if context.target_files:
            return [
                f if os.path.isabs(f) else os.path.join(self.path, f)
                for f in context.target_files
            ]

        # Get files based on Git diff if base_revision is specified
        if context.base_revision and self._is_git_repo:
            return self.get_changed_files(context.base_revision)

        # Otherwise analyse all files
        all_files = []

        for root, _, files in os.walk(self.path):
            if ".git" in root.split(os.path.sep):
                continue

            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.path)

                # Check for ignorable patterns
                if any(
                    fnmatch.fnmatch(rel_path, pattern)
                    for pattern in context.ignore_patterns
                ):
                    continue

                all_files.append(file_path)

                if len(all_files) >= context.max_files:
                    return all_files
        return all_files
