num = [1, 1, 1, 2, 2, 2, 3,2]
n = len(num)
target = 2
occurrences = 0

for i in range(n):
    if num[i] == target:
        occurrences += 1

print("Occurrence of element", occurrences)
