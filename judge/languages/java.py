from __future__ import annotations

import subprocess
import tempfile
import threading
from pathlib import Path

from ..challenges import Signature
from ..types import Type
from .base import Language, PrepareResult, register

HARNESS_SRC = Path(__file__).resolve().parent.parent / "harness" / "java"

_PRIMITIVES = {
    "int": "int", "long": "long", "double": "double", "boolean": "boolean",
    "char": "char", "string": "String", "void": "void", "ListNode": "ListNode", "TreeNode": "TreeNode",
}
_BOXED = {
    "int": "Integer", "long": "Long", "double": "Double", "boolean": "Boolean",
    "char": "Character", "string": "String", "ListNode": "ListNode", "TreeNode": "TreeNode",
}

# Shown above the starter code; the classes themselves are compiled with the harness.
_NODE_DOCS = {
    "ListNode": ("/**\n"
                 " * Definition for singly-linked list (provided, do not redefine it).\n"
                 " * public class ListNode {\n"
                 " *     int val;\n"
                 " *     ListNode next;\n"
                 " *     ListNode() {}\n"
                 " *     ListNode(int val) { this.val = val; }\n"
                 " *     ListNode(int val, ListNode next) { this.val = val; this.next = next; }\n"
                 " * }\n"
                 " */\n"),
    "TreeNode": ("/**\n"
                 " * Definition for a binary tree node (provided, do not redefine it).\n"
                 " * public class TreeNode {\n"
                 " *     int val;\n"
                 " *     TreeNode left;\n"
                 " *     TreeNode right;\n"
                 " *     TreeNode() {}\n"
                 " *     TreeNode(int val) { this.val = val; }\n"
                 " *     TreeNode(int val, TreeNode left, TreeNode right) {\n"
                 " *         this.val = val;\n"
                 " *         this.left = left;\n"
                 " *         this.right = right;\n"
                 " *     }\n"
                 " * }\n"
                 " */\n"),
}


@register
class Java(Language):
    id = "java"
    name = "Java"
    monaco_language = "java"
    solution_filename = "Solution.java"
    time_multiplier = 1.0
    executables = ("java", "javac")

    def __init__(self):
        self._harness_dir: Path | None = None
        self._lock = threading.Lock()

    def type_name(self, t: Type, boxed: bool = False) -> str:
        if t.kind == "scalar":
            return (_BOXED if boxed else _PRIMITIVES)[t.name]
        if t.kind == "array":
            return f"{self.type_name(t.inner)}[]"
        return f"List<{self.type_name(t.inner, boxed=True)}>"

    def starter_code(self, sig: Signature) -> str:
        params = ", ".join(f"{self.type_name(p.type)} {p.name}" for p in sig.params)
        ret = self.type_name(sig.returns)
        comment = ""
        if sig.output_arg is not None:
            comment = f"        // Do not return anything, modify {sig.params[sig.output_arg].name} in-place instead.\n"
        used = set().union(sig.returns.names(), *(p.type.names() for p in sig.params))
        docs = "".join(_NODE_DOCS[n] for n in sorted(used) if n in _NODE_DOCS)
        return (
            "import java.util.*;\n\n"
            + docs +
            "class Solution {\n"
            f"    public {ret} {sig.method}({params}) {{\n"
            f"{comment}"
            "        \n"
            "    }\n"
            "}\n"
        )

    def _harness(self) -> Path:
        """Compile the harness once per server process and reuse it."""
        with self._lock:
            if self._harness_dir is None:
                out = Path(tempfile.mkdtemp(prefix="codearena-java-harness-"))
                srcs = [str(p) for p in HARNESS_SRC.glob("*.java")]
                # Main loads Solution reflectively, so it compiles without it.
                subprocess.run(["javac", "-encoding", "UTF-8", "-d", str(out), *srcs],
                               check=True, capture_output=True, text=True)
                self._harness_dir = out
            return self._harness_dir

    def prepare(self, workdir: Path, code: str) -> PrepareResult:
        harness = self._harness()
        src = workdir / self.solution_filename
        src.write_text(code)
        proc = subprocess.run(
            ["javac", "-g", "-encoding", "UTF-8", "-cp", str(harness), "-d", str(workdir), self.solution_filename],
            cwd=workdir, capture_output=True, text=True, timeout=30,
        )
        if proc.returncode != 0:
            return PrepareResult(False, (proc.stderr or proc.stdout).strip())
        return PrepareResult(True)

    def run_command(self, workdir: Path, job_path: Path, results_path: Path) -> list[str]:
        cp = f"{workdir}:{self._harness()}"
        return ["java", "-Xmx1g", "-XX:+UseSerialGC", "-cp", cp, "Main", str(job_path), str(results_path)]
