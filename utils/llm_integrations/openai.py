from openai import OpenAI
from utils.constants import Constants


class OpenAIPlugin:

  def __init__(self):
    self.ai_client = OpenAI(api_key=Constants.api_key)
    pass

  def invoke(self, query: str, chat_history: str, context: str) -> str:
    try:
      return self.ai_client.chat.completions.create(
      model=Constants.llm_model,
      messages=[{"role": "system", "content": Constants.prompt_template},{"role": "user", "content": f"Chat history:\n{chat_history}\nContext:\n{context}\n\nQuestion: {query}\n"}])
    except Exception as e:
      raise e
