original_list = [1, 2, 3]
print(original_list[::-1])




original_list = [1, 2, 3, 4, 5, 6]
start = 0
end = len(original_list) - 1

while start < end:
    original_list[start], original_list[end] = original_list[end], original_list[start]
    start += 1
    end -= 1
print(original_list)
