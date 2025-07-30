from typing import Protocol, TypeVar
from nora3 import asm
from nora3.builtin_types import SymbolTable
from nora3.common import MappingHolder, Emitter


class TackyGenerationError(Exception): ...


Res = TypeVar("Res")


class ToAsm[Res](Protocol):
    def to_asm(self) -> Res: ...


class Value(ToAsm): ...


class Constant(Value):
    def __init__(self, value: int) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"Constant({self.value})"

    def to_asm(self) -> asm.Imm:
        return asm.Imm(self.value)


class Null(Value):
    def __init__(self):
        pass

    def __repr__(self) -> str:
        return "Null()"

    def to_asm(self) -> asm.Null:
        return asm.Null()


class Variable(Value):
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"Variable({self.name})"

    def to_asm(self) -> asm.Pseudo:
        return asm.Pseudo(self.name)


class Instruction(Emitter): ...


class Return(Instruction):
    def __init__(self, value: Value) -> None:
        self.value = value

    def __repr__(self) -> str:
        value = repr(self.value)
        return f"Ret({value})"

    def emit(self, instructions: list[asm.Instruction]) -> None:
        assert isinstance((src := self.value.to_asm()), asm.Operand)
        dst = asm.Ax(4)
        instructions.extend(
            [
                asm.Mov(src, dst),
                asm.Ret(),
            ]
        )


class Unary(Instruction, MappingHolder):
    def __init_subclass__(cls, op: type[asm.Unary] | None = None) -> None:
        cls.mapping[cls] = op

    def __init__(self, src: Value, dst: Value) -> None:
        self.src = src
        self.dst = dst

    def __repr__(self) -> str:
        src = repr(self.src)
        dst = repr(self.dst)
        return f"{self.__class__.__name__}({src} -> {dst})"

    def emit(self, instructions: list[asm.Instruction]) -> None:
        src = self.src.to_asm()
        dst = self.dst.to_asm()
        instructions.extend(
            [
                asm.Mov(src, dst),
                self.mapping[self.__class__](dst),
            ]
        )


# fmt: off
class Complement(Unary, op=asm.Not): ...
class Negate(Unary, op=asm.Neg): ...
# fmt: on

# TODO use x86 inc/dec functions


class PrefixIncrement(Unary):
    def __init__(self, src: Value, dst: Value) -> None:
        self.src = src
        self.dst = dst

    def emit(self, instructions: list[asm.Instruction]) -> None:
        src = self.src.to_asm()
        dst = self.dst.to_asm()
        instructions.extend(
            [
                asm.Add(asm.Imm(1), src),
                asm.Mov(src, dst),
            ]
        )


class PrefixDecrement(Unary):
    def emit(self, instructions: list[asm.Instruction]) -> None:
        src = self.src.to_asm()
        dst = self.dst.to_asm()
        instructions.extend(
            [
                asm.Subtract(asm.Imm(1), src),
                asm.Mov(src, dst),
            ]
        )


class PostfixIncrement(Unary):
    def emit(self, instructions: list[asm.Instruction]) -> None:
        src = self.src.to_asm()
        dst = self.dst.to_asm()
        instructions.extend(
            [
                asm.Mov(src, dst),
                asm.Add(asm.Imm(1), src),
            ]
        )


class PostfixDecrement(Unary):
    def emit(self, instructions: list[asm.Instruction]) -> None:
        src = self.src.to_asm()
        dst = self.dst.to_asm()
        instructions.extend(
            [
                asm.Mov(src, dst),
                asm.Subtract(asm.Imm(1), src),
            ]
        )


class Not(Unary):
    def emit(self, instructions: list[asm.Instruction]) -> None:
        src = self.src.to_asm()
        dst = self.dst.to_asm()
        instructions.extend(
            [
                asm.Cmp(asm.Imm(0), src),
                asm.Mov(asm.Imm(0), dst),
                asm.SetCC("e", dst),
            ]
        )


