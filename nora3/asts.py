from typing import Protocol, Self

from nora3 import tacky
from nora3 import tok
from nora3.builtin_types import (
    Type,
    FuncType,
    IntType,
    SymbolTable,
    InitialValue,
    NoInitializer,
    Tentative,
    Initial,
    FuncAttrs,
    StaticAttrs,
    LocalAttrs,
)
from nora3.common import (
    MappingHolder,
    Emitter,
    Unreachable,
    make_label_name,
    make_temp_variable_name,
    make_variable_name,
)


# fmt: off
class ResolverError(Exception): ...
class TypeCheckerError(Exception): ...
# fmt: on


class ToTacky[Res](Protocol):
    def to_tacky(self, symbol_table: SymbolTable) -> Res: ...


class MapEntry:
    def __init__(self, name: str, from_current_scope: bool, has_linkage: bool = False) -> None:
        self.name = name
        self.from_current_scope = from_current_scope
        self.has_linkage = has_linkage

    def __repr__(self) -> str:
        return f"Entry({self.name} cur={self.from_current_scope} link={self.has_linkage})"


class Resolver(Protocol):
    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> Self: ...
    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> Self: ...
    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> Self: ...

    def mangle_label(self, label: str, function_name: str) -> str:
        return f".label.{function_name}.{label}"

    def copy_variable_map(self, identifier_map: dict[str, MapEntry]) -> dict[str, MapEntry]:
        return {name: MapEntry(me.name, False, me.has_linkage) for name, me in identifier_map.items()}


class TypeChecker(Protocol):
    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None: ...


class Expr(Emitter, Resolver, TypeChecker):
    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> Self:
        raise NotImplementedError("cannot resolve goto labels for expressions")

    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> Self:
        raise NotImplementedError("cannot resolve loop labels for expressions")


class Constant(Expr):
    def __init__(self, value: int) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"Constant({self.value})"

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Constant:
        return tacky.Constant(self.value)

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> "Constant":
        return Constant(self.value)

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        pass


class Variable(Expr):
    def __init__(self, token: tok.Token) -> None:
        assert isinstance(token.tokentype, tok.Identifier)
        self.name = token.tokentype.value

    @classmethod
    def from_str(cls, name: str) -> "Variable":
        var = Variable.__new__(cls)
        var.name = name
        return var

    def __repr__(self) -> str:
        return f"Variable({self.name})"

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Variable:
        return tacky.Variable(self.name)

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> "Variable":
        if self.name not in identifier_map:
            raise ResolverError(f"undefined variable: {self.name}")

        unique_name = identifier_map[self.name].name
        return Variable(tok.Token(-1, -1, tok.Identifier(unique_name)))

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        var = symbol_table[self.name]
        if isinstance(var, FuncType):
            raise TypeCheckerError(f"function name {self.name} used as a variable")


class Unary(Expr, MappingHolder):
    tacky_type: type[tacky.Unary]

    def __init__(self, expr: Expr) -> None:
        self.expr = expr

    def __repr__(self) -> str:
        expr = repr(self.expr)
        return f"{self.__class__.__name__}({expr})"

    def __init_subclass__(cls, tokentype: tok.TokenType | None, op: type[tacky.Unary]) -> None:
        if tokentype is not None:
            cls.mapping[tokentype] = cls
        cls.tacky_type = op

    @classmethod
    def from_tokentype(cls, tokentype: type[tok.TokenType]) -> type["Unary"]:
        if (unary := cls.mapping.get(tokentype())) is None:
            raise TypeError(f"token is not a unary operator: {tokentype}")
        return unary

    @classmethod
    def is_unary_tokentype(cls, tokentype: tok.TokenType) -> bool:
        if cls.mapping.get(tokentype) is None:
            return False
        return True

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        src = self.expr.emit(instructions)
        dst = tacky.Variable(make_temp_variable_name())
        instructions.append(self.tacky_type(src, dst))
        return dst

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> "Unary":
        if self.__class__ in {PrefixIncrement, PrefixDecrement, PostfixIncrement, PostfixDecrement}:
            if not isinstance(self.expr, Variable):
                raise ResolverError(
                    f"expr for {self.__class__.__name__} must be variable, not {self.expr.__class__.__name__}"
                )

        expr = self.expr.resolve_identifiers(identifier_map, inside_func)
        return self.__class__(expr)

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        self.expr.typecheck(symbol_table, file_scope)


# fmt: off
class Complement(Unary, tokentype=tok.Tilde(), op=tacky.Complement): ...
class Negate(Unary, tokentype=tok.Hyphen(), op=tacky.Negate): ...
class Not(Unary, tokentype=tok.Bang(), op=tacky.Not): ...
class PrefixIncrement(Unary, tokentype=tok.PlusPlus(), op=tacky.PrefixIncrement): ...
class PrefixDecrement(Unary, tokentype=tok.HyphenHyphen(), op=tacky.PrefixDecrement): ...
class PostfixIncrement(Unary, tokentype=None, op=tacky.PostfixIncrement): ...
class PostfixDecrement(Unary, tokentype=None, op=tacky.PostfixDecrement): ...
# fmt: on


