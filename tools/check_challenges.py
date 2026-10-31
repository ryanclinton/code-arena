#!/usr/bin/env python3
"""Validate challenges by submitting every reference solution through the real judge.

    python3 tools/check_challenges.py               # all challenges, all languages
    python3 tools/check_challenges.py two-sum       # one challenge
    python3 tools/check_challenges.py -l java       # one language
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from judge import challenges, runner  # noqa: E402
from judge.languages import all_languages  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", help="challenge ids (folder names)")
    ap.add_argument("-l", "--language", action="append", help="language id(s) to check")
    args = ap.parse_args()

    challenges.load_all()
    targets = [challenges.get(i) for i in args.ids] if args.ids else challenges.all_challenges()
    if None in targets:
        sys.exit(f"Unknown challenge id. Available: {', '.join(c.id for c in challenges.all_challenges())}")
    langs = [l for l in all_languages() if not args.language or l.id in args.language]

    failures = 0
    for c in targets:
        print(f"{c.id}: {len(c.sample_tests)} sample / {len(c.all_tests)} total tests")
        for lang in langs:
            ok, msg = lang.available()
            code = c.solution_code(lang.solution_filename)
            if not ok or code is None:
                print(f"  {lang.id:8} skipped ({msg or 'no reference solution'})")
                continue
            res = runner.run(c, lang, code, "submit", with_reference=False)
            good = res["verdict"] == runner.ACCEPTED
            failures += not good
            detail = (f"{res['passed']}/{res['total']}  {res['runtime_ms']:.1f} ms  "
                      f"{res['memory_kb'] / 1024:.1f} MB") if "passed" in res else ""
            print(f"  {lang.id:8} {'OK  ' if good else 'FAIL'} {res['verdict']:22} {detail}")
            if not good:
                print("    " + str(res.get("error") or res.get("failed_case")).replace("\n", "\n    "))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
