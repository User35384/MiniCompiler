# 运算符表
operator_set = {"+","-","*","/","<","<=",">",">=","=",":=",'<>'}
# 分隔符表
sep_set = {";","(",")",",","'",'"'}
# 关键字表
key_set = {
    "VAR", "CONST", "PROCEDURE", "CALL", "BEGIN","END", "IF",  "THEN", "WHILE", "DO",
  "ELSE", "WRITE", "READ","PROGRAM",}
# 数据类型
type_set = {"INT","BOOLEAN","CHAR","STRING"}
# 括号配对判断
kuo_set = {'(':')'}
# 转义字符后面可跟字符
special_char_set={"'","\"","\\","n","r","t"}
# 数字类型数据能包含的字符
number_set={"0","1","2","3","4","5","6","7","8","9",".","e","f"}

class word_analysis():
    def __init__(self, file='test.c'):
        self.word_list = []          # 输出单词列表
        self.name_list = []          # 变量
        self.tokens = []
        self.create_table(file)
        # self.print_result()

    def print_result(self):
        for word in self.word_list:
            print(word)

    def split(self,file):
        line_count=0
        lines=file.read().splitlines()

        is_operator=False
        is_string=False
        is_char=False
        is_trans=False
        words=[]
        word=''

        for line in lines:
            line_count+=1
            #任何一个字符有可能是单纯代表其内容或者是在字符或者字符串内
            for ch in line:
                #读取到分隔符
                if ch in sep_set:
                    if is_operator:
                        is_operator=False
                        words.append({'line': line_count, 'word': word})
                        word=''
                    #接下来是字符
                    if ch == "'":
                        #被转义作为本字符出现
                        if is_trans:
                            is_trans = False
                            word+=ch
                        else:
                            #作为用来标志接下来是一个字符类型数据的标识符
                            if is_char == False:
                                is_char=True
                            else:
                                is_char = False
                                if (word[0]=='\\' and len(word) == 2) or (not is_trans and len(word) == 1):
                                    is_trans = False
                                    words.append({'line': line_count, 'word': word})
                                    word = ''
                                else:
                                    print(f"编译错误，发生在第{line_count}行")
                            words.append({'line': line_count, 'word': ch})
                    #接下来是字符串
                    elif ch == "\"":
                        # 被转义作为本字符出现
                        if is_trans:
                            is_trans = False
                            word += ch
                        else:
                            #作为用来标志接下来是字符串内容的标识符
                            if is_string==False:
                                is_string=True
                            else:
                                is_string=False
                                words.append({'line': line_count, 'word': word})
                                word=''
                            words.append({'line': line_count, 'word': ch})
                    #其他分隔符，只能代表本符号或者字符串内符号
                    else:
                        #作为字符串或字符内符号
                        if is_string or is_char:
                            if is_trans:
                                print(f"编译错误，发生在第{line_count}行")
                                return
                            else:
                                word+=ch
                        #作为有作用的分隔符
                        else:
                            if len(word)>0:
                                words.append({'line': line_count, 'word': word})
                                word=''
                            words.append({'line': line_count, 'word': ch})
                #读取到运算符
                elif ch in operator_set:
                    #作为字符串或字符
                    if is_string or is_char:
                        if is_trans:
                            print(f"编译错误，发生在第{line_count}行")
                            return
                        else:
                            word+=ch
                    #作为运算符
                    else:
                        if is_operator:
                            word+=ch
                            #无此类型双字符运算符
                            if(word not in operator_set):
                                print(f"编译错误，发生在第{line_count}行")
                                return
                        else:
                            if len(word)>0:
                                words.append({'line': line_count, 'word': word})
                                word=''
                            is_operator=True
                            word+=ch
                #读取到其他字符(变量，常量(字符，字符串，整型，浮点型)，转义字符等)
                else:
                    if is_operator:
                        is_operator=False
                        words.append({'line': line_count, 'word': word})
                        word=''
                    #此字符应该是一个字符类型
                    if is_char:
                        if is_trans:
                            if ch in special_char_set:
                                word+=ch
                                is_trans=False
                            else:
                                print(f"编译错误，发生在第{line_count}行")
                                return
                        else:
                            if ch=='\\':
                                is_trans=True
                            word+=ch
                    #字符串类型
                    elif is_string:
                        if is_trans:
                            if ch not in special_char_set:
                                print(f"编译错误，发生在第{line_count}行")
                                return
                            else:
                                is_trans=False
                        else:
                            if ch =='\\':
                                is_trans=True
                        word+=ch
                    #处理源代码中不是被单引号和双引号括起来的内容
                    else:
                        if ch != ' ':
                            if ch==':':
                                is_operator=True
                            word+=ch
                        else:
                            if len(word)>0:
                                words.append({'line': line_count, 'word': word})
                                word=''
            if(len(word)>0):
                words.append({'line': line_count, 'word': word})
                word=''
        return words

    #数字类型里面有整数和小数，并且有正负，小数里面可能最后有一个字母f，或者有字母e代表次方1
    def check_number(self,word):
        double_e=False
        can_f=False
        cant_dot=False
        end=False
        must_int=False
        is_float=False

        #检查第一个字符,不可以为e和f
        if word[0]=='e' or word[0]=='f':
            return None

        #检查最后一个字符，不可以是e
        if word[-1]=='e':
            return None

        #逐个检查
        for char in word:
            if end:
                return None
            #如果有不合规的字符
            if char not in number_set:
                return None
            match char:
                #.前面可以跟任何数字字符串或不跟，后面只不能再跟.
                case ".":
                    is_float=True
                    if cant_dot or must_int:
                        return None
                    else:
                        cant_dot=True
                        can_f=True
                    break
                #f应该作为最后一个字符，或者在作为最后一个字符的时候前面有小数点或者e表明其是小数
                case "f":
                    is_float=True
                    if not can_f or must_int:
                        return None
                    end=True
                    break
                #e前面无所谓（除了f），e后面必须跟一个整型数据，即不可以读取到.和e就行
                case "e":
                    is_float=True
                    if double_e:
                        return None
                    else:
                        double_e=True
                        can_f=True
                        cant_dot=True
                        must_int=True
                    break
        if is_float:
            return 'FLOAT'
        else:
            return 'NUMBER'

    #变量名称以字母和下划线开头，包含数字字母下划线
    def check_variable(self, word):
        if word[0] >= 'a' and word[0] <= 'z' or word[0] >= 'A' and word[0] <= 'Z' or word[0] == '_':
            for w in word:
                if w >= 'a' and w <= 'z' or w >= 'A' and w <= 'Z' or w == '_' or w >= '0' and w <= '9':
                    continue
                else:
                    return False
            return True
        return False

    #operator_set = {"+", "-", "*", "/", "<", "<=", ">", ">=", "=", ":="}
    def get_operator_type(self, word):
        match(word):
            case '+': return 'PLUS'
            case '-': return 'MINUS'
            case '*': return 'STAR'
            case '/': return 'SLASH'
            case ':=': return 'ASSIGN'
            case '=': return 'EQUAL'
            case '<>': return 'NOT_EQUAL'
            case '<': return 'LESS'
            case '<=': return 'LESS_EQ'
            case '>': return 'GREATER'
            case '>=': return 'GREATER_EQ'

    # sep_set = {";", "(", ")", ",", "'", '"'}
    def get_sep_type(self, word):
        match(word):
            case ';': return 'SEMI'
            case ',': return 'COMMA'
            case '(': return 'LPAREN'
            case ')': return 'RPAREN'

    def get_keyword_type(self, word):
        return word

    def get_type_type(self, word):
        return word

    def create_table(self, file):
        is_char=False
        is_string=False

        f=open(file, 'r', encoding='UTF-8')

        elements = self.split(f)

        for e in elements:
            line=e['line']
            word=e['word']
            if is_char:
                self.word_list.append({'line':line,'word':word,'type':'CHAR'})
                is_char=False
            elif is_string:
                self.word_list.append({'line':line,'word':word,'type':'STRING'})
                is_string=False
            # 判断是否为运算符
            elif word in operator_set:
                element_type=self.get_operator_type(word)
                self.word_list.append({'line':line,'word':word,'type':element_type})
            # 判断是否为分隔符
            elif word in sep_set:
                element_type = self.get_sep_type(word)
                self.word_list.append({'line':line,'word':word,'type':element_type})
                if word=="'":
                    is_char=True
                elif word=="\"":
                    is_string=True
            #判断是否为关键字
            elif word in key_set:
                element_type=self.get_keyword_type(word)
                self.word_list.append({'line':line,'word':word,'type':element_type})
            #判断是否为数据类型
            elif word in type_set:
                element_type=self.get_type_type(word)
                self.word_list.append({'line':line,'word':word,'type':element_type})
            #其他字符：变量名，常量（数字）
            else:
            #是否为数字
                type_result = self.check_number(word)
                if type_result != None:
                    self.word_list.append({'line':line,'word':word,'type':type_result})
                    continue
                if self.check_variable(word):
                    if word not in self.name_list:
                        self.word_list.append({'line': line, 'word': word, 'type': 'IDENTIFIER'})
                        self.name_list.append({'line':line,'word':word,'type':'IDENTIFIER'})
                    continue
                print(f"编译发生错误，在第{line}行")

        self.word_list.append({'line':0,'word':'#','type':'#'})


if __name__ == "__main__":
    a = word_analysis('PL0code.txt')
    a.print_result()
