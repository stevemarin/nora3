from inspect import currentframe
from typing import Iterable

from nora3 import tok
from nora3 import asts


# fmt: off
class TemporaryParseError(Exception): ...
class ParserEofError(Exception): ...
class ParserError(Exception): ...
# fmt: on


class TokenTypeError(Exception):
    def __init__(self, token: tok.Token, expected: Iterable[type[tok.TokenType]]) -> None:
        self.token = token
        self.expected = expected

    def __str__(self) -> str:
        expected = " or ".join(map(str, map(lambda x: x.__name__, self.expected)))
        return f"expected {expected}, got {self.token.tokentype} @ {self.token.line}:{self.token.offset}"


class Parser:
    tokens: list[tok.Token]
    idx: int = 0

    def __init__(self, tokens: list[tok.Token]) -> None:
        self.tokens = tokens
        self.idx = 0

    def eat(self, expected: type[tok.TokenType] | None = None) -> tok.Token:
        try:
            token = self.tokens[self.idx]
            self.idx += 1
        except IndexError:
            assert (frame := currentframe()) is not None
            assert (f_back := frame.f_back) is not None
            calling_function = f_back.f_code.co_name
            raise ParserEofError(f"unexpected EOF found in {calling_function} function")

        if expected is None or isinstance(token.tokentype, expected):
            return token
        else:
            raise TokenTypeError(token, [expected])

    def peek(self) -> tok.Token:
        try:
            return self.tokens[self.idx]
        except IndexError:
            assert (frame := currentframe()) is not None
            assert (f_back := frame.f_back) is not None
            calling_function = f_back.f_code.co_name
            raise ParserEofError(f"unexpected EOF found in {calling_function} function")

    def peek2(self, tokentype: type[tok.TokenType]) -> bool:
        try:
            tt = self.tokens[self.idx + 1].tokentype
        except IndexError:
            return False

        return True if isinstance(tt, tokentype) else False

    def function_arguments(self) -> list[asts.Expr]:
        if self.peek().tokentype is tok.RightParen():
            return []

        args = [self.expr()]
        while self.peek().tokentype is not tok.RightParen():
            _ = self.eat(tok.Comma)
            args.append(self.expr())
        return args

    def factor(self) -> asts.Expr:
        match type((token := self.eat()).tokentype):
            case tok.LiteralInt:
                res: asts.Expr = asts.Constant(int(token.tokentype.value))
            case tok.Identifier if self.peek().tokentype is tok.LeftParen():  # function call
                name = token.tokentype.value
                _ = self.eat(tok.LeftParen)
                args = self.function_arguments()
                _ = self.eat(tok.RightParen)
                return asts.FuncCall(name, args)
            case tok.Identifier:
                res = asts.Variable(token)
            case t if asts.Unary.is_unary_tokentype(t()):
                inner = self.factor()
                res = asts.Unary.from_tokentype(t)(inner)
            case tok.LeftParen:
                inner = self.expr()
                _ = self.eat(tok.RightParen)
                res = inner
            case _:
                raise ParserError(
                    f"expected an expression, found {token.tokentype} @ {token.line}:{token.offset - len(token)}"
                )

        # prefix incr/decr are parsed via the parser as unary operators
        # postfix incr/decr are added here after individual factors
        match self.peek().tokentype:
            case tok.PlusPlus():
                _ = self.eat()
                return asts.PostfixIncrement(res)
            case tok.HyphenHyphen():
                _ = self.eat()
                return asts.PostfixDecrement(res)
            case _:
                return res

    def conditional_middle(self) -> asts.Expr:
        _ = self.eat(tok.Question)
        middle = self.expr()
        _ = self.eat(tok.Colon)
        return middle

    def expr(self, minimum_precedence: int = 0) -> asts.Expr:
        left = self.factor()
        while True:
            next_token = self.peek()

            try:
                binary_type = asts.Binary.from_tokentype(next_token.tokentype)
            except TypeError:
                break

            if binary_type.precedence < minimum_precedence:
                break

            if binary_type.associativity == "right":
                assert binary_type.precedence == 1
                _ = self.eat()
                right = self.expr(binary_type.precedence)
                left = binary_type(left, right)
            elif binary_type.precedence == 3:
                middle = self.conditional_middle()
                right = self.expr(binary_type.precedence + 1)
                left = asts.Conditional(left, middle, right)
            else:
                _ = self.eat()
                right = self.expr(binary_type.precedence + 1)
                left = binary_type(left, right)

        return left

    @staticmethod
    def storage_class(storage_classes: list[tok.StorageSpecifier]) -> tok.StorageSpecifier:
        if len(storage_classes) > 1:
            raise ParserError(f"invalid storage classes: {storage_classes}")
        return storage_classes[0]

    def type_and_storage_class(
        self,
        specifiers: list[tok.Specifier],
    ) -> tuple[tok.TypeSpecifier, tok.StorageSpecifier | None]:
        types, storage_classes = [], []
        for specifier in specifiers:
            if isinstance(specifier, tok.TypeSpecifier):
                types.append(specifier)
            elif isinstance(specifier, tok.StorageSpecifier):
                storage_classes.append(specifier)
            else:
                raise ParserError(f"unknown specifier: {specifier}")

        if len(types) != 1:
            raise ParserError(f"invalid types: {types}")
        else:
            type_ = types[0]

        assert isinstance(type_, tok.Int)

        if len(storage_classes) > 0:
            storage_class = self.storage_class(storage_classes)
        else:
            storage_class = None

        return (type_, storage_class)

    def var_decl(
        self, name: str, type_: tok.TypeSpecifier, storage_class: tok.StorageSpecifier | None
    ) -> asts.VarDecl:
        match (token := self.peek()).tokentype:
            case tok.Semicolon():
                expr = None
            case tok.Equal():
                _ = self.eat(tok.Equal)
                expr = self.expr()
            case _:
                raise TokenTypeError(token, (tok.Semicolon, tok.Equal))

        _ = self.eat(tok.Semicolon)
        return asts.VarDecl(name, expr, type_, storage_class)

    def func_params(self) -> list[asts.Variable]:
        if self.peek().tokentype is tok.Void():
            _ = self.eat(tok.Void)
            return []
        elif self.peek().tokentype is tok.RightParen():
            return []

        _ = self.eat(tok.Int)
        params = [asts.Variable.from_str(self.eat(tok.Identifier).tokentype.value)]
        while self.peek().tokentype is not tok.RightParen():
            _ = self.eat(tok.Comma)
            _ = self.eat(tok.Int)
            params.append(asts.Variable.from_str(self.eat(tok.Identifier).tokentype.value))
        return params

    def func_decl(
        self, name: str, type_: tok.TypeSpecifier, storage_class: tok.StorageSpecifier | None
    ) -> asts.FuncDecl:
        _ = self.eat(tok.LeftParen)
        params = self.func_params()
        _ = self.eat(tok.RightParen)

        if self.peek().tokentype is tok.Semicolon():
            _ = self.eat(tok.Semicolon)
            return asts.FuncDecl(name, params, None, type_, storage_class)

        _ = self.eat(tok.LeftBrace)
        body: list[asts.BlockItem] = []
        while self.peek().tokentype is not tok.RightBrace():
            body.append(self.block_item())
        _ = self.eat(tok.RightBrace)

        return asts.FuncDecl(name, params, asts.Block(body), type_, storage_class)

    def declaration(self) -> asts.Declaration:
        specifiers: list[tok.Specifier] = []
        while isinstance((specifier := self.peek()).tokentype, tok.Specifier):
            _ = self.eat()
            specifiers.append(specifier.tokentype)
        try:
            type_, storage_class = self.type_and_storage_class(specifiers)
        except ParserError as e:
            raise ParserError(f"{e} @ {specifier.line}:{specifier.offset}")

        name = self.eat(tok.Identifier).tokentype.value

        if self.peek().tokentype is tok.LeftParen():
            return self.func_decl(name, type_, storage_class)
        else:
            return self.var_decl(name, type_, storage_class)

    def for_init(self) -> asts.Declaration | asts.Expr | None:
        if (token := self.peek()).tokentype is tok.Semicolon():
            _ = self.eat(tok.Semicolon)
            return None
        elif token.tokentype is tok.Int():
            decl = self.declaration()
            if isinstance(decl, asts.FuncDecl):
                raise ParserError(f"cannot declare function in for loop init @ {token.line}:{token.offset}")
            return decl
        else:
            expr = self.expr()
            _ = self.eat(tok.Semicolon)
            return expr

    def stmt(self) -> asts.Stmt:
        match type(self.peek().tokentype):
            case tok.Return:
                _ = self.eat(tok.Return)
                expr = self.expr()
                _ = self.eat(tok.Semicolon)
                return asts.Return(expr)
            case tok.If:
                _ = self.eat(tok.If)
                _ = self.eat(tok.LeftParen)
                cond = self.expr(0)
                _ = self.eat(tok.RightParen)
                then = self.stmt()
                if isinstance(self.peek().tokentype, tok.Else):
                    _ = self.eat(tok.Else)
                    else_ = self.stmt()
                else:
                    else_ = None
                return asts.If(cond, then, else_)
            case tok.Goto:
                _ = self.eat(tok.Goto)
                target = self.eat(tok.Identifier).tokentype.value
                _ = self.eat(tok.Semicolon)
                return asts.Goto(target)
            case tok.Semicolon:
                _ = self.eat(tok.Semicolon)
                return asts.Null()
            case tok.Identifier if self.peek2(tok.Colon):
                name = self.eat(tok.Identifier).tokentype.value
                _ = self.eat(tok.Colon)
                return asts.Label(name)
            case tok.LeftBrace:
                _ = self.eat(tok.LeftBrace)
                items = []
                while self.peek().tokentype is not tok.RightBrace():
                    item = self.block_item()
                    items.append(item)
                _ = self.eat(tok.RightBrace)
                return asts.Compound(asts.Block(items))
            case tok.Break:
                _ = self.eat(tok.Break)
                _ = self.eat(tok.Semicolon)
                return asts.Break()
            case tok.Continue:
                _ = self.eat(tok.Continue)
                _ = self.eat(tok.Semicolon)
                return asts.Continue()
            case tok.While:
                _ = self.eat(tok.While)
                _ = self.eat(tok.LeftParen)
                cond = self.expr()
                _ = self.eat(tok.RightParen)
                body = self.stmt()
                return asts.While(cond, body)
            case tok.Do:
                _ = self.eat(tok.Do)
                body = self.stmt()
                _ = self.eat(tok.While)
                _ = self.eat(tok.LeftParen)
                cond = self.expr()
                _ = self.eat(tok.RightParen)
                _ = self.eat(tok.Semicolon)
                return asts.DoWhile(cond, body)
            case tok.For:
                _ = self.eat(tok.For)
                _ = self.eat(tok.LeftParen)
                init = self.for_init()
                maybe_cond = None if self.peek().tokentype is tok.Semicolon() else self.expr()
                _ = self.eat(tok.Semicolon)
                maybe_post = None if self.peek().tokentype is tok.RightParen() else self.expr()
                _ = self.eat(tok.RightParen)
                body = self.stmt()
                return asts.For(init, maybe_cond, maybe_post, body)
            case tok.Switch:
                raise NotImplementedError("no switch yet")
            case _:
                stmt = asts.Expression(self.expr())
                _ = self.eat(tok.Semicolon)
                return stmt

    def block_item(self) -> asts.BlockItem:
        match self.peek().tokentype:
            case t if isinstance(t, tok.Specifier):
                return self.declaration()
            case _:
                return self.stmt()

    def program(self) -> asts.Program:
        functions = []
        while self.idx < len(self.tokens):
            assert isinstance((func := self.declaration()), asts.Declaration)
            functions.append(func)

        return asts.Program(functions, {})

    def parse(self) -> asts.Program:
        return self.program()


if __name__ == "__main__":
    from nora3.lex import Lexer

    src = """
int f(void) {
    static int i = 0;
    static int j = 0;
    static int k = 1;
    static int l = 48;
    i += 1;
    j -= i;
    k *= j;
    l /= 2;

    // expected values after 3 invocations:
    // i = 3
    // j = -6
    // k = -18
    // l = 6
    if (i != 1) {
        return 1;
    }
    if (j != -6) {
        return 2;
    }
    if (k != -18) {
        return 3;
    }
    if (l != 6) {
        return 4;
    }
    return 0;
}

int main(void) {
    f();
    f();
    return f();
}
"""
    pseudo: dict[str, int] = {}

    tokens = Lexer(src).lex()
    print("tokens:")
    for t in tokens:
        print("    ", t)

    ast = Parser(tokens).parse()
    print(ast)

    ast = ast.resolve()
    print("ast", repr(ast))

    ir = ast.to_tacky()
    print("ir", repr(ir))

    ass = ir.to_asm()
    print("ass", repr(ass))

    ass.replace_pseudo(0, pseudo)
    print("psuedo", repr(ass))

    ass = ass.fix_instructions()
    print("fix", repr(ass))

    code = ass.codegen()

    print(pseudo)
    print(code)
