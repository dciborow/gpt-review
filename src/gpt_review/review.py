from gpt_review._ask import _ask


class Reviewer:
  """Definition of GPT-Review Public Interfaces"""
  def ask(self, prompt: ModelPrompt, params: ModelParams=None, indexes: ModelIndexes=None) -> ModelResponse:
    """Ask a GPT a prompt"""
    _ask(**prompt.asInput(), **params.asInput(), **indexes.asInput())
