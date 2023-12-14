import re


class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    def __init__(self):
        self.source_code = self.getTestCode()
        self.tokens = []
        self.tokenize()
        self.tokens.append(Token("#", "#"))

    def tokenize(self):
        token_specs = [
            ('PROGRAM',    r'PROGRAM'),
            ('BEGIN',      r'BEGIN'),
            ('END',        r'END'),
            ('CONST',      r'CONST'),
            ('VAR',        r'VAR'),
            ('WHILE',      r'WHILE'),
            ('DO',         r'DO'),
            ('IF',         r'IF'),
            ('THEN',       r'THEN'),
            ('IDENTIFIER', r'[a-zA-Z][a-zA-Z0-9]*'),
            ('NUMBER',     r'\d+'),
            ('PLUS',       r'\+'),
            ('MINUS',      r'-'),
            ('STAR',       r'\*'),
            ('SLASH',      r'/'),
            ('ASSIGN',     r':='),
            ('EQUAL',      r'='),
            ('NOT_EQUAL',  r'<>'),
            ('LESS',       r'<'),
            ('LESS_EQ',    r'<='),
            ('GREATER',    r'>'),
            ('GREATER_EQ', r'>='),
            ('LPAREN',     r'\('),
            ('RPAREN',     r'\)'),
            ('SEMI',       r';'),
            ('COMMA',      r','),
            ('WS',         r'[ \t\r\n]+'),
            ('MISMATCH',   r'.')  # 任何其他字符
        ]
        token_regex = '|'.join(
            f'(?P<{name}>{regex})' for name, regex in token_specs)
        for mo in re.finditer(token_regex, self.source_code):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'WS':
                continue
            elif kind == 'MISMATCH':
                raise RuntimeError(f'Unexpected character: {value[0]}')
            self.tokens.append(Token(kind, value))

    # 由外部文件得到测试代码
    def getTestCode(self):
        file_name = "PL0code.txt"
        # file_name = "testCode.txt"
        file = open(file_name, 'r', encoding='utf-8')
        testCode = file.read()
        file.close()
        return testCode

    def get_next_token(self):
        return self.tokens.pop(0) if self.tokens else None



if __name__ == "__main__":
    lexer = Lexer()
    tokens = lexer.tokens
    for token in tokens:
        print(token)


# PL0code = """
# PROGRAM example
# VAR x, y;
# BEGIN
# x := 1;
# y := 2;
# WHILE x < 5 DO x := x + 1;
# IF y > 0 THEN y := y - 1;
# y := y + x;
# END
# """
# lexer = Lexer(PL0code)
# token = lexer.get_next_token()
# while token:
#     print(token)
#     token = lexer.get_next_token()
