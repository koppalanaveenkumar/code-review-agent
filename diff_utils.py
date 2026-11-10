import re
import sys
from pathlib import Path

HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def number_diff(diff: str) -> str:
    """Prefix each added and context line with its line number in the new file.

    Removed lines get no number, because they no longer exist in the new file.
    """
    output = []
    new_line = 0
    in_hunk = False

    for line in diff.splitlines():
        if line.startswith("diff --git"):
            in_hunk = False
            output.append(line)
            continue

        match = HUNK_HEADER.match(line)
        if match:
            in_hunk = True
            new_line = int(match.group(1))
            output.append(line)
            continue

        if not in_hunk or line.startswith("\\"):
            # File headers (---, +++, index) and "\ No newline at end of file"
            output.append(line)
        elif line.startswith("+"):
            output.append(f"{new_line:>4} + {line[1:]}")
            new_line += 1
        elif line.startswith("-"):
            output.append(f"     - {line[1:]}")
        else:
            output.append(f"{new_line:>4}   {line[1:]}")
            new_line += 1

    return "\n".join(output)


if __name__ == "__main__":
    print(number_diff(Path(sys.argv[1]).read_text(encoding="utf-8")))
    