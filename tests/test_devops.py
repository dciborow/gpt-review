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
)

from gpt_review._devops import DevOpsClient


TOKEN = "wek2yfvavgvvtgan2wvltm4jlqpyusgbl3icm3v2hsnz7vmyclva"  # os.getenv("ADO_TOKEN", "token1")
ORG = "msazure"  # os.getenv("ADO_ORG", "org1")
PROJECT = "one"  # os.getenv("ADO_PROJECT", "proj1")
REPO = "azure-gaming"  # os.getenv("ADO_REPO", "repo1")
PR_ID = 8063875  # os.getenv("ADO_PR_ID", "pr1")
COMMIT_ID = 141344325  # os.getenv("ADO_COMMIT_ID", "commit1");

COMMENT_ID = 141344325
SOURCE = "36f9a015ee220516f5f553faaa1898ab10972536"
TARGET = "ecea1ea7db038317e94b45e090781410dc519b85"

SAMPLE_PAYLOAD = """
{
  "id": "4ab6dfc4-5868-4ba2-bd8e-f067708bcc53",
  "eventType": "ms.vss-code.git-pullrequest-comment-event",
  "publisherId": "tfs",
  "message": {
    "text": "Daniel Ciborowski has commented on a pull request"
  },
  "detailedMessage": {
    "text": "Daniel Ciborowski has commented on a pull request\r\ncopilot: summary\r\n"
  },
  "resource": {
    "comment": {
      "id": 1,
      "parentCommentId": 0,
      "author": {
        "displayName": "Daniel Ciborowski",
        "url": "https://spsprodwus23.vssps.visualstudio.com/A41b4f3ee-c651-4a14-9847-b7cbb5315b80/_apis/Identities/0ef5b3af-3e01-48fd-9bd3-2f701c8fdebe",
        "_links": {
          "avatar": {
            "href": "https://msazure.visualstudio.com/_apis/GraphProfile/MemberAvatars/aad.OTgwYzcxNzEtMDI2Ni03YzVmLTk0YzEtMDNlYzU2YjViYjY4"
          }
        },
        "id": "0ef5b3af-3e01-48fd-9bd3-2f701c8fdebe",
        "uniqueName": "dciborow@microsoft.com",
        "imageUrl": "https://msazure.visualstudio.com/_apis/GraphProfile/MemberAvatars/aad.OTgwYzcxNzEtMDI2Ni03YzVmLTk0YzEtMDNlYzU2YjViYjY4",
        "descriptor": "aad.OTgwYzcxNzEtMDI2Ni03YzVmLTk0YzEtMDNlYzU2YjViYjY4"
      },
      "content": "copilot: summary",
      "publishedDate": "2023-05-12T18:43:35.28Z",
      "lastUpdatedDate": "2023-05-12T18:43:35.28Z",
      "lastContentUpdatedDate": "2023-05-12T18:43:35.28Z",
      "commentType": "text",
      "usersLiked": [],
      "_links": {
        "self": {
          "href": "https://msazure.visualstudio.com/_apis/git/repositories/612d9367-8ab6-4929-abe6-b5b5ad7b5ad3/pullRequests/8063875/threads/141414332/comments/1"
        },
        "repository": {
          "href": "https://msazure.visualstudio.com/b32aa71e-8ed2-41b2-9d77-5bc261222004/_apis/git/repositories/612d9367-8ab6-4929-abe6-b5b5ad7b5ad3"
        },
        "threads": {
          "href": "https://msazure.visualstudio.com/_apis/git/repositories/612d9367-8ab6-4929-abe6-b5b5ad7b5ad3/pullRequests/8063875/threads/141414332"
        },
        "pullRequests": {
          "href": "https://msazure.visualstudio.com/_apis/git/pullRequests/8063875"
        }
      }
    },
    "pullRequest": {
      "repository": {
        "id": "612d9367-8ab6-4929-abe6-b5b5ad7b5ad3",
        "name": "Azure-Gaming",
        "url": "https://msazure.visualstudio.com/b32aa71e-8ed2-41b2-9d77-5bc261222004/_apis/git/repositories/612d9367-8ab6-4929-abe6-b5b5ad7b5ad3",
        "project": {
          "id": "b32aa71e-8ed2-41b2-9d77-5bc261222004",
          "name": "One",
          "description": "MSAzure/One is the VSTS project containing all Azure team code bases and work items.\nPlease see https://aka.ms/azaccess for work item and source access policies.",
          "url": "https://msazure.visualstudio.com/_apis/projects/b32aa71e-8ed2-41b2-9d77-5bc261222004",
          "state": "wellFormed",
          "revision": 307061,
          "visibility": "organization",
          "lastUpdateTime": "2023-05-12T17:40:59.963Z"
        },
        "size": 508859977,
        "remoteUrl": "https://msazure.visualstudio.com/DefaultCollection/One/_git/Azure-Gaming",
        "sshUrl": "msazure@vs-ssh.visualstudio.com:v3/msazure/One/Azure-Gaming",
        "webUrl": "https://msazure.visualstudio.com/DefaultCollection/One/_git/Azure-Gaming",
        "isDisabled": false,
        "isInMaintenance": false
      },
      "pullRequestId": 8063875,
      "codeReviewId": 8836473,
      "status": "active",
      "createdBy": {
        "displayName": "Daniel Ciborowski",
        "url": "https://spsprodwus23.vssps.visualstudio.com/A41b4f3ee-c651-4a14-9847-b7cbb5315b80/_apis/Identities/0ef5b3af-3e01-48fd-9bd3-2f701c8fdebe",
        "_links": {
          "avatar": {
            "href": "https://msazure.visualstudio.com/_apis/GraphProfile/MemberAvatars/aad.OTgwYzcxNzEtMDI2Ni03YzVmLTk0YzEtMDNlYzU2YjViYjY4"
          }
        },
        "id": "0ef5b3af-3e01-48fd-9bd3-2f701c8fdebe",
        "uniqueName": "dciborow@microsoft.com",
        "imageUrl": "https://msazure.visualstudio.com/_api/_common/identityImage?id=0ef5b3af-3e01-48fd-9bd3-2f701c8fdebe",
        "descriptor": "aad.OTgwYzcxNzEtMDI2Ni03YzVmLTk0YzEtMDNlYzU2YjViYjY4"
      },
      "creationDate": "2023-05-05T03:11:26.8599393Z",
      "title": "title1",
      "description": "description1",
      "sourceRefName": "refs/heads/dciborow/update-pr",
      "targetRefName": "refs/heads/main",
      "mergeStatus": "succeeded",
      "isDraft": false,
      "mergeId": "0e7397c6-5f11-402c-a5c6-c5a12b105350",
      "lastMergeSourceCommit": {
        "commitId": "ecea1ea7db038317e94b45e090781410dc519b85",
        "url": "https://msazure.visualstudio.com/b32aa71e-8ed2-41b2-9d77-5bc261222004/_apis/git/repositories/612d9367-8ab6-4929-abe6-b5b5ad7b5ad3/commits/ecea1ea7db038317e94b45e090781410dc519b85"
      },
      "lastMergeTargetCommit": {
        "commitId": "36f9a015ee220516f5f553faaa1898ab10972536",
        "url": "https://msazure.visualstudio.com/b32aa71e-8ed2-41b2-9d77-5bc261222004/_apis/git/repositories/612d9367-8ab6-4929-abe6-b5b5ad7b5ad3/commits/36f9a015ee220516f5f553faaa1898ab10972536"
      },
      "lastMergeCommit": {
        "commitId": "d5fc735b618647a78a0aff006445b67bfe4e8185",
        "author": {
          "name": "Daniel Ciborowski",
          "email": "dciborow@microsoft.com",
          "date": "2023-05-05T14:23:49Z"
        },
        "committer": {
          "name": "Daniel Ciborowski",
          "email": "dciborow@microsoft.com",
          "date": "2023-05-05T14:23:49Z"
        },
        "comment": "Merge pull request 8063875 from dciborow/update-pr into main",
        "url": "https://msazure.visualstudio.com/b32aa71e-8ed2-41b2-9d77-5bc261222004/_apis/git/repositories/612d9367-8ab6-4929-abe6-b5b5ad7b5ad3/commits/d5fc735b618647a78a0aff006445b67bfe4e8185"
      },
      "reviewers": [],
      "url": "https://msazure.visualstudio.com/b32aa71e-8ed2-41b2-9d77-5bc261222004/_apis/git/repositories/612d9367-8ab6-4929-abe6-b5b5ad7b5ad3/pullRequests/8063875",
      "supportsIterations": true,
      "artifactId": "vstfs:///Git/PullRequestId/b32aa71e-8ed2-41b2-9d77-5bc261222004%2f612d9367-8ab6-4929-abe6-b5b5ad7b5ad3%2f8063875"
    }
  },
  "resourceVersion": "2.0",
  "resourceContainers": {
    "collection": {
      "id": "41bf5486-7392-4b7a-a7e3-a735c767e3b3",
      "baseUrl": "https://msazure.visualstudio.com/"
    },
    "account": {
      "id": "41b4f3ee-c651-4a14-9847-b7cbb5315b80",
      "baseUrl": "https://msazure.visualstudio.com/"
    },
    "project": {
      "id": "b32aa71e-8ed2-41b2-9d77-5bc261222004",
      "baseUrl": "https://msazure.visualstudio.com/"
    }
  },
  "createdDate": "2023-05-12T18:43:41.9219485Z"
}
"""


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
        ) -> MockResponse:
            return MockResponse("mock response")

    def mock_get_core_client(self) -> MockDevOpsClient:
        return MockDevOpsClient()

    monkeypatch.setattr("azure.devops.released.client_factory.ClientFactory.get_core_client", mock_get_core_client)


