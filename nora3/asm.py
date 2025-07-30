from typing import Protocol

from nora3.builtin_types import StaticAttrs, SymbolTable
from nora3.common import Unreachable


class Codegen(Protocol):
    def codegen(self) -> str: ...


class ReplacePseudo(Protocol):
    def replace_pseudo(self, stack_size: int, variable_map: dict[str, int], symbol_table: SymbolTable) -> int: ...


class FixInstructions(Protocol):
    def fix_instructions(self, instructions: list["Instruction"]) -> None: ...


class Operand(Codegen): ...


class Imm(Operand):
    def __init__(self, value: int):
        self.value = value

    def __repr__(self) -> str:
        return f"Imm({self.value})"

    def codegen(self) -> str:
        return f"${self.value}"


class Null(Operand):
    def __repr__(self) -> str:
        return "Null()"

    def codegen(self) -> str:
        return ""


class Register(Operand):
    mapping: dict[int, str]

    def __init_subclass__(cls, one: str, two: str, four: str, eight: str) -> None:
        cls.mapping = {1: one, 2: two, 4: four, 8: eight}

    def __init__(self, nbytes: int) -> None:
        assert nbytes in {1, 2, 4, 8}
        self.nbytes = nbytes

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.nbytes})"

    def as_one_byte(self) -> "Register":
        return self.__class__(1)

    def codegen(self) -> str:
        return "%" + self.mapping[self.nbytes]


# fmt: off
class Ax(Register, one="al", two="ax", four="eax", eight="rax"): ...
class Cx(Register, one="cl", two="cx", four="ecx", eight="rcx"): ...
class Dx(Register, one="dl", two="dx", four="edx", eight="rdx"): ...
class Di(Register, one="dil", two="di", four="edi", eight="rdi"): ...
class Si(Register, one="sil", two="si", four="esi", eight="rsi"): ...
class R8(Register, one="r8b", two="r8w", four="r8d", eight="r8"): ...
class R9(Register, one="r9b", two="r9w", four="r9d", eight="r9"): ...
class R10(Register, one="r10b", two="r10w", four="r10d", eight="r10"): ...
class R11(Register, one="r11b", two="r11w", four="r11d", eight="r11"): ...
# fmt: on


class Pseudo(Operand):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"Pseudo({self.name})"

    def codegen(self) -> str:
        raise Unreachable()


class Stack(Operand):
    def __init__(self, size: int):
        self.size = size

    def __repr__(self) -> str:
        return f"Stack({self.size})"

    def codegen(self) -> str:
        return f"{self.size}(%rbp)"


class Data(Operand):
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"Data({self.name})"

    def codegen(self) -> str:
        return f"{self.name}(%rip)"


class Instruction(Codegen, ReplacePseudo, FixInstructions):
    code: str

    @classmethod
    def _replace_pseudo(
        cls, pseudo: Pseudo, stack_size: int, mapping: dict[str, int], symbol_table: SymbolTable
    ) -> tuple[Stack | Data, int]:
        if pseudo.name in mapping:
            return Stack(mapping[pseudo.name]), stack_size
        else:
            if pseudo.name in symbol_table and isinstance(symbol_table[pseudo.name].attrs, StaticAttrs):
                return Data(pseudo.name), stack_size
            else:
                stack_size -= 4
                mapping[pseudo.name] = stack_size
                return Stack(stack_size), stack_size

    def replace_pseudo(self, stack_size: int, variable_map: dict[str, int], symbol_table: SymbolTable) -> int:
        for name, item in self.__dict__.items():
            if isinstance(item, Pseudo):
                stack, stack_size = self._replace_pseudo(item, stack_size, variable_map, symbol_table)
                setattr(self, name, stack)

        return stack_size

    def fix_instructions(self, instructions: list["Instruction"]) -> None:
        instructions.append(self)


class Mov(Instruction):
    code: str = "movl"

    def __init__(self, src: Operand, dst: Operand) -> None:
        self.src = src
        self.dst = dst

    def __repr__(self) -> str:
        src = repr(self.src)
        dst = repr(self.dst)
        return f"Mov({src} -> {dst})"

    def codegen(self) -> str:
        src = self.src.codegen()
        dst = self.dst.codegen()
        return f"    {self.code:6}    {src:6}, {dst:6}"

    def fix_instructions(self, instructions: list[Instruction]) -> None:
        if isinstance(self.src, Stack | Data) and isinstance(self.dst, Stack | Data):
            r10 = R10(4)
            instructions.extend(
                [
                    Mov(self.src, r10),
                    Mov(r10, self.dst),
                ]
            )
        else:
            instructions.append(self)