class Binary(Expr, MappingHolder):
    tacky_type: type[tacky.Binary] | None
    precedence: int
    associativity: str
    compound_op: type[tacky.Binary] | None

    def __init_subclass__(
        cls,
        tokentype: tok.TokenType,
        precedence: int,
        tacky_type: type[tacky.Binary] | None = None,
        associativity: str = "left",
        compound_op: type[tacky.Binary] | None = None,
    ) -> None:
        cls.mapping[tokentype] = cls
        cls.tacky_type = tacky_type
        cls.precedence = precedence
        cls.associativity = associativity
        cls.compound_op = compound_op

    def __init__(self, left: Expr, right: Expr) -> None:
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        left = repr(self.left)
        right = repr(self.right)
        return f"{self.__class__.__name__}({left} . {right})"

    @classmethod
    def from_tokentype(cls, tokentype: tok.TokenType) -> type["Binary"]:
        if (binary := cls.mapping.get(tokentype)) is None:
            raise TypeError(f"token is not a unary operator: {tokentype}")
        return binary

    def _assign_emit(self, instructions: list[tacky.Instruction]) -> tacky.Variable:
        assert isinstance(self.left, Variable)
        left = self.left.emit(instructions)
        right = self.right.emit(instructions)

        if self.compound_op is None:
            instructions.append(tacky.Copy(right, left))
            return left
        else:
            dst = tacky.Variable(make_temp_variable_name())
            instructions.extend([self.compound_op(left, right, dst), tacky.Copy(dst, left)])
            return left

    def _non_assign_emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        left = self.left.emit(instructions)
        right = self.right.emit(instructions)
        dst = tacky.Variable(make_temp_variable_name())
        assert self.tacky_type is not None
        instructions.append(self.tacky_type(left, right, dst))
        return dst

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        if self.precedence == 1:
            return self._assign_emit(instructions)
        else:
            return self._non_assign_emit(instructions)

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> Self:
        if self.precedence == 1 and not isinstance(self.left, Variable):
            raise ResolverError(f"invalid lvalue: {self.left.__class__.__name__}")

        left = self.left.resolve_identifiers(identifier_map, inside_func)
        right = self.right.resolve_identifiers(identifier_map, inside_func)
        return self.__class__(left, right)

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        self.left.typecheck(symbol_table, file_scope)
        self.right.typecheck(symbol_table, file_scope)


# fmt: off
class Multiply(Binary, tokentype=tok.Star(), precedence=50, tacky_type=tacky.Multiply): ...
class Divide(Binary, tokentype=tok.ForwardSlash(), precedence=50, tacky_type=tacky.Divide): ...
class Remainder(Binary, tokentype=tok.Percent(), precedence=50, tacky_type=tacky.Remainder): ...
class Add(Binary, tokentype=tok.Plus(), precedence=45, tacky_type=tacky.Add): ...
class Subtract(Binary, tokentype=tok.Hyphen(), precedence=45, tacky_type=tacky.Subtract): ...
class LeftShift(Binary, tokentype=tok.LessLess(), precedence=40, tacky_type=tacky.LeftShift): ...
class RightShift(Binary, tokentype=tok.GreaterGreater(), precedence=40, tacky_type=tacky.RightShift): ...
class LessThan(Binary, tokentype=tok.Less(), precedence=35, tacky_type=tacky.LessThan): ...
class LessOrEqual(Binary, tokentype=tok.LessEqual(), precedence=35, tacky_type=tacky.LessOrEqual): ...
class GreaterThan(Binary, tokentype=tok.Greater(), precedence=35, tacky_type=tacky.GreaterThan): ...
class GreaterOrEqual(Binary, tokentype=tok.GreaterEqual(), precedence=35, tacky_type=tacky.GreaterOrEqual): ...
class Equal(Binary, tokentype=tok.EqualEqual(), precedence=30, tacky_type=tacky.Equal): ...
class NotEqual(Binary, tokentype=tok.BangEqual(), precedence=30, tacky_type=tacky.NotEqual): ...
class BitwiseAnd(Binary, tokentype=tok.Ampersand(), precedence=24, tacky_type=tacky.BitwiseAnd): ...
class BitwiseXOr(Binary, tokentype=tok.Caret(), precedence=22, tacky_type=tacky.BitwiseXOr): ...
class BitwiseOr(Binary, tokentype=tok.Bar(), precedence=20, tacky_type=tacky.BitwiseOr): ...
# fmt: on


class Assign(Binary, tokentype=tok.Equal(), precedence=1, associativity="right"):
    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        super().typecheck(symbol_table, file_scope)


