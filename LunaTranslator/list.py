 
with open('t.ini','r',encoding='utf8') as ff:
    x=ff.read().split('\n')
with open('z.ini','r',encoding='utf8') as ff:
    y=ff.read().split('\n')
for i in range(len(x)):
    print(f'"{y[i]}":"{x[i]}",')
