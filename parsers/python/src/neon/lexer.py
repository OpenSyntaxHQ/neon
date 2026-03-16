from __future__ import annotations

from dataclasses import dataclass

from .errors import LexError


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    column: int
    end_line: int
    end_column: int


_SIMPLE_TOKENS: dict[str, str] = {
    "{": "LBRACE",
    "}": "RBRACE",
    "[": "LBRACKET",
    "]": "RBRACKET",
    ":": "COLON",
    ",": "COMMA",
    "(": "LPAREN",
    ")": "RPAREN",
    "@": "AT",
}


class Lexer:
    def __init__(self, text: str) -> None:
        self.text = text
        self.length = len(text)
        self.index = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while not self._is_eof():
            self._skip_ws_and_comments()
            if self._is_eof():
                break

            ch = self._peek()
            if ch in _SIMPLE_TOKENS:
                tokens.append(self._read_simple())
            elif ch == '"':
                tokens.append(self._read_string())
            elif ch == "-" or ch.isdigit():
                tokens.append(self._read_number())
            elif ch.isalpha() or ch == "_":
                tokens.append(self._read_identifier_or_keyword())
            else:
                raise LexError(
                    "E_LEX_UNEXPECTED_CHAR",
                    f"Unexpected character: {ch}",
                    self.line,
                    self.column,
                )

        tokens.append(Token("EOF", "", self.line, self.column, self.line, self.column))
        return tokens

    def _skip_ws_and_comments(self) -> None:
        while not self._is_eof():
            ch = self._peek()
            if ch in {" ", "\t", "\r", "\n"}:
                self._advance()
                continue
            if ch == "#":
                self._skip_line_comment()
                continue
            if ch == "/":
                nxt = self._peek(1)
                if nxt == "/":
                    self._advance()
                    self._advance()
                    self._skip_line_comment()
                    continue
                if nxt == "*":
                    self._advance()
                    self._advance()
                    self._skip_block_comment()
                    continue
            break

    def _skip_line_comment(self) -> None:
        while not self._is_eof() and self._peek() != "\n":
            self._advance()

    def _skip_block_comment(self) -> None:
        start_line = self.line
        start_col = self.column - 2
        while not self._is_eof():
            if self._peek() == "*" and self._peek(1) == "/":
                self._advance()
                self._advance()
                return
            self._advance()
        raise LexError(
            "E_LEX_UNTERMINATED_COMMENT",
            "Unterminated block comment",
            start_line,
            start_col,
        )

    def _read_simple(self) -> Token:
        ch = self._peek()
        line, col = self.line, self.column
        self._advance()
        return Token(_SIMPLE_TOKENS[ch], ch, line, col, self.line, self.column)

    def _read_string(self) -> Token:
        line, col = self.line, self.column
        self._advance()  # opening quote
        chars: list[str] = []

        while not self._is_eof():
            ch = self._peek()
            if ch == '"':
                self._advance()
                return Token("STRING", "".join(chars), line, col, self.line, self.column)
            if ch == "\\":
                self._advance()
                if self._is_eof():
                    raise LexError("E_LEX_UNTERMINATED_STRING", "Unterminated string", line, col)
                esc = self._peek()
                self._advance()
                if esc == '"':
                    chars.append('"')
                elif esc == "\\":
                    chars.append("\\")
                elif esc == "/":
                    chars.append("/")
                elif esc == "b":
                    chars.append("\b")
                elif esc == "f":
                    chars.append("\f")
                elif esc == "n":
                    chars.append("\n")
                elif esc == "r":
                    chars.append("\r")
                elif esc == "t":
                    chars.append("\t")
                elif esc == "u":
                    chars.append(self._read_unicode_escape(line, col))
                else:
                    raise LexError(
                        "E_LEX_INVALID_ESCAPE",
                        f"Invalid string escape: \\{esc}",
                        self.line,
                        self.column,
                    )
                continue
            if ord(ch) < 0x20:
                if ch in {"\n", "\r"}:
                    raise LexError("E_LEX_UNTERMINATED_STRING", "Unterminated string", line, col)
                raise LexError("E_LEX_INVALID_ESCAPE", "Control character in string", self.line, self.column)
            chars.append(ch)
            self._advance()

        raise LexError("E_LEX_UNTERMINATED_STRING", "Unterminated string", line, col)

    def _read_unicode_escape(self, line: int, col: int) -> str:
        hexdigits: list[str] = []
        for _ in range(4):
            if self._is_eof():
                raise LexError("E_LEX_INVALID_ESCAPE", "Incomplete unicode escape", line, col)
            ch = self._peek()
            if ch not in "0123456789abcdefABCDEF":
                raise LexError("E_LEX_INVALID_ESCAPE", "Invalid unicode escape", self.line, self.column)
            hexdigits.append(ch)
            self._advance()
        return chr(int("".join(hexdigits), 16))

    def _read_number(self) -> Token:
        line, col = self.line, self.column
        start = self.index

        if self._peek() == "-":
            self._advance()
            if self._is_eof() or not self._peek().isdigit():
                raise LexError("E_LEX_INVALID_NUMBER", "Invalid number", line, col)

        if self._peek() == "0":
            self._advance()
            if not self._is_eof() and self._peek().isdigit():
                raise LexError("E_LEX_INVALID_NUMBER", "Leading zeros are not allowed", self.line, self.column)
        else:
            self._consume_digits()

        if not self._is_eof() and self._peek() == ".":
            self._advance()
            if self._is_eof() or not self._peek().isdigit():
                raise LexError("E_LEX_INVALID_NUMBER", "Invalid fraction", self.line, self.column)
            self._consume_digits()

        if not self._is_eof() and self._peek() in {"e", "E"}:
            self._advance()
            if not self._is_eof() and self._peek() in {"+", "-"}:
                self._advance()
            if self._is_eof() or not self._peek().isdigit():
                raise LexError("E_LEX_INVALID_NUMBER", "Invalid exponent", self.line, self.column)
            self._consume_digits()

        raw = self.text[start : self.index]
        return Token("NUMBER", raw, line, col, self.line, self.column)

    def _read_identifier_or_keyword(self) -> Token:
        line, col = self.line, self.column
        start = self.index
        self._advance()
        while not self._is_eof() and (self._peek().isalnum() or self._peek() in {"_", "-"}):
            self._advance()

        value = self.text[start : self.index]
        kind = {
            "true": "TRUE",
            "false": "FALSE",
            "null": "NULL",
        }.get(value, "IDENT")
        return Token(kind, value, line, col, self.line, self.column)

    def _consume_digits(self) -> None:
        while not self._is_eof() and self._peek().isdigit():
            self._advance()

    def _peek(self, offset: int = 0) -> str:
        return self.text[self.index + offset]

    def _advance(self) -> None:
        ch = self.text[self.index]
        self.index += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

    def _is_eof(self) -> bool:
        return self.index >= self.length


def tokenize(text: str) -> list[Token]:
    return Lexer(text).tokenize()
