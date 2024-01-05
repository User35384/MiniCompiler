# from cifa import word_analysis            # 旧词法分析器
from Lexer import Lexer                     # 词法分析器
from getLRTable import LRTableGenerator     # 根据语法规则生成LR分析表


class ASTNode:
    def __init__(self, type):
        self.type = type
        self.value = None  # 节点的值，初始化为None
        self.numValue = None  # 节点的数值，初始化为None
        # value对应token的word域，如果是一个IDENTIFIER，它的word可以是x，example等等
        # 而其numValue则必须是一个数值，type为NUMBER的符号，其value就等于其numValue
        self.children = []

    def addChild(self, pos, child):
        self.children.insert(pos, child)

    def setNumValue(self,numValue):
        self.numValue = numValue

    def setValue(self, value):
        self.value = value
        # type为NUMBER的符号，其value就等于其numValue
        if self.type == 'NUMBER':
            self.numValue = value


class Parser:
    def __init__(self, lexer, LRTable, rules):
        self.lexer = lexer
        # self.tokens = lexer.word_list
        self.tokens = lexer.token_list
        self.currentTokenIndex = 0
        self.LRTable = LRTable
        self.rules = rules
        self.VT, self.VN = self.getWords(self.rules)
    # 使用LR分析表和词法分析器产生的token序列来进行LR(1)分析
        self.ASTRoot = None
    # 存储所有的变量/常量定义等定义
        self.defineStorage = []


    # 获取当前读到的token，并使index+1
    def getToken(self):
        if self.currentTokenIndex < len(self.tokens):
            token = self.tokens[self.currentTokenIndex]
            self.currentTokenIndex = self.currentTokenIndex + 1
            return token
        else:
            print("已经读完全部token")
            return None

    # 从语法规则中获取所有终结符和非终结符
    def getWords(self, rules):
        VT = []  # 终结符
        VN = []  # 非终结符
        for rule in rules:
            if rule.left[0].isupper() and rule.left not in VT:
                VT.append(rule.left)
            elif rule.left[0].islower() and rule.left not in VN:
                VN.append(rule.left)
            for word in rule.right:
                if word[0].isupper() and word not in VT:
                    VT.append(word)
                elif word[0].islower() and word not in VN:
                    VN.append(word)

        return VT, VN

    def run(self):
        # 符号栈和状态栈初始化
        statusStack = []
        statusStack.append(0)
        symbolStack = []
        symbolStack.append('#')
        # token栈，用于存储符号的类型和值（symbol只存类型，因为在后面规约的时候要换，但是根据规约规则只能append符号类型）
        tokenStack = []
        # 出错标记 和 当前正要读取的token 初始化
        errorFlag = False
        token = self.getToken()
        # 用于构造语法树的栈
        ASTBuildStack = []
        # 开启语法分析主循环
        while self.currentTokenIndex <= len(self.tokens):
            currentStatus = statusStack[-1]        # 当前状态是状态栈的栈顶元素
            shiftWord = token['type']                 # token的类型就是接收的符号
            # token是字典，有三个key-value，三个键分别是：'line'-行数, 'type'-符号类型, 'word'-符号的值
            try:
                mapWord1,mapWord2 = self.LRTable[(currentStatus, shiftWord)]  # 读出表中对应的元素
            except KeyError:
                print(f"error : 状态{currentStatus}下不接收符号{shiftWord}")
                errorFlag = True
                raise Exception(f"Parser-Error : 状态{currentStatus}下不接收符号{shiftWord}")
                break
            if errorFlag == False:
                if mapWord1 == "shift":
                    # 将要shift到的状态加入到状态栈栈顶
                    shiftStatusNO = mapWord2
                    statusStack.append(shiftStatusNO)
                    # 将读入的符号类型type存入符号栈symbolStack
                    symbolStack.append(shiftWord)
                    # 将这个符号的类型type和其值value加入词条栈tokenStack（直接存token）
                    tokenStack.append(token)
                    # 读取下一个符号
                    token = self.getToken()

                    # print(f"状态{currentStatus}遇到符号{shiftWord},进行{mapWord1}至状态{shiftStatusNO}")
                    # print("当前符号栈和状态栈的栈内元素为: ")
                    # print("符号栈: ", symbolStack)
                    # print("状态栈: ", statusStack)
                    # print("词条栈: ", tokenStack)
                    # print("")

                elif mapWord1 == "reduce":
                    ruleNO = mapWord2
                    rule = self.rules[ruleNO]
                    rightLength = len(rule.right)

                    # # 在reduce时进行相应的操作来构建AST
                    thisNode = ASTNode(rule.left)
                    # # print("测试如下：")
                    # # print("栈中的符号依次为：")
                    # for node in ASTBuildStack:
                    #     print(node.type, end=' ')
                    # # print("")
                    # # print("规约规则右侧的符号依次为：")
                    # for word in rule.right:
                    #     print(word, end=' ')
                    # print("")

                    # 当栈中的节点类型正好是本条reduce规则右侧的符号类型时，不需新建节点
                    # 逆序查看栈中所有的非终结符，看其个数和内容是否与本规则完全对应
                    for index, word in enumerate(reversed(rule.right)):
                        # print(f"这是规约规则右侧中倒数第{index}个符号:{word}")
                        if word in self.VN:
                            newNode = ASTBuildStack.pop()
                            newNode.setValue(tokenStack[-index-1]['word'])   # 子节点的value设置为词条栈中对应词条的word值
                            # 这里必须是-index-1 !! 因为索引为'-1'才是倒数第一个，也就是倒数时索引为'0'的那一项
                            thisNode.addChild(0, newNode)
                            # print(f"插入非终结符{newNode.type},其值为{newNode.value}")
                        elif word in self.VT:
                            newNode = ASTNode(word)
                            newNode.setValue(tokenStack[-index-1]['word'])   # 子节点的value设置为词条栈中对应词条的word值
                            thisNode.addChild(0, newNode)
                            # print(f"插入终结符{newNode.type},其值为{newNode.value}")
                    # 在添加完本节点所有的子节点后，调用reduceLogic函数来计算本节点的对应值
                    thisValue = self.reduceLogic(rule, thisNode)
                    thisNode.setValue(thisValue)
                    self.ASTRoot = thisNode
                    ASTBuildStack.append(thisNode)
                    # 如果这条规则右边有n个符号，符号栈和状态栈都将栈顶的n个元素吐出
                    while rightLength > 0:
                        statusStack.pop()
                        symbolStack.pop()
                        tokenStack.pop()   # 词条栈配合也吐出
                        rightLength = rightLength - 1
                    # 规则左侧的符号进入符号栈
                    symbolStack.append(rule.left)
                    # 将对应的规约左侧的token也加入词条栈
                    tokenStack.append({'line': None, 'type': rule.left, 'word': thisNode.value})

                    # print(f"状态{currentStatus}遇到符号{shiftWord},进行{mapWord1},")
                    # print(f"使用{ruleNO}号规则:{rule.left}->{rule.right}进行规约,共退出{len(rule.right)}个状态和符号,")
                    # print(f"加入新符号{rule.left}")
                    # print("当前符号栈和状态栈的栈内元素为: ")
                    # print("符号栈: ", symbolStack)
                    # print("状态栈: ", statusStack)

                    # 从吐出n个元素后的状态栈取栈顶，查表得到该状态接收当前符号栈栈顶符号的动作
                    currentStatus = statusStack[-1]
                    currentSymbol = symbolStack[-1]
                    gotoWord1,gotoWord2 = self.LRTable[(currentStatus,currentSymbol)]
                    # if gotoWord1 == "goto":
                    #     print("goto")
                    gotoStatus = gotoWord2
                    statusStack.append(gotoStatus)

                    # print(f"新状态{currentStatus}遇到符号{currentSymbol}，进行{gotoWord1}至状态{gotoWord2}")
                    # print("当前符号栈和状态栈的栈内元素为: ")
                    # print("符号栈: ", symbolStack)
                    # print("状态栈: ", statusStack)
                    # print("")

                elif mapWord1 == "accept":
                    print(f"状态{currentStatus}遇到符号{shiftWord},进行{mapWord1}")
                    # print("当前符号栈和状态栈的栈内元素为: ")
                    # print("符号栈: ", symbolStack)
                    # print("状态栈: ", statusStack)
                    print("语法分析成功")
                    print("")
                    break

    # 根据规约类型和此节点的子节点等信息，来计算此节点value域的取值
    def reduceLogic(self, reduceRule, thisNode):
        r = reduceRule
        length = len(thisNode.children)

        if r.left == 'varDeclaration_1':
            # varDeclaration_1 -> VAR IDENTIFIER
            if length == 2 and r.right[0] == 'VAR' and r.right[1] == 'IDENTIFIER':
                child_IDENTIFIER = thisNode.children[1]
                # 将定义的变量加入定义库中,value置为空
                self.defineStorage.append({'identifier': child_IDENTIFIER.value, 'value': None})
                return None
            # varDeclaration_1 -> varDeclaration_1 COMMA IDENTIFIER
            if length == 3 and r.right[0] == 'varDeclaration_1' and r.right[1] == 'COMMA' and r.right[2] == 'IDENTIFIER':
                child_IDENTIFIER = thisNode.children[2]
                # 将定义的变量加入定义库中,value置为空
                self.defineStorage.append({'identifier': child_IDENTIFIER.value, 'value': None})

        if r.left == 'term':
            # term -> factor
            if length == 1 and r.right[0] == 'factor':
                child_factor = thisNode.children[0]
                thisNode.setNumValue(child_factor.numValue)
                thisValue = child_factor.value
                return thisValue

        if r.left == 'factor':
            # factor -> NUMBER
            if length == 1 and r.right[0] == 'NUMBER':
                child_NUMBER = thisNode.children[0]
                thisNode.setNumValue(child_NUMBER.numValue)
                thisValue = child_NUMBER.value
                return thisValue
            # factor -> IDENTIFIER
            if length == 1 and r.right[0] == 'IDENTIFIER':
                child_IDENTIFIER = thisNode.children[0]
                # 查找符号表，得到这个变量的取值
                for define in self.defineStorage:
                    if define['identifier'] == child_IDENTIFIER.value:
                        child_IDENTIFIER.setNumValue(define['value'])

                thisNode.setNumValue(child_IDENTIFIER.numValue)
                thisValue = child_IDENTIFIER.value
                return thisValue

        if r.left == 'expression':
            # expression -> term
            if length == 1 and r.right[0] == 'term':
                child_term = thisNode.children[0]
                thisNode.setNumValue(child_term.numValue)
                thisValue = child_term.value
                return thisValue

        if r.left == 'assignment':
            # assignment -> IDENTIFIER ASSIGN expression
            if length == 3 and r.right[0] == 'IDENTIFIER' and r.right[1] == 'ASSIGN' and r.right[2] == 'expression':
                child_IDENTIFIER = thisNode.children[0]
                child_expression = thisNode.children[2]
                # 将表达式的值赋给标识符节点
                child_IDENTIFIER.setNumValue(child_expression.numValue)
                # 在定义库中找到这个变量的定义，将其值置为表达式的值
                for define in self.defineStorage:
                    if define['identifier'] == child_IDENTIFIER.value:
                        define['value'] = child_expression.numValue
                return None  # assignment这个赋值语句本身没有值

        if r.left == 'relation':
            # relation -> LESS
            if length == 1 and r.right[0] == 'LESS':
                child_LESS = thisNode.children[0]
                thisValue = child_LESS.value
                return thisValue

            if length == 1 and r.right[0] == 'GREATER':
                child_GREATER = thisNode.children[0]
                thisValue = child_GREATER.value
                return thisValue

        return None


    # 打印语法树
    def printAST(self, root, depth):

        print("    " * (depth)+f"[{depth}]" + str(root.type)+ f"({root.value}={root.numValue})")

        for child in root.children:
            self.printAST(child, depth+1)




if __name__ == "__main__":
    # 获取LR分析表
    tableGenerator = LRTableGenerator()
    LRTable = tableGenerator.getTable()
    grammarRules = tableGenerator.getRules()

    filePath = "testCodes/PL0code.txt"
    # 词法分析
    lexer = Lexer(filePath)
    # 语法分析
    parser = Parser(lexer, LRTable, grammarRules)
    parser.run()

    # 递归输出语法树
    print("源代码的抽象语法树如下: ")
    parser.printAST(parser.ASTRoot, 0)

