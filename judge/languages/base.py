"""Base class for language plugins.

To add a language, create ``judge/languages/<name>.py`` with a subclass of
``Language`` decorated with ``@register``, and a harness that:

  1. reads a job file (JSON) with keys:
       method, param_types, return_type, output_arg, tests (list of arg lists)
  2. loads the user's ``Solution`` class, and for each test converts the JSON
     args to native values, calls the method on a fresh instance, and times it
  3. appends one JSON line per test to the results file:
       {"i": n, "status": "ok", "output": ..., "time_ns": ..., "stdout": "..."}
       {"i": n, "status": "error", "error": "...", "stdout": "..."}
     or a single {"fatal": "..."} line if the solution cannot be loaded.

The judge handles everything else: process limits, timing, memory, grading.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from ..challenges import Signature
from ..types import Type


@dataclass
class PrepareResult:
    ok: bool
    error: str = ""


class Language:
    id: str = ""
    name: str = ""
    monaco_language: str = ""  # editor syntax mode
    solution_filename: str = ""  # file name for user code and reference solutions
    time_multiplier: float = 1.0  # time-limit scaling relative to the problem's base limit
    executables: tuple[str, ...] = ()

    def available(self) -> tuple[bool, str]:
        missing = [e for e in self.executables if shutil.which(e) is None]
        if missing:
            return False, f"Missing executable(s): {', '.join(missing)}"
        return True, ""

    # ---- code generation ----------------------------------------------
    def type_name(self, t: Type) -> str:
        raise NotImplementedError

    def starter_code(self, sig: Signature) -> str:
        raise NotImplementedError

    # ---- execution ----------------------------------------------------
    def prepare(self, workdir: Path, code: str) -> PrepareResult:
        """Write the user's code into workdir and compile it if needed."""
        raise NotImplementedError

    def run_command(self, workdir: Path, job_path: Path, results_path: Path) -> list[str]:
        """Command that runs the harness against the prepared code."""
        raise NotImplementedError


_REGISTRY: dict[str, Language] = {}


def register(cls):
    inst = cls()
    _REGISTRY[inst.id] = inst
    return cls


def registry() -> dict[str, Language]:
    return _REGISTRY
