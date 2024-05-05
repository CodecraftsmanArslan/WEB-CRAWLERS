nums = [1, 4, 20, 3, 10, 5]
n=len(nums)
target = 33

start=0
current_sum=0
flag=False

for i in range(n):
    current_sum += nums[i]  
    while(current_sum>target):
        current_sum -=nums[start]
        start+=1
    if(current_sum==target):
        print("Indices:", start, "-", i) 
        flag=True

if not found:
    print("element not found")