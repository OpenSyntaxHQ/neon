from __future__ import annotations

from .ast import (
    ArrayNode,
    BoolNode,
    IdentifierNode,
    Node,
    NullNode,
    NumberNode,
    ObjectNode,
    PairNode,
    StringNode,
    TagNode,
)
from .errors import NeonSyntaxError
from .lexer import Token, tokenize


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0

    def parse(self) -> Node:
        node = self._parse_value()
        tok = self._current()
        if tok.kind != "EOF":
            raise NeonSyntaxError(
                "E_SYN_TRAILING_TOKENS",
                "Unexpected trailing tokens",
                tok.line,
                tok.column,
                end_line=tok.end_line,
                end_column=tok.end_column,
            )
        return node

    def _parse_value(self) -> Node:
        tok = self._current()
        if tok.kind == "LBRACE":
            return self._parse_object()
        if tok.kind == "LBRACKET":
            return self._parse_array()
        if tok.kind == "STRING":
            self._advance()
            return StringNode(tok.line, tok.column, tok.end_line, tok.end_column, tok.value)
        if tok.kind == "NUMBER":
            self._advance()
            return NumberNode(tok.line, tok.column, tok.end_line, tok.end_column, tok.value)
        if tok.kind == "TRUE":
            self._advance()
            return BoolNode(tok.line, tok.column, tok.end_line, tok.end_column, True)
        if tok.kind == "FALSE":
            self._advance()
            return BoolNode(tok.line, tok.column, tok.end_line, tok.end_column, False)
        if tok.kind == "NULL":
            self._advance()
            return NullNode(tok.line, tok.column, tok.end_line, tok.end_column)
        if tok.kind == "AT":
            return self._parse_tag()
        if tok.kind == "IDENT":
            self._advance()
            return IdentifierNode(tok.line, tok.column, tok.end_line, tok.end_column, tok.value)

        raise NeonSyntaxError(
            "E_SYN_EXPECTED_VALUE",
            f"Expected a value, got {tok.kind}",
            tok.line,
            tok.column,
            end_line=tok.end_line,
            end_column=tok.end_column,
        )

    def _parse_object(self) -> ObjectNode:
        start = self._expect("LBRACE")
        pairs: list[PairNode] = []

        if self._current().kind == "RBRACE":
            end = self._expect("RBRACE")
            return ObjectNode(start.line, start.column, end.end_line, end.end_column, pairs)

        while True:
            key_tok = self._current()
            if key_tok.kind not in {"STRING", "IDENT"}:
                raise NeonSyntaxError(
                    "E_SYN_EXPECTED_TOKEN",
                    f"Expected object key, got {key_tok.kind}",
                    key_tok.line,
                    key_tok.column,
                    end_line=key_tok.end_line,
                    end_column=key_tok.end_column,
                )
            self._advance()
            key = key_tok.value

            self._expect("COLON")
            value = self._parse_value()
            pairs.append(PairNode(key=key, key_line=key_tok.line, key_column=key_tok.column, value=value))

            tok = self._current()
            if tok.kind == "COMMA":
                self._advance()
                if self._current().kind == "RBRACE":
                    end = self._expect("RBRACE")
                    return ObjectNode(start.line, start.column, end.end_line, end.end_column, pairs)
                continue
            if tok.kind == "RBRACE":
                end = self._expect("RBRACE")
                return ObjectNode(start.line, start.column, end.end_line, end.end_column, pairs)

            raise NeonSyntaxError(
                "E_SYN_EXPECTED_TOKEN",
                f"Expected ',' or '}}', got {tok.kind}",
                tok.line,
                tok.column,
                end_line=tok.end_line,
                end_column=tok.end_column,
            )

    def _parse_array(self) -> ArrayNode:
        start = self._expect("LBRACKET")
        items: list[Node] = []

        if self._current().kind == "RBRACKET":
            end = self._expect("RBRACKET")
            return ArrayNode(start.line, start.column, end.end_line, end.end_column, items)

        while True:
            items.append(self._parse_value())
            tok = self._current()
            if tok.kind == "COMMA":
                self._advance()
                if self._current().kind == "RBRACKET":
                    end = self._expect("RBRACKET")
                    return ArrayNode(start.line, start.column, end.end_line, end.end_column, items)
                continue
            if tok.kind == "RBRACKET":
                end = self._expect("RBRACKET")
                return ArrayNode(start.line, start.column, end.end_line, end.end_column, items)
            raise NeonSyntaxError(
                "E_SYN_EXPECTED_TOKEN",
                f"Expected ',' or ']', got {tok.kind}",
                tok.line,
                tok.column,
                end_line=tok.end_line,
                end_column=tok.end_column,
            )

    def _parse_tag(self) -> TagNode:
        at_tok = self._expect("AT")
        name_tok = self._expect("IDENT")
        self._expect("LPAREN")

        args: list[Node] = []
        if self._current().kind != "RPAREN":
            while True:
                args.append(self._parse_value())
                tok = self._current()
                if tok.kind == "COMMA":
                    self._advance()
                    continue
                if tok.kind == "RPAREN":
                    break
                raise NeonSyntaxError(
                    "E_SYN_EXPECTED_TOKEN",
                    f"Expected ',' or ')', got {tok.kind}",
                    tok.line,
                    tok.column,
                    end_line=tok.end_line,
                    end_column=tok.end_column,
                )

        end = self._expect("RPAREN")
        return TagNode(at_tok.line, at_tok.column, end.end_line, end.end_column, name_tok.value, args)

    def _expect(self, kind: str) -> Token:
        tok = self._current()
        if tok.kind != kind:
            raise NeonSyntaxError(
                "E_SYN_EXPECTED_TOKEN",
                f"Expected {kind}, got {tok.kind}",
                tok.line,
                tok.column,
                end_line=tok.end_line,
                end_column=tok.end_column,
            )
        self._advance()
        return tok

    def _current(self) -> Token:
        return self.tokens[self.index]

    def _advance(self) -> None:
        self.index += 1


def parse_text(text: str) -> Node:
    return Parser(tokenize(text)).parse()