# fmt: off
class AddAssign(Assign, tokentype=tok.PlusEqual(), precedence=1, compound_op=tacky.Add, associativity="right"): ...
class MinusAssign(Assign, tokentype=tok.HyphenEqual(), precedence=1, compound_op=tacky.Subtract, associativity="right"): ...
class MultiplyAssign(Assign, tokentype=tok.StarEqual(), precedence=1, compound_op=tacky.Multiply, associativity="right"): ...
class DivideAssign(Assign, tokentype=tok.ForwardSlashEqual(), precedence=1, compound_op=tacky.Divide, associativity="right"): ...
class RemainderAssign(Assign, tokentype=tok.PercentEqual(), precedence=1, compound_op=tacky.Remainder, associativity="right"): ...
class AndAssign(Assign, tokentype=tok.AmpersandEqual(), precedence=1, compound_op=tacky.BitwiseAnd, associativity="right"): ...
class OrAssign(Assign, tokentype=tok.BarEqual(), precedence=1, compound_op=tacky.BitwiseOr, associativity="right"): ...
class XorAssign(Assign, tokentype=tok.CaretEqual(), precedence=1, compound_op=tacky.BitwiseXOr, associativity="right"): ...
class LeftShiftAssign(Assign, tokentype=tok.LessLessEqual(), precedence=1, compound_op=tacky.LeftShift, associativity="right"): ...
class RightShigfAssign(Assign, tokentype=tok.GreaterGreaterEqual(), precedence=1, compound_op=tacky.RightShift, associativity="right"): ...
# fmt: on


class And(Binary, tokentype=tok.AmpersandAmpersand(), precedence=10):
    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        dst = tacky.Variable(make_temp_variable_name())
        false_label = make_label_name("and.false")
        end_label = make_label_name("and.end")

        left = self.left.emit(instructions)
        instructions.append(tacky.JumpIfZero(left, false_label))

        right = self.right.emit(instructions)
        instructions.extend(
            [
                tacky.JumpIfZero(right, false_label),
                tacky.Copy(tacky.Constant(1), dst),
                tacky.Jump(end_label),
                tacky.Label(false_label),
                tacky.Copy(tacky.Constant(0), dst),
                tacky.Label(end_label),
            ]
        )

        return dst

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        super().typecheck(symbol_table, file_scope)


class Or(Binary, tokentype=tok.BarBar(), precedence=5):
    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        dst = tacky.Variable(make_temp_variable_name())
        true_label = make_label_name("or.true")
        end_label = make_label_name("or.end")

        left = self.left.emit(instructions)
        instructions.append(tacky.JumpIfNotZero(left, true_label))

        right = self.right.emit(instructions)
        instructions.extend(
            [
                tacky.JumpIfNotZero(right, true_label),
                tacky.Copy(tacky.Constant(0), dst),
                tacky.Jump(end_label),
                tacky.Label(true_label),
                tacky.Copy(tacky.Constant(1), dst),
                tacky.Label(end_label),
            ]
        )

        return dst

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        super().typecheck(symbol_table, file_scope)


class Conditional(Binary, tokentype=tok.Question(), precedence=3):
    def __init__(self, left: Expr, middle: Expr, right: Expr):
        super().__init__(left, right)
        self.middle = middle

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> "Conditional":
        left = self.left.resolve_identifiers(identifier_map, inside_func)
        middle = self.middle.resolve_identifiers(identifier_map, inside_func)
        right = self.right.resolve_identifiers(identifier_map, inside_func)
        return Conditional(left, middle, right)

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        end_label = make_label_name("end")
        else_label = make_label_name("else")
        dst = tacky.Variable(make_temp_variable_name())

        cond = self.left.emit(instructions)
        instructions.append(tacky.JumpIfZero(cond, else_label))
        then_val = self.middle.emit(instructions)
        instructions.extend(
            [
                tacky.Copy(then_val, dst),
                tacky.Jump(end_label),
                tacky.Label(else_label),
            ]
        )
        else_val = self.right.emit(instructions)
        instructions.extend(
            [
                tacky.Copy(else_val, dst),
                tacky.Label(end_label),
            ]
        )

        return dst

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        super().typecheck(symbol_table, file_scope)
        self.middle.typecheck(symbol_table, file_scope)


class FuncCall(Expr):
    def __init__(self, name: str, args: list[Expr]) -> None:
        self.name = name
        self.args = args

    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> Self:
        return self

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> "FuncCall":
        if self.name in identifier_map:
            unique_name = identifier_map[self.name]
            unique_args = []
            for arg in self.args:
                unique_args.append(arg.resolve_identifiers(identifier_map, inside_func))
            return FuncCall(unique_name.name, unique_args)
        raise ResolverError(f"undeclared function: {self.name}")

    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> Self:
        return self

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        args = [arg.emit(instructions) for arg in self.args]
        dst = tacky.Variable(make_temp_variable_name())
        instructions.append(tacky.FuncCall(self.name, args, dst))
        return dst

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        type_ = symbol_table[self.name]
        if isinstance(type_, IntType):
            raise TypeCheckerError(f"variable {self.name} used as a function name")

        assert isinstance(type_, FuncType)
        if len(type_.params) != len(self.args):
            raise TypeCheckerError(
                f"function {self.name} called with wrong number of arguments: {len(type_.params)} != {len(self.args)}"
            )

        for arg in self.args:
            arg.typecheck(symbol_table, file_scope)


