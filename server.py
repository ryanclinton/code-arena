#!/usr/bin/env python3
"""CodeArena: a local LeetCode-style practice server.

    python3 server.py [--port 8000]

No third-party dependencies; Java support needs a JDK (java + javac) on PATH.
"""

from __future__ import annotations

import argparse
import errno
import json
import sys
import mimetypes
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from judge import challenges, runner, storage
from judge.languages import all_languages, get_language

STATIC = Path(__file__).resolve().parent / "static"
MAX_BODY = 2 * 1024 * 1024


def language_list():
    out = []
    for lang in all_languages():
        ok, msg = lang.available()
        out.append({"id": lang.id, "name": lang.name, "monaco": lang.monaco_language,
                    "available": ok, "message": msg})
    return out


def challenge_summary(c):
    return {"id": c.id, "title": c.title, "difficulty": c.difficulty, "category": c.category, "tags": c.tags}


def challenge_detail(c):
    sig = c.signature
    starters = {}
    for lang in all_languages():
        starters[lang.id] = c.starter_override(lang.solution_filename) or lang.starter_code(sig)
    return {
        **challenge_summary(c),
        "description": c.description,
        "params": [{"name": p.name, "type": str(p.type)} for p in sig.params],
        "returns": str(sig.returns),
        "starters": starters,
        "samples": [{"args": [json.dumps(a) for a in t["args"]], "expected": json.dumps(t["expected"])}
                    for t in c.sample_tests],
        "test_count": len(c.all_tests),
        "time_limit_ms": c.time_limit_ms,
        "solution_languages": [l.id for l in all_languages() if c.solution_code(l.solution_filename)],
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "CodeArena/1.0"

    def log_message(self, fmt, *args):
        if not self.path.startswith("/static"):
            super().log_message(fmt, *args)

    def _json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status, msg):
        self._json({"error": msg}, status)

    def _static(self, rel: str):
        path = (STATIC / rel).resolve()
        if not path.is_file() or STATIC not in path.parents:
            return self._error(404, "Not found")
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        parts = [p for p in url.path.split("/") if p]
        try:
            if not parts:
                return self._static("index.html")
            if parts[0] in ("favicon.ico", "apple-touch-icon.png", "apple-touch-icon-precomposed.png"):
                return self._static("icon.svg")
            if parts[0] == "static":
                return self._static("/".join(parts[1:]))
            if parts[:2] == ["api", "languages"]:
                return self._json(language_list())
            if parts[:2] == ["api", "progress"]:
                return self._json({"progress": storage.progress()})
            if parts[:2] == ["api", "problems"]:
                if len(parts) == 2:
                    return self._json([challenge_summary(c) for c in challenges.all_challenges()])
                c = challenges.get(parts[2])
                if not c:
                    return self._error(404, "Unknown problem")
                if len(parts) == 3:
                    return self._json(challenge_detail(c))
                if parts[3] == "workspace":
                    return self._json(storage.workspace(c.id))
                if parts[3] == "solution":
                    lang = get_language(parse_qs(url.query).get("lang", ["python"])[0])
                    if not lang:
                        return self._error(400, "Unknown language")
                    return self._json({"language": lang.id, "code": c.solution_code(lang.solution_filename),
                                       "explanation": c.solution_explanation()})
            return self._error(404, "Not found")
        except Exception:
            traceback.print_exc()
            return self._error(500, "Server error")

    def do_POST(self):
        parts = [p for p in urlparse(self.path).path.split("/") if p]
        length = int(self.headers.get("Content-Length", 0))
        if length > MAX_BODY:
            return self._error(413, "Request too large")
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
            if parts == ["api", "run"]:
                return self._run(body)
            if parts == ["api", "import"]:
                return self._json({"imported": storage.import_browser_data(body)})
            if len(parts) == 4 and parts[:2] == ["api", "problems"] and parts[3] in ("code", "cases"):
                c = challenges.get(parts[2])
                if not c:
                    return self._error(404, "Unknown problem")
                if parts[3] == "code":
                    if not get_language(body["language"]):
                        return self._error(400, "Unknown language")
                    storage.save_code(c.id, body["language"], body.get("code"))
                else:
                    storage.save_cases(c.id, body.get("cases"))
                return self._json({"saved": True})
            return self._error(404, "Not found")
        except (KeyError, TypeError, json.JSONDecodeError):
            return self._error(400, "Malformed request")
        except Exception as e:
            traceback.print_exc()
            return self._error(500, f"Server error: {e}")

    def _run(self, body):
        try:
            c = challenges.get(body["problem_id"])
            lang = get_language(body["language"])
            if not c or not lang:
                return self._error(400, "Unknown problem or language")
            ok, msg = lang.available()
            if not ok:
                return self._error(400, f"{lang.name} is not available: {msg}")
            mode = body.get("mode", "test")
            if mode not in ("test", "submit"):
                return self._error(400, "mode must be 'test' or 'submit'")
            code = body.get("code", "")
            storage.save_code(c.id, lang.id, code)  # running or submitting also saves your code
            result = runner.run(c, lang, code, mode, body.get("custom_tests"))
            if mode == "submit":
                result["submission_id"] = storage.add_submission(c.id, lang.id, code, result)
            return self._json(result)
        except (KeyError, json.JSONDecodeError):
            return self._error(400, "Malformed request")
        except Exception as e:
            traceback.print_exc()
            return self._error(500, f"Judge error: {e}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    try:
        httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            sys.exit(f"Port {args.port} is already in use (is CodeArena already running?). "
                     f"Stop the other process or pick another port: --port {args.port + 1}")
        raise
    loaded = challenges.load_all()
    print(f"Loaded {len(loaded)} challenges; languages: "
          + ", ".join(f"{l['name']}{'' if l['available'] else ' (unavailable)'}" for l in language_list()))
    print(f"CodeArena running at http://{args.host}:{args.port}  (Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