class Unary(Instruction):
    code: str

    def __init_subclass__(cls, code: str) -> None:
        cls.code = code

    def __init__(self, src: Operand) -> None:
        self.src = src

    def __repr__(self) -> str:
        src = repr(self.src)
        return f"{self.__class__.__name__}({src})"

    def codegen(self) -> str:
        src = self.src.codegen()
        return f"    {self.code:6}    {src:6}"


# fmt: off
class Neg(Unary, code="negl"): ...
class Not(Unary, code="notl"): ...
# fmt: on


class Binary(Instruction):
    code: str

    def __init_subclass__(cls, code: str) -> None:
        cls.code = code

    def __init__(self, src: Operand, dst: Operand) -> None:
        self.src = src
        self.dst = dst

    def __repr__(self) -> str:
        src = repr(self.src)
        dst = repr(self.dst)
        return f"{self.__class__.__name__}({src} -> {dst})"

    def codegen(self) -> str:
        src = self.src.codegen()
        dst = self.dst.codegen()
        return f"    {self.code:6}    {src:6}, {dst:6}"


class Add(Binary, code="addl"):
    def fix_instructions(self, instructions: list["Instruction"]) -> None:
        if isinstance(self.src, Stack | Data) and isinstance(self.dst, Stack | Data):
            r10 = R10(4)
            instructions.extend(
                [
                    Mov(self.src, r10),
                    Add(r10, self.dst),
                ]
            )
        else:
            instructions.append(self)


class Subtract(Binary, code="subl"):
    def fix_instructions(self, instructions: list["Instruction"]) -> None:
        if isinstance(self.src, Stack | Data) and isinstance(self.dst, Stack | Data):
            r10 = R10(4)
            instructions.extend(
                [
                    Mov(self.src, r10),
                    Subtract(r10, self.dst),
                ]
            )
        else:
            instructions.append(self)


class Multiply(Binary, code="imull"):
    def fix_instructions(self, instructions: list["Instruction"]) -> None:
        if isinstance(self.dst, Stack | Data):
            r11 = R11(4)
            instructions.extend(
                [
                    Mov(self.dst, r11),
                    Multiply(self.src, r11),
                    Mov(r11, self.dst),
                ]
            )
        else:
            instructions.append(self)


class LeftShift(Binary, code="sall"):
    def fix_instructions(self, instructions: list["Instruction"]) -> None:
        if isinstance(self.src, Imm) or (isinstance(self.src, Register) and self.src.nbytes == 1):
            instructions.append(self)
        else:
            cx = Cx(4)
            instructions.extend(
                [
                    Mov(self.src, cx),
                    LeftShift(cx, self.dst),
                ]
            )


class RightShift(Binary, code="sarl"):
    def fix_instructions(self, instructions: list["Instruction"]) -> None:
        if isinstance(self.src, Imm) or (isinstance(self.src, Register) and self.src.nbytes == 1):
            instructions.append(self)
        else:
            cx = Cx(4)
            instructions.extend(
                [
                    Mov(self.src, cx),
                    RightShift(cx, self.dst),
                ]
            )


class BitwiseAnd(Binary, code="andl"):
    def fix_instructions(self, instructions: list["Instruction"]) -> None:
        if isinstance(self.src, Stack | Data) and isinstance(self.dst, Stack | Data):
            r10 = R10(4)
            instructions.extend(
                [
                    Mov(self.src, r10),
                    BitwiseAnd(r10, self.dst),
                ]
            )
        else:
            instructions.append(self)


class BitwiseOr(Binary, code="orl"):
    def fix_instructions(self, instructions: list["Instruction"]) -> None:
        if isinstance(self.src, Stack | Data) and isinstance(self.dst, Stack | Data):
            r10 = R10(4)
            instructions.extend(
                [
                    Mov(self.src, r10),
                    BitwiseOr(r10, self.dst),
                ]
            )
        else:
            instructions.append(self)


