import google.generativeai as genai
from utils.constants import Constants


class GeminiPlugin:
  def __init__(self):
    genai.configure(api_key=Constants.gemini_api_key)
    self.model = genai.GenerativeModel('gemini-1.5-flash')

  def invoke(self, query: str, chat_history: str, context: str) -> str:
    try:
      messages = [
          {"role": "system", "content": Constants.prompt_template},
          {"role": "user", "content": (
              f"Chat history:\n{chat_history}\n"
              f"Context:\n{context}\n\n"
              f"Question: {query}\n"
          )}
      ]
      response = self.model.generate_content(
        
      )
      return response["choices"][0]["message"]["content"]
    except Exception as e:
      raise e
