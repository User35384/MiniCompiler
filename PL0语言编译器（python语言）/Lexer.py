# 运算符表
operator_set = {"+","-","*","/","<","<=",">",">=","=",":=",'<>'}
# 分隔符表
sep_set = {";","(",")",","}
# 关键字表
key_set = {
    "VAR", "CONST", "PROCEDURE", "CALL", "BEGIN","END", "IF",  "THEN", "WHILE", "DO",
  "ELSE", "WRITE", "READ","PROGRAM",}
#空白集
space_set={' ','\r','\t','\n'}

class Lexer():

    def __init__(self, file_name='testCodes/PL0code.txt'):

        self.token_list=[]
        self.name_list=[]
        self.pos=0
        self.first_set=[]

        self.get_first_set()
        self.create_list(file_name)
        self.print_result()

    def get_first_set(self):
        for element in sep_set:
            self.first_set.append(element[0])
        for element in operator_set:
            self.first_set.append(element[0])

    def print_result(self):
        for word in self.token_list:
            print(word)

    def is_digital(self,word):
        if ord(word) >= ord('0') and ord(word) <= ord('9'):
            return True
        else:
            return False

    def is_alphabet(self,word):
        if ord(word) >= ord('a') and ord(word) <= ord('z') or ord(word) >= ord('A') and ord(word) <= ord('Z'):
            return True
        else:
            return False

    def is_space(self,word):
        if word in space_set:
            return True
        else:
            return False

    def is_legal_punctuation(self,word):
        if word in self.first_set:
            return True
        else:
            return False

    def get_punctuation_type(self,word):
        match (word):
            case '+': return 'PLUS'
            case '-': return 'MINUS'
            case '*': return 'STAR'
            case '/': return 'SLASH'
            case '=': return 'EQUAL'
            case ';': return 'SEMI'
            case ',': return 'COMMA'
            case '(': return 'LPAREN'
            case ')': return 'RPAREN'


    def create_list(self,file_name):
        file=open(file_name,'r',encoding='UTF-8')

        line_count = 0
        lines = file.readlines()

        for line in lines:
            current_pos=0
            line_count+=1
            while current_pos<len(line):
                word=''
                if self.is_space(line[current_pos]):
                    current_pos+=1
                    continue
                elif self.is_digital(line[current_pos]):
                    word+=line[current_pos]
                    current_pos+=1
                    while self.is_digital(line[current_pos]):
                        word+=line[current_pos]
                        current_pos+=1
                        if current_pos>=len(line):
                            break
                    self.token_list.append({'line':line_count,'word':word,'type':'NUMBER'})
                elif self.is_alphabet(line[current_pos]):
                    word+=line[current_pos]
                    current_pos+=1
                    while self.is_digital(line[current_pos]) or self.is_alphabet(line[current_pos]):
                        word+=line[current_pos]
                        current_pos+=1
                        if current_pos>=len(line):
                            break
                    if word in key_set:
                        type=word
                    else:
                        type='IDENTIFIER'
                        if word not in self.name_list:
                            self.name_list.append({'name':word,'value':None})
                    self.token_list.append({'line':line_count,'word':word,'type':type})
                elif self.is_legal_punctuation(line[current_pos]):
                    match line[current_pos]:
                        case ('+'|'-'|'*'|'/'|'='|';'|'('|')'|','):
                            word+=line[current_pos]
                            current_pos += 1
                            type=self.get_punctuation_type(word)
                            self.token_list.append({'line': line_count, 'word': word,'type':type})
                        case '<':
                            word += line[current_pos]
                            current_pos += 1
                            if current_pos >= len(line):
                                break
                            if line[current_pos]=='=':
                                word += line[current_pos]
                                current_pos += 1
                                self.token_list.append({'line': line_count, 'word': word,'type':'LESS_EQ'})
                            elif line[current_pos]=='>':
                                word += line[current_pos]
                                current_pos += 1
                                self.token_list.append({'line': line_count, 'word': word,'type':'NOT_EQUAL'})
                            else:
                                self.token_list.append({'line': line_count, 'word': word,'type':'LESS'})
                        case '>':
                            word += line[current_pos]
                            current_pos += 1
                            if current_pos >= len(line):
                                break
                            if line[current_pos]=='=':
                                word += line[current_pos]
                                current_pos += 1
                                self.token_list.append({'line': line_count, 'word': word,'type':'GREATER_EQ'})
                            else:
                                self.token_list.append({'line': line_count, 'word': word,'type':'GREATER'})
                        case ':':
                            word += line[current_pos]
                            current_pos += 1
                            if current_pos >= len(line):
                                break
                            if line[current_pos]=='=':
                                word += line[current_pos]
                                current_pos += 1
                                self.token_list.append({'line': line_count, 'word': word,'type':'ASSIGN'})
                            else:
                                print(f'编译错误，在第{line_count}行')
                                return
                else:
                    print(f'编译错误，在第{line_count}行')
                    return
        self.token_list.append({'line':line_count,'word':'#','type':'#'})


x=Lexer("testCodes/PL0code.txt")