import google.generativeai as genai
from utils.constants import Constants
from google.generativeai.types import generation_types
import click
import os


class GeminiPlugin:
  def __init__(self):
    genai.configure(api_key=Constants.gemini_api_key)
    self.model = genai.GenerativeModel(
      'gemini-2.0-flash', system_instruction=Constants.prompt_template)
    self.chat_session = None
    os.environ["GRPC_VERBOSITY"] = "ERROR"
    os.environ["GLOG_minloglevel"] = "2"

  def start_chat(self, chat_history: list[dict] = None):
    if chat_history is None:
      chat_history = []

    history = []
    for message in chat_history:
      history.append({
          "role": message["role"],
          "parts": [{"text": message["content"]}]
      })

    self.chat_session = self.model.start_chat(history=history)

  def invoke(self, query: str, chat_history: list[str], context: str) -> generation_types.GenerateContentResponse:
    try:
      if Constants.gemini_api_key is None:
        raise ValueError("Gemini API key is not set")
      if self.chat_session is None:
        # click.secho(
        #   "No previous chat session, starting new session..", fg="yellow")
        self.start_chat(chat_history)
      message = ""

      if context:
        message += f"Context:\n{context}\n\n"
        click.secho("Context added to the message", fg="yellow")
      message += f"Question: {query}"

      response = self.chat_session.send_message(message, stream=True)
      click.secho("recieved response from llm", fg="green")
      for chunk in response:
        click.echo(chunk.text, nl=False)
      return response.text
    except Exception as e:
      raise e
