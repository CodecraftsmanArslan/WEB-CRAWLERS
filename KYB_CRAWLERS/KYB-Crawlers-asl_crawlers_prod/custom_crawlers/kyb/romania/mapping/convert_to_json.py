import csv
import json

f = open('5nomenclator_stari_firma.csv','r', encoding='ISO-8859-2')
rows = f.readlines()[1:]
data = {}
for row in rows:
    row = row.strip()
    cols = row.split('|')
    cod = cols[0]
    denumire = cols[1]
    data[cod] = denumire

json_data = json.dumps(data, ensure_ascii=False)
ff = open('mapping.json','w', encoding='ISO-8859-2')
ff.write(json_data)
ff.close()
print(json_data)
