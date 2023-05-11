"""Azure DevOps API Wrappers."""
import json

import requests
from requests.models import Response

from azure.devops.connection import Connection
from azure.devops.v7_1.git.git_client_base import GitClientBase
from msrest.authentication import BasicAuthentication


def _create_client(pat, org) -> GitClientBase:
    # Fill in with your personal access token and org URL
    personal_access_token = pat
    organization_url = f"https://dev.azure.com/{org}"

    # Create a connection to the org
    credentials = BasicAuthentication("", personal_access_token)
    connection = Connection(base_url=organization_url, creds=credentials)

    # Get a client (the "core" client provides access to projects, teams, etc)
    core_client = connection.clients.get_core_client()
    return core_client.get_git_client()


def _create_comment(token, org, project, repository_id, pull_request_id, comment_id, text) -> Response:
    """
    Create a comment on a pull request.

    Args:
        token (str): The Azure DevOps token.
        org (str): The Azure DevOps organization.
        project (str): The Azure DevOps project.
        repository_id (str): The Azure DevOps repository ID.
        pull_request_id (str): The Azure DevOps pull request ID.
        comment_id (str): The Azure DevOps comment ID.
        text (str): The text of the comment.

    Returns:
        Response: The response from the API.
    """
    git_client = _create_client(token, org)
    return git_client.update_thread(text, repository_id, pull_request_id, comment_id)


def _update_pr(token, org, project, repository_id, pull_request_id, title, description) -> Response:
    """
    Update a pull request.

    Args:
        token (str): The Azure DevOps token.
        org (str): The Azure DevOps organization.
        project (str): The Azure DevOps project.
        repository_id (str): The Azure DevOps repository ID.
        pull_request_id (str): The Azure DevOps pull request ID.
        title (str): The title of the pull request.
        description (str): The description of the pull request.

    Returns:
        Response: The response from the API.
    """
    url = f"https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repository_id}/pullrequests/{pull_request_id}?api-version=6.0"

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    data = {"title": title, "description": description}

    return requests.patch(url, headers=headers, data=json.dumps(data), timeout=10)


def _get_diff(token, org, project, repository_id, diff_common_commit, base_version, target_version) -> Response:
    """
    Get the diff between two commits.

    Args:
        token (str): The Azure DevOps token.
        org (str): The Azure DevOps organization.
        project (str): The Azure DevOps project.
        repository_id (str): The Azure DevOps repository ID.
        diff_common_commit (str): The common commit between the two versions.
        base_version (str): The base version.
        target_version (str): The target version.

    Returns:
        Response: The response from the API.
    """
    url = f"https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repository_id}/diffsCommonCommit/{diff_common_commit}?api-version=6.0"

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    data = {"baseVersion": base_version, "targetVersion": target_version}

    return requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
