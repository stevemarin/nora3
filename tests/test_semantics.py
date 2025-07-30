import os
from nora3 import TEST_DIR
from nora3.lex import Lexer
from nora3.parse import Parser, ParserError, TokenTypeError
from nora3.asts import ResolverError, TypeCheckerError


def test_declared_after_use() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "declared_after_use.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: a"


def test_invalid_lvalue() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "invalid_lvalue.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "invalid lvalue: Add"


def test_invalid_lvalue_2() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "invalid_lvalue_2.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "invalid lvalue: Not"


def test_mixed_precedence_assignment() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "mixed_precedence_assignment.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "invalid lvalue: Multiply"


def test_redefine() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "redefine.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "conflicting local definitions for a"


def test_undeclared_var_and() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "undeclared_var_and.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: a"


def test_undeclared_var_compare() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "undeclared_var_compare.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: a"


def test_undeclared_var_unary() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "undeclared_var_unary.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: a"


def test_undeclared_var() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "undeclared_var.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: a"


def test_use_then_redefine() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "use_then_redefine.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "conflicting local definitions for a"


def test_compound_invalid_lvalue_2() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "extra_credit", "compound_invalid_lvalue_2.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "invalid lvalue: AddAssign"


def test_compound_invalid_lvalue() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "extra_credit", "compound_invalid_lvalue.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "invalid lvalue: Negate"


def test_postfix_decr_non_lvalue() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "extra_credit", "postfix_decr_non_lvalue.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got HyphenHyphen() @ 6:16"


def test_postfix_incr_non_lvalue() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "extra_credit", "postfix_incr_non_lvalue.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "expr for PostfixIncrement must be variable, not Assign"


def test_prefix_decr_non_lvalue() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "extra_credit", "prefix_decr_non_lvalue.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "expr for PrefixDecrement must be variable, not Constant"


def test_prefix_incr_non_lvalue() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "extra_credit", "prefix_incr_non_lvalue.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "expr for PrefixIncrement must be variable, not Add"


def test_pundeclared_bitwise_op() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "extra_credit", "undeclared_bitwise_op.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: a"


def test_pundeclared_compound_assignment_use() -> None:
    path = os.path.join(
        TEST_DIR, "chapter_5", "invalid_semantics", "extra_credit", "undeclared_compound_assignment_use.c"
    )
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: a"


def test_undeclared_compound_assignment() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "extra_credit", "undeclared_compound_assignment.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: a"


def test_undeclared_postfix_decr() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "extra_credit", "undeclared_postfix_decr.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: a"


