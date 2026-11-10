import argparse
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_git_diff() -> str:
    """Return the uncommitted changes in the current git repository."""
    result = subprocess.run(
        ["git", "diff"], capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        sys.exit(f"git diff failed: {result.stderr}")
    return result.stdout


def review(diff: str, system_prompt: str) -> str:
    client = OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )
    response = client.chat.completions.create(
        model=os.environ["MODEL"],
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"<diff>\n{diff}\n</diff>"},
        ],
    )
    print(f"[tokens] input={response.usage.prompt_tokens} "
          f"output={response.usage.completion_tokens}\n")
    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="AI code reviewer")
    parser.add_argument("--prompt", default="prompts/v2_strict.md",
                        help="Path to the system prompt file")
    parser.add_argument("--diff-file",
                        help="Review a saved diff instead of current changes")
    args = parser.parse_args()

    system_prompt = Path(args.prompt).read_text(encoding="utf-8")
    if args.diff_file:
        diff = Path(args.diff_file).read_text(encoding="utf-8")
    else:
        diff = get_git_diff()

    if not diff.strip():
        print("No changes to review.")
        return
    print(review(diff, system_prompt))



if __name__ == "__main__":
    main()