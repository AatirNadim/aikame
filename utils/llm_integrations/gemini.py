import google.generativeai as genai
from utils.constants import Constants
import click


class GeminiPlugin:
  def __init__(self):
    api_key = Constants.gemini_api_key
    if api_key is None:
      raise ValueError("API key for Gemini not found.")
    genai.configure(api_key=Constants.gemini_api_key)
    self.model = genai.GenerativeModel('gemini-2.0-flash')
    self.chat_session = None

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

  def invoke(self, query: str, chat_history: list[str], context: str) -> str:
    try:
      if self.chat_session is None:
        click.secho(
          "No previos chat session, starting new session..", fg="yellow")
        self.start_chat(chat_history)
      message = ""

      if context:
        message += f"Context:\n{context}\n\n"
        click.secho("Context added to the message", fg="yellow")
      message += f"Question: {query}"

      response = self.chat_session.send_message(message)
      return response.text
    except Exception as e:
      raise e
