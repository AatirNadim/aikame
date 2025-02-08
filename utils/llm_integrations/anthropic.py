import anthropic
from utils.constants import Constants
import click


# give the system instruction to the model
# attach the chat history to the model at the beginning of every chat session

class ClaudeModel:
  def __init__(self):
    self.client = anthropic.Client(api_key=Constants.anthropic_api_key)
    self.model = Constants.anthropic_model

  def invoke(self, query: str, chat_history: list[Constants.MessageInstance],  local_context) -> str:

    if isinstance(local_context, list):
      context_text = "\n".join(local_context)
    else:
      context_text = local_context

    history_for_context = f"System instructions:\n{Constants.prompt_template}Chat history:\n"
    for message in chat_history:
      history_for_context += f"{message.role}: {message.content}\n"

    prompt = f"{context_text}\n\User: {query}\n\nAssistant:"

    # Request a streaming completion from the Claude model.
    response_stream = self.client.completions.create(
        model=self.model,
        prompt=prompt,
        max_tokens_to_sample=1024,
        stream=True
    )

    response = ""
    for chunk in response_stream:
      # Each chunk is expected to be a dict with a 'completion' key.
      click.echo(chunk["completion"], nl=False)
      response += chunk["completion"]

    return response
