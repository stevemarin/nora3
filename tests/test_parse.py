import os

from nora3 import TEST_DIR
from nora3.lex import Lexer
from nora3.parse import ParserEofError, TokenTypeError, ParserError, Parser


def test_end_before_expr() -> None:
    path = os.path.join(TEST_DIR, "chapter_1", "invalid_parse", "end_before_expr.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserEofError as e:
        assert str(e) == "unexpected EOF found in factor function"


def test_extra_junk() -> None:
    path = os.path.join(TEST_DIR, "chapter_1", "invalid_parse", "extra_junk.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "invalid types: [] @ 6:3"
    # except TokenTypeError as e:
    #     assert str(e) == "expected Int, got Identifier(foo) @ 6:3"


def test_invalid_function_name() -> None:
    path = os.path.join(TEST_DIR, "chapter_1", "invalid_parse", "invalid_function_name.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Identifier, got LiteralInt(3) @ 2:5"


def test_keyword_wrong_case() -> None:
    path = os.path.join(TEST_DIR, "chapter_1", "invalid_parse", "keyword_wrong_case.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got LiteralInt(0) @ 2:12"


def test_missing_type() -> None:
    path = os.path.join(TEST_DIR, "chapter_1", "invalid_parse", "missing_type.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "invalid types: [] @ 5:4"
    # except TokenTypeError as e:
    #     assert str(e) == "expected Int, got Identifier(main) @ 5:4"


def test_misspelled_keyword() -> None:
    path = os.path.join(TEST_DIR, "chapter_1", "invalid_parse", "misspelled_keyword.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got LiteralInt(0) @ 2:13"


def test_no_semicolon() -> None:
    path = os.path.join(TEST_DIR, "chapter_1", "invalid_parse", "no_semicolon.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got RightBrace() @ 3:1"


def test_not_expression() -> None:
    path = os.path.join(TEST_DIR, "chapter_1", "invalid_parse", "not_expression.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Int() @ 2:11"


def test_space_in_keyword() -> None:
    path = os.path.join(TEST_DIR, "chapter_1", "invalid_parse", "space_in_keyword.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got Identifier(n) @ 2:11"


def test_switched_parens() -> None:
    path = os.path.join(TEST_DIR, "chapter_1", "invalid_parse", "switched_parens.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon or Equal, got RightParen() @ 1:10"


def test_unclosed_brace() -> None:
    path = os.path.join(TEST_DIR, "chapter_1", "invalid_parse", "unclosed_brace.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserEofError as e:
        assert str(e) == "unexpected EOF found in func_decl function"


def test_unclosed_paren() -> None:
    path = os.path.join(TEST_DIR, "chapter_1", "invalid_parse", "unclosed_paren.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Int, got LeftBrace() @ 1:11"


def test_extra_paren() -> None:
    path = os.path.join(TEST_DIR, "chapter_2", "invalid_parse", "extra_paren.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got RightParen() @ 3:15"


def test_missing_const() -> None:
    path = os.path.join(TEST_DIR, "chapter_2", "invalid_parse", "missing_const.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Semicolon() @ 2:12"


def test_missing_semicolon() -> None:
    path = os.path.join(TEST_DIR, "chapter_2", "invalid_parse", "missing_semicolon.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got RightBrace() @ 3:1"


def test_nested_missing_const() -> None:
    path = os.path.join(TEST_DIR, "chapter_2", "invalid_parse", "nested_missing_const.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Semicolon() @ 3:13"


def test_parenthesize_operand() -> None:
    path = os.path.join(TEST_DIR, "chapter_2", "invalid_parse", "parenthesize_operand.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found RightParen() @ 2:13"


def test_unclosed_paren_2() -> None:
    path = os.path.join(TEST_DIR, "chapter_2", "invalid_parse", "unclosed_paren.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected RightParen, got Semicolon() @ 3:14"


def test_wrong_order() -> None:
    path = os.path.join(TEST_DIR, "chapter_2", "invalid_parse", "wrong_order.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Semicolon() @ 2:13"


def test_double_operation() -> None:
    path = os.path.join(TEST_DIR, "chapter_3", "invalid_parse", "double_operation.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found ForwardSlash() @ 2:15"


def test_imbalanced_paren() -> None:
    path = os.path.join(TEST_DIR, "chapter_3", "invalid_parse", "imbalanced_paren.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected RightParen, got Semicolon() @ 2:18"


def test_malformed_paren() -> None:
    path = os.path.join(TEST_DIR, "chapter_3", "invalid_parse", "malformed_paren.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got LeftParen() @ 2:14"


def test_misplaced_semicolon() -> None:
    path = os.path.join(TEST_DIR, "chapter_3", "invalid_parse", "misplaced_semicolon.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected RightParen, got Semicolon() @ 2:18"


def test_missing_first_op() -> None:
    path = os.path.join(TEST_DIR, "chapter_3", "invalid_parse", "missing_first_op.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found ForwardSlash() @ 2:11"


def test_missing_open_paren() -> None:
    path = os.path.join(TEST_DIR, "chapter_3", "invalid_parse", "missing_open_paren.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got RightParen() @ 2:17"


def test_missing_second_op() -> None:
    path = os.path.join(TEST_DIR, "chapter_3", "invalid_parse", "missing_second_op.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Semicolon() @ 2:15"


def test_no_semicolon_2() -> None:
    path = os.path.join(TEST_DIR, "chapter_3", "invalid_parse", "no_semicolon.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got RightBrace() @ 3:1"


def test_bitwise_double_operator() -> None:
    path = os.path.join(TEST_DIR, "chapter_3", "invalid_parse", "extra_credit", "bitwise_double_operator.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Bar() @ 4:15"


def test_missing_const_2() -> None:
    path = os.path.join(TEST_DIR, "chapter_4", "invalid_parse", "missing_const.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Semicolon() @ 3:11"


def test_missing_first_op_2() -> None:
    path = os.path.join(TEST_DIR, "chapter_4", "invalid_parse", "missing_first_op.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found LessEqual() @ 2:11"


def test_missing_operand() -> None:
    path = os.path.join(TEST_DIR, "chapter_4", "invalid_parse", "missing_operand.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Greater() @ 2:15"


def test_missing_second_op_2() -> None:
    path = os.path.join(TEST_DIR, "chapter_4", "invalid_parse", "missing_second_op.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Semicolon() @ 2:17"


def test_missing_semicolon_2() -> None:
    path = os.path.join(TEST_DIR, "chapter_4", "invalid_parse", "missing_semicolon.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got RightBrace() @ 3:1"


def test_unary_missing_semicolon() -> None:
    path = os.path.join(TEST_DIR, "chapter_4", "invalid_parse", "unary_missing_semicolon.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got RightBrace() @ 4:1"


def test_compound_invalid_operator() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_parse", "compound_invalid_operator.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Equal() @ 6:8"


def test_declare_keyword_as_var() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_parse", "declare_keyword_as_var.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Identifier, got Return() @ 2:14"


def test_invalid_specifier() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_parse", "invalid_specifier.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon or Equal, got Identifier(bar) @ 2:15"


def test_invalid_type() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_parse", "invalid_type.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got Identifier(a) @ 2:10"


def test_invalid_variable_name() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_parse", "invalid_variable_name.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Identifier, got LiteralInt(10) @ 3:10"


def test_malformed_compound_assignment() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_parse", "malformed_compound_assignment.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found ForwardSlash() @ 7:7"


def test_malformed_decrement() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_parse", "malformed_decrement.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Semicolon() @ 6:9"


def test_malformed_increment() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_parse", "malformed_increment.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Plus() @ 6:8"


def test_malformed_less_equal() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_parse", "malformed_less_equal.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Equal() @ 6:15"


def test_malformed_not_equal() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_parse", "malformed_not_equal.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got Bang() @ 6:14"


def test_missing_semicolon_3() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_parse", "missing_semicolon.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got Identifier(a) @ 3:5"


def test_return_in_assignment() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_parse", "return_in_assignment.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Identifier, got LiteralInt(10) @ 3:10"


def test_binary_decrement() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_parse", "extra_credit", "binary_decrement.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got LiteralInt(1) @ 3:17"


def test_binary_increment() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_parse", "extra_credit", "binary_increment.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got LiteralInt(1) @ 3:17"


def test_compound_initializer() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_parse", "extra_credit", "compound_initializer.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon or Equal, got PlusEqual() @ 2:12"


def test_increment_declaration() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_parse", "extra_credit", "increment_declaration.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon or Equal, got PlusPlus() @ 2:11"


def test_declaration_as_statement() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_parse", "declaration_as_statement.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Int() @ 3:8"


def test_empty_if_body() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_parse", "empty_if_body.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Else() @ 2:11"


def test_if_assignment() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_parse", "if_assignment.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found If() @ 3:12"


def test_if_no_parenst() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_parse", "if_no_parens.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected LeftParen, got LiteralInt(0) @ 2:8"


def test_incomplete_ternary() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_parse", "incomplete_ternary.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Colon, got Semicolon() @ 2:17"


def test_malformed_ternary_2() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_parse", "malformed_ternary_2.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Colon, got Semicolon() @ 2:25"


def test_malformed_ternary() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_parse", "malformed_ternary.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got Colon() @ 2:22"


def test_mismatched_nesting() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_parse", "mismatched_nesting.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Else() @ 7:4"


def test_wrong_ternary_delimiter() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_parse", "wrong_ternary_delimiter.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Colon, got Semicolon() @ 5:21"


def test_goto_without_label() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_parse", "extra_credit", "goto_without_label.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Identifier, got Semicolon() @ 2:9"


def test_kw_label() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_parse", "extra_credit", "kw_label.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Colon() @ 2:10"


# def test_label_declaration() -> None:
#     path = os.path.join(TEST_DIR, "chapter_6", "invalid_parse", "extra_credit", "label_declaration.c")
#     with open(path, "r") as fh:
#         src = fh.read()
#     tokens = Lexer(src).lex()

#     try:
#         _ = Parser(tokens).parse()
#         assert False, "didn't fail successfully"
#     except TokenTypeError as e:
#         assert str(e) == "expected Identifier, got Semicolon() @ 2:9"


def test_label_expression_clause() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_parse", "extra_credit", "label_expression_clause.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got Colon() @ 2:15"


def test_label_outside_function() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_parse", "extra_credit", "label_outside_function.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "invalid types: [] @ 1:5"
    # except TokenTypeError as e:
    #     assert str(e) == "expected Int, got Identifier(label) @ 1:5"


# def test_label_without_statement() -> None:
#     path = os.path.join(TEST_DIR, "chapter_6", "invalid_parse", "extra_credit", "label_without_statement.c")
#     with open(path, "r") as fh:
#         src = fh.read()
#     tokens = Lexer(src).lex()


#     try:
#         _ = Parser(tokens).parse()
#         assert False, "didn't fail successfully"
#     except TokenTypeError as e:
#         assert str(e) == "expected Int, got Identifier(label) @ 1:5"


def test_parenthesized_label() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_parse", "extra_credit", "parenthesized_label.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Identifier, got LeftParen() @ 2:9"


def test_extra_brace() -> None:
    path = os.path.join(TEST_DIR, "chapter_7", "invalid_parse", "extra_brace.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "invalid types: [] @ 5:10"
    # except TokenTypeError as e:
    #     assert str(e) == "expected Int, got Return() @ 5:10"


def test_missing_brace() -> None:
    path = os.path.join(TEST_DIR, "chapter_7", "invalid_parse", "missing_brace.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserEofError as e:
        assert str(e) == "unexpected EOF found in stmt function"


def test_missing_semicolon_4() -> None:
    path = os.path.join(TEST_DIR, "chapter_7", "invalid_parse", "missing_semicolon.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got RightBrace() @ 6:5"


def test_ternary_blocks() -> None:
    path = os.path.join(TEST_DIR, "chapter_7", "invalid_parse", "ternary_blocks.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found LeftBrace() @ 3:15"


def test_decl_as_loop_body() -> None:
    path = os.path.join(TEST_DIR, "chapter_8", "invalid_parse", "decl_as_loop_body.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Int() @ 3:8"


def test_do_extra_semicolon() -> None:
    path = os.path.join(TEST_DIR, "chapter_8", "invalid_parse", "do_extra_semicolon.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected While, got Semicolon() @ 4:6"


def test_do_missing_semicolon() -> None:
    path = os.path.join(TEST_DIR, "chapter_8", "invalid_parse", "do_missing_semicolon.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got Return() @ 5:10"


def test_do_while_empty_parens() -> None:
    path = os.path.join(TEST_DIR, "chapter_8", "invalid_parse", "do_while_empty_parens.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found RightParen() @ 4:11"


def test_extra_for_header_clause() -> None:
    path = os.path.join(TEST_DIR, "chapter_8", "invalid_parse", "extra_for_header_clause.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected RightParen, got Semicolon() @ 2:38"


def test_invalid_for_declaration() -> None:
    path = os.path.join(TEST_DIR, "chapter_8", "invalid_parse", "invalid_for_declaration.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Int() @ 2:11"


def test_missing_for_header_clause() -> None:
    path = os.path.join(TEST_DIR, "chapter_8", "invalid_parse", "missing_for_header_clause.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found RightParen() @ 2:19"


def test_paren_mismatch() -> None:
    path = os.path.join(TEST_DIR, "chapter_8", "invalid_parse", "paren_mismatch.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found RightParen() @ 2:20"


def test_statement_in_condition() -> None:
    path = os.path.join(TEST_DIR, "chapter_8", "invalid_parse", "statement_in_condition.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Int() @ 2:10"


def test_while_missing_paren() -> None:
    path = os.path.join(TEST_DIR, "chapter_8", "invalid_parse", "while_missing_paren.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected LeftParen, got LiteralInt(1) @ 2:11"


def test_call_non_identifier() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_parse", "call_non_identifier.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got LeftParen() @ 8:13"


def test_decl_wrong_closing_delim() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_parse", "decl_wrong_closing_delim.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Comma, got RightBrace() @ 4:21"


def test_fun_decl_for_loop() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_parse", "fun_decl_for_loop.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "cannot declare function in for loop init @ 3:12"


def test_funcall_wrong_closing_delim() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_parse", "funcall_wrong_closing_delim.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Comma, got RightBrace() @ 8:33"


def test_function_call_declaration() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_parse", "function_call_declaration.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Int() @ 7:15"


def test_function_returning_function() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_parse", "function_returning_function.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected LeftBrace, got LeftParen() @ 6:14"


def test_initialize_function_as_variable() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_parse", "initialize_function_as_variable.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected LeftBrace, got Equal() @ 6:15"


def test_trailing_comma_decl() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_parse", "trailing_comma_decl.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Int, got RightParen() @ 2:15"


def test_trailing_comma() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_parse", "trailing_comma.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found RightParen() @ 7:23"


def test_unclosed_paren_decl() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_parse", "unclosed_paren_decl.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Comma, got LeftBrace() @ 1:22"


def test_var_init_in_param_list() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_parse", "var_init_in_param_list.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Comma, got Equal() @ 2:22"

def test_extern_param() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_parse", "extern_param.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Int, got Extern() @ 2:12"

def test_missing_parameter_list() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_parse", "missing_parameter_list.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon or Equal, got LeftBrace() @ 2:7"

def test_missing_type_specifier() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_parse", "missing_type_specifier.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "invalid types: [] @ 4:10"

def test_multi_storage_class_fun() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_parse", "multi_storage_class_fun.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "invalid storage classes: [Static(), Extern()] @ 2:21"

def test_multi_storage_class_var() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_parse", "multi_storage_class_var.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "invalid storage classes: [Static(), Extern()] @ 3:25"


def test_static_and_extern() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_parse", "static_and_extern.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "invalid storage classes: [Static(), Extern()] @ 2:19"


def test_static_param() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_parse", "static_param.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Int, got Static() @ 2:12"


def test_extern_label() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_parse", "extra_credit", "extern_label.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "invalid types: [] @ 4:12"



def test_file_scope_label() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_parse", "extra_credit", "file_scope_label.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "invalid types: [] @ 2:1"


def test_static_label() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_parse", "extra_credit", "static_label.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "invalid types: [] @ 4:12"


