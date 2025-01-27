import openai
from .constants import llm_model, prompt_template, api_key





def get_response(augmented_query: str) -> str:
  try:
    response = openai.chat.completions.create(
      model = llm_model,
      messages=[{
        'role': 'system',
        # TODO: determine whether the formatting is working correctly
        'content': prompt_template.format(context=augmented_query, question="What is the answer to this question?")
			},
      {
        'role': "user"
        'content': 
			}

			]
		)


