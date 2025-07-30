from typing import Callable, Never, Protocol, TypeVar

KT = TypeVar("KT")
VT = TypeVar("VT")


class Singleton(Protocol):
    def __new__(cls):
        try:
            return getattr(cls, "instance")
        except AttributeError:
            instance = super(Singleton, cls).__new__(cls)
            setattr(cls, "instance", instance)
            return instance


class MappingHolder[KT, VT]:
    mapping: dict[KT, VT] = {}

    def __init_subclass__(cls, cls1: KT | None = None, cls2: VT | None = None) -> None:
        if cls1 is not None and cls2 is not None:
            cls.mapping[cls1] = cls2
        elif cls1 is None and cls2 is None:
            cls.mapping = {}
        else:
            raise ValueError("both KT and VT should be None or not None")


def Unreachable() -> Never:
    assert False, "unreachable"


Instr = TypeVar("Instr")
Res = TypeVar("Res")


class Emitter[Instr, Res](Protocol):
    def emit(self, instructions: list[Instr]) -> Res: ...


def make_make_temp_variable() -> Callable[[], str]:
    counter = 0

    def make_temp_variable() -> str:
        nonlocal counter
        counter += 1
        return f".tmpvar.{counter}"

    return make_temp_variable


def make_make_variable() -> Callable[[str], str]:
    counter = 0

    def make_variable(name: str) -> str:
        nonlocal counter
        counter += 1
        return f".var.{name}.{counter}"

    return make_variable


def make_make_label() -> Callable[[str], str]:
    counter = 0

    def make_label(name: str) -> str:
        nonlocal counter
        counter += 1
        return f".label.{name}.{counter}"

    return make_label


make_temp_variable_name = make_make_temp_variable()
make_variable_name = make_make_variable()
make_label_name = make_make_label()
