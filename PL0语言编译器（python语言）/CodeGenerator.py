from Lexer import Lexer
from Parser import Parser, LRTableGenerator


class PL0CodeGenerator:
    def __init__(self, parser):
        self.instructions = []  # 存储生成的中间代码
        self.symbolTable = {}   # 符号表，用于存储常量和变量符号
        self.temp_counter_t = 0   # 用于生成临时变量
        self.temp_counter_l = 0   # 用于生成标签
        self.parser = parser

    def new_temp(self):
        # 生成一个新的临时变量
        temp_name = f"T{self.temp_counter_t}"
        self.temp_counter_t += 1
        return temp_name

    def new_label(self):
        # 生成一个新的标签
        label_name = f"L{self.temp_counter_l}"
        self.temp_counter_l += 1
        return label_name

    # 新的中间代码指令

    def add_instruction(self, instruction):
        self.instructions.append(instruction)

    def visit(self, node):
        if len(node.children) > 0:
            rType = node.type.upper()
            # print(f"当前访问节点类型: {node.type},规约类型为:{rType}")
            method_name = f'visit{rType}'
            visitor = getattr(self, method_name, self.generic_visit)
            return visitor(node)
        else:
            # print(f"当前访问节点类型: {node.type},是叶节点")
            return node.value

    def generic_visit(self, node):
        # print(f"当前节点类型：{node.type}此节点规约没有操作")
        for child in node.children:
            self.visit(child)

    # 赋值语句
    def visitASSIGNMENT(self, node):
        # assignment -> IDENTIFIER ASSIGN expression
        # print(f"处理赋值表达式中...访问其前两个节点{node.children[0].type}和{node.children[2].type}")
        # 赋值表达式左侧的变量名
        identifier_name = node.children[0].value
        if ('var',identifier_name) in self.symbolTable.keys():
            # print(f"符号表中存在变量{identifier_name}")
            # 赋值表达式右侧的值
            expr_value = self.visit(node.children[2])
            self.symbolTable[('var', identifier_name)] = expr_value   # 将符号表中对应符号的值
            # print(f"处理了赋值表达式{identifier_name}={expr_value}")
            self.add_instruction(f"{identifier_name} = {expr_value}")
        else:
            if ('const', identifier_name) in self.symbolTable.keys():
                raise Exception(f"CodeGenerator-Error:常量{identifier_name}不能被赋值")
            else:
                raise Exception(f"CodeGenerator-Error:符号表中并没有变量{identifier_name}")

    # 表达式（加减）
    def visitEXPRESSION(self, node):
        # 对应 expression -> term
        if len(node.children) == 1:
            return self.visit(node.children[0])
        # 对应 expression -> expression MINUS term
        # 对应 expression -> expression PLUS term
        left = self.visit(node.children[0])
        right = self.visit(node.children[2])
        op = node.children[1].value
        temp = self.new_temp()
        self.add_instruction(f"{temp} = {left} {op} {right}")
        return temp

    # TERM项（乘除）
    def visitTERM(self, node):
        # 对应 term -> factor
        if len(node.children) == 1:
            factor_node = node.children[0]
            # 当某基本项被用到时，要检查它是否被定义以及如果是变量是否有被初始化
            if factor_node.type == "IDENTIFIER":
                iden_name = factor_node.value
                # 假设是常量，检查这个常量是否在符号表中
                if ('const', iden_name) not in self.symbolTable.keys():
                    raise Exception(f"未定义的常量{iden_name}")
                # 假设是变量，检查这个变量是否在符号表中
                if ('var', iden_name) not in self.symbolTable.keys():
                    raise Exception(f"未定义的变量{iden_name}")
                # 若变量在符号表中，检查这个变量是否有被初始化
                else:
                    if self.symbolTable[('var', iden_name)] is None:
                        raise Exception(f"变量{iden_name}未初始化")
            else:
                return self.visit(node.children[0])
        # 对应 term -> term STAR factor
        # 对应 term -> term SLASH factor
        left = self.visit(node.children[0])
        right = self.visit(node.children[2])
        op = node.children[1].value
        temp = self.new_temp()
        self.add_instruction(f"{temp} = {left} {op} {right}")
        return temp


    # FACTOR 因子
    def visitFACTOR(self, node):
        # 对应 factor -> IDDENTIFIER
        if node.children[0].type == "IDENTIFIER":
            idenName = node.children[0].value   # 获取变量/常量名
            if ('const', idenName) in self.symbolTable.keys():
                # print(f"常量{idenName}在符号表中")
                self.visit(node.children[0])
                return self.visit(node.children[0])
            elif ('var', idenName) in self.symbolTable.keys():
                # print(f"变量{idenName}在符号表中")
                if self.symbolTable[('var',idenName)] == None:
                     raise Exception(f"CodeGenerator-Error:变量{idenName}尚未初始化")
                return self.visit(node.children[0])
            else:
                raise Exception(f"CodeGenerator-Error:存在未声明的符号{idenName}")
        # 对应 factor -> NUMBER
        elif node.children[0].type == "NUMBER":
            return self.visit(node.children[0])
        # 对应 factor -> LPAREN expression RPAREN
        else:
            expr_node = node.children[1]
            return self.visit(expr_node)

    # 条件
    def visitCONDITION(self, node):
        # 对应 condition -> expression relation expression
        left = self.visit(node.children[0])
        right = self.visit(node.children[2])
        op = node.children[1].value
        temp = self.new_temp()
        self.add_instruction(f"{temp} = {left} {op} {right}")
        return temp

    def visitCONDITIONSTATEMENT(self, node):
        # 对应 conditionStatement -> IF condition THEN statement
        condition_code = self.visit(node.children[1])
        label_end = self.new_label()
        self.add_instruction(f"IF NOT {condition_code} GOTO {label_end}")
        # 访问 THEN 之后的节点
        self.visit(node.children[3])
        self.add_instruction(f"LABEL {label_end}")

    # WHILE语句的处理还有问题
    def visitWHILESTATEMENT(self, node):
        # 对应 whileStatement -> WHILE condition DO statement
        label_start = self.new_label()
        label_end = self.new_label()
        self.add_instruction(f"LABEL {label_start}")
        # 访问条件表达式
        condition_code = self.visit(node.children[1])
        self.add_instruction(f"IF NOT {condition_code} GOTO {label_end}")

        # 访问 DO 之后的语句
        self.visit(node.children[3])
        self.add_instruction(f"GOTO {label_start}")
        self.add_instruction(f"LABEL {label_end}")

    def visitCOMPOUNDSTATEMENT(self, node):
        for statement in node.children:
            self.visit(statement)

    def visitVARDECLARATION_1(self, node):
        varName = None
        # 对应 varDeclaration_1 -> varDeclaration_1 COMMA IDENTIFIER
        if node.children[0].type == 'varDeclaration_1':
            # print("处理 varDeclaration_1 -> varDeclaration_1 COMMA IDENTIFIER 变量定义节点中...")
            # 在符号表中加入这个变量，其值先置为0
            varName = node.children[2].value
            self.symbolTable[('var', varName)] = None
            self.visitVARDECLARATION_1(node.children[0])  # 继续用本visit函数访问子节点
        # 对应 varDeclaration_1 -> VAR IDENTIFIER
        else:
            # print("处理 varDeclaration_1 -> VAR IDENTIFIER 变量定义节点中...")
            # 在符号表中加入这个变量，其值先置为0
            varName = node.children[1].value
            self.symbolTable[('var', varName)] = None
        # print(f"已将{varName}加入符号表")

    def visitCONSTDECLARATION_1(self, node):
        constName = None
        constValue = None
        # 对应 constDeclaration_1 -> constDeclaration_1 COMMA constDefinition
        if node.children[0].type == "constDeclaration_1":
            # print("处理 constDeclaration_1 -> constDeclaration_1 COMMA constDefinition 常量定义节点中...")
            constDefiNode = node.children[2]   # 常量定义的节点
            # 语法规则: constDefinition -> IDENTIFIER EQUAL NUMBER
            constName = constDefiNode.children[0].value
            constValue = constDefiNode.children[2].value
            self.symbolTable[('const',constName)] = constValue  # 在符号表中加入此常量和其值
            self.add_instruction(f"{constName} = {constValue}")  # 在中间代码中加入语句
            self.visitCONSTDECLARATION_1(node.children[0])  # 继续用本visit函数访问子节点
        # 对应 constDeclaration_1 -> CONST constDefinition
        else:
            # print("处理 constDeclaration_1 -> CONST constDefinition 常量定义节点中...")
            constDefiNode = node.children[1]
            # 语法规则: constDefinition -> IDENTIFIER EQUAL NUMBER
            constName = constDefiNode.children[0].value
            constValue = constDefiNode.children[2].value
            self.symbolTable[('const',constName)] = constValue  # 在符号表中加入此常量和其值
            self.add_instruction(f"{constName} = {constValue}")  # 在中间代码中加入语句
        # print(f"已将{constName}={constValue}加入符号表")

    def visitPROGRAM(self, node):
        # print("访问PROGRAM节点")
        for child in node.children:
            self.visit(child)  # Visit the main compound statement

    def generator(self):
        self.visit(parser.ASTRoot)


