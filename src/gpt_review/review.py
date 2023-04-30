
class Reviewer:
  def ask(self, prompt: ModelPrompt, params: ModelParams=None, indexes: ModelIndexes=None) -> ModelResponse:
    """Ask a GPT a prompt"""
    _ask(**prompt.asInput(), **params.asInput(), **indexes.asInput())
