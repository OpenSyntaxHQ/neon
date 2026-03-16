from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Node:
    line: int
    column: int
    end_line: int
    end_column: int


@dataclass(frozen=True)
class StringNode(Node):
    value: str


@dataclass(frozen=True)
class NumberNode(Node):
    raw: str


@dataclass(frozen=True)
class BoolNode(Node):
    value: bool


@dataclass(frozen=True)
class NullNode(Node):
    pass


@dataclass(frozen=True)
class IdentifierNode(Node):
    name: str


@dataclass(frozen=True)
class ArrayNode(Node):
    items: list[Node]


@dataclass(frozen=True)
class PairNode:
    key: str
    key_line: int
    key_column: int
    value: Node


@dataclass(frozen=True)
class ObjectNode(Node):
    pairs: list[PairNode]


@dataclass(frozen=True)
class TagNode(Node):
    name: str
    args: list[Node]
