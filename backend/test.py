from openai import OpenAI
from backend.settings import OPENAI_API_KEY
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.jiekou.ai/openai"
)

response = client.chat.completions.create(
    model="gpt-5.1",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ],
    max_completion_tokens=4096,
    # temperature=0.7
)

print(response.choices[0].message.content)