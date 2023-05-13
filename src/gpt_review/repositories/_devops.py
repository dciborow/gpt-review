"""Azure DevOps Package Wrappers to Simplify Usage."""
import logging
import json
import os
from typing import Dict, Iterator, List, Optional, Iterable

from msrest.authentication import BasicAuthentication

from azure.devops.connection import Connection
from azure.devops.v7_1.git.models import (
    Comment,
    GitCommitDiffs,
    GitBaseVersionDescriptor,
    GitTargetVersionDescriptor,
    GitBlobRef,
    GitVersionDescriptor,
    GitPullRequest,
    GitPullRequestCommentThread,
)
from azure.devops.v7_1.git.git_client import GitClient
from knack.arguments import ArgumentsContext
from knack import CLICommandsLoader
from knack.commands import CommandGroup

from gpt_review._ask import _ask
from gpt_review._command import GPTCommandGroup
from gpt_review._review import _summarize_files
from gpt_review.repositories._repository import _RepositoryClient

import itertools


MIN_CONTEXT_LINES = 5
SURROUNDING_CONTEXT = 5


class _DevOpsClient(_RepositoryClient):
    """Azure DevOps API Client Wrapper."""

    @staticmethod
    def post_pr_summary(diff, link=None, access_token=None) -> Dict[str, str]:
        """
        Get a review of a PR.

        Requires the following environment variables:
            - LINK: The link to the PR.
                Example: https://<org>.visualstudio.com/<project>/_git/<repo>/pullrequest/<pr_id>
                    or   https://dev.azure.com/<org>/<project>/_git/<repo>/pullrequest/<pr_id>
            - ADO_TOKEN: The GitHub access token.

        Args:
            diff (str): The patch of the PR.

        Returns:
            Dict[str, str]: The review.
        """
        link = os.getenv("LINK", link)
        access_token = os.getenv("ADO_TOKEN", access_token)

        if link and access_token:
            review = _summarize_files(diff)

            if "dev.azure.com" in link:
                org = link.split("/")[3]
                project = link.split("/")[4]
                repo = link.split("/")[6]
                pr_id = link.split("/")[8]
            else:
                org = link.split("/")[2].split(".")[0]
                project = link.split("/")[3]
                repo = link.split("/")[5]
                pr_id = link.split("/")[7]

            _DevOpsClient(pat=access_token, org=org, project=project, repository_id=repo).update_pr(
                pull_request_id=pr_id,
                description=review,
            )
            return {"response": "PR posted"}

        logging.warning("No PR to post too")
        return {"response": "No PR to post too"}

    @staticmethod
    def get_pr_diff(patch_repo=None, patch_pr=None, access_token=None) -> str:
        """
        Get the diff of a PR.

        Args:
            patch_repo (str): The repo.
            patch_pr (str): The PR.
            access_token (str): The GitHub access token.

        Returns:
            str: The diff of the PR.
        """

    def __init__(self, pat, org, project, repository_id) -> None:
        personal_access_token = pat
        organization_url = f"https://dev.azure.com/{org}"

        # Create a connection to the org
        credentials = BasicAuthentication("", personal_access_token)
        connection = Connection(base_url=organization_url, creds=credentials)

        # Get a client (the "core" client provides access to projects, teams, etc)
        self.connection = connection
        self.client: GitClient = connection.clients_v7_1.get_git_client()
        self.project = project
        self.repository_id = repository_id

    def create_comment(self, pull_request_id: int, comment_id: int, text) -> Comment:
        """
        Create a comment on a pull request.

        Args:
            token (str): The Azure DevOps token.
            org (str): The Azure DevOps organization.
            project (str): The Azure DevOps project.
            repository_id (str): The Azure DevOps repository ID.
            pull_request_id (int): The Azure DevOps pull request ID.
            comment_id (int): The Azure DevOps comment ID.
            text (str): The text of the comment.

        Returns:
            Comment: The response from the API.
        """
        new_comment = Comment(content=text)
        return self.client.create_comment(
            new_comment, self.repository_id, pull_request_id, comment_id, project=self.project
        )

    def _get_comment_thread(self, pull_request_id: str, thread_id: str) -> GitPullRequestCommentThread:
        """
        Get a comment thread.

        Args:
            pull_request_id (str): The Azure DevOps pull request ID.
            thread_id (str): The Azure DevOps thread ID.

        Returns:
            GitPullRequestCommentThread: The response from the API.
        """
        return self.client.get_pull_request_thread(
            repository_id=self.repository_id, pull_request_id=pull_request_id, thread_id=thread_id, project=self.project
        )

    def _get_changed_blobs(
        self,
        sha1: str,
        download: bool = None,
        file_name: str = None,
        resolve_lfs: bool = None,
    ) -> GitBlobRef:
        """
        Get the changed blobs in a commit.

        Args:
            sha1 (str): The SHA1 of the commit.
            download (bool): Whether to download the blob.
            file_name (str): The name of the file.
            resolve_lfs (bool): Whether to resolve LFS.

        Returns:
            GitBlobRef: The response from the API.
        """
        return self.client.get_blob(
            repository_id=self.repository_id,
            project=self.project,
            sha1=sha1,
            download=download,
            file_name=file_name,
            resolve_lfs=resolve_lfs,
        )

    def update_pr(self, pull_request_id, title=None, description=None) -> GitPullRequest:
        """
        Update a pull request.

        Args:
            pull_request_id (str): The Azure DevOps pull request ID.
            title (str): The title of the pull request.
            description (str): The description of the pull request.

        Returns:
            GitPullRequest: The response from the API.
        """
        return self.client.update_pull_request(
            git_pull_request_to_update=GitPullRequest(title=title, description=description),
            repository_id=self.repository_id,
            project=self.project,
            pull_request_id=pull_request_id,
        )

    def _get_commit_diff(
        self,
        diff_common_commit: bool,
        base_version: GitBaseVersionDescriptor,
        target_version: GitTargetVersionDescriptor,
    ) -> GitCommitDiffs:
        """
        Get the diff between two commits.

        Args:
            diff_common_commit (bool): Whether to diff the common commit.
            base_version (GitBaseVersionDescriptor): The base version.
            target_version (GitTargetVersionDescriptor): The target version.

        Returns:
            Response: The response from the API.
        """
        return self.client.get_commit_diffs(
            repository_id=self.repository_id,
            project=self.project,
            diff_common_commit=diff_common_commit,
            base_version_descriptor=base_version,
            target_version_descriptor=target_version,
        )

    def _read_all_text(
        self,
        path: str,
        commit_id: str = None,
        **kwargs,
    ) -> str:
        """
        Read all text from a file.

        Args:
            path (str): The path to the file.
            commit_id (str): The commit ID.
            **kwargs: Any additional keyword arguments.

        Returns:
            str: The text of the file.
        """
        byte_iterator = self.client.get_item_content(
            repository_id=self.repository_id,
            path=path,
            project=self.project,
            version_descriptor=GitVersionDescriptor(commit_id, version_type="commit") if commit_id else None,
            **kwargs,
        )
        return "".join(byte.decode("utf-8") for byte in byte_iterator)

    async def read_all_text_async(self, path: str, commit_id, **kwargs) -> Iterator[bytes]:
        """
        Read all text from a file asynchronously.

        Args:
            path (str): The path to the file.
            commit_id (str): The commit ID.
            **kwargs: Any additional keyword arguments.

        Returns:
            Iterator[bytes]: The bytes of the file.
        """
        return await self.client._read_all_text(path=path, commit_id=commit_id)

    @staticmethod
    def process_comment_payload(payload: str):
        """
        Extract question from Service Bus payload.

        Args:
            payload (str): The Service Bus payload.

        Returns:
            str: The question from the Azure DevOps Comment.
        """
        payload = json.loads(payload)
        return payload["resource"]["comment"]["content"]

    def get_patch(self, pull_request_event, pull_request_id, comment_id) -> List[str]:
        """
        Get the diff of a pull request.

        Args:
            pull_request_event (dict): The pull request event.
            pull_request_id (str): The Azure DevOps pull request ID.
            comment_id (str): The Azure DevOps comment ID.

        Returns:
            List[str]: The diff of the pull request.
        """
        context = ContextProvider(self)
        thread = self._get_comment_thread(pull_request_id=pull_request_id, thread_id=comment_id)

        return context.get_patch(thread_context=thread.thread_context, pull_request_event=pull_request_event)


