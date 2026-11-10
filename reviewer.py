import os
import subprocess
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SYSTEM_PROMPT = """You are a senior software engineer doing a code review.
Review the git diff you are given. Only comment on lines that were added or changed.
For each problem you find, give:
- File and line
- Severity: bug, security, or style
- What is wrong
- How to fix it
If the diff has no problems, say so. Do not invent problems."""


def get_diff() -> str:
    """Return the uncommitted changes in the current git repository."""
    result = subprocess.run(
        ["git", "diff"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        sys.exit(f"git diff failed: {result.stderr}")
    return result.stdout


def review(diff: str) -> str:
    client = OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )
    response = client.chat.completions.create(
        model=os.environ["MODEL"],
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Review this diff:\n\n{diff}"},
        ],
    )
    print(f"[tokens] input={response.usage.prompt_tokens} "
          f"output={response.usage.completion_tokens}\n")
    return response.choices[0].message.content


def main():
    diff = get_diff()
    if not diff.strip():
        print("No changes to review.")
        return
    print(review(diff))


if __name__ == "__main__":
    main()