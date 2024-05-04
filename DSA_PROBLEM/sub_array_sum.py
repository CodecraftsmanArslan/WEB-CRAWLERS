nums = [1,4,20,3,10,5] 
n=len(nums)
target = 33

left=0
right=0
current_sum=0

for i in range(n):
    current_sum += nums[i]  
    if (current_sum<target):
        left += 1
    elif(target>current_sum):
        current_sum -= nums[right] 
        right+=1
    elif(current_sum==target):
        print(nums[right]," ",nums[left])

