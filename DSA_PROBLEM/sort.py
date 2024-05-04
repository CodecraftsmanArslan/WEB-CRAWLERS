array_list = [2, 1, 4, 3]
n = len(array_list)

for i in range(n - 1):  
    if array_list[i] > array_list[i + 1]:
        temp = array_list[i]
        array_list[i] = array_list[i + 1]
        print(array_list[i]) 
        array_list[i + 1] = temp
        print( array_list[i + 1])
print(array_list)







