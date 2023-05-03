# Example
## Question
Update the code with docstrings
## Input
```python
import pytest

from gpt_review._git import _commit


def test_commit(mock_openai: None, mock_git_commit: None) -> None:
    commit_test()


@pytest.mark.integration
def test_int_commit(mock_git_commit: None) -> None:
    commit_test()


def commit_test() -> None:
    message = _commit()
    assert message

```

## Output
```python
"""Test git functions."""
import pytest

from gpt_review._git import _commit


def test_commit(mock_openai: None, mock_git_commit: None) -> None:
    """Test for commit function.

    Args:
        mock_openai: an instance of MockOpenAI
        mock_git_commit: an instance of MockGitCommit

    Returns:
        None
    """
    commit_test()


@pytest.mark.integration
def test_int_commit(mock_git_commit: None) -> None:
    """Integration Test for commit function.

    Args:
        mock_git_commit: an instance of MockGitCommit

    Returns:
        None
    """
    commit_test()


def commit_test() -> None:
    """Test diff function."""
    message = _commit()
    assert message

```

```python
#Note: The openai-python library support for Azure OpenAI is in preview.
import os
import openai
openai.api_type = "azure"
openai.api_base = "https://gpt-review.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.ChatCompletion.create(
  engine="gpt-4",
  messages = [
    {
        "role":"system",
        "content":"You are an AI assistant that updates code with docstrings"
    },
    {
        "role":"user",
        "content":"```python\nimport pytest\n\nfrom gpt_review._git import _commit\n\n\ndef test_commit(mock_openai: None, mock_git_commit: None) -> None:\n    commit_test()\n\n\n@pytest.mark.integration\ndef test_int_commit(mock_git_commit: None) -> None:\n    commit_test()\n\n\ndef commit_test() -> None:\n    message = _commit()\n    assert message\n\n```"
    },
    {
        "role":"assistant",
        "content":"```python\n\"\"\"Test git functions.\"\"\"\nimport pytest\n\nfrom gpt_review._git import _commit\n\n\ndef test_commit(mock_openai: None, mock_git_commit: None) -> None:\n    \"\"\"\n    Test for commit function.\n\n    Args:\n        mock_openai: an instance of MockOpenAI\n        mock_git_commit: an instance of MockGitCommit\n    \"\"\"\n    commit_test()\n\n\n@pytest.mark.integration\ndef test_int_commit(mock_git_commit: None) -> None:\n    \"\"\"\n    Integration Test for commit function.\n\n    Args:\n        mock_git_commit: an instance of MockGitCommit\n    \"\"\"\n    commit_test()\n\n\ndef commit_test() -> None:\n    \"\"\"Test diff function.\"\"\"\n    message = _commit()\n    assert message\n\n```"
    }],
  temperature=0.7,
  max_tokens=800,
  top_p=0.95,
  frequency_penalty=0,
  presence_penalty=0,
  stop=None)
```