class BlockItem(Emitter, Resolver, TypeChecker): ...


class Declaration(BlockItem, ToTacky):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name


class VarDecl(Declaration):
    def __init__(
        self, name: str, expr: Expr | None, type_: tok.TypeSpecifier, storage_class: tok.StorageSpecifier | None
    ) -> None:
        super().__init__(name)
        self.expr = expr
        self.type_ = type_
        self.storage_class = storage_class

    def __repr__(self) -> str:
        expr = repr(self.expr)
        return f"VariableleDeclaration({self.name} = {expr} {self.storage_class})"

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        if self.expr is not None and self.storage_class is None:
            v = self.expr.emit(instructions)
            instructions.append(tacky.Copy(v, tacky.Variable(self.name)))
        return tacky.Null()

    def to_tacky(self, symbol_table: SymbolTable) -> tacky.Variable | None:
        match symbol_table[self.name].attrs:
            case attrs if isinstance(attrs, StaticAttrs):
                return None
            case attrs if isinstance(attrs, LocalAttrs):
                return tacky.Variable(self.name)
            case _:
                Unreachable()

    def resolve_identifiers_file_scope(self, identifier_map: dict[str, MapEntry]) -> "VarDecl":
        identifier_map[self.name] = MapEntry(self.name, True, True)
        return self

    def resolve_identifiers_block_scope(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> "VarDecl":
        if self.name in identifier_map:
            prev_entry = identifier_map[self.name]
            if prev_entry.from_current_scope:
                if not (prev_entry.has_linkage and self.storage_class is tok.Extern()):
                    raise ResolverError(f"conflicting local definitions for {self.name}")

        if self.storage_class is tok.Extern():
            identifier_map[self.name] = MapEntry(self.name, True, True)
            return self
        else:
            unique_name = make_variable_name(self.name)
            identifier_map[self.name] = MapEntry(unique_name, True, False)
            init = self.expr.resolve_identifiers(identifier_map, inside_func) if self.expr is not None else None
            return VarDecl(unique_name, init, self.type_, self.storage_class)

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> "VarDecl":
        if inside_func:
            return self.resolve_identifiers_block_scope(identifier_map, inside_func)
        else:
            return self.resolve_identifiers_file_scope(identifier_map)

    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> Self:
        return self

    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> Self:
        return self

    def typecheck_file_scope(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        assert file_scope

        if self.expr is None:
            if self.storage_class is tok.Extern():
                initial_value: InitialValue = NoInitializer()
            else:
                initial_value = Tentative()
        elif isinstance(self.expr, Constant):
            initial_value = Initial(self.expr.value)
        else:
            raise TypeCheckerError(f"non-constant initializer for {self.name}: {self.expr}")

        globl = self.storage_class is not tok.Static()

        if self.name in symbol_table:
            old_decl = symbol_table[self.name]

            # file-scope variables must be static
            if not isinstance(old_decl.attrs, StaticAttrs):
                raise TypeCheckerError(f"cannot redeclare function {self.name} as file-scope variable")

            if not isinstance(old_decl, IntType):
                raise TypeCheckerError(f"function {self.name} redefined as variable")

            assert isinstance(old_decl, IntType)
            if self.storage_class is tok.Extern():
                globl = old_decl.attrs.globl
            elif old_decl.attrs.globl != globl:
                raise TypeCheckerError(f"conflicting variable linkage for {self.name}")

            if isinstance(old_decl.attrs.initial_value, Initial):
                if isinstance(initial_value, Initial):
                    raise TypeCheckerError(f"conflicting file-scope variable definitions: {self.name}")
                else:
                    initial_value = old_decl.attrs.initial_value
            elif not isinstance(initial_value, Initial) and old_decl.attrs.initial_value == Tentative():
                initial_value = Tentative()

        attrs = StaticAttrs(initial_value, globl)
        symbol_table[self.name] = IntType(attrs)

    def typecheck_block_scope(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        assert not file_scope

        if self.storage_class is tok.Extern():
            if self.expr is not None:
                raise TypeCheckerError(f"initializer on local extern variable declaration for {self.name}")
            elif self.name in symbol_table:
                old_decl = symbol_table[self.name]
                if not isinstance(old_decl, IntType):
                    raise TypeCheckerError(f"function {self.name} redecalred as variable")
            else:
                symbol_table[self.name] = IntType(StaticAttrs(NoInitializer(), True))

        elif self.storage_class is tok.Static():
            if isinstance(self.expr, Constant):
                initial_value = Initial(self.expr.value)
            elif self.expr is None:
                initial_value = Initial(0)
            else:
                raise TypeCheckerError(f"non-constant initializer on local static variable {self.name}")
            symbol_table[self.name] = IntType(StaticAttrs(initial_value, False))
        else:
            symbol_table[self.name] = IntType(LocalAttrs())
            if self.expr is not None:
                self.expr.typecheck(symbol_table, file_scope)

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        if file_scope:
            self.typecheck_file_scope(symbol_table, file_scope)
        else:
            self.typecheck_block_scope(symbol_table, file_scope)


class FuncDecl(Declaration):
    def __init__(
        self,
        name: str,
        params: list[Variable],
        body: "Block | None",
        type_: tok.TypeSpecifier,
        storage_class: tok.StorageSpecifier | None,
    ) -> None:
        super().__init__(name)
        self.params = params
        self.body = body
        self.type_ = type_
        self.storage_class = storage_class

    def __repr__(self) -> str:
        body = "" if self.body is None else repr(self.body)
        return f"{self.name}\n{body}"

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        # called when a function is defined below the top-level
        assert self.body is None
        return tacky.Null()

    def to_tacky(self, symbol_table) -> tacky.FuncDecl | None:
        # called when a function is defined at the top-level
        if self.body is None:
            return None

        params = [tacky.Variable(param.name) for param in self.params]
        assert isinstance((attrs := symbol_table[self.name].attrs), FuncAttrs)

        # if self.body is None:
        #     return tacky.FuncDecl(self.name, attrs.globl, params, [])

        instructions: list[tacky.Instruction] = []
        for block_item in self.body.items:
            _ = block_item.emit(instructions)
        instructions.append(tacky.Return(tacky.Constant(0)))
        return tacky.FuncDecl(self.name, attrs.globl, params, instructions)

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> "FuncDecl":
        if inside_func and self.body is not None:
            raise ResolverError(f"cannot define function {self.name} inside function")

        if inside_func and self.storage_class is tok.Static():
            raise ResolverError(f"function {self.name} in block scope cannot be static")

        if self.name in identifier_map:
            prev_entry = identifier_map[self.name]
            if prev_entry.from_current_scope and not prev_entry.has_linkage:
                raise ResolverError(f"duplication function definition: {self.name}")

        identifier_map[self.name] = MapEntry(self.name, True, True)

        inner_identifier_map = self.copy_variable_map(identifier_map)

        params = []
        for param in self.params:
            # function parameters are like variable declarations inside function scope
            var_decl = VarDecl(param.name, None, tok.Int(), None).resolve_identifiers(inner_identifier_map, True)
            params.append(Variable.from_str(var_decl.name))
        body = None if self.body is None else self.body.resolve_identifiers(inner_identifier_map, True)

        return FuncDecl(self.name, params, body, self.type_, self.storage_class)

    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> "FuncDecl":
        body = None if self.body is None else self.body.resolve_goto_labels(labels, self.name)

        for label, defined in labels.items():
            if not defined:
                raise ResolverError(f"goto undefined label: {label}")

        return FuncDecl(self.name, self.params, body, self.type_, self.storage_class)

    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> "FuncDecl":
        body = None if self.body is None else self.body.resolve_loop_labels(current_label, self.name)
        return FuncDecl(self.name, self.params, body, self.type_, self.storage_class)

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        params: list[Type] = [IntType(LocalAttrs()) for _ in self.params]
        has_body = self.body is not None
        already_defined = False
        globl = not isinstance(self.storage_class, tok.Static)

        if self.name in symbol_table:
            old_decl = symbol_table[self.name]

            if not isinstance(old_decl, FuncType):
                raise TypeCheckerError(f"incompatible function declarations for: {self.name}")
            elif len(old_decl.params) != len(params):
                raise TypeCheckerError(f"function {self.name} redefined from {len(old_decl.params)} to {len(params)} parameters")
            elif old_decl.params != params:
                old_params = " ".join(map(repr, old_decl.params))
                new_params = " ".join(map(repr, params))
                raise TypeCheckerError(
                    f"function {self.name} defined with different params: ({old_params}) != ({new_params})"
                )

            assert isinstance(old_decl.attrs, FuncAttrs)

            already_defined = old_decl.attrs.defined
            if already_defined and has_body:
                raise TypeCheckerError(f"function {self.name} is defined more than once")

            if (
                old_decl.attrs.globl
                and isinstance(self.storage_class, tok.StorageSpecifier)
                and isinstance(self.storage_class, tok.Static)
            ):
                raise TypeCheckerError(f"static function decl follows non-static for {self.name}")
            globl = old_decl.attrs.globl

        defined = already_defined or has_body
        attrs = FuncAttrs(defined, globl)
        symbol_table[self.name] = FuncType(params, has_body or already_defined, attrs)
        if has_body:
            for param in self.params:
                symbol_table[param.name] = IntType(LocalAttrs())
            assert self.body is not None
            self.body.typecheck(symbol_table, file_scope)


class Stmt(BlockItem): ...


class Block(Stmt):
    def __init__(self, items: list[BlockItem]) -> None:
        self.items = items

    def __repr__(self) -> str:
        return "\n" + "\n".join("        " + repr(item) for item in self.items)

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        for item in self.items:
            _ = item.emit(instructions)
        return tacky.Null()

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> "Block":
        items = [item.resolve_identifiers(identifier_map, inside_func) for item in self.items]
        return Block(items)

    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> "Block":
        return Block([item.resolve_goto_labels(labels, function_name) for item in self.items])

    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> "Block":
        items = [item.resolve_loop_labels(current_label, function_name) for item in self.items]
        return Block(items)

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        for item in self.items:
            item.typecheck(symbol_table, False)


class Return(Stmt):
    def __init__(self, expr: Expr) -> None:
        self.expr = expr

    def __repr__(self) -> str:
        expr = repr(self.expr)
        return f"Return({expr})"

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        dst = self.expr.emit(instructions)
        instructions.append(tacky.Return(dst))
        return dst

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> "Return":
        return Return(self.expr.resolve_identifiers(identifier_map, inside_func))

    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> Self:
        return self

    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> Self:
        return self

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        self.expr.typecheck(symbol_table, file_scope)


class Expression(Stmt):
    def __init__(self, expr: Expr) -> None:
        self.expr = expr

    def __repr__(self) -> str:
        expr = repr(self.expr)
        return f"Expression({expr})"

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        return self.expr.emit(instructions)

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> "Expression":
        return Expression(self.expr.resolve_identifiers(identifier_map, inside_func))

    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> Self:
        return self

    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> Self:
        return self

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        self.expr.typecheck(symbol_table, file_scope)


class If(Stmt):
    def __init__(self, cond: Expr, then: Stmt, else_: Stmt | None) -> None:
        self.cond = cond
        self.then = then
        self.else_ = else_

    def __repr__(self) -> str:
        cond = repr(self.cond)
        then = repr(self.then)
        else_ = None if self.else_ is None else repr(self.else_)
        return f"If({cond} ? {then} : {else_})"

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        end_label = make_label_name("end")
        else_label = make_label_name("else")
        cond = self.cond.emit(instructions)
        instructions.append(tacky.JumpIfZero(cond, else_label))
        _ = self.then.emit(instructions)
        instructions.extend(
            [
                tacky.Jump(end_label),
                tacky.Label(else_label),
            ]
        )
        if self.else_ is not None:
            _ = self.else_.emit(instructions)
        instructions.append(tacky.Label(end_label))
        return tacky.Null()

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> "If":
        cond = self.cond.resolve_identifiers(identifier_map, inside_func)
        then = self.then.resolve_identifiers(identifier_map, inside_func)
        else_ = None if self.else_ is None else self.else_.resolve_identifiers(identifier_map, inside_func)
        return If(cond, then, else_)

    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> "If":
        then = self.then.resolve_goto_labels(labels, function_name)
        else_ = None if self.else_ is None else self.else_.resolve_goto_labels(labels, function_name)
        return If(self.cond, then, else_)

    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> "If":
        then = self.then.resolve_loop_labels(current_label, function_name)
        else_ = None if self.else_ is None else self.else_.resolve_loop_labels(current_label, function_name)
        return If(self.cond, then, else_)

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        self.cond.typecheck(symbol_table, file_scope)
        self.then.typecheck(symbol_table, file_scope)
        self.else_.typecheck(symbol_table, file_scope) if self.else_ is not None else ...


class Label(Stmt):
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"Label({self.name})"

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        instructions.append(tacky.Label(self.name))
        return tacky.Null()

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> Self:
        return self

    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> "Label":
        name = self.mangle_label(self.name, function_name)

        if (seen := labels.get(name)) is not None and seen:
            raise ResolverError(f"label already used: {name}")
        else:
            labels[name] = True

        return Label(name)

    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> Self:
        return self

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        pass


class Goto(Stmt):
    def __init__(self, target: str) -> None:
        self.target = target

    def __repr__(self) -> str:
        return f"Goto({self.target})"

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        instructions.append(tacky.Jump(self.target))
        return tacky.Null()

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> Self:
        return self

    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> "Goto":
        name = self.mangle_label(self.target, function_name)
        if name not in labels:
            labels[name] = False

        return Goto(name)

    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> Self:
        return self

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        pass


class Compound(Stmt):
    def __init__(self, block: Block) -> None:
        self.block = block

    def __repr__(self) -> str:
        return f"Block({self.block})"

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        return self.block.emit(instructions)

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> "Compound":
        inner_identifier_map = self.copy_variable_map(identifier_map)
        return Compound(self.block.resolve_identifiers(inner_identifier_map, inside_func))

    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> "Compound":
        return Compound(self.block.resolve_goto_labels(labels, function_name))

    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> "Compound":
        return Compound(self.block.resolve_loop_labels(current_label, function_name))

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        self.block.typecheck(symbol_table, file_scope)


class Break(Stmt):
    def __init__(self, label: str | None = None) -> None:
        self.label = label

    def __repr__(self) -> str:
        label = "" if self.label is None else self.label
        return f"Break({label})"

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> Self:
        return self

    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> Self:
        return self

    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> "Break":
        if current_label is None:
            raise ResolverError("break statement outside of loop")
        return Break(current_label)

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        assert self.label is not None
        instructions.append(tacky.Jump(f"__break__{self.label}"))
        return tacky.Null()

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        pass


class Continue(Stmt):
    def __init__(self, label: str | None = None) -> None:
        self.label = label

    def __repr__(self) -> str:
        label = "" if self.label is None else self.label
        return f"Continue({label})"

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> Self:
        return self

    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> Self:
        return self

    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> "Continue":
        if current_label is None:
            raise ResolverError("continue statement outside of loop")
        return Continue(current_label)

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        assert self.label is not None
        instructions.append(tacky.Jump(f"__continue__{self.label}"))
        return tacky.Null()

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        pass


class While(Stmt):
    def __init__(self, cond: Expr, body: Stmt, label: str | None = None) -> None:
        self.cond = cond
        self.body = body
        self.label = label

    def __repr__(self) -> str:
        cond = repr(self.cond)
        body = repr(self.body)

        return f"""
        While|{self.label}| ({cond})
          {body.replace("\n", "\n        ")}
        ) """.strip()

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> "While":
        cond = self.cond.resolve_identifiers(identifier_map, inside_func)
        body = self.body.resolve_identifiers(identifier_map, inside_func)
        return While(cond, body)

    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> "While":
        body = self.body.resolve_goto_labels(labels, function_name)
        return While(self.cond, body)

    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> "While":
        current_label = make_label_name(f"while.{function_name}")
        body = self.body.resolve_loop_labels(current_label, function_name)
        return While(self.cond, body, current_label)

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        assert self.label is not None
        continue_ = tacky.Label(f"__continue__{self.label}")
        break_ = tacky.Label(f"__break__{self.label}")

        instructions.append(continue_)
        dst = self.cond.emit(instructions)
        instructions.append(tacky.JumpIfZero(dst, break_.label))
        _ = self.body.emit(instructions)
        instructions.extend(
            [
                tacky.Jump(continue_.label),
                break_,
            ]
        )

        return tacky.Null()

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        self.cond.typecheck(symbol_table, file_scope)
        self.body.typecheck(symbol_table, file_scope)


class DoWhile(Stmt):
    def __init__(self, cond: Expr, body: Stmt, label: str | None = None) -> None:
        self.cond = cond
        self.body = body
        self.label = label

    def __repr__(self) -> str:
        cond = repr(self.cond)
        body = repr(self.body)

        return f"""
        Do|{self.label}| (
          {body.replace("\n", "\n        ")}
        ) While ({cond})""".strip()

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> "DoWhile":
        cond = self.cond.resolve_identifiers(identifier_map, inside_func)
        body = self.body.resolve_identifiers(identifier_map, inside_func)
        return DoWhile(cond, body)

    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> "DoWhile":
        body = self.body.resolve_goto_labels(labels, function_name)
        return DoWhile(self.cond, body)

    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> "DoWhile":
        current_label = make_label_name(f"dowhile.{function_name}")
        body = self.body.resolve_loop_labels(current_label, function_name)
        return DoWhile(self.cond, body, current_label)

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        assert self.label is not None
        start = tacky.Label(f"__start__{self.label}")
        continue_ = tacky.Label(f"__continue__{self.label}")
        break_ = tacky.Label(f"__break__{self.label}")

        instructions.append(start)
        _ = self.body.emit(instructions)
        instructions.append(continue_)
        dst = self.cond.emit(instructions)
        instructions.extend(
            [
                tacky.JumpIfNotZero(dst, start.label),
                break_,
            ]
        )
        return tacky.Null()

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        self.cond.typecheck(symbol_table, file_scope)
        self.body.typecheck(symbol_table, file_scope)


class For(Stmt):
    def __init__(
        self,
        init: Expr | Declaration | None,
        cond: Expr | None,
        post: Expr | None,
        body: Stmt,
        label: str | None = None,
    ) -> None:
        self.init = init
        self.cond = cond
        self.post = post
        self.body = body
        self.label = label

    def __repr__(self) -> str:
        init = None if self.init is None else repr(self.init)
        cond = None if self.cond is None else repr(self.cond)
        post = None if self.post is None else repr(self.post)
        body = repr(self.body)

        return f"""
        For|{self.label}| (
          init = {init}
          cond = {cond}
          post = {post}
          {body.replace("\n", "\n        ")}
        )""".strip()

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> "For":
        new_identifier_map = self.copy_variable_map(identifier_map)
        init = None if self.init is None else self.init.resolve_identifiers(new_identifier_map, inside_func)
        cond = None if self.cond is None else self.cond.resolve_identifiers(new_identifier_map, inside_func)
        post = None if self.post is None else self.post.resolve_identifiers(new_identifier_map, inside_func)
        body = self.body.resolve_identifiers(new_identifier_map, inside_func)
        return For(init, cond, post, body)

    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> "For":
        body = self.body.resolve_goto_labels(labels, function_name)
        return For(self.init, self.cond, self.post, body)

    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> "For":
        current_label = make_label_name(f"for.{function_name}")
        body = self.body.resolve_loop_labels(current_label, function_name)
        return For(self.init, self.cond, self.post, body, current_label)

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        assert self.label is not None
        start = tacky.Label(f"__start__{self.label}")
        continue_ = tacky.Label(f"__continue__{self.label}")
        break_ = tacky.Label(f"__break__{self.label}")

        if self.init is not None:
            _ = self.init.emit(instructions)
        instructions.append(start)
        if self.cond is not None:
            dst = self.cond.emit(instructions)
            instructions.append(tacky.JumpIfZero(dst, break_.label))
        _ = self.body.emit(instructions)
        instructions.append(continue_)
        if self.post is not None:
            _ = self.post.emit(instructions)
        instructions.extend(
            [
                tacky.Jump(start.label),
                break_,
            ]
        )

        return tacky.Null()

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        self.init.typecheck(symbol_table, file_scope) if self.init is not None else ...
        if isinstance(self.init, Declaration):
            assert not isinstance(self.init, FuncDecl)
            assert not isinstance((init := symbol_table[self.init.name]), FuncType)
            if not isinstance(init.attrs, LocalAttrs):
                raise TypeCheckerError(f"cannot apply storage-class specifiers in for loop init for {self.init}")

        self.cond.typecheck(symbol_table, file_scope) if self.cond is not None else ...
        self.body.typecheck(symbol_table, file_scope)
        self.post.typecheck(symbol_table, file_scope) if self.post is not None else ...


class Null(Stmt):
    def __init__(self):
        pass

    def __repr__(self) -> str:
        return "Null()"

    def emit(self, instructions: list[tacky.Instruction]) -> tacky.Value:
        return tacky.Null()

    def resolve_identifiers(self, identifier_map: dict[str, MapEntry], inside_func: bool) -> "Null":
        return Null()

    def resolve_goto_labels(self, labels: dict[str, bool], function_name: str) -> "Null":
        return Null()

    def resolve_loop_labels(self, current_label: str | None, function_name: str) -> "Null":
        return Null()

    def typecheck(self, symbol_table: SymbolTable, file_scope: bool) -> None:
        pass


class Program:
    def __init__(self, decls: list[Declaration], symbol_table: SymbolTable) -> None:
        self.decls = decls
        self.symbol_table = symbol_table

    def __repr__(self) -> str:
        return "\n".join(decl.name + ":\n" + repr(decl) for decl in self.decls)

    def convert_symbols_to_tacky(self) -> list[tacky.TopLevel]:
        tacky_defs: list[tacky.TopLevel] = []
        for name, entry in self.symbol_table.items():
            if isinstance(entry, FuncType):
                continue

            attrs = entry.attrs
            if not isinstance(attrs, StaticAttrs):
                continue

            assert isinstance(attrs.initial_value, InitialValue)
            if isinstance((init := attrs.initial_value), Initial):
                tacky_defs.append(tacky.StaticVar(name, attrs.globl, init.value))
            elif isinstance(attrs.initial_value, Tentative):
                tacky_defs.append(tacky.StaticVar(name, attrs.globl, 0))
            elif isinstance(attrs.initial_value, NoInitializer):
                continue
            else:
                Unreachable()

        return tacky_defs

    def to_tacky(self) -> tacky.Program:
        decls = [decl.to_tacky(self.symbol_table) for decl in self.decls]
        decls.extend(self.convert_symbols_to_tacky())
        return tacky.Program([f for f in decls if f is not None], self.symbol_table)

    def resolve(self) -> "Program":
        decls = []
        identifier_map: dict[str, MapEntry] = {}
        for decl in self.decls:
            decl = decl.resolve_identifiers(identifier_map, False)
            decl = decl.resolve_goto_labels({}, decl.name)
            decl = decl.resolve_loop_labels(None, decl.name)
            decl.typecheck(self.symbol_table, True)
            decls.append(decl)
        return Program(decls, self.symbol_table)


if __name__ == "__main__":
    expr: Expr = Constant(3)
    expr = Unary.from_tokentype(tok.Hyphen)(expr)
    expr = Unary.from_tokentype(tok.Tilde)(expr)

    instructions: list[tacky.Instruction] = []
    print(expr.emit(instructions))
    print(instructions)
