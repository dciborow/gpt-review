import os
import pytest
import requests_mock
from dataclasses import dataclass

from gpt_review._devops import _create_comment, _update_pr, _get_diff


TOKEN = os.getenv("ADO_TOKEN", "token1")
PROJECT = os.getenv("ADO_PROJECT", "proj1")
ORG = os.getenv("ADO_ORG", "org1")
REPO = os.getenv("ADO_REPO", "repo1")


@pytest.fixture
def mock_req():
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def mock_update_thread(monkeypatch) -> None:
    @dataclass
    class MockResponse:
        text: str
        status_code: int = 203

    def mock_update_thread(self, text, repository_id, pull_request_id, comment_id) -> MockResponse:
        return MockResponse("mock response")

    monkeypatch.setattr("azure.devops.v7_1.git.git_client_base.GitClientBase.update_thread", mock_update_thread)

    class MockDevOpsClient:
        def get_git_client(self) -> "MockDevOpsClient":
            return MockDevOpsClient()

        def update_thread(self, text, repository_id, pull_request_id, comment_id) -> MockResponse:
            return MockResponse("mock response")

        def get_commit_diffs(
            self,
            repository_id,
            project=None,
            diff_common_commit=None,
            top=None,
            skip=None,
            base_version_descriptor=None,
            target_version_descriptor=None,
        ):
            return MockResponse("mock response")

    def mock_get_core_client(self) -> MockDevOpsClient:
        return MockDevOpsClient()

    monkeypatch.setattr("azure.devops.released.client_factory.ClientFactory.get_core_client", mock_get_core_client)


def test_create_comment(mock_update_thread) -> None:
    response = _create_comment(TOKEN, ORG, PROJECT, REPO, "pr1", "comment1", "text1")
    assert response.text == "mock response"


def test_update_pr(mock_req) -> None:
    mock_req.patch(
        "https://dev.azure.com/org1/proj1/_apis/git/repositories/repo1/pullrequests/pr1?api-version=6.0",
        text="mock response",
    )
    response = _update_pr(TOKEN, ORG, PROJECT, REPO, "pr1", "title1", "description1")
    assert response.text == "mock response"


def test_get_diff(mock_update_thread) -> None:
    response = _get_diff(TOKEN, ORG, PROJECT, REPO, "commit1", "version1", "version2")
    assert response.text == "mock response"


@pytest.mark.integration
def test_create_comment_integration(mock_update_thread) -> None:
    response = _create_comment(TOKEN, ORG, PROJECT, REPO, "pr1", "comment1", "text1")
    assert response.status_code == 203


@pytest.mark.integration
def test_update_pr_integration() -> None:
    response = _update_pr(TOKEN, ORG, PROJECT, REPO, "pr1", "title1", "description1")
    assert response.status_code == 401


@pytest.mark.integration
def test_get_diff_integration(mock_update_thread) -> None:
    response = _get_diff(TOKEN, ORG, PROJECT, REPO, "commit1", "version1", "version2")
    assert response.status_code == 203