def _review(diff: str = ".diff", link=None, access_token=None) -> Dict[str, str]:
    """Review Azure DevOps PR with Open AI, and post response as a comment.

    Args:
        link (str): The link to the PR.
        access_token (str): The Azure DevOps access token.

    Returns:
        Dict[str, str]: The response.
    """
    # diff = _DevOpsClient.get_pr_diff(repository, pull_request, access_token)
    with open(diff, "r", encoding="utf8") as file:
        diff_contents = file.read()

    _DevOpsClient.post_pr_summary(diff_contents, link, access_token)
    return {"response": "Review posted as a comment."}


def _comment(question: str, comment_id: int, diff: str = ".diff", link=None, access_token=None) -> Dict[str, str]:
    """Review Azure DevOps PR with Open AI, and post response as a comment.

    Args:
        question (str): The question to ask.
        comment_id (int): The comment ID.
        diff(str): The diff file.
        link (str): The link to the PR.
        access_token (str): The Azure DevOps access token.

    Returns:
        Dict[str, str]: The response.
    """
    # diff = _DevOpsClient.get_pr_diff(repository, pull_request, access_token)

    if os.path.exists(diff):
        with open(diff, "r", encoding="utf8") as file:
            diff_contents = file.read()
            question = f"{diff_contents}\n{question}"

    link = os.getenv("LINK", link)
    access_token = os.getenv("ADO_TOKEN", access_token)

    if link and access_token:
        response = _ask(
            question=question,
        )
        if "dev.azure.com" in link:
            org = link.split("/")[3]
            project = link.split("/")[4]
            repo = link.split("/")[6]
            pr_id = link.split("/")[8]
        else:
            org = link.split("/")[2].split(".")[0]
            project = link.split("/")[3]
            repo = link.split("/")[5]
            pr_id = link.split("/")[7]

    _DevOpsClient(pat=access_token, org=org, project=project, repository_id=repo).create_comment(
        pull_request_id=pr_id, comment_id=comment_id, text=response["response"]
    )
    return {"response": "Review posted as a comment.", "text": response["response"]}


