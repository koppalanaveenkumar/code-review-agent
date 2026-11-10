import argparse
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from diff_utils import number_diff
from models import ReviewResult

load_dotenv()

MAX_ATTEMPTS = 2


def get_git_diff() -> str:
    """Return the uncommitted changes in the current git repository."""
    result = subprocess.run(
        ["git", "diff"], capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        sys.exit(f"git diff failed: {result.stderr}")
    return result.stdout


def call_llm(client: OpenAI, messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model=os.environ["MODEL"],
        temperature=0,
        messages=messages,
        response_format={"type": "json_object"},
    )
    usage = response.usage
    print(f"[tokens] input={usage.prompt_tokens} output={usage.completion_tokens}",
          file=sys.stderr)
    return response.choices[0].message.content


def review(diff: str, system_prompt: str) -> ReviewResult:
    client = OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"<diff>\n{number_diff(diff)}\n</diff>"},
    ]

    for attempt in range(1, MAX_ATTEMPTS + 1):
        raw = call_llm(client, messages)
        try:
            return ReviewResult.model_validate_json(raw)
        except ValidationError as error:
            print(f"[attempt {attempt}] output failed validation, retrying...",
                  file=sys.stderr)
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": f"Your JSON did not match the required shape:\n{error}\n"
                           "Return the corrected JSON only.",
            })

    sys.exit("The model did not return valid JSON after retrying.")


def print_result(result: ReviewResult) -> None:
    if not result.comments:
        print("LGTM — no issues found.")
        return
    for c in result.comments:
        print(f"[{c.severity.upper()}] {c.file}:{c.line} — {c.problem}")
        print(f"    Example: {c.example}")
        print(f"    Fix: {c.fix}\n")


def main():
    parser = argparse.ArgumentParser(description="AI code reviewer")
    parser.add_argument("--prompt", default="prompts/v3_json.md",
                        help="Path to the system prompt file")
    parser.add_argument("--diff-file",
                        help="Review a saved diff instead of current changes")
    parser.add_argument("--json", action="store_true",
                        help="Print the raw JSON result")
    args = parser.parse_args()

    system_prompt = Path(args.prompt).read_text(encoding="utf-8")
    diff = (Path(args.diff_file).read_text(encoding="utf-8")
            if args.diff_file else get_git_diff())

    if not diff.strip():
        print("No changes to review.")
        return

    result = review(diff, system_prompt)
    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        print_result(result)


if __name__ == "__main__":
    main()