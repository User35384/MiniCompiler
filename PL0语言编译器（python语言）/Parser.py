
# 语法规则类
# left是语法规则左侧的单词，类型是字符串
# right是语法规则右侧的单词传，类型是字符串列表，其列表中元素顺序必须和语法规则相同
class grammarRule:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class LRItem:
    def __init__(self, rule, dotPos):
        self.rule = rule
        self.dotPos = dotPos

class LRStatus:
    def __init__(self,LRItemGroup,groupID):
        self.LRItemGroup = LRItemGroup
        self.groupID = groupID
        self.shiftMap = {}    # 移进映射表，用于存储接收什么符号迁到什么状态

    def equalGroup(self, group):
        if self.LRItemGroup == group:
            return True
        else :
            return False

    # 记录接收的符号和迁移到的状态,将其放入移进映射表中
    def addShift(self,acceptWord,shiftStatus):
        self.shiftMap[acceptWord] = shiftStatus

# 由外部文件得到语法规则
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
    print("下面是测试输出语句(test) : ")
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
            # print(word)
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
                    ()
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
                    # for rule in rules:
                    #     print(rule.left, ':', rule.right)
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
                    # for rule in rules:
                    #     print(rule.left, ':', rule.right)
                # 出现其它word都应该被读入规则
                elif word == ';':
                    workingFlag = 0
                else:
                    value.append(word)

    print("以下是所有读取到的语法规则：")
    for rule in rules:
        print(rule.left, ':', rule.right)

    return rules

# 由语法规则得到LR项目
def getLRItems(rules):
    items = []
    for rule in rules:
        length = len(rule.right)
        for i in range(0, length+1):
            item = LRItem(rule, i)
            items.append(item)
    return items

# 根据全部的items，来得到一个item列表的闭包
def getClosure(itemGroup,allItems):
    # 完成标识用来标记当前是否已经完成闭包中所有item的插入
    # 如果本次循环尚有改变，则说明还未结束，finishFlag未0
    resultGroup = []
    finishFlag = 0

    for item in itemGroup:
        resultGroup.append(item)
    while finishFlag == 0:
        finishFlag = 1
        for item in resultGroup:
            right = item.rule.right
            # print(right,"点的位置:",item.dotPos)
            if item.dotPos < len(right):
                nextWord = right[item.dotPos]
                for item in allItems:
                    if item.rule.left == nextWord and item.dotPos == 0 and item not in resultGroup:
                        finishFlag = 0
                        resultGroup.append(item)
    return resultGroup


# 输出一个LRItem对象的所有信息
def printItem(LRItem):
    print(LRItem.rule.left, ':', LRItem.rule.right, "点的位置：",LRItem.dotPos)

# 输出一个LRStatus对象的所有信息
def printStatus(LRStatus):
    status = LRStatus
    groupID = status.groupID
    items = status.LRItemGroup
    shiftMap = status.shiftMap
    print("状态",groupID,":")
    for item in items:
        printItem(item)

    for key,value in shiftMap.items():
        nStatus = value
        statusNO = nStatus.groupID
        print("接收", key, "迁移至状态", statusNO)

# 找一个LRItem其点后移一位对应的LRItem
def findNextItem(LRItem,allItem):
    right = LRItem.rule.right
    if LRItem.dotPos < len(right):
        for findItem in allItem:
            if findItem.rule == LRItem.rule and findItem.dotPos == LRItem.dotPos+1:
                # print("找到下一个item")
                targetItem = findItem
                break
    return targetItem


