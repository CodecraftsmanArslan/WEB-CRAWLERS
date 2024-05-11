# s = "The quick brown fox jumps over the lazy dog"
# s_without_spaces = s.replace(" ", "").replace(",","")
# seen=set()


# for i in s_without_spaces:
#     seen.add(i)
# print(len(seen))




s = "Bawds jog, flick quartz, vex nymph"
alphabets="abcdefghijklmnopqrstuvwxyz"
flag=True

for i in alphabets:
    if i not in s.lower():
        flag=False


if (flag==True):
    print("panagram")
else:
    print("not panagram")