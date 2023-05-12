"""Azure DevOps Package Wrappers to Simplify Usage."""
from typing import Iterator

from requests.models import Response
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


class DevOpsClient:
    """Azure DevOps API Client Wrapper."""

    def __init__(self, pat, org, project, repository_id) -> None:
        personal_access_token = pat
        organization_url = f"https://dev.azure.com/{org}"

        # Create a connection to the org
        credentials = BasicAuthentication("", personal_access_token)
        connection = Connection(base_url=organization_url, creds=credentials)

        # Get a client (the "core" client provides access to projects, teams, etc)
        self.client: GitClient = connection.clients_v7_1.get_git_client()
        self.project = project
        self.repository_id = repository_id

    def _create_comment(self, pull_request_id: int, comment_id: int, text) -> Comment:
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

    def _update_pr(self, pull_request_id, title=None, description=None) -> GitPullRequest:
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
    ) -> Iterator[bytes]:
        """
        Read all text from a file.

        Args:
            path (str): The path to the file.
            commit_id (str): The commit ID.
            **kwargs: Any additional keyword arguments.

        Returns:
            Iterator[bytes]: The bytes of the file.
        """
        return self.client.get_item_content(
            repository_id=self.repository_id,
            path=path,
            project=self.project,
            version_descriptor=GitVersionDescriptor(commit_id, version_type="commit"),
            **kwargs,
        )