class Binary(Instruction, MappingHolder):
    mode: str
    op: type[asm.Binary] | None
    cc: str | None
    reg: type[asm.Register] | None

    def __init_subclass__(
        cls,
        mode: str,
        op: type[asm.Binary] | None = None,
        cond: str | None = None,
        reg: type[asm.Register] | None = None,
    ) -> None:
        assert mode in {"arithmatic", "division", "relational"}
        cls.mode = mode
        cls.op = op
        cls.cc = cond
        cls.reg = reg

    def __init__(self, left: Value, right: Value, dst: Value) -> None:
        self.left = left
        self.right = right
        self.dst = dst

    def __repr__(self) -> str:
        left = repr(self.left)
        right = repr(self.right)
        dst = repr(self.dst)
        return f"{self.__class__.__name__}({left} . {right} -> {dst})"

    def emit_arithmatic(self, instructions: list[asm.Instruction]) -> None:
        assert self.op is not None
        left = self.left.to_asm()
        right = self.right.to_asm()
        dst = self.dst.to_asm()
        instructions.extend(
            [
                asm.Mov(left, dst),
                self.op(right, dst),
            ]
        )

    def emit_division(self, instructions: list[asm.Instruction]) -> None:
        assert self.reg is not None
        left = self.left.to_asm()
        right = self.right.to_asm()
        dst = self.dst.to_asm()
        instructions.extend(
            [
                asm.Mov(left, asm.Ax(4)),
                asm.Cdq(),
                asm.Idiv(right),
                asm.Mov(self.reg(4), dst),
            ]
        )

    def emit_comparison(self, instructions: list[asm.Instruction]) -> None:
        assert self.cc is not None
        left = self.left.to_asm()
        right = self.right.to_asm()
        dst = self.dst.to_asm()
        instructions.extend(
            [
                asm.Cmp(right, left),
                asm.Mov(asm.Imm(0), dst),
                asm.SetCC(self.cc, dst),
            ]
        )

    def emit(self, instructions: list[asm.Instruction]) -> None:
        match self.mode:
            case "arithmatic":
                self.emit_arithmatic(instructions)
            case "division":
                self.emit_division(instructions)
            case "relational":
                self.emit_comparison(instructions)
            case t:
                raise ValueError(f"unknown binary operator type: {t}")


# fmt: off
class Add(Binary, mode="arithmatic", op=asm.Add): ...
class Subtract(Binary, mode="arithmatic", op=asm.Subtract): ...
class Multiply(Binary, mode="arithmatic", op=asm.Multiply): ...
class LeftShift(Binary, mode="arithmatic", op=asm.LeftShift): ...
class RightShift(Binary, mode="arithmatic", op=asm.RightShift): ...
class BitwiseAnd(Binary, mode="arithmatic", op=asm.BitwiseAnd): ...
class BitwiseOr(Binary, mode="arithmatic", op=asm.BitwiseOr): ...
class BitwiseXOr(Binary, mode="arithmatic", op=asm.BitwiseXor): ...
class Equal(Binary, mode="relational", cond="e"): ...
class NotEqual(Binary, mode="relational", cond="ne"): ...
class LessThan(Binary, mode="relational", cond="l"): ...
class LessOrEqual(Binary, mode="relational", cond="le"): ...
class GreaterThan(Binary, mode="relational", cond="g"): ...
class GreaterOrEqual(Binary, mode="relational", cond="ge"): ...
class Divide(Binary, mode="division", reg=asm.Ax): ...
class Remainder(Binary, mode="division", reg=asm.Dx): ...
# fmt: on


class Copy(Instruction):
    def __init__(self, src: Value, dst: Value) -> None:
        self.src = src
        self.dst = dst

    def __repr__(self) -> str:
        src = repr(self.src)
        dst = repr(self.dst)
        return f"Copy({src} -> {dst})"

    def emit(self, instructions: list[asm.Instruction]) -> None:
        src = self.src.to_asm()
        dst = self.dst.to_asm()
        instructions.append(asm.Mov(src, dst))


class Jump(Instruction):
    def __init__(self, label: str) -> None:
        self.label = label

    def __repr__(self) -> str:
        return f"Jump({self.label})"

    def emit(self, instructions: list[asm.Instruction]) -> None:
        instructions.append(asm.Jmp(self.label))


class JumpIfZero(Instruction):
    def __init__(self, cond: Value, label: str) -> None:
        self.cond = cond
        self.label = label

    def __repr__(self) -> str:
        cond = repr(self.cond)
        return f"JumpIfZero({cond} -> {self.label})"

    def emit(self, instructions: list[asm.Instruction]) -> None:
        instructions.extend(
            [
                asm.Cmp(asm.Imm(0), self.cond.to_asm()),
                asm.JmpCC("e", self.label),
            ]
        )


