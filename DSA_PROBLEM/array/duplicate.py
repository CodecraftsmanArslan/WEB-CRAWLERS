# // brut force solution
arr_list = [1, 2, 3, 6, 3, 6, 1]
n = len(arr_list)

for i in range(n):
    for j in range(i+1, n):  
        if arr_list[i] == arr_list[j]:
            print(arr_list[i])


arr_list = [1, 2, 3, 6, 3, 6, 1]
seen = set()
duplicates = []

for num in arr_list:
    if num in seen:
        duplicates.append(num)
    else:
        seen.add(num)

print("Duplicate elements:", duplicates)