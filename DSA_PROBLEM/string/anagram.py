str1 = "geeks"
str2 = "eggkf"
k = 1

freq_map = {}

for c in str1:
    if c in freq_map:
        freq_map[c] += 1
    else:
        freq_map[c] = 1

count = 0
for i in str2:
    if i in freq_map and freq_map[i] > 0:
        freq_map[i] -= 1
    else:
        count += 1

# Check if lengths are unequal
if len(str1) != len(str2):
    print("Not an anagram")
elif count <= k:
    print("Anagram")
else:
    print("Not an anagram")