class DevOpsCommandGroup(GPTCommandGroup):
    """Ask Command Group."""

    @staticmethod
    def load_command_table(loader: CLICommandsLoader) -> None:
        with CommandGroup(loader, "ado", "gpt_review.repositories._devops#{}", is_preview=True) as group:
            group.command("review", "_review", is_preview=True)
            group.command("comment", "_comment", is_preview=True)

    @staticmethod
    def load_arguments(loader: CLICommandsLoader) -> None:
        """Add patch_repo, patch_pr, and access_token arguments."""
        with ArgumentsContext(loader, "ado") as args:
            args.argument(
                "diff",
                type=str,
                help="Git diff to review.",
                default=".diff",
            )
            args.argument(
                "access_token",
                type=str,
                help="The Azure DevOps access token, or set ADO_TOKEN",
                default=None,
            )
            args.argument(
                "link",
                type=str,
                help="The link to the PR.",
                default=None,
            )

        with ArgumentsContext(loader, "ado comment") as args:
            args.positional("question", type=str, nargs="+", help="Provide a question to ask GPT.")
            args.argument(
                "comment_id",
                type=int,
                help="The comment ID of Azure DevOps Pull Request Comment.",
                default=None,
            )


class ContextProvider:
    """Provides context for a given line in a file."""

    def __init__(self, devops_client: _DevOpsClient) -> None:
        """
        Initialize a new instance of ContextProvider.

        Args:
            devops_client (_DevOpsClient): The DevOps client.
        """
        self.devops_client = devops_client

    def get_patch(self, thread_context, pull_request_event) -> List[str]:
        """
        Get the patch for a given thread context.

        Args:
            thread_context (ThreadContext): The thread context.
            pull_request_event (PullRequestEvent): The pull request event.

        Returns:
            List[str]: The patch.
        """
        pull_request = pull_request_event["pullRequest"]
        if not pull_request:
            raise ValueError("pull_request_event.pullRequest is required")

        original_content_task = self.devops_client._read_all_text(path=thread_context.file_path, check_if_exists=True)
        changed_content_task = self.devops_client._read_all_text(
            path=thread_context.file_path,
            commit_id=pull_request["lastMergeSourceCommit"]["commitId"],
            check_if_exists=True,
        )
        # original_content = await original_content_task
        # changed_content = await changed_content_task
        original_content = original_content_task
        changed_content = changed_content_task

        left_selection = None
        right_selection = None
        if original_content and thread_context.left_file_start and thread_context.left_file_end:
            left_selection = self._get_selection(
                original_content, thread_context.left_file_start.line, thread_context.left_file_end.line
            )

            if not changed_content or not thread_context.right_file_start or not thread_context.right_file_end:
                raise ValueError("Both left and right selection cannot be None")

            right_selection = self._get_selection(
                changed_content, thread_context.right_file_start.line, thread_context.right_file_end.line
            )

        if changed_content and thread_context.right_file_start and thread_context.right_file_end:
            right_selection = self._get_selection(
                changed_content, thread_context.right_file_start.line, thread_context.right_file_end.line
            )

        if not left_selection and not right_selection:
            raise ValueError("Both left and right selection cannot be None")

        return self._create_patch(left_selection or [], right_selection or [], thread_context.file_path)

    async def get_patches(self, pull_request_event, condensed=False) -> Iterable[List[str]]:
        """
        Get the patches for a given pull request event.

        Args:
            pull_request_event (Any): The pull request event to retrieve patches for.
            condensed (bool, optional): If True, returns a condensed version of the patch. Defaults to False.

        Returns:
            Iterable[List[str]]: An iterable of lists containing the patches for the pull request event.
        """
        pull_request_id = pull_request_event["pullRequest"]["pullRequestId"]
        if not pull_request_id:
            raise ValueError("pull_request_event.pullRequest is required")

        git_changes = await self.devops_client.get_changed_blobs_async(pull_request_event["pullRequest"])
        all_patches = []

        for git_change in git_changes:
            all_patches.append(
                await self._get_change_async(
                    git_change, pull_request_event["pullRequest"]["lastMergeSourceCommit"]["commitId"], condensed
                )
            )

        return all_patches

    def _get_selection(self, file_contents: str, line_start: int, line_end: int) -> List[str]:
        lines = file_contents.splitlines()

        if line_end - line_start < MIN_CONTEXT_LINES:
            return lines

        if line_start < 1 or line_start > len(lines) or line_end < 1 or line_end > len(lines):
            raise ValueError(
                f"Selection region lineStart = {line_start}, lineEnd = {line_end}, lines length = {len(lines)}"
            )

        if line_start == line_end:
            return [lines[line_start - 1]]

        return lines[line_start - 1 : line_end]

    async def _get_change_async(self, git_change, source_commit_head, condensed=False) -> List[str]:
        return await self._get_git_change_async(self.devops_client, git_change.item.path, source_commit_head, condensed)

    async def _get_git_change_async(self, git_client, file_path, source_commit_head, condensed=False) -> List[str]:
        original_content = git_client.read_all_text_async(file_path, check_if_exists=True)
        changed_content = git_client.read_all_text_async(file_path, commit_id=source_commit_head, check_if_exists=True)
        return self._create_patch(await original_content, await changed_content, file_path, condensed)

    def _create_patch(
        self, original_content: Optional[str], changed_content: Optional[str], file_path: str, condensed=False
    ) -> List[str]:
        left = original_content.splitlines() if original_content else []
        right = changed_content if changed_content else []
        return self._create_patch_list(left, right, file_path, condensed)

    def _create_patch_list(self, left: List[str], right: List[str], file_path: str, condensed=False) -> List[str]:
        dp = self._calculate_minimum_change_needed(left, right)
        l, r = 1, 1
        patch = []

        while l < len(left) and r < len(right):
            if dp[l][r] == dp[l - 1][r - 1]:
                patch.append(left[l - 1])
                l += 1
                r += 1
            elif dp[l - 1][r] < dp[l][r - 1]:
                patch.append(f"- {left[l - 1]}")
                l += 1
            else:
                patch.append(f"+ {right[r - 1]}")
                r += 1

        while l <= len(left):
            patch.append(f"- {left[l - 1]}")
            l += 1

        while r <= len(right):
            patch.append(f"+ {right[r - 1]}")
            r += 1

        if condensed:
            patch = self._get_condensed_patch(patch)

        patch.insert(0, file_path)
        return patch

    def _get_condensed_patch(self, patch: List[str]) -> List[str]:
        buffer = []
        result = []
        trailing_context = 0

        for line in patch:
            if line.startswith("+") or line.startswith("-"):
                result.extend(buffer[-SURROUNDING_CONTEXT:])
                buffer.clear()
                result.append(line)
                trailing_context = SURROUNDING_CONTEXT
            elif trailing_context > 0:
                result.append(line)
                trailing_context -= 1
            else:
                buffer.append(line)

        return result

    def _calculate_minimum_change_needed(self, left: List[str], right: List[str]) -> List[List[int]]:
        dp = [[0] * (len(right) + 1) for _ in range(len(left) + 1)]

        for i, j in itertools.product(range(len(left) + 1), range(len(right) + 1)):
            if i == 0 or j == 0:
                dp[i][j] = 0
            elif left[i - 1] == right[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

        return dp
