"""Discovers and loads challenges from the ``challenges/`` directory.

A challenge is a folder containing:

    problem.json      metadata + function signature + judging options
    description.md    problem statement (Markdown)
    tests.py          SAMPLE list and a hidden(rng) function returning cases
    solutions/        reference solutions, one per language (solution.py, Solution.java, ...)
                      plus an optional README.md explaining the approach
    validator.py      (optional) custom checker: validate(args, expected, actual)
    starters/         (optional) hand-written starter code overriding the generated one

Each test case is a dict: {"args": [...], "expected": <optional>, "name": <optional>}.
If "expected" is omitted it is computed by running the Python reference solution,
so large generated cases only need inputs.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import random
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType

from .types import Type, parse_type

ROOT = Path(__file__).resolve().parent.parent
CHALLENGES_DIR = ROOT / "challenges"
PYTHON_PRELUDE = ROOT / "judge" / "harness" / "python" / "prelude.py"
_codec_spec = importlib.util.spec_from_file_location("codearena_codec", ROOT / "judge" / "harness" / "python" / "codec.py")
codec = importlib.util.module_from_spec(_codec_spec)
_codec_spec.loader.exec_module(codec)


@dataclass
class Param:
    name: str
    type: Type


@dataclass
class Signature:
    method: str
    params: list[Param]
    returns: Type
    output_arg: int | None = None  # for void methods: which argument holds the answer

    @property
    def result_type(self) -> Type:
        if self.output_arg is not None:
            return self.params[self.output_arg].type
        return self.returns


@dataclass
class Challenge:
    id: str
    title: str
    difficulty: str
    tags: list[str]
    category: str
    order: int
    path: Path
    signature: Signature
    compare: str  # exact | unordered | unordered_nested | validator
    time_limit_ms: int
    description: str
    _sample: list[dict] | None = field(default=None, repr=False)
    _hidden: list[dict] | None = field(default=None, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    # ---- modules -------------------------------------------------------
    def _load_module(self, filename: str, name: str, prelude: bool = False) -> ModuleType | None:
        path = self.path / filename
        if not path.exists():
            return None
        spec = importlib.util.spec_from_file_location(f"challenge_{self.id.replace('-', '_')}_{name}", path)
        module = importlib.util.module_from_spec(spec)
        if prelude:
            exec(PYTHON_PRELUDE.read_text(), module.__dict__)
        spec.loader.exec_module(module)
        return module

    @property
    def validator(self):
        mod = self._load_module("validator.py", "validator")
        return getattr(mod, "validate", None) if mod else None

    def reference_callable(self):
        """Returns a function(args) -> result using the Python reference solution."""
        mod = self._load_module("solutions/solution.py", "reference", prelude=True)
        sig = self.signature

        types = [str(p.type) for p in sig.params]
        ns = vars(mod)

        def call(args):
            args = [codec.decode(a, t, ns) for a, t in zip(copy.deepcopy(args), types)]
            result = getattr(mod.Solution(), sig.method)(*args)
            output = args[sig.output_arg] if sig.output_arg is not None else result
            return codec.encode(output, str(sig.result_type))

        return call

    # ---- tests ---------------------------------------------------------
    def _materialize(self, cases: list[dict]) -> list[dict]:
        ref = None
        out = []
        for c in cases:
            c = dict(c)
            if "expected" not in c:
                if ref is None:
                    ref = self.reference_callable()
                c["expected"] = ref(c["args"])
            out.append(c)
        return out

    def _ensure_tests(self) -> None:
        with self._lock:
            if self._sample is not None:
                return
            mod = self._load_module("tests.py", "tests")
            old_limit = sys.getrecursionlimit()
            sys.setrecursionlimit(max(old_limit, 100_000))
            try:
                self._sample = self._materialize(list(mod.SAMPLE))
                rng = random.Random(self.id)
                self._hidden = self._materialize(list(mod.hidden(rng)))
            finally:
                sys.setrecursionlimit(old_limit)

    @property
    def sample_tests(self) -> list[dict]:
        self._ensure_tests()
        return self._sample

    @property
    def all_tests(self) -> list[dict]:
        self._ensure_tests()
        return self._sample + self._hidden

    # ---- files ---------------------------------------------------------
    def solution_code(self, filename: str) -> str | None:
        p = self.path / "solutions" / filename
        return p.read_text() if p.exists() else None

    def solution_explanation(self) -> str:
        p = self.path / "solutions" / "README.md"
        return p.read_text() if p.exists() else ""

    def starter_override(self, filename: str) -> str | None:
        p = self.path / "starters" / filename
        return p.read_text() if p.exists() else None


def _load_challenge(path: Path) -> Challenge:
    meta = json.loads((path / "problem.json").read_text())
    sig = meta["signature"]
    signature = Signature(
        method=sig["method"],
        params=[Param(p["name"], parse_type(p["type"])) for p in sig["params"]],
        returns=parse_type(sig.get("returns", "void")),
        output_arg=sig.get("output_arg"),
    )
    return Challenge(
        id=path.name,
        title=meta["title"],
        difficulty=meta.get("difficulty", "Easy"),
        tags=meta.get("tags", []),
        category=meta.get("category") or (meta.get("tags") or ["Other"])[0],
        order=meta.get("order", 1000),
        path=path,
        signature=signature,
        compare=meta.get("compare", "exact"),
        time_limit_ms=meta.get("time_limit_ms", 2000),
        description=(path / "description.md").read_text(),
    )


_registry: dict[str, Challenge] = {}


def load_all() -> dict[str, Challenge]:
    _registry.clear()
    found = []
    for p in sorted(CHALLENGES_DIR.iterdir()):
        if (p / "problem.json").exists():
            found.append(_load_challenge(p))
    for c in sorted(found, key=lambda c: (c.order, c.title)):
        _registry[c.id] = c
    return _registry


def get(challenge_id: str) -> Challenge | None:
    if not _registry:
        load_all()
    return _registry.get(challenge_id)


def all_challenges() -> list[Challenge]:
    if not _registry:
        load_all()
    return list(_registry.values())