if __name__ == "__main__":
    tableGenerator = LRTableGenerator()
    LRTable = tableGenerator.getTable()
    grammarRules = tableGenerator.getRules()
    # 词法分析

    # 项目要求中给到的测试源代码
    lexer = Lexer('testCodes/PL0code.txt')
    # 三个较为复杂的测试源代码
    # lexer = Lexer('testCodes/sample1.txt')
    # lexer = Lexer('testCodes/sample2.txt')
    # lexer = Lexer('testCodes/sample3.txt')
    # 报错测试代码
    # lexer = Lexer('testCodes/errorTest1.txt')   # 变量未初始化(中间代码生成报错)
    # lexer = Lexer('testCodes/errorTest2.txt')  # 变量名写错，识别为未声明变量(中间代码生成报错)
    # lexer = Lexer('testCodes/errorTest3.txt')  # 给常量二次赋值(中间代码生成报错)
    # lexer = Lexer('testCodes/errorTest4.txt')  # 将赋值号:=写为=(语法分析报错)
    # lexer = Lexer('testCodes/errorTest5.txt')  # 变量标识符开头使用下划线(词法分析报错)
    # lexer = Lexer('testCodes/errorTest6.txt')  # 语句结束后分号缺失(语法分析报错)
    # 语法分析
    parser = Parser(lexer, LRTable, grammarRules)
    parser.run()
    # 递归打印抽象语法树
    # print("源代码的抽象语法树如下: ")
    # parser.printAST(parser.ASTRoot, 0)
    # 中间代码生成
    code_generator = PL0CodeGenerator(parser)
    # 输出中间代码（从根开始遍历）
    code_generator.generator()
    print("生成的中间代码如下 :")
    for instr in code_generator.instructions:
        print(instr)
