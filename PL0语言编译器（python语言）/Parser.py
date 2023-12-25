# from cifa import word_analysis            # 旧词法分析器
from Lexer import Lexer                     # 词法分析器
from getLRTable import LRTableGenerator     # 根据语法规则生成LR分析表


class ASTNode:
    def __init__(self, type):
        self.type = type
        self.value = 0
        self.children = []

    def addChild(self, pos, child):
        self.children.insert(pos, child)


    def setValue(self,value):
        self.value = value


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
        # 出错标记 和 当前正要读取的token 初始化
        errorFlag = False
        token = self.getToken()
        # 用于构造语法树的栈
        ASTBuildStack = []
        # 开启语法分析主循环
        while self.currentTokenIndex <= len(self.tokens):
            currentStatus = statusStack[-1]        # 当前状态是状态栈的栈顶元素
            shiftWord = token['type']                 # token的类型就是接收的符号
            try:
                mapWord1,mapWord2 = self.LRTable[(currentStatus, shiftWord)]  # 读出表中对应的元素
            except KeyError:
                print(f"error : 状态{currentStatus}下不接收符号{shiftWord}")
                errorFlag = True
                break
            if errorFlag == False:
                if mapWord1 == "shift":
                    # 将要shift到的状态加入到状态栈栈顶
                    shiftStatusNO = mapWord2
                    statusStack.append(shiftStatusNO)
                    # 将读入的符号加入符号栈栈顶
                    symbolStack.append(shiftWord)
                    # 读取下一个符号
                    token = self.getToken()

                    print(f"状态{currentStatus}遇到符号{shiftWord},进行{mapWord1}至状态{shiftStatusNO}")
                    print("当前符号栈和状态栈的栈内元素为: ")
                    print("符号栈: ", symbolStack)
                    print("状态栈: ", statusStack)
                    print("")

                elif mapWord1 == "reduce":
                    ruleNO = mapWord2
                    rule = self.rules[ruleNO]
                    rightLength = len(rule.right)
                    # 在reduce时进行相应的操作来构建AST
                    # 当栈中的节点类型正好是本条reduce规则右侧的符号类型时，不需新建节点
                    thisNode = ASTNode(rule.left)
                    print("测试如下：")
                    print("栈中的符号依次为：")
                    for node in ASTBuildStack:
                        print(node.type, end=' ')
                    print("")
                    print("规约规则右侧的符号依次为：")
                    for word in rule.right:
                        print(word, end=' ')
                    print("")

                    # 逆序查看栈中所有的非终结符，看其个数和内容是否与本规则完全对应
                    for index, word in enumerate(reversed(rule.right)):
                        if word in self.VN:
                            newNode = ASTBuildStack.pop()
                            thisNode.addChild(0, newNode)
                            print(f"插入非终结符{newNode.type}")
                        elif word in self.VT:
                            newNode = ASTNode(word)
                            thisNode.addChild(0, newNode)
                            print(f"插入终结符{newNode.type}")
                    self.ASTRoot = thisNode
                    ASTBuildStack.append(thisNode)
                    # 如果这条规则右边有n个符号，符号栈和状态栈都将栈顶的n个元素吐出
                    while rightLength > 0:
                        statusStack.pop()
                        symbolStack.pop()
                        rightLength = rightLength - 1
                    # 规则左侧的符号进入符号栈
                    symbolStack.append(rule.left)

                    print(f"状态{currentStatus}遇到符号{shiftWord},进行{mapWord1},")
                    print(f"使用{ruleNO}号规则:{rule.left}->{rule.right}进行规约,共退出{len(rule.right)}个状态和符号,")
                    print(f"加入新符号{rule.left}")
                    print("当前符号栈和状态栈的栈内元素为: ")
                    print("符号栈: ", symbolStack)
                    print("状态栈: ", statusStack)

                    # 从吐出n个元素后的状态栈取栈顶，查表得到该状态接收当前符号栈栈顶符号的动作
                    currentStatus = statusStack[-1]
                    currentSymbol = symbolStack[-1]
                    gotoWord1,gotoWord2 = self.LRTable[(currentStatus,currentSymbol)]
                    if gotoWord1 == "goto":
                        print("goto")
                    gotoStatus = gotoWord2
                    statusStack.append(gotoStatus)

                    print(f"新状态{currentStatus}遇到符号{currentSymbol}，进行{gotoWord1}至状态{gotoWord2}")
                    print("当前符号栈和状态栈的栈内元素为: ")
                    print("符号栈: ", symbolStack)
                    print("状态栈: ", statusStack)
                    print("")

                elif mapWord1 == "accept":

                    print(f"状态{currentStatus}遇到符号{shiftWord},进行{mapWord1}")
                    print("当前符号栈和状态栈的栈内元素为: ")
                    print("符号栈: ", symbolStack)
                    print("状态栈: ", statusStack)
                    print("语法分析成功")
                    print("")
                    break

    # 打印语法树
    def printAST(self, root, depth):

        print("    " * (depth) + f"[{depth}]" + str(root.type))
        for child in root.children:
            self.printAST(child, depth+1)




if __name__ == "__main__":
    # 获取LR分析表
    tableGenerator = LRTableGenerator()
    LRTable = tableGenerator.getTable()
    grammarRules = tableGenerator.getRules()

    filePath = "testCodes"
    fileName = "PL0code.txt"
    file = filePath + '/' + fileName

    # 定义词法&语法分析器对象
    lexer = Lexer(file)
    parser = Parser(lexer, LRTable, grammarRules)

    parser.run()
    parser.printAST(parser.ASTRoot, 0)