def test_undeclared_prefix_incr() -> None:
    path = os.path.join(TEST_DIR, "chapter_5", "invalid_semantics", "extra_credit", "undeclared_prefix_incr.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: a"


def test_invalid_var_in_if() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_semantics", "invalid_var_in_if.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: c"


def test_ternary_assign() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_semantics", "ternary_assign.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "invalid lvalue: Conditional"


def test_undeclared_var_in_ternary() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_semantics", "undeclared_var_in_ternary.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: a"


def test_duplicate_labels() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_semantics", "extra_credit", "duplicate_labels.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "label already used: .label.main.label"


def test_goto_missing_label() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_semantics", "extra_credit", "goto_missing_label.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "goto undefined label: .label.main.label"


def test_goto_variable() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_semantics", "extra_credit", "goto_variable.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "goto undefined label: .label.main.a"


def test_undeclared_var_in_labeled_statement() -> None:
    path = os.path.join(
        TEST_DIR, "chapter_6", "invalid_semantics", "extra_credit", "undeclared_var_in_labeled_statement.c"
    )
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: a"


def test_use_label_as_variable() -> None:
    path = os.path.join(TEST_DIR, "chapter_6", "invalid_semantics", "extra_credit", "use_label_as_variable.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: a"


def test_double_define_after_scope() -> None:
    path = os.path.join(TEST_DIR, "chapter_7", "invalid_semantics", "double_define_after_scope.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "conflicting local definitions for a"


def test_double_define() -> None:
    path = os.path.join(TEST_DIR, "chapter_7", "invalid_semantics", "double_define.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "conflicting local definitions for a"


def test_out_of_scope() -> None:
    path = os.path.join(TEST_DIR, "chapter_7", "invalid_semantics", "out_of_scope.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: a"


def test_use_before_declare() -> None:
    path = os.path.join(TEST_DIR, "chapter_7", "invalid_semantics", "use_before_declare.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: b"


def test_different_labels_same_scope() -> None:
    path = os.path.join(TEST_DIR, "chapter_7", "invalid_semantics", "extra_credit", "different_labels_same_scope.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "conflicting local definitions for a"


def test_duplicate_labels_different_scopes() -> None:
    path = os.path.join(
        TEST_DIR, "chapter_7", "invalid_semantics", "extra_credit", "duplicate_labels_different_scopes.c"
    )
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "label already used: .label.main.l"


def test_goto_use_before_declare() -> None:
    path = os.path.join(TEST_DIR, "chapter_7", "invalid_semantics", "extra_credit", "goto_use_before_declare.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: y"


def test_break_not_in_loop() -> None:
    path = os.path.join(TEST_DIR, "chapter_8", "invalid_semantics", "break_not_in_loop.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "break statement outside of loop"


def test_continue_not_in_loop() -> None:
    path = os.path.join(TEST_DIR, "chapter_8", "invalid_semantics", "continue_not_in_loop.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "continue statement outside of loop"


def test_out_of_scope_do_loop() -> None:
    path = os.path.join(TEST_DIR, "chapter_8", "invalid_semantics", "out_of_scope_do_loop.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: a"


def test_out_of_scope_loop_variable() -> None:
    path = os.path.join(TEST_DIR, "chapter_8", "invalid_semantics", "out_of_scope_loop_variable.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: i"


def test_assign_fun_to_variable() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_types", "assign_fun_to_variable.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "function name x used as a variable"


def test_assign_value_to_function() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_types", "assign_value_to_function.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "function name x used as a variable"


def test_call_variable_as_function() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_types", "call_variable_as_function.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "variable .var.x.26 used as a function name"


def test_conflicting_function_declarations() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_types", "conflicting_function_declarations.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "function foo redefined from 1 to 2 parameters"


def test_conflicting_local_function_declaration() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_types", "conflicting_local_function_declaration.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "function foo redefined from 1 to 2 parameters"


def test_divide_by_function() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_types", "divide_by_function.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "function name x used as a variable"


def test_multiple_function_definitions_2() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_types", "multiple_function_definitions_2.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "function foo is defined more than once"


def test_multiple_function_definitions() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_types", "multiple_function_definitions.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "function foo is defined more than once"


def test_too_few_args() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_types", "too_few_args.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "function foo called with wrong number of arguments: 2 != 1"


def test_too_many_args() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_types", "too_many_args.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "function foo called with wrong number of arguments: 1 != 2"


def test_bitwise_op_function() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_types", "extra_credit", "bitwise_op_function.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "function name x used as a variable"


def test_compound_assign_function_lhs() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_types", "extra_credit", "compound_assign_function_lhs.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "function name x used as a variable"


def test_compound_assign_function_rhs() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_types", "extra_credit", "compound_assign_function_rhs.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "function name x used as a variable"


def test_postfix_incr_fun_name() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_types", "extra_credit", "postfix_incr_fun_name.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "function name x used as a variable"


def test_prefix_decr_fun_name() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_types", "extra_credit", "prefix_decr_fun_name.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "function name x used as a variable"


def test_switch_on_function() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_types", "extra_credit", "switch_on_function.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except NotImplementedError as e:
        assert str(e) == "no switch yet"


def test_goto_cross_function() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_labels", "extra_credit", "goto_cross_function.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "goto undefined label: .label.main.label"


def test_goto_function() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_labels", "extra_credit", "goto_function.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "goto undefined label: .label.main.foo"


def test_assign_to_fun_call() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_declarations", "assign_to_fun_call.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "invalid lvalue: FuncCall"


def test_decl_params_with_same_name() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_declarations", "decl_params_with_same_name.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "conflicting local definitions for a"


def test_nested_function_definition() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_declarations", "nested_function_definition.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "cannot define function foo inside function"


def test_params_with_same_name() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_declarations", "params_with_same_name.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "conflicting local definitions for a"


def test_redefine_fun_as_var() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_declarations", "redefine_fun_as_var.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "conflicting local definitions for foo"


def test_redefine_parameter() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_declarations", "redefine_parameter.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "conflicting local definitions for a"


def test_redefine_var_as_fun() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_declarations", "redefine_var_as_fun.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "duplication function definition: foo"


def test_undeclared_fun() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_declarations", "undeclared_fun.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undeclared function: foo"


def test_wrong_parameter_names() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_declarations", "wrong_parameter_names.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: a"


def test_call_label_as_function() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_declarations", "extra_credit", "call_label_as_function.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undeclared function: a"


def test_compound_assign_to_fun_call() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_declarations", "extra_credit", "compound_assign_to_fun_call.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "invalid lvalue: FuncCall"


def test_decrement_fun_call() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_declarations", "extra_credit", "decrement_fun_call.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except TokenTypeError as e:
        assert str(e) == "expected Semicolon, got HyphenHyphen() @ 5:9"


def test_increment_fun_call() -> None:
    path = os.path.join(TEST_DIR, "chapter_9", "invalid_declarations", "extra_credit", "increment_fun_call.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "expr for PrefixIncrement must be variable, not FuncCall"


def test_conflicting_function_linkage_2() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_types", "conflicting_function_linkage_2.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "static function decl follows non-static for foo"


def test_conflicting_function_linkage() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_types", "conflicting_function_linkage.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "static function decl follows non-static for foo"


def test_conflicting_global_definitions() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_types", "conflicting_global_definitions.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "conflicting file-scope variable definitions: foo"


def test_conflicting_variable_linkage_2() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_types", "conflicting_variable_linkage_2.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "conflicting variable linkage for x"


def test_conflicting_variable_linkage() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_types", "conflicting_variable_linkage.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "conflicting variable linkage for foo"


def test_extern_for_loop_counter() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_types", "extern_for_loop_counter.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Extern() @ 6:9"


def test_extern_variable_initializer() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_types", "extern_variable_initializer.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "initializer on local extern variable declaration for i"


def test_non_constant_static_initializer() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_types", "non_constant_static_initializer.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "non-constant initializer for b: Add(Constant(1) . Variable(a))"


def test_non_constant_static_local_initializer() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_types", "non_constant_static_local_initializer.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "non-constant initializer on local static variable .var.b.47"


def test_redeclare_file_scope_var_as_fun() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_types", "redeclare_file_scope_var_as_fun.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "incompatible function declarations for: foo"


def test_redeclare_fun_as_file_scope_var() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_types", "redeclare_fun_as_file_scope_var.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "cannot redeclare function foo as file-scope variable"


def test_redeclare_fun_as_var() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_types", "redeclare_fun_as_var.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "function foo redecalred as variable"


def test_static_block_scope_function_declaration() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_types", "static_block_scope_function_declaration.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "function foo in block scope cannot be static"


def test_static_for_loop_counter() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_types", "static_for_loop_counter.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()

    try:
        _ = Parser(tokens).parse()
        assert False, "didn't fail successfully"
    except ParserError as e:
        assert str(e) == "expected an expression, found Static() @ 6:9"


def test_use_file_scope_variable_as_fun() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_types", "use_file_scope_variable_as_fun.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except TypeCheckerError as e:
        assert str(e) == "variable foo used as a function name"

# def test_static_var_case() -> None:
#     path = os.path.join(TEST_DIR, "chapter_10", "invalid_types", "extra_credit", "static_var_case.c")
#     with open(path, "r") as fh:
#         src = fh.read()
#     tokens = Lexer(src).lex()
#     ast = Parser(tokens).parse()

#     try:
#         _ = ast.resolve()
#         assert False, "didn't fail successfully"
#     except TypeCheckerError as e:
#         assert str(e) == "variable foo used as a function name"

def test_goto_global_var() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_labels", "extra_credit", "goto_global_var.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "goto undefined label: .label.main.x"


def test_conflicting_local_declarations() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_declarations", "conflicting_local_declarations.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "conflicting local definitions for x"



def test_extern_follows_local_var() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_declarations", "extern_follows_local_var.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "conflicting local definitions for x"


def test_extern_follows_static_local_var() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_declarations", "extern_follows_static_local_var.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "conflicting local definitions for x"


def test_local_var_follows_extern() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_declarations", "local_var_follows_extern.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "conflicting local definitions for i"


def test_out_of_scope_extern_var() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_declarations", "out_of_scope_extern_var.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: a"



def test_redefine_param_as_identifier_with_linkage() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_declarations", "redefine_param_as_identifier_with_linkage.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "conflicting local definitions for i"



def test_undeclared_global_variable() -> None:
    path = os.path.join(TEST_DIR, "chapter_10", "invalid_declarations", "undeclared_global_variable.c")
    with open(path, "r") as fh:
        src = fh.read()
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()

    try:
        _ = ast.resolve()
        assert False, "didn't fail successfully"
    except ResolverError as e:
        assert str(e) == "undefined variable: x"

