"""Basic Shell Commands for Git."""
import logging
import os
from typing import Dict

from knack import CLICommandsLoader
from knack.commands import CommandGroup
from git.repo import Repo

from gpt_review._command import GPTCommandGroup
from gpt_review._review import _request_goal


def _find_git_dir(path=".") -> str:
    while path != "/":
        if os.path.exists(os.path.join(path, ".git")):
            return path
        path = os.path.abspath(os.path.join(path, os.pardir))
    raise FileNotFoundError(".git directory not found")


def _diff() -> str:
    """
    Get the diff of the PR
    - run git commands via python
    """
    return Repo.init(_find_git_dir()).git.diff(None, cached=True)


def _commit_message() -> str:
    """Commit the changes."""

    goal = """
Create a short, single-line, git commit message for these changes
"""
    diff = _diff()
    logging.debug("Diff: %s", diff)

    return _request_goal(diff, goal)


def _commit() -> Dict[str, str]:
    """Run git commit with a commit message generated by GPT."""
    message = _commit_message()
    logging.debug("Commit Message: %s", message)
    repo = Repo.init(_find_git_dir())
    commit = repo.git.commit(message=message)
    return {"response": commit}


class GitCommandGroup(GPTCommandGroup):
    """Ask Command Group."""

    @staticmethod
    def load_command_table(loader: CLICommandsLoader) -> None:
        with CommandGroup(loader, "git", "gpt_review._git#{}") as group:
            group.command("commit", "_commit", is_preview=True)