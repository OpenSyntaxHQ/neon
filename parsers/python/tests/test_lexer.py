from __future__ import annotations

import pytest

from neon.errors import LexError
from neon.lexer import tokenize


def test_tokenize_basic_with_comments() -> None:
    text = '{"a": 1, // comment\n "b": true}'
    tokens = tokenize(text)
    kinds = [t.kind for t in tokens]
    assert "LBRACE" in kinds
    assert "STRING" in kinds
    assert "NUMBER" in kinds
    assert kinds[-1] == "EOF"


def test_unterminated_string_raises() -> None:
    with pytest.raises(LexError) as exc:
        tokenize('{"a": "x}')
    assert exc.value.code == "E_LEX_UNTERMINATED_STRING"


def test_leading_zero_number_raises() -> None:
    with pytest.raises(LexError) as exc:
        tokenize('{"a": 01}')
    assert exc.value.code == "E_LEX_INVALID_NUMBER"
