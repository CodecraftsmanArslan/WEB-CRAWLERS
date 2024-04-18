import pandas as pd

df = pd.read_excel("portugal3.xlsx",engine='openpyxl')

def remove_spaces(phone_number):
    return phone_number.replace(" ", "")

df['telephone']  = df['telephone'].apply(lambda x: remove_spaces(x) if isinstance(x, str) else x)
df['fax']=df['fax'].apply(lambda x: remove_spaces(x) if isinstance(x, str) else x)

df.to_excel('portugal4.xlsx')



