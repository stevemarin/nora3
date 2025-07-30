from typing import TypeVar


class InitialValue: ...


class Tentative(InitialValue):
    def __eq__(self, value: object) -> bool:
        return isinstance(value, Tentative)


class Initial(InitialValue):
    def __init__(self, value: int) -> None:
        self.value = value

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Initial) and self.value == value.value


class NoInitializer(InitialValue):
    def __eq__(self, value: object) -> bool:
        return isinstance(value, NoInitializer)


class IdentifierAttrs: ...


class FuncAttrs(IdentifierAttrs):
    def __init__(self, defined: bool, globl: bool) -> None:
        self.defined = defined
        self.globl = globl

    def __eq__(self, value: object, /) -> bool:
        return isinstance(value, FuncAttrs) and self.defined == value.defined and self.globl == value.globl


class StaticAttrs(IdentifierAttrs):
    def __init__(self, initial_value: InitialValue, globl: bool) -> None:
        self.initial_value = initial_value
        self.globl = globl

    def __eq__(self, value: object, /) -> bool:
        return (
            isinstance(value, StaticAttrs) and self.initial_value == value.initial_value and self.globl == value.globl
        )


class LocalAttrs(IdentifierAttrs):
    def __eq__(self, value: object, /) -> bool:
        return isinstance(value, LocalAttrs)


class Type: ...


class FuncType(Type):
    def __init__(self, params: list[Type], defined: bool, attrs: IdentifierAttrs) -> None:
        self.params = params
        self.defined = defined
        self.attrs = attrs

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, FuncType) or len(self.params) != len(value.params):
            return False

        for idx in range(len(self.params)):
            if self.params[idx] != value.params[idx]:
                return False

        return True

    def __repr__(self) -> str:
        params = " ".join(map(repr, self.params))
        return f"FuncType({params})"


class IntType(Type):
    def __init__(self, attrs: IdentifierAttrs) -> None:
        self.attrs = attrs

    def __eq__(self, value: object, /) -> bool:
        return isinstance(value, IntType)

    def __repr__(self) -> str:
        return "IntType()"


Res = TypeVar("Res")
SymbolTable = dict[str, IntType | FuncType]
