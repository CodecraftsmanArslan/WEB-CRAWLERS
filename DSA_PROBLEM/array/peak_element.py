arr = [1, 3, 20, 4, 1, 0]
n=len(arr)
high=n-1
low=0

while(low<high):
    mid = (low+high)// 2
    if (mid==0 or arr[mid+1]<arr[mid]) and (mid==n-1 or arr[mid-1]<arr[mid]):
        print(arr[mid])
        break

    elif arr[mid]<arr[mid+1]:
        low=mid+1

    else:
        high=mid-1