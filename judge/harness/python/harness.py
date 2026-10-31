"""Python test harness. Usage: harness.py <solution.py> <job.json> <results.jsonl>"""

import contextlib
import importlib.util
import io
import json
import os
import sys
import threading
import time
import traceback

MAX_STDOUT = 10_000

HERE = os.path.dirname(os.path.abspath(__file__))
PRELUDE = os.path.join(HERE, "prelude.py")
_spec = importlib.util.spec_from_file_location("codec", os.path.join(HERE, "codec.py"))
codec = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(codec)


def user_traceback(exc):
    frames = [f for f in traceback.extract_tb(exc.__traceback__)
              if not f.filename.endswith(("harness.py", "codec.py"))]
    message = "".join(traceback.format_exception_only(type(exc), exc))
    if not frames:  # raised by the harness itself, e.g. a cycle in a returned list
        return message
    return "Traceback (most recent call last):\n" + "".join(traceback.format_list(frames)) + message


def main():
    solution_path, job_path, results_path = sys.argv[1:4]
    with open(job_path) as f:
        job = json.load(f)
    out = open(results_path, "w")

    def emit(obj):
        out.write(json.dumps(obj) + "\n")
        out.flush()

    namespace = {"__name__": "solution"}
    try:
        with open(PRELUDE) as f:
            exec(f.read(), namespace)
        with open(solution_path) as f:
            code = compile(f.read(), "solution.py", "exec")
        exec(code, namespace)
        solution_cls = namespace["Solution"]
        getattr(solution_cls, job["method"])
    except Exception:
        emit({"fatal": traceback.format_exc()})
        return

    method = job["method"]
    output_arg = job.get("output_arg")
    param_types = job["param_types"]
    result_type = param_types[output_arg] if output_arg is not None else job["return_type"]
    for i, raw in enumerate(job["tests"]):
        buf = io.StringIO()
        try:
            args = [codec.decode(a, t, namespace) for a, t in zip(raw, param_types)]
            fn = getattr(solution_cls(), method)
            with contextlib.redirect_stdout(buf):
                start = time.perf_counter_ns()
                result = fn(*args)
                elapsed = time.perf_counter_ns() - start
            output = args[output_arg] if output_arg is not None else result
            emit({"i": i, "status": "ok", "output": codec.encode(output, result_type), "time_ns": elapsed,
                  "stdout": buf.getvalue()[:MAX_STDOUT]})
        except RecursionError:
            emit({"i": i, "status": "error", "error": "RecursionError: maximum recursion depth exceeded",
                  "stdout": buf.getvalue()[:MAX_STDOUT]})
        except Exception as e:
            emit({"i": i, "status": "error", "error": user_traceback(e),
                  "stdout": buf.getvalue()[:MAX_STDOUT]})
    out.close()


if __name__ == "__main__":
    sys.setrecursionlimit(1_000_000)
    threading.stack_size(512 * 1024 * 1024)
    t = threading.Thread(target=main)
    t.start()
    t.join()