class JumpIfNotZero(Instruction):
    def __init__(self, cond: Value, label: str) -> None:
        self.cond = cond
        self.label = label

    def __repr__(self) -> str:
        cond = repr(self.cond)
        return f"JumpIfNotZero({cond} -> {self.label})"

    def emit(self, instructions: list[asm.Instruction]) -> None:
        instructions.extend(
            [
                asm.Cmp(asm.Imm(0), self.cond.to_asm()),
                asm.JmpCC("ne", self.label),
            ]
        )


class Label(Instruction):
    def __init__(self, label: str) -> None:
        self.label = label

    def __repr__(self) -> str:
        return f"Label({self.label})"

    def emit(self, instructions: list[asm.Instruction]) -> None:
        instructions.append(asm.Label(self.label))


class FuncCall(Instruction):
    def __init__(self, name: str, args: list[Value], dst: Value) -> None:
        self.name = name
        self.args = args
        self.dst = dst

    def __repr__(self) -> str:
        args = " ".join(map(repr, self.args))
        return f"{self.name}({args} dst={self.dst})"

    def emit(self, instructions: list[asm.Instruction]) -> None:
        arg_registers = [asm.Di, asm.Si, asm.Dx, asm.Cx, asm.R8, asm.R9]

        # adjust stack size
        register_args, stack_args = self.args[:6], self.args[6:]
        stack_padding = 0 if len(stack_args) % 2 == 0 else 8

        if stack_padding != 0:
            instructions.append(asm.AllocateStack(-stack_padding))

        # pass args in registers
        for idx, tacky_arg in enumerate(register_args):
            register = arg_registers[idx]
            asm_arg = tacky_arg.to_asm()
            instructions.append(asm.Mov(asm_arg, register(4)))

        # pass args on stack
        for tacky_arg in reversed(stack_args):
            asm_arg = tacky_arg.to_asm()
            if isinstance(asm_arg, asm.Register | asm.Imm):
                instructions.append(asm.Push(asm_arg))
            else:
                instructions.extend(
                    [
                        asm.Mov(asm_arg, asm.Ax(4)),
                        asm.Push(asm.Ax(8)),
                    ]
                )

        # call function
        instructions.append(asm.Call(self.name))

        # adjust stack pointer
        bytes_to_remove = 8 * len(stack_args) + stack_padding
        if bytes_to_remove != 0:
            instructions.append(asm.DeallocateStack(bytes_to_remove))

        # get return value
        asm_dst = self.dst.to_asm()
        instructions.append(asm.Mov(asm.Ax(4), asm_dst))


class TopLevel(ToAsm):
    def __init__(self, name: str, globl: bool):
        self.name = name
        self.globl = globl


class StaticVar(TopLevel):
    def __init__(self, name: str, globl: bool, init: int) -> None:
        super().__init__(name, globl)
        self.init = init

    def __repr__(self) -> str:
        return f"StaticVar({self.name})"

    def to_asm(self) -> asm.StaticVar:
        return asm.StaticVar(self.name, self.globl, self.init)


class FuncDecl(TopLevel):
    def __init__(self, name: str, globl: bool, params: list[Variable], body: list[Instruction]) -> None:
        super().__init__(name, globl)
        self.params = params
        self.body = body

    def __repr__(self) -> str:
        body = "\n".join("    " + repr(item) for item in self.body)
        return f"{self.name}:\n{body}"

    def to_asm(self) -> asm.Function:
        instructions: list[asm.Instruction] = []

        arg_registers = [asm.Di, asm.Si, asm.Dx, asm.Cx, asm.R8, asm.R9]
        for idx, reg_param in enumerate(self.params[:6]):
            instructions.append(asm.Mov(arg_registers[idx](4), reg_param.to_asm()))

        for idx, stack_param in enumerate(self.params[6:]):
            instructions.append(asm.Mov(asm.Stack((idx + 2) * 8), stack_param.to_asm()))

        for instr in self.body:
            instr.emit(instructions)

        return asm.Function(self.name, self.globl, instructions)


class Program(ToAsm):
    def __init__(self, top_level: list[TopLevel], symbol_table: SymbolTable) -> None:
        self.top_level = top_level
        self.symbol_table = symbol_table

    def __repr__(self) -> str:
        return "\n".join(top_level.name + ":\n" + repr(top_level) for top_level in self.top_level)

    def to_asm(self) -> asm.Program:
        return asm.Program([func.to_asm() for func in self.top_level], self.symbol_table)


if __name__ == "__main__":
    instructions: list[asm.Instruction] = []
    c = Negate(Constant(3), Variable("aaa"))
    c.emit(instructions)
    print(instructions)
