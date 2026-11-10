import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL="openai/gpt-oss-120b"

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

response = client.chat.completions.create(
    model=MODEL,
    temperature=0,
    messages=[
        {"role": "user", "content": "Explain what an API is in 3 sentence."}
    ]
)

print(response.choices[0].message.content)
print("\nInput tokens:", response.usage.prompt_tokens)
print("Output tokens:", response.usage.completion_tokens)