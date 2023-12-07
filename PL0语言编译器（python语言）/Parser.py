
file_name = "rules" + "/" + "ParserRules.txt"
f = open( file_name, 'r',encoding = 'utf-8' )


print(f.readline())
print(f.tell())
f.close()