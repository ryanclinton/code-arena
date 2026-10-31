"""Language-neutral type grammar used in challenge signatures.

Scalar types:  int, long, double, boolean, string, char, void
Node types:    ListNode (JSON [1,2,3]), TreeNode (level order, JSON [1,null,2])
Array types:   T[]          e.g. int[], string[], int[][]
List types:    list<T>      e.g. list<int>, list<list<string>>

Language plugins translate these into their own type names (see
``Language.type_name``), so a challenge is written once and works in every
language.
"""

from __future__ import annotations

from dataclasses import dataclass

NODE_TYPES = {"ListNode", "TreeNode"}
SCALARS = {"int", "long", "double", "boolean", "string", "char", "void"} | NODE_TYPES


@dataclass(frozen=True)
class Type:
    kind: str  # "scalar" | "array" | "list"
    name: str = ""  # scalar name when kind == "scalar"
    inner: "Type | None" = None  # element type for array/list

    def __str__(self) -> str:
        if self.kind == "scalar":
            return self.name
        if self.kind == "array":
            return f"{self.inner}[]"
        return f"list<{self.inner}>"

    def names(self) -> set[str]:
        """Every scalar or node name used in this type."""
        return {self.name} if self.kind == "scalar" else self.inner.names()

    @property
    def is_float(self) -> bool:
        if self.kind == "scalar":
            return self.name == "double"
        return self.inner.is_float


def parse_type(text: str) -> Type:
    text = text.strip()
    if text.endswith("[]"):
        return Type("array", inner=parse_type(text[:-2]))
    if text.startswith("list<") and text.endswith(">"):
        return Type("list", inner=parse_type(text[5:-1]))
    if text in SCALARS:
        return Type("scalar", name=text)
    raise ValueError(f"Unknown type: {text!r}")