class BitwiseXor(Binary, code="xorl"):
    def fix_instructions(self, instructions: list["Instruction"]) -> None:
        if isinstance(self.src, Stack | Data) and isinstance(self.dst, Stack | Data):
            r10 = R10(4)
            instructions.extend(
                [
                    Mov(self.src, r10),
                    BitwiseXor(r10, self.dst),
                ]
            )
        else:
            instructions.append(self)


class Cmp(Instruction):
    code: str = "cmpl"

    def __init__(self, left: Operand, right: Operand) -> None:
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        left = repr(self.left)
        right = repr(self.right)
        return f"Cmp({left} . {right})"

    def codegen(self) -> str:
        left = self.left.codegen()
        right = self.right.codegen()
        return f"    {self.code:6}    {left:6}, {right:6}"

    def fix_instructions(self, instructions: list["Instruction"]) -> None:
        if isinstance(self.right, Imm):
            reg: Register = R11(4)
            instructions.extend(
                [
                    Mov(self.right, reg),
                    Cmp(self.left, reg),
                ]
            )
        elif isinstance(self.left, Stack | Data) and isinstance(self.right, Stack | Data):
            reg = R10(4)
            instructions.extend(
                [
                    Mov(self.left, reg),
                    Cmp(reg, self.right),
                ]
            )
        else:
            instructions.append(self)


class Idiv(Instruction):
    code: str = "idivl"

    def __init__(self, divisor: Operand) -> None:
        self.divisor = divisor

    def __repr__(self) -> str:
        divisor = repr(self.divisor)
        return f"Idiv({divisor})"

    def codegen(self) -> str:
        divisor = self.divisor.codegen()
        return f"    {self.code:6}    {divisor}"

    def fix_instructions(self, instructions: list[Instruction]) -> None:
        if isinstance(self.divisor, Imm):
            r10 = R10(4)
            instructions.extend(
                [
                    Mov(self.divisor, r10),
                    Idiv(r10),
                ]
            )
        else:
            instructions.append(self)


class Cdq(Instruction):
    code: str = "cdq"

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return "Cdq()"

    def codegen(self) -> str:
        return f"    {self.code}"


class Jmp(Instruction):
    code: str = "jmp"

    def __init__(self, label: str) -> None:
        self.label = label

    def __repr__(self) -> str:
        return f"Jmp({self.label})"

    def codegen(self) -> str:
        return f"    {self.code:6}    .L{self.label}"


class JmpCC(Instruction):
    code: str = "j"

    def __init__(self, cond: str, label: str) -> None:
        self.cond = cond
        self.label = label

    def __repr__(self) -> str:
        return f"JmpCC({self.cond}, {self.label})"

    def codegen(self) -> str:
        code = f"{self.code}{self.cond}"
        return f"    {code:6}    .L{self.label}"


class SetCC(Instruction):
    code: str = "set"

    def __init__(self, cond: str, src: Operand) -> None:
        self.cond = cond
        self.src = src

    def __repr__(self) -> str:
        src = repr(self.src)
        return f"SetCC({self.cond}, {src})"

    def codegen(self) -> str:
        src = self.src.codegen()
        code = f"{self.code}{self.cond}"
        return f"    {code:6}    {src}"


class Label(Instruction):
    code: str = ""

    def __init__(self, label: str) -> None:
        self.label = label

    def __repr__(self) -> str:
        return f"Label({self.label}"

    def codegen(self) -> str:
        return f".L{self.label}:"


class AllocateStack(Instruction):
    code: str = "subq"

    def __init__(self, size: int) -> None:
        self.size = size

    def __repr__(self) -> str:
        return f"AllocateStack({self.size})"

    def codegen(self) -> str:
        return f"""    {self.code}    ${-self.size}, %rsp
    # --- Function Start"""


class DeallocateStack(Instruction):
    code: str = "addq"

    def __init__(self, size: int) -> None:
        self.size = size

    def __repr__(self) -> str:
        return f"DeallocateStack({self.size})"

    def codegen(self) -> str:
        return f"""    {self.code}    ${self.size}, %rsp"""


class Push(Instruction):
    code: str = "pushq"

    def __init__(self, operand: Operand) -> None:
        self.operand = operand

    def __repr__(self) -> str:
        return f"DeallocateStack({repr(self.operand)})"

    def codegen(self) -> str:
        return f"""    {self.code}    {self.operand.codegen()}"""


