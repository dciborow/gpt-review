import os
import pytest
import requests_mock
from dataclasses import dataclass
from azure.devops.v7_1.git.models import (
    GitBaseVersionDescriptor,
    GitTargetVersionDescriptor,
    GitCommitDiffs,
    GitPullRequest,
    Comment,
    GitPullRequestCommentThread,
)

from gpt_review.repositories._devops import _DevOpsClient, _comment

# Azure Devops PAT requires
# - Code: 'Read','Write'
# - Pull Request Threads: 'Read & Write'
TOKEN = os.getenv("ADO_TOKEN", "token1")

ORG = os.getenv("ADO_ORG", "msazure")
PROJECT = os.getenv("ADO_PROJECT", "one")
REPO = os.getenv("ADO_REPO", "azure-gaming")
PR_ID = int(os.getenv("ADO_PR_ID", 8063875))
COMMENT_ID = int(os.getenv("ADO_COMMENT_ID", 141344325))

SOURCE = os.getenv("ADO_COMMIT_SOURCE", "36f9a015ee220516f5f553faaa1898ab10972536")
TARGET = os.getenv("ADO_COMMIT_TARGET", "ecea1ea7db038317e94b45e090781410dc519b85")

SAMPLE_PAYLOAD = """{
  "resource": {
    "comment": {
      "content": "copilot: summary of this changed code"
    }
  }
}
"""


@pytest.fixture
def mock_req():
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def mock_ado_client(monkeypatch) -> None:
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

        def create_comment(self, comment, repository_id, pull_request_id, thread_id, project=None) -> Comment:
            return Comment()

        def get_pull_request_thread(
            self, repository_id, pull_request_id, thread_id, project=None, iteration=None, base_iteration=None
        ) -> GitPullRequestCommentThread:
            return GitPullRequestCommentThread()

        def update_pull_request(
            self, git_pull_request_to_update, repository_id, pull_request_id, project=None
        ) -> GitPullRequest:
            return GitPullRequest()

        def get_commit_diffs(
            self,
            repository_id,
            project=None,
            diff_common_commit=None,
            top=None,
            skip=None,
            base_version_descriptor=None,
            target_version_descriptor=None,
        ) -> GitCommitDiffs:
            return GitCommitDiffs()

    def mock_client(self) -> MockDevOpsClient:
        return MockDevOpsClient()

    monkeypatch.setattr("azure.devops.released.client_factory.ClientFactory.get_core_client", mock_client)
    monkeypatch.setattr("azure.devops.v7_1.client_factory.ClientFactoryV7_1.get_git_client", mock_client)


@pytest.fixture
def devops_client() -> _DevOpsClient:
    return _DevOpsClient(TOKEN, ORG, PROJECT, REPO)


def test_create_comment(devops_client: _DevOpsClient, mock_ado_client: None) -> None:
    response = devops_client.create_comment(pull_request_id=PR_ID, comment_id=COMMENT_ID, text="text1")
    assert isinstance(response, Comment)


def test_update_pr(devops_client: _DevOpsClient, mock_ado_client: None) -> None:
    response = devops_client.update_pr(pull_request_id=PR_ID, title="title1", description="description1")
    assert isinstance(response, GitPullRequest)


def test_get_diff(devops_client: _DevOpsClient, mock_ado_client: None) -> None:
    response = devops_client._get_commit_diff(
        diff_common_commit=True,
        base_version=GitBaseVersionDescriptor(version=SOURCE, version_type="commit"),
        target_version=GitTargetVersionDescriptor(target_version=TARGET, target_version_type="commit"),
    )
    assert isinstance(response, GitCommitDiffs)


@pytest.mark.integration
def test_create_comment_integration(devops_client: _DevOpsClient) -> None:
    response = devops_client.create_comment(pull_request_id=PR_ID, comment_id=COMMENT_ID, text="text1")
    assert isinstance(response, Comment)


@pytest.mark.integration
def test_update_pr_integration(devops_client: _DevOpsClient) -> None:
    response = devops_client.update_pr(PR_ID, description="description1")
    assert isinstance(response, GitPullRequest)
    response = devops_client.update_pr(PR_ID, title="Sample PR Title")
    assert isinstance(response, GitPullRequest)


@pytest.mark.integration
def test_get_diff_integration(devops_client: _DevOpsClient) -> None:
    response = devops_client._get_commit_diff(
        diff_common_commit=True,
        base_version=GitBaseVersionDescriptor(version=SOURCE, version_type="commit"),
        target_version=GitTargetVersionDescriptor(target_version=TARGET, target_version_type="commit"),
    )
    assert isinstance(response, GitCommitDiffs)


def process_payload_test() -> None:
    question = _DevOpsClient.process_payload(SAMPLE_PAYLOAD)
    link = "https://msazure.visualstudio.com/One/_git/Azure-Gaming/pullrequest/8063875"
    _comment(question, comment_id=COMMENT_ID, link=link)


def test_process_payload(mock_ado_client: None) -> None:
    process_payload_test()


@pytest.mark.integration
def test_process_payload_integration() -> None:
    process_payload_test()
