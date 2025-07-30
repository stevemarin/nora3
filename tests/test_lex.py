import os

from nora3 import TEST_DIR
from nora3.lex import InvalidCharacter, InvalidNumber, Lexer


def test_at_sign() -> None:
    path = os.path.join(TEST_DIR, "chapter_1", "invalid_lex", "at_sign.c")
    with open(path, "r") as fh:
        src = fh.read()

    try:
        _ = Lexer(src).lex()
        assert False, "didn't fail successfully"
    except InvalidCharacter as e:
        assert (e.value, e.line, e.offset) == ("@", 4, 13)


def test_backslash() -> None:
    path = os.path.join(TEST_DIR, "chapter_1", "invalid_lex", "backslash.c")
    with open(path, "r") as fh:
        src = fh.read()

    try:
        _ = Lexer(src).lex()
        assert False, "didn't fail successfully"
    except InvalidCharacter as e:
        assert (e.value, e.line, e.offset) == ("\\", 2, 1)


def test_backtick() -> None:
    path = os.path.join(TEST_DIR, "chapter_1", "invalid_lex", "backtick.c")
    with open(path, "r") as fh:
        src = fh.read()

    try:
        _ = Lexer(src).lex()
        assert False, "didn't fail successfully"
    except InvalidCharacter as e:
        assert (e.value, e.line, e.offset) == ("`", 2, 1)


def test_invalid_identifier() -> None:
    path = os.path.join(TEST_DIR, "chapter_1", "invalid_lex", "invalid_identifier.c")
    with open(path, "r") as fh:
        src = fh.read()

    try:
        _ = Lexer(src).lex()
        assert False, "didn't fail successfully"
    except InvalidNumber as e:
        assert (e.value, e.line, e.offset) == ("1foo", 3, 15)


def test_invalid_identifier_2() -> None:
    path = os.path.join(TEST_DIR, "chapter_1", "invalid_lex", "invalid_identifier_2.c")
    with open(path, "r") as fh:
        src = fh.read()

    try:
        _ = Lexer(src).lex()
        assert False, "didn't fail successfully"
    except InvalidCharacter as e:
        assert (e.value, e.line, e.offset) == ("@", 3, 12)

def test_bad_label() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_lex", "extra_credit", "bad_label.c")
    with open(path, "r") as fh:
        src = fh.read()

    try:
        _ = Lexer(src).lex()
        assert False, "didn't fail successfully"
    except InvalidNumber as e:
        assert str(e) == "invalid number '0invalid_label' @ 2:18"

