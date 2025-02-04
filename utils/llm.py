import openai
from .constants import Constants


def get_response(augmented_query: str) -> str:
  try:
    response = openai.chat.completions.create(
      model = Constants.llm_model,
      messages=[{
        'role': 'system',
        # TODO: determine whether the formatting is working correctly
        'content': Constants.prompt_template.format(context=augmented_query, question="What is the answer to this question?")
                        },
      {
        'role': "user"
        'content':
                        }

                        ]
                )
  except Exception as e:
    return str(e)
