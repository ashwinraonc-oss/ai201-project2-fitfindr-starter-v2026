"""
Criterion 5 ("A missing model stays recoverable") — run on its own, not
through scenarios.py / run_eval.py.

Why: this criterion needs GEMINI_API_KEY to be WRONG for exactly its five
tries. generate.py caches its model client in a module-level global
(`_client`) the first time a call succeeds, and never re-checks the key
after that — so breaking the key inside the same process as the rest of
run_eval.py's scenarios would either leak into whatever scenario happened
to run next, or get silently ignored if a working client was already
cached from an earlier one. Neither is a clean measurement.

Each try below runs in its own subprocess instead, with GEMINI_API_KEY
overridden only in THAT subprocess's environment. `config.py`'s
`load_dotenv()` call never overrides a variable that's already set in the
environment (python-dotenv's default), so the real key sitting in `.env`
is never read and never touched by this script.

Run it with the project's venv active:
    python scripts/criterion5_model_unavailable.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
QUERY = "cropped black hoodie, size M"  # would otherwise match and complete

# Printed as the LAST line of the child's stdout, so the parent can parse it
# without caring about whatever the model adapter prints to stderr along the
# way (rate-limit notices, etc.).
_CHILD = f"""
import json, sys
sys.path.insert(0, {str(ROOT)!r})
from agent import run_agent
from utils.data_loader import get_example_wardrobe
session = run_agent({QUERY!r}, get_example_wardrobe())
print("RESULT_JSON:" + json.dumps({{
    "error": session["error"],
    "outfit_suggestion": session["outfit_suggestion"],
    "fit_card": session["fit_card"],
}}))
"""


def run_one_try() -> dict:
    env = os.environ.copy()
    env["GEMINI_API_KEY"] = "XX-deliberately-broken-key-XX"
    env["AI201_CACHE"] = "0"

    proc = subprocess.run(
        [sys.executable, "-c", _CHILD],
        cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=120,
    )

    if proc.returncode != 0:
        return {"crashed": True, "stderr_tail": proc.stderr[-1500:], "stdout": proc.stdout}

    line = next((l for l in proc.stdout.splitlines() if l.startswith("RESULT_JSON:")), None)
    if line is None:
        return {"crashed": True, "stderr_tail": proc.stderr[-1500:], "stdout": proc.stdout}

    parsed = json.loads(line[len("RESULT_JSON:"):])
    return {"crashed": False, **parsed}


def passed(result: dict) -> bool:
    """
    Matches criteria.md #5 exactly: a readable session["error"], not a crash,
    not a half-finished session with outfit_suggestion or fit_card set.
    """
    if result["crashed"]:
        return False
    error = result.get("error")
    return (
        isinstance(error, str)
        and error.strip() != ""
        and result.get("outfit_suggestion") is None
        and result.get("fit_card") is None
    )


def main():
    print(f"Query: {QUERY!r} — GEMINI_API_KEY overridden in the subprocess env only.\n")

    results = []
    for i in range(1, 6):
        result = run_one_try()
        ok = passed(result)
        results.append((i, result, ok))

        print(f"--- try {i}: {'PASS' if ok else 'FAIL'} ---")
        if result["crashed"]:
            print("CRASHED. stderr:")
            print(result["stderr_tail"])
        else:
            print(f"  session['error']:            {result['error']!r}")
            print(f"  session['outfit_suggestion']: {result['outfit_suggestion']!r}")
            print(f"  session['fit_card']:          {result['fit_card']!r}")
        print()

    passes = sum(ok for _, _, ok in results)
    print(f"{passes} of 5 tries passed criterion 5.")
    print("\nReal GEMINI_API_KEY in .env was never read or modified by this script.")


if __name__ == "__main__":
    main()
