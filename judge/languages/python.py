from __future__ import annotations

import sys
import traceback
from pathlib import Path

from ..challenges import Signature
from ..types import Type
from .base import Language, PrepareResult, register

HARNESS = Path(__file__).resolve().parent.parent / "harness" / "python" / "harness.py"

_SCALARS = {
    "int": "int", "long": "int", "double": "float", "boolean": "bool",
    "string": "str", "char": "str", "void": "None",
    "ListNode": "Optional[ListNode]", "TreeNode": "Optional[TreeNode]",
}

# Shown above the starter code; the classes themselves come from prelude.py.
_NODE_DOCS = {
    "ListNode": ("# Definition for singly-linked list (provided, no need to define it).\n"
                 "# class ListNode:\n"
                 "#     def __init__(self, val=0, next=None):\n"
                 "#         self.val = val\n"
                 "#         self.next = next\n"),
    "TreeNode": ("# Definition for a binary tree node (provided, no need to define it).\n"
                 "# class TreeNode:\n"
                 "#     def __init__(self, val=0, left=None, right=None):\n"
                 "#         self.val = val\n"
                 "#         self.left = left\n"
                 "#         self.right = right\n"),
}


@register
class Python(Language):
    id = "python"
    name = "Python 3"
    monaco_language = "python"
    solution_filename = "solution.py"
    time_multiplier = 4.0

    def available(self):
        return True, ""  # the judge itself runs on Python

    def type_name(self, t: Type) -> str:
        if t.kind == "scalar":
            return _SCALARS[t.name]
        return f"List[{self.type_name(t.inner)}]"

    def starter_code(self, sig: Signature) -> str:
        params = ", ".join(f"{p.name}: {self.type_name(p.type)}" for p in sig.params)
        ret = self.type_name(sig.returns)
        body = "        pass\n"
        if sig.output_arg is not None:
            body = f"        \"\"\"\n        Do not return anything, modify {sig.params[sig.output_arg].name} in-place instead.\n        \"\"\"\n        pass\n"
        used = set().union(sig.returns.names(), *(p.type.names() for p in sig.params))
        docs = "".join(_NODE_DOCS[n] + "\n" for n in sorted(used) if n in _NODE_DOCS)
        return (
            docs +
            "class Solution:\n"
            f"    def {sig.method}(self, {params}) -> {ret}:\n"
            f"{body}"
        )

    def prepare(self, workdir: Path, code: str) -> PrepareResult:
        (workdir / self.solution_filename).write_text(code)
        try:
            compile(code, self.solution_filename, "exec")
        except SyntaxError:
            return PrepareResult(False, traceback.format_exc(limit=0))
        return PrepareResult(True)

    def run_command(self, workdir: Path, job_path: Path, results_path: Path) -> list[str]:
        return [sys.executable, "-I", str(HARNESS), str(workdir / self.solution_filename),
                str(job_path), str(results_path)]