class Call(Instruction):
    code: str = "call"

    def __init__(self, label: str) -> None:
        self.label = label

    def __repr__(self) -> str:
        return f"Call({self.label})"

    def codegen(self) -> str:
        return f"""    {self.code}    {self.label}"""


class Ret(Instruction):
    def __repr__(self) -> str:
        return "Ret()"

    def codegen(self) -> str:
        return r"""    # --- Ret
    movq      %rbp,   %rsp
    popq      %rbp
    ret"""


class TopLevel(Codegen):
    def __init__(self, name: str, globl: bool) -> None:
        self.name = name
        self.globl = globl


class StaticVar(TopLevel):
    def __init__(self, name: str, globl: bool, init: int) -> None:
        super().__init__(name, globl)
        self.init = init

    def replace_pseudo(self, stack_size: int, variable_map: dict[str, int], symbol_table: SymbolTable) -> None:
        return
    
    def __repr__(self) -> str:
        return f"StaticVar({self.name} = {self.init} {self.globl})"

    def codegen(self) -> str:
        globl = f"    .globl {self.name}" if self.globl else ""
        if self.init == 0:
            section = "    .bss"
            init = "    .zero 4"
        else:
            section = "    .data"
            init = f"    .long {self.init}"
        return f"""
{globl}
{section}
    .align 4
{self.name}:
{init}
"""

    def fix_instructions(self) -> "StaticVar":
        return self


class Function(TopLevel):
    def __init__(self, name: str, globl: bool, instructions: list[Instruction], stack_size: int | None = None) -> None:
        super().__init__(name, globl)
        self.instructions = instructions
        self.stack_size = stack_size

    def __repr__(self) -> str:
        body = "\n".join(["    " + repr(i) for i in self.instructions])
        return f"{self.name}\n{body}"

    def replace_pseudo(self, stack_size: int, variable_map: dict[str, int], symbol_table: SymbolTable) -> None:
        stack_size = 0
        for instruction in self.instructions:
            stack_size = instruction.replace_pseudo(stack_size, variable_map, symbol_table)
        self.stack_size = stack_size

    def codegen(self) -> str:
        instructions = "\n".join([i.codegen() for i in self.instructions])
        globl = f"    .globl {self.name}" if self.globl else ""
        return f"""    
{globl}
    .text
{self.name}:
    pushq   %rbp
    movq    %rsp, %rbp
{instructions}"""

    def fix_instructions(self) -> "Function":
        assert self.stack_size is not None

        instructions: list[Instruction] = []
        for instruction in self.instructions:
            instruction.fix_instructions(instructions)

        remainder = self.stack_size % 16

        if (remainder := self.stack_size % 16) == 0:
            stack_size = self.stack_size
        else:
            stack_size = self.stack_size - remainder
        assert stack_size % 16 == 0
        instructions.insert(0, AllocateStack(stack_size))

        return Function(self.name, self.globl, instructions)


class Program(Codegen):
    def __init__(self, functions: list[Function], symbol_table: SymbolTable) -> None:
        self.functions = functions
        self.symbol_table = symbol_table

    def __repr__(self) -> str:
        return "\n".join(map(repr, self.functions))

    def codegen(self) -> str:
        return f"""{"\n".join([func.codegen() for func in self.functions])}

    .section .note.GNU-stack,"",@progbits
"""

    def replace_pseudo(self, stack_size: int, variable_map: dict[str, int]) -> None:
        for func in self.functions:
            func.replace_pseudo(stack_size, variable_map, self.symbol_table)

    def fix_instructions(self) -> "Program":
        funcs = [func.fix_instructions() for func in self.functions]
        return Program(funcs, self.symbol_table)


if __name__ == "__main__":
    from nora3.lex import Lexer
    from nora3.parse import Parser

    src = """
int main(void) {
    int a = 0 && a;
    return a;
}
"""
    tokens = Lexer(src).lex()
    ast = Parser(tokens).parse()
    ast = ast.resolve()
    ir = ast.to_tacky()
    ass = ir.to_asm()
    ass.replace_pseudo(0, {})
    ass = ass.fix_instructions()
    code = ass.codegen()

    print(code)
