nums = [2,3,-2,4]

current_product = nums[0]  
max_product = nums[0]      

for num in nums[1:]:     
    current_product = max(num, current_product * num)
    max_product = max(max_product, current_product)

print(max_product)















