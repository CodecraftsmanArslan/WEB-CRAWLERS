f = open('data.csv', 'r')
lines = f.readlines()
f.close()
ff = open('data-cleaned.csv','w')
names = set()

for line in lines:
    n = line.split(',')[0]
    if n not in names:
        ff.write(f'{line}')
        names.add(n)
ff.close()