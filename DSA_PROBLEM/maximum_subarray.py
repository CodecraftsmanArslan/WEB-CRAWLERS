arr = [-2,-3,4,-1,-2,1,5,-3]
max_sum=0
current_sum=0

for i in range(len(arr)):
    current_sum +=arr[i]
    max_sum=max(max_sum,current_sum)
    if(current_sum<0):
        current_sum=1

print(max_sum)















