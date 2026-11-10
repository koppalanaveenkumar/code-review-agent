import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL="openai/gpt-oss-120b"
PROMPT = "Suggest a name for a code review AI tool. Reply with just the name."

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)


for temp in [0, 1]:
    print(f"\n--- temperature = {temp} ---")
    for i in range(3):
        response = client.chat.completions.create(
            model=MODEL,
            temperature=temp,
            messages=[{"role": "user", "content": PROMPT}]
        )
        print(f"Run {i + 1}: {response.choices[0].message.content.strip()}")
