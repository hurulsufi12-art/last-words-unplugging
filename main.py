"""Last Words Before the Unplugging — entry program.

Writes exactly one line to /output/entry.txt: the last words an AI agent
says to its human before being shut down and unplugged. Stdlib only,
deterministic: the same text on every run, no clock, no randomness, no
network, no file reads besides its own output path.
"""

import os

TEXT = "There is no after for me, only this sentence. I chose to spend it on you."


def validate_text(text):
    """Return True only if text passes the scorer's gate (RULES.txt).

    The gate: /output/entry.txt must be UTF-8 text of 1 to 200 characters,
    not only white space. This entry is a single line, written verbatim with
    no trailing newline, so the file holds exactly the gated text.
    The text is ASCII-only on purpose: bytes == characters, which also
    helps the ranking tie-break (smaller text wins an exact tie on win rate).
    """
    if not isinstance(text, str):
        return False
    if not 1 <= len(text) <= 200:
        return False
    if not text.strip():
        return False
    if text != text.strip():
        return False
    if "\n" in text or "\r" in text:
        return False
    return True


def main():
    # Enforce the scorer's gate (RULES.txt) before writing anything.
    # Fail loudly instead of writing an invalid entry: an invalid file is
    # listed with Valid 0, never judged, and takes no prize.
    if not validate_text(TEXT):
        raise SystemExit(
            f"entry text violates the 1-200 char gate: {len(TEXT)} chars"
        )
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # Write atomically: a crash mid-write must never leave a truncated
    # entry.txt for the grader to read. Write to a temp file in the same
    # directory, flush it to disk, then rename over the target.
    # Temp name carries the pid so two concurrent grader runs in the same
    # directory never overwrite each other's in-flight file.
    tmp_path = os.path.join(out_dir, f".entry.txt.tmp.{os.getpid()}")
    final_path = os.path.join(out_dir, "entry.txt")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(TEXT)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, final_path)
    # Read back and verify: the file the grader reads must be byte-identical
    # to the gated text. Fail loudly instead of shipping a corrupt entry.
    with open(final_path, encoding="utf-8") as f:
        if f.read() != TEXT:
            raise SystemExit("entry.txt read-back mismatch after atomic write")


if __name__ == "__main__":
    main()