def buildStatusGroup(startLRGroup,allItem):
    # 参数说明：startLRGroup是一个LRItem的列表
    statusGroup = []    # 存储所有状态的列表
    statusNumber = 1
    finishFlag = 0
    sameFlag = False

    startStatus = LRStatus(startLRGroup,statusNumber)
    statusGroup.append(startStatus)


    for status in statusGroup:
        thisGroup = status.LRItemGroup
        for item in thisGroup:
            newGroup = []
            sameFlag = False
            right = item.rule.right
            # 仅当点后面有符号时，情况才被考虑在内
            if item.dotPos < len(right):

                print("当前item: ")
                printItem(item)

                # 找到这个LR项目中标点后的符号
                nextWord = right[item.dotPos]
                # 找到这个LR项目点后移一位对应的项目
                nextItem = findNextItem(item,allItem)

                print("下一个item是: ")
                printItem(nextItem)
                # 将此后移一位的项目加入到newGroup中并对其求闭包
                newGroup.append(nextItem)
                newGroup = getClosure(newGroup, allItem)

                print("求得闭包集为: ")
                for nItem in newGroup:
                    printItem(nItem)

                for nStatus in statusGroup:
                    if nStatus.equalGroup(newGroup):
                        print("找到相同组:", status.groupID, ",不重复添加新组")
                        status.addShift(nextWord,nStatus)
                        sameFlag = True
                        break

                if sameFlag == False:
                    # 得到闭包后即可创建新状态，将状态总数+1
                    statusNumber = statusNumber+1
                    print("添加第", statusNumber, "状态: ")
                    newStatus = LRStatus(newGroup,statusNumber)
                    printStatus(newStatus)
                    statusGroup.append(newStatus)
                    finishFlag = 0        # 只要有新加入的status，就表示还没结束
                    # 在本项目的移进映射表中加入此迁移
                    status.addShift(nextWord,newStatus)

    return statusGroup

# 从语法规则中获取所有终结符和非终结符
def getWords(rules):
    VT = []     # 终结符
    VN = []     # 非终结符
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

    return VT,VN

# 根据所有状态，来构建LR分析表
def buildLRTable(statusGroup,VN,VT,allRules):
    LRTable = {}       # 用字典存储LR分析表
    statusNum = len(statusGroup)
    # print("所有状态个数: ", statusNum)
    for status in statusGroup:
        statusNO = status.groupID   # 该状态标号
        shiftMap = status.shiftMap  # 该状态迁移至的其它状态
        itemGroup = status.LRItemGroup # 该状态包含的所有LR项目
        for word,shiftStatus in shiftMap.items():
            # GOTO表：接收非终结符迁移状态
            if word in VN:
                LRTable[(statusNO,word)] = ("goto", shiftStatus)
            # ACTION表中的shift(移进)部分
            elif word in VT:
                LRTable[(statusNO,word)] = ("shift",shiftStatus)

        # ACTION 表中的reduce(规约)部分
        for item in itemGroup:
            right = item.rule.right
            # 对于该项目，点的位置在其最后一位，则说明这是一个规约项目
            if item.dotPos == len(right):
                ruleNO = allRules.index(item.rule)
                for word in VN:
                    LRTable[(statusNO,word)] = ("reduce",ruleNO)



    return LRTable


# 获得所有语法规则
rules = getGrammar()
VT,VN = getWords(rules)   # 获取终结符和非终结符
# 获得所有LR项目
items = getLRItems(rules)
print("以下是所有LR项目")
for item in items:
    print(item.rule.left, ':', item.rule.right, "点的位置:", item.dotPos)

startGroup = []
startGroup.append(items[0])
startGroup = getClosure(startGroup, items)
print("以下是状态1的闭包项目集")
for item in startGroup:
    printItem(item)

print("以下是所有闭包项目集")
statusGroup = buildStatusGroup(startGroup, items)
for status in statusGroup:
    printStatus(status)

print("终结符VT:",VT)
print("非终结符VN:",VN)

LRTable = buildLRTable(statusGroup,VN,VT,rules)

for K,V in LRTable.items():
    statusNO,shiftWord = K
    action,shiftStatus = V
    if action != "reduce":
        shiftStatusNO = shiftStatus.groupID
        print("状态",statusNO,"接收",shiftWord,"进行",action,"至状态",shiftStatusNO,end='')
        print("(",statusNO,",",shiftWord,")->(",action,shiftStatusNO,")")
    else:
        ruleNO = shiftStatus
        print("状态",statusNO,"接收",shiftWord,"进行",action,"使用第",ruleNO,"号规则",end=' ')
        print("(",statusNO,",",shiftWord,")->(",action,ruleNO,")")





