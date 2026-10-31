"""Runs user code against a challenge's tests and produces a verdict."""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

from . import compare
from .challenges import Challenge
from .languages import Language

DISPLAY_LIMIT = 2000
STARTUP_ALLOWANCE_S = 3.0

ACCEPTED = "Accepted"
WRONG = "Wrong Answer"
RUNTIME = "Runtime Error"
COMPILE = "Compile Error"
TLE = "Time Limit Exceeded"
INVALID = "Invalid Input"

_reference_stats: dict[tuple[str, str], dict] = {}
_reference_lock = threading.Lock()


def _display(value) -> str:
    text = json.dumps(value, separators=(",", ":"))
    if len(text) > DISPLAY_LIMIT:
        return text[:DISPLAY_LIMIT] + f"… ({len(text):,} chars total)"
    return text


def _execute(cmd: list[str], cwd: Path, timeout_s: float) -> dict:
    """Run a process, enforcing a wall-clock timeout and measuring peak memory."""
    stdout_path, stderr_path = cwd / "_stdout.txt", cwd / "_stderr.txt"
    with open(stdout_path, "wb") as so, open(stderr_path, "wb") as se:
        proc = subprocess.Popen(cmd, cwd=cwd, stdout=so, stderr=se, stdin=subprocess.DEVNULL,
                                start_new_session=True)
    timed_out = threading.Event()

    def kill():
        timed_out.set()
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    timer = threading.Timer(timeout_s, kill)
    start = time.perf_counter()
    timer.start()
    _, status, usage = os.wait4(proc.pid, 0)
    timer.cancel()
    wall = time.perf_counter() - start
    proc.returncode = os.waitstatus_to_exitcode(status)
    # ru_maxrss is bytes on macOS, kilobytes on Linux
    maxrss_kb = usage.ru_maxrss // 1024 if sys.platform == "darwin" else usage.ru_maxrss
    return {
        "returncode": proc.returncode,
        "timed_out": timed_out.is_set(),
        "wall_ms": wall * 1000,
        "memory_kb": maxrss_kb,
        "stderr": stderr_path.read_text(errors="replace")[-5000:],
    }


def _read_results(path: Path) -> tuple[list[dict], str | None]:
    results, fatal = [], None
    if not path.exists():
        return results, fatal
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            break  # partially written line from a killed process
        if "fatal" in obj:
            fatal = obj["fatal"]
        else:
            results.append(obj)
    return results, fatal


def _build_cases(challenge: Challenge, mode: str, custom: list | None) -> list[dict]:
    if mode == "submit":
        return challenge.all_tests
    if custom is None:
        return challenge.sample_tests
    ref = challenge.reference_callable()
    cases = []
    for args in custom:
        if not isinstance(args, list) or len(args) != len(challenge.signature.params):
            raise ValueError(f"Each test case needs {len(challenge.signature.params)} argument(s).")
        try:
            expected = ref(args)
        except Exception as e:  # reference crashed => input is outside the problem's constraints
            raise ValueError(f"Reference solution rejected this input ({type(e).__name__}: {e}). "
                             "Check that it matches the problem constraints.")
        cases.append({"args": args, "expected": expected})
    return cases


def run(challenge: Challenge, lang: Language, code: str, mode: str,
        custom_tests: list | None = None, with_reference: bool = True) -> dict:
    sig = challenge.signature
    try:
        cases = _build_cases(challenge, mode, custom_tests)
    except ValueError as e:
        return {"verdict": INVALID, "mode": mode, "error": str(e)}

    limit_ms = challenge.time_limit_ms * lang.time_multiplier
    workdir = Path(tempfile.mkdtemp(prefix="codearena-run-"))
    try:
        prep = lang.prepare(workdir, code)
        if not prep.ok:
            return {"verdict": COMPILE, "mode": mode, "error": prep.error}

        job_path, results_path = workdir / "_job.json", workdir / "_results.jsonl"
        job_path.write_text(json.dumps({
            "method": sig.method,
            "param_types": [str(p.type) for p in sig.params],
            "return_type": str(sig.returns),
            "output_arg": sig.output_arg,
            "tests": [c["args"] for c in cases],
        }))
        proc = _execute(lang.run_command(workdir, job_path, results_path), workdir,
                        timeout_s=limit_ms / 1000 + STARTUP_ALLOWANCE_S)
        results, fatal = _read_results(results_path)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    if fatal:
        return {"verdict": RUNTIME, "mode": mode, "error": fatal}

    validator = challenge.validator if challenge.compare == "validator" else None
    names = [p.name for p in sig.params]
    graded = []
    verdict = ACCEPTED
    error = None
    total_ns = 0
    for i, case in enumerate(cases):
        entry = {
            "index": i,
            "name": case.get("name"),
            "input": [{"name": n, "value": _display(v)} for n, v in zip(names, case["args"])],
            "expected": _display(case["expected"]),
        }
        res = results[i] if i < len(results) else None
        if res is None:
            if proc["timed_out"]:
                entry.update(passed=False, error="Time limit exceeded on this test.")
                case_verdict = TLE
            else:
                tail = proc["stderr"].strip() or f"Process exited with code {proc['returncode']}"
                entry.update(passed=False, error=tail)
                case_verdict = RUNTIME
        elif res["status"] == "error":
            entry.update(passed=False, error=res["error"], stdout=res.get("stdout", ""))
            case_verdict = RUNTIME
        else:
            total_ns += res["time_ns"]
            ok, msg = compare.check(challenge.compare, case["args"], case["expected"], res["output"], validator)
            entry.update(passed=ok, output=_display(res["output"]), stdout=res.get("stdout", ""),
                         time_ms=round(res["time_ns"] / 1e6, 3), message=msg)
            case_verdict = ACCEPTED if ok else WRONG
        graded.append(entry)
        if case_verdict != ACCEPTED and verdict == ACCEPTED:
            verdict = case_verdict
            error = entry.get("error")
            if mode == "submit":
                break

    runtime_ms = total_ns / 1e6
    if verdict == ACCEPTED and mode == "submit" and runtime_ms > limit_ms:
        verdict = TLE
        error = f"Total runtime {runtime_ms:.0f} ms exceeded the {limit_ms:.0f} ms limit."

    passed = sum(1 for g in graded if g["passed"])
    result = {
        "verdict": verdict,
        "mode": mode,
        "language": lang.id,
        "passed": passed,
        "total": len(cases),
        "runtime_ms": round(runtime_ms, 2),
        "memory_kb": proc["memory_kb"],
        "wall_ms": round(proc["wall_ms"]),
        "time_limit_ms": limit_ms,
        "error": error,
    }
    if mode == "test":
        result["cases"] = graded
    else:
        failing = [g for g in graded if not g["passed"]]
        result["failed_case"] = failing[0] if failing else None
        if verdict == ACCEPTED:
            result["slowest_ms"] = max((g.get("time_ms", 0) for g in graded), default=0)
            if with_reference:
                result["reference"] = reference_stats(challenge, lang)
    return result


def reference_stats(challenge: Challenge, lang: Language) -> dict | None:
    """Runtime/memory of the reference solution in this language (cached)."""
    key = (challenge.id, lang.id)
    with _reference_lock:
        if key in _reference_stats:
            return _reference_stats[key]
    code = challenge.solution_code(lang.solution_filename)
    if code is None:
        return None
    res = run(challenge, lang, code, "submit", with_reference=False)
    stats = None
    if res["verdict"] == ACCEPTED:
        stats = {"runtime_ms": res["runtime_ms"], "memory_kb": res["memory_kb"]}
    with _reference_lock:
        _reference_stats[key] = stats
    return stats
