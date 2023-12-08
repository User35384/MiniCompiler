
# 语法规则类
# left是语法规则左侧的单词，类型是字符串
# right是语法规则右侧的单词传，类型是字符串列表，其列表中元素顺序必须和语法规则相同
class grammarRule:
    def __init__(self, left, right):
        self.left = left
        self.right = right




def getGrammar():
    file_name = "rules" + "/" + "ParserRules.txt"
    input = []  # 存储每一行的列表
    grammar = []  # 存储语法规则

    # 从语法规则文件夹读取每一行，存到input列表中
    file = open(file_name, 'r', encoding='utf-8')
    line = file.readline()  # 读取第一行
    while line:
        input.append(line.strip())  # 去除行末尾的换行符，并添加到列表中
        line = file.readline()  # 读取下一行
    file.close()
    print("所有行如下：")
    for line in input:
        print(line)

    # 从input列表中提取不是注释的行
    for line in input:
        if not line.startswith("//") and line != '':
            grammar.append(line)

    print("所有语法规则如下：")
    for line in grammar:
        print(line)

    # 从所有行中得到一个语法规则表
    print("test")
    rules = []    # 用列表存储所有语法规则
    key = ""     # 存储规则左侧
    value = []   # 存储规则右侧
    workingFlag = 0  # 表示当前读入某个语法规则的状态
    # （workingFlag具体数值：0表示刚开始或刚读完一个，1表示正在读单个语法规则，2表示正在读并列的语法规则）
    for line in grammar:
        list = line.split(" ")
        # 把其中的空字符串去掉
        Nlist = []
        for word in list:
            if word != "":
                Nlist.append(word)
        list = Nlist

        for word in list:
            print(word)
            # 这个单词是规则左侧单词，赋值给key字符串
            if workingFlag == 0:
                # 许多语法规则被写成并列的格式时
                if word == '|':
                    workingFlag = 2
                    value = []
                    print("并列规则")
                elif word != ';':
                    key = word
                    value = []
                    workingFlag = 1
                    print("读入规则左侧，切入状态1")

            # 这个单词是规则右侧单词，加入到value列表中
            elif workingFlag == 1:
                # 读到冒号不算在内
                if word == ':':
                    print("读到冒号，开始读取语法规则右侧")
                elif word == '|':
                    value = []
                    workingFlag = 2
                    print("读到|分隔符，开始读取并列语法规则")
                # 在一个规则的结尾，必须有以#开头的单词，当读到它时，结束此规则的读取
                elif word.startswith('#'):
                    rule = grammarRule(key,value)
                    rules.append(rule)
                    print("读入规则+1")
                    for rule in rules:
                        print(rule.left, ':', rule.right)
                    workingFlag = 0
                # 其它情况应该被加入到value内
                else:
                    value.append(word)
                    print("读入单词+1")

            # 涉及到并列语法规则的读取
            elif workingFlag == 2:
                # 在一个规则的结尾，必须有以#开头的单词，当读到它时，结束此规则的读取
                if word.startswith('#'):
                    rule = grammarRule(key, value)
                    rules.append(rule)
                    workingFlag = 0
                    print("读入规则+1")
                    for rule in rules:
                        print(rule.left, ':', rule.right)
                # 出现其它word都应该被读入规则
                elif word == ';':
                    workingFlag = 0
                else:
                    value.append(word)

    print("以下是所有读取到的语法规则：")
    for rule in rules:
        print(rule.left, ':', rule.right)


getGrammar()