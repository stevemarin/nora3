from string import ascii_letters, digits, whitespace as _whitespace

from nora3 import tok

TAB_WIDTH = 4
LONGEST_OPERATOR_LENGTH = 3

alpha = frozenset(ascii_letters + "_")
numeric = frozenset(digits)
alphanumeric = alpha | numeric
whitespace = frozenset(_whitespace)


class UnexpectedEOF(Exception):
    value: str

    def __init__(self, value: str) -> None:
        super().__init__()
        self.value = value

    def __str__(self) -> str:
        return f"unexpected EOF at {self.value}"


class InvalidNumber(Exception):
    value: str
    line: int
    offset: int

    def __init__(self, line: int, offset: int, value: str) -> None:
        super().__init__()
        self.line = line
        self.offset = offset
        self.value = value

    def __str__(self) -> str:
        return f"invalid number '{self.value}' @ {self.line}:{self.offset}"


class InvalidCharacter(Exception):
    line: int
    offset: int
    value: str

    def __init__(self, line: int, offset: int, value: str) -> None:
        super().__init__()
        self.line = line
        self.offset = offset
        self.value = value

    def __str__(self) -> str:
        return f"invalid character '{self.value}' @ {self.line}:{self.offset}"


class Lexer:
    def __init__(self, src: str) -> None:
        self.src = src
        self.idx = 0
        self.line = 1
        self.offset = 0

    def eat(self, nchars: int = 1) -> str | None:
        chars = self.src[self.idx:self.idx + nchars]
        if chars == "":
            return None
        elif len(chars) < nchars:
            raise UnexpectedEOF(f"Lexer.eat({nchars})")
        
        self.idx += nchars

        for char in chars:
            if char == "\n":
                self.offset = 0
                self.line += 1
            else:
                self.offset += TAB_WIDTH if char == "\t" else 1

        return chars

    def peek(self, nchars: int = 1) -> str | None:
        chars = self.src[self.idx:self.idx + nchars]
        if nchars > 1 and len(chars) < nchars:
            raise UnexpectedEOF(f"Lexer.peek({nchars})")
        elif chars == "":
            return None

        return chars

    def directive(self) -> None:
        while (c := self.peek()) is not None and c != "\n":
            _ = self.eat()

    def single_line_comment(self) -> None:
        assert self.eat() == "/"
        while (c := self.peek()) is not None and c != "\n":
            _ = self.eat()

    def multi_line_comment(self) -> None:
        assert self.eat() == "*"
        while (next2 := self.peek(2)) is not None and next2 != "*/":
            _ = self.eat()
        _ = self.eat(2)

    def numbers(self, char: str) -> tok.Token:
        chars = [char]
        while (c := self.peek()) is not None and c in alphanumeric:
            chars.append(c)
            _ = self.eat()

        value = "".join(chars)
        if len(set(chars) - numeric) != 0:
            raise InvalidNumber(self.line, self.offset, value)
        else:
            return tok.Token(self.line, self.offset, tok.LiteralInt(value))

    def letters(self, char: str) -> tok.Token:
        chars = [char]
        while (c := self.peek()) in alphanumeric:
            chars.append(c)
            _ = self.eat()

        v = "".join(chars)
        try:
            return tok.Token(self.line, self.offset, tok.Keyword().mapping[v])
        except KeyError:
            return tok.Token(self.line, self.offset, tok.Identifier(v))

    def characters(self, char: str) -> tok.Token:
        for num_chars in reversed(range(0, LONGEST_OPERATOR_LENGTH)):
            try:
                next_chars = self.peek(num_chars)
            except UnexpectedEOF:
                continue
            
            if next_chars is not None and (tokentype := tok.Character().mapping.get(char + next_chars)) is not None:
                _ = self.eat(num_chars)
                return tok.Token(self.line, self.offset, tokentype)

        return tok.Token(self.line, self.offset, tok.Character().mapping[char])

    def lex(self) -> list[tok.Token]:
        tokens = []
        while (char := self.eat()) is not None:
            if char in whitespace:
                continue
            elif char == tok.Pound.value:
                self.directive()
            elif char == tok.ForwardSlash.value and self.peek() == tok.ForwardSlash.value:
                self.single_line_comment()
            elif char == tok.ForwardSlash.value and self.peek() == tok.Star.value:
                self.multi_line_comment()
            elif char in numeric:
                tokens.append(self.numbers(char))
            elif char in alpha:
                tokens.append(self.letters(char))
            elif char in tok.characters:
                tokens.append(self.characters(char))
            else:
                raise InvalidCharacter(self.line, self.offset, char)

        return tokens


if __name__ == "__main__":

    src = """
int main(void) {
    // test case w/ multi-digit constant
    return 100;
}
"""
    lexer = Lexer(src)
    for token in lexer.lex():
        print("TOKEN:", token)