@pytest.fixture
def devops_client() -> DevOpsClient:
    return DevOpsClient(TOKEN, ORG, PROJECT, REPO)


def test_create_comment(devops_client: DevOpsClient, mock_update_thread) -> None:
    response = devops_client._create_comment(pull_request_id=PR_ID, comment_id=COMMENT_ID, text="text1")
    assert isinstance(response, Comment)


def test_update_pr(devops_client: DevOpsClient, mock_update_thread) -> None:
    response = devops_client._update_pr(pull_request_id=PR_ID, title="title1", description="description1")
    assert isinstance(response, GitPullRequest)


def test_get_diff(devops_client: DevOpsClient, mock_update_thread) -> None:
    response = devops_client._get_commit_diff(
        diff_common_commit=True,
        base_version=GitBaseVersionDescriptor(version=SOURCE, version_type="commit"),
        target_version=GitTargetVersionDescriptor(target_version=TARGET, target_version_type="commit"),
    )
    assert isinstance(response, GitCommitDiffs)


@pytest.mark.integration
def test_create_comment_integration(devops_client: DevOpsClient) -> None:
    response = devops_client._create_comment(pull_request_id=PR_ID, comment_id=141344325, text="text1")
    assert isinstance(response, Comment)


@pytest.mark.integration
def test_update_pr_integration(devops_client: DevOpsClient) -> None:
    response = devops_client._update_pr(PR_ID, "title1", "description1")
    assert isinstance(response, GitPullRequest)


@pytest.mark.integration
def test_get_diff_integration(devops_client: DevOpsClient) -> None:
    response = devops_client._get_commit_diff(
        diff_common_commit=True,
        base_version=GitBaseVersionDescriptor(version=SOURCE, version_type="commit"),
        target_version=GitTargetVersionDescriptor(target_version=TARGET, target_version_type="commit"),
    )
    assert isinstance(response, GitCommitDiffs)
