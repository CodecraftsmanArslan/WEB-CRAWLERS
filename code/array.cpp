// #include<iostream>
// using namespace std;
// int main(){

//     int N=5,i,k=4;
//     int count=0; 
//     int arr[]={1 ,2 ,3, 4, 5};

//     for (i=0 ; i<N ;i++){
//         if(arr[i]==k){ 
//              count = i;  
//              }
//         }
//         cout<<count;
// }



// #include<iostream>
// using namespace std;
// int main(){
//     int a[] = {0, -1, 2, -3, 1},temp,sum;
//     int n=sizeof(a)/sizeof(a[0]);

//     for(int i=0; i<n ;i++){
//         sum+=a[i];
//         if(sum==0){
//             cout<<sum<<"true";
//         }
//     }
    
// }











// #include<iostream>
// using namespace std;
// int main()
// {
//     int arr[] = {3, 4, 7, 8, 6, 2, 1};
//     int n= sizeof(arr)/sizeof(arr[0]);
//     int flag;
//     for (int i = 1; i <=n-2; i++){
//         if(flag==1){
//             if(arr[i]>arr[i+1]){
//                 swap(arr[i],arr[i+1]);
//                 }
//         }

//         else{
//             if(arr[i]<arr[i+1]){
//                 swap(arr[i],arr[i+1]);
//             }
//         }
//         flag=!flag;
//         }
//     for (int i=0; i<n; i++)
//         cout << arr[i] << " ";
        
// }


// #include<iostream>
// using namespace std;
// int main(){
//     int arr[]={1, 1, 2, 2, 2, 2, 3};
//     int c;
//     int x=7,count=0;

//     for (int i=0; i<n; i++){
//         if(x==arr[i]){
//             count++;
//         }
       
//     }
//     cout<<count<<endl;
// }




// #include<iostream>
// using namespace std;
// int main(){
//     int N[]={1,2,3,4};
//     int x=sizeof(N)/sizeof(N[0]);
//     int y=5;

//     for (int i=0;i<x;i++){
//         if( N[i]==0){
//             N[i]=y;
//             cout<<N[i];  
//         }
//         else if(N[i]!=0){
//             cout<<N[i];
//             }
//     }
// }



// #include<iostream>
// using namespace std;
// int main(){
//     int arr[]={1, 0, 1, 1, 0};
//     int n= sizeof(arr)/sizeof(arr[0]);
//     int temp;

//     for(int i=0;i<n;i++){
//         for(int j=0;j<n;j++){
//             if(arr[j]>arr[j+1]){
//             temp=arr[j+1];
//             arr[j+1]=arr[j];
//             arr[j]=temp;
//         }

//         }
        
//     }
//     for(int j=0;j<n;j++){
//         cout<<arr[j]<<endl;
//     }

// }







//4 Remove duplicate element from unsorted array

   


// #include<iostream>
// using namespace std;
// int main(){
//     int a[] = {3, 1, 1};
//     int b[] = {6, 5, 4};
//     int n = sizeof(a)/sizeof(a[0]);
//     int k = sizeof(b)/sizeof(b[0]);
//     int temp;
//     int sum;
//     int t;
//     int result=0;
//     for(int i=0;i<n;i++){
//         if(a[i]>a[i+1]){
//             temp=a[i+1];
//             a[i+1]=a[i];
//             a[i]=temp;
//         }
//     }
//     for(int i=0;i<n;i++){
//         result+= (a[i] * b[i]); 
        
//     }
//     cout<<result;
    
// }   


// sum question through greedy and two pointer
// #include<iostream>
// using namespace std;
// int main(){
//     int num[]={-3,2,3,3,6,8,15};
//     int target=6;
//     int start=0;
//     int end=(sizeof(num)/sizeof(num[0]))-1;
//     int result;

//     while(start<end){
//         int t=num[start]+num[end];
//         if (t==target){
//             result=t;
//             break;
//         }
//         else if(t<target){
//             start++;
//         }
//         else{
//             end++;
//         }
      
//     }
//     cout<<result;
// }


// #include<iostream>
// using namespace std;
// int main(){
//     int arr[ ]={5, 9, 2, 6} ;
//     int n = sizeof(arr)/sizeof(arr[0]);
//     int max=2;
//     int result;
//     for(int i=0;i<n;i++){
//         if(arr[i]==max){
//             result=arr[i];
//         }
//         else{
//             continue;
//         }

//     }
//     cout<<result;   
// }


// segregation of even and odd
// #include<iostream>
// using namespace std;
// int main(){
//     int arr[] = {12, 34, 45, 9, 8, 90, 3};
//     int n = sizeof(arr)/sizeof(arr[0]);
//     int temp;
//     int per;

//     for(int i=0;i<n;i++){
//         for(int j=0;j<n;j++){
//             if(arr[j]>arr[j+1]){
//                 temp=arr[j+1];
//                 arr[j+1]=arr[j];
//                 arr[j]=temp;
//                 }
//             }

//         }
//     for(int i=0;i<=n;i++){
//         if(arr[i]%2==0){
//              cout<<arr[i]<<endl;
//              }
//         }

//     for(int i=0;i<n;i++){
//         if(arr[i]%2!=0){
//              cout<<arr[i]<<endl;
//              }
//         }
// }



// strange sorting
// #include<iostream>
// using namespace std;
// int main(){
//    int a[] ={7, 1, 5, 3, 9};
//    int b[] ={8, 4, 3, 5, 2, 6};
//    int arr[100];
//    int r;
//    int i;
//    int temp;
//    int n = sizeof(a)/sizeof(a[0]);
//    int m = sizeof(b)/sizeof(b[0]);
//    for(int i=0;i<n;i++){
//       arr[r++]=a[i];
      
//    }
//    for(i=0;i<m;i++){
//       arr[r++]=b[i];
      
//    }
//    for(i=0;i<n+m;i++){
//       for(int j=i+1 ;j<n+m;j++){
//          if(arr[i]>arr[j]){
//             temp=arr[j];
//             arr[j]=arr[i];
//             arr[i]=temp;
//             }
//       }
//    }
//    for(int i=0;i<n+m;i++){
//       cout<<arr[i];
//    }
// }
//    for(int i=0 ;i<n+m;i++){
//       for(int j=i+1 ;j<n+m;j++){
//          if(arr[i]==arr[j]){
//             for(int k=j;k=n+m;k++){
//                arr[k]=arr[k+1];
//             }
//             n--;
//             j--;
//          }    
//       }
         
//    }
//    for(int i=0;i<n+m;i++){
//       cout<<arr[i];
//    }
   
// }

 

// 




// #include<iostream>
// using namespace std;
// int main(){
//     int arr[]={2, 4, 6, 8, 12};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     int sum=0;
//     int last;
//     for(int i=0 ; i<n ;i++){
//         sum+=arr[i];
//         if(sum%2==0){
//             last=sum+5;

//         }
//     }
//     cout<<last-sum;
// }




// #include<iostream>
// using namespace std;
// int main(){
//     int arr[]={1, 3, 3, 4};
//     int start=0;
//     int end=(sizeof(arr)/sizeof(arr[0]))-1;
//     int x=3;
//     int mid;
//     while(start<end){
//         mid=(start+end)/2;
//         if(arr[mid]==x){
//             start=start+1;
            
//         }
//         else if(arr[mid]<end){
//             end=mid-1;
//         }
//     }
//     cout<<start<<" "<<end;
// }



    
// find first and last occuerence 0f x
// #include<iostream>
// using namespace std;
// int main(){

//     int arr[]={1, 2, 2, 2, 2, 3, 4, 7, 8, 8 };
//     int start=0;
//     int end=(sizeof(arr)/sizeof(arr[0]))-1;
//     int x=2;
//     int mid;
//     int result;
//     while(start<end){
//         mid=(start+end)/2;
//         if(arr[mid]==x){
//             result=mid;
//             end=mid-1;
//         }
//         else if(arr[mid]<x){
//             start=mid+1;
//         }
//         else{
//             end=mid-1;
//         }
//     }
//     cout<<start<<" ";
//     start=0;
//     end=(sizeof(arr)/sizeof(arr[0]))-1;
//     while(start<end){
//         mid=(start+end)/2;
//         if(arr[mid]==x){
//             result=mid;
//             start=mid+1;
            
//         }
//         else if(arr[mid]>x){
//              end=mid-1;
//         }
//     }
//     cout<<result;

// }




// find first and last occuerence 0f x
// #include<iostream>
// using namespace std;
// int main(){

//     int arr[]={ 1, 2, 2, 2, 2, 3, 4, 7, 8, 8};
//     int start=0;
//     int end=(sizeof(arr)/sizeof(arr[0]))-1;
//     int x=8;
//     int mid;
//     int result;
//     while(start<end){
//         mid=(start+end)/2;
//         if(arr[mid]<x){
//             start=mid+1;

//         }
//         else if(arr[mid]<x){
//             start=mid+1;


//         }
//         else{
//             end=mid-1;
//         }
//     }
//     cout<<"first occuerence: "<<start<<endl;
//     start=0;
//     end=(sizeof(arr)/sizeof(arr[0]))-1;
//     while(start<end){
//         mid=start+(end-start)/2;
//         if(arr[mid]<x){
//             start=mid+1;

//         }
//         else if(arr[mid]<x){
//             start=mid+1;


//         }
//         else{
//             end=mid+1;
//             cout<<"second occuerence: "<<end;
//             break;        
//     }
//     }
// }




// find first and last occuerence 0f x
// #include<iostream>
// using namespace std;
// int main(){

//     int arr[]={21,32,51,70,71};
//     int start=0;
//     int end=(sizeof(arr)/sizeof(arr[0]))-1;
//     int x=70;
//     int mid;
//     int result;
//     while(start<end){
//         mid=(start+end)/2;
//         if(arr[mid]<x){
//             start=mid+1;
//         }
//         else if(arr[mid]==x){
//             end=mid-1;
//         }
//     }
//     cout<<"first occuerence= "<<start;
// } 





   
// #include<iostream>
// using namespace std;
// int main(){

//     int arr[]={1,2,3,7,5};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     int sum=0;
//     int x=12;
//     int result;
//     for(int i=0;i<n;i++){
//         for (int j=i;j<n;j++){
//             sum+=arr[j];
//             result=sum;
//             }
//         }
//         cout<<result<<endl;
//     }




// #include<iostream>
// using namespace std;

// struct Node{
//     int data;
//     Node *next;
        
//     };

//     Node *head=NULL;



    
// void insert(int d){
//     Node *first=new Node;
//     first->data=d;
//     first->next=NULL;

//     if(head==NULL){
//         head=first;
//     }
//     else{
//         Node *last=head;
//         while(last->next!=NULL){
//             last=last->next;
//         }
//         last->next=first;
//     }

// };

// void remove(int d){
//     if(head->data==d){
//         Node *t=head;
//         head=head->next;
//         delete t;

//     }
//     else{
//         Node *current=head->next;
//         Node *previous= head;
//         while(current!=NULL){
//             if (current->data ==d){
//                 previous->next=current->next;
//                 delete current;
//                 break;

//             }
//             previous=current;
//             current=current->next;
            
//         }
        
//     }


// }



// void search(int d){
//     bool found =false;
//     Node *s=head;
//     while(s!=NULL){
//         if(s->data==d){
//             found =true;
//         }
//         s=s->next;
//     }
//     if(found==true){
//         cout<<"found"<<endl;
//     }
//     else{
//         cout<<" not found"<<endl;
//     }


// }

// void print(){
//     Node *temp=head;
//     while(temp!=NULL){
//         cout<<temp->data<<" ";
//         temp=temp->next;
//     }
//     cout<<endl;
// }



// int main(){
//     insert(1);
//     insert(2);
//     insert(3);
//     insert(4);

//     search(3);


//     remove(4);
//     print();
// return 0;
// }




// #include<iostream>
// using namespace std;
// int main(){

// int arr[]={2,7,8,9};
// int start=0;
// int end=(sizeof(arr)/sizeof(arr[0]))-1;
// int sum=0;
// int target=9;
// int result;

// while(start<end){

//     sum=arr[start]+arr[end];
//     if(sum==target){
//         cout<<start<<" "<<end;
//         break;
//     }
//     else if(sum<target){
//         end=end-1;
//         }
//     else{
//         end--;
//     }
//     }
// }


// #include<iostream>
// #include <cstring>
// using namespace std;

// int main(){

// char s[100];
// char large_word[50];
// int max=0;
// int c=0;
// int index;
// int i;
// int l;
// cout<<"Enter number=";
// cin>>s;
// l= strlen(s);

// for(i=0;i<l;i++){
//     if (s[i] !=' '){
//         c++;
//     }
//     else{
//         if(c>max){
//             max=c;
//             index=i-max;
//         }
//         c=0;
//         }
//     }

//     if(c>max){
//         max=c;
//         index=l-max;
//     }
//     int j=0;
//     for(i=index;i<index+max;i++){
//         large_word[j]=s[i];
//         j++;
//     }
//     large_word[j ]='\0';
//     cout<<large_word;

// }


// #include<iostream>
// using namespace std;
// int main(){
//     int num;
//     int i;
//     int n=8;
//     int fact=1;
//     for(i=1;i<=n;i++){
//         fact*=i;
//         }
//         cout<<fact;
// }

// find second largest element in array
// #include<iostream>
// using namespace std;
// int main(){
//     int arr[]={21,32,34};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     int max1=0;
//     int max2=0;

//     for(int i=0;i<n;i++){
//         if(arr[i]>max1){
//             max2=max1;
//             max1=arr[i];
//         }
//         else if(arr[i]>max2){
//             max2=arr[i];
//         }
       
//     }
//     cout<<max2;
// }














// #include<iostream>
// using namespace std;
// int main(){
//     int n;

//     cout<<"enter number";
//     cin>>n;


//     if(n==1){
//         cout<<"I";
//     }
//     else if(n==5){
//         cout<<" V";
//     }
//     else if(n==10){
//         cout<<"X";
//     }
//     else if(n==50){
//         cout<<"L";
//     }
// }



// maximum sum with subarray
// #include<iostream>
// using namespace std;
// int main(){
//     int arr[]={1,2,3,4,5,6,7,8,9,10};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     int start=0;
//     int sum=0;
//     int s=15;
//     int flag;

//     for(int i=0;i<n;i++){
//         sum=sum+arr[i];
//         while(sum>s){
//             sum=sum-arr[start];
//             start++;
//         }
//         if(sum==s){
//             cout<<start+1<<" "<<i+1;
//             flag=1;
//             break;
//         }
//         if(flag==0){
//             cout<<-1;
//         }
//     }
// }


// maximum sum with contigous subarray
// #include<iostream>
// using namespace std;
// int main(){
//  int maxSum = INT_MIN, sum = 0;
//         for(int i = 0; i < n; i++){
//             sum = sum + arr[i];
//             maxSum = max(maxSum, sum);
            
//             if(sum < 0){
//                 sum = 0;
//             }
//         }
        
//         return maxSum;

// }

// Brute Force Approach for maximum contigous subarray

// #include<iostream>
// using namespace std;

// void maxSubArray(int arr[],int n){
//    int sum,max1=0,max2=0;
//    for(int i=0;i<n;i++){
//       sum=0;
//       for(int j=i;j<n;j++){
//          sum+=arr[j];
//       if(sum>max1){
//          max1=sum;
//          }
//       else if(max1>max2){
//          max2=max1;
//       }
//    }
// }
//    cout<<max2;
      
// }

// int main(){
//    int arr[]={1,2,3,-2,5};
//    int n=sizeof(arr)/sizeof(arr[0]);
//    maxSubArray(arr,n);
// }
// rotate array 1 method

// #include<iostream>
// #include <vector>
// using namespace std;
// int main(){
//     int arr[]={1,2,3,4,5};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     int k=2;
//     int i;
//     int temp[n];
//     int t;
//     for(i=0;i<n;i++){
//         temp[(i+k)%n]=arr[i];
//         }
//     for(int u=0;u<n;u++){
//         cout<<temp[u];
//     }
// }



// rotate array 2 method

// #include<iostream>
// #include <vector>
// using namespace std;
// int main(){
//     int arr[]={1,2,3,4,5};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     int k=2;
//     int t=0;
//     int temp[n];

//     for(int i=k;i<n;i++){
//         temp[t]=arr[i];
//         t++;
//     }

//     for(int i=0;i<k;i++){
//         temp[t]=arr[i];
//         t++;

//     }

//     for(int i=0;i<n;i++){
//         arr[i]=temp[i];
//     }
    
//     for(int i=0;i<n;i++){
//         cout<<arr[i]<<" ";

//     }

// }





// wave array
// #include<iostream>
// using namespace std;
// int main(){
//     int arr[]={2,4,7,8,9,10};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     for(int i=0;i<n-1;i++){
//          int temp=arr[i];
//          arr[i]=arr[i+1];
//          arr[i+1]=temp;
//          i++;
//          }
//     for(int i=0;i<n;i++){
//         cout<<arr[i]<<" ";
//     }

   
// }





// #include<iostream>
// using namespace std;
// int main(){
//     int a1[] = {10, 5, 2, 23, 19};
//     int a2[] = {19, 5, 3};
//     int flag;
//     int n1=sizeof(a1)/sizeof(a1[0]);
//     int n2=sizeof(a2)/sizeof(a2[0]);
//      for(int i=0;i<n2;i++){
//       for(int j=0 ;j<n1;j++){
//         if(a2[i]==a1[j]){
//             flag=0;
//         }
//         else{
//             flag=1;
//         }
//     }
//     }
//      if(flag==0){
//         cout<<"yes";
//     }
//     else if(flag==1){
//         cout<<"no";
//     }
// }




// #include<iostream>
// using namespace std;
// int main(){
//     int arr[]={2,-4,7,-8,9};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     int temp[6];
//     int i;
//     int t=0;
//     int k=0;

//     for(int i=0;i<n;i++){
//         if(arr[i]>0){
//             temp[i]=arr[i];
//             }
//     }
//     k=i;
//     for(int i=0;i<n;i++){
//         if(arr[i]<0){
//             temp[k]=arr[i];
//             k++;
//             }
//     }
//     for(int i=0;i<k;i++){
//         cout<<temp[i];
//     }
// }








// #include<iostream>
// using namespace std;
// int main(){
//     int a1[]={1,2,3};
//     int a2[]={2,5,6};
//     int m=sizeof(a1)/sizeof(a1[0]);
//     int n=sizeof(a2)/sizeof(a2[0]);
//     int t=0;
//     int k=0;
//     int i;
//     int temp[6];


//     for(i=0;i<m;i++){
//         temp[i]=a1[i];
//         }
//     k = i;
//     for(i=0;i<n;i++){
//         temp[k]=a2[i];
//         k++;
//     }

//     for(int j=0;j<k;j++){
//         cout<<temp[j];
//     }
// }








// Count pairs with given sum
// #include<iostream>
// using namespace std;
// int main(){

//     int arr[]={1, 5, 7, -1};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     int target=6;
//     int sum;
//     int a=0;


//     for(int i=0;i<n;i++){
//         for(int j=i+1;j<n;j++){
//             sum=arr[i]+arr[j];
//             if(sum==target){
//                 a++;
//             }
//         }
//     }
//     cout<<a;
// }

// Find the Missing Number using xor approach
// #include<iostream>
// using namespace std;
// int main(){
//      int arr[]={1, 2, 3, 5};
//      int n=sizeof(arr)/sizeof(arr[0]);
//      int x1=arr[0];
//      int x2=1;
//      int miss;
//      for (int i=1;i<n;i++){
//         x1=x1^arr[i];
//      }
//      for (int i=2;i<=n+1;i++){
//         x2=x2^i;
//      }
//      miss=x1^x2;
//      cout<<miss;
// }

// #include<iostream>
// using namespace std;
// bool KeyPair(int arr[], int n,int target){
//    int sum;
//    for(int i=0;i<n;i++){
//         for(int j=i+1;j<n;j++){
//             sum=arr[i]+arr[j];
//             if(sum==target){
//                return 1 ;
              
//             }
//          }
//       }
//       return 0;
// }


// int main(){
//    int arr[]={1, 8, 45, 6, 8, 2};
//    int n=sizeof(arr)/sizeof(arr[0]);
//    int target=16;
//    if (KeyPair(arr,n,target)){
//       cout<<"yes";
//    }
//    else {
//         cout << "No" << target << endl;
//     }
 
// }





// #include<iostream>
// using namespace std;


// void KeyPair(int arr[],int end){
//    int sum;
//    int target=16;
//    int start=0;
//    int result;
//    int t;
//    int flag;

//    while(start<end){
//       t=arr[start]+arr[end];
//       if (t==target){
//          flag=0;
//          break;
//       }
//       else if(t<target){
//          start++;
//       }
//       else{
//          end++;
//       }
   
//    }
//    if(flag==0){
//        cout<<"yes";
//        }
// }
   


// int main(){
//    int arr[]={1, 4, 45, 6, 10, 8};
//    int end=sizeof(arr)/sizeof(arr[0]);
//    KeyPair(arr,end);

// }






// #include<iostream>
// using namespace std;

// void SmallestSum(int arr[],int n,int target){
//    int sum=0;
//    int t;
//    int c=0;
//    for(int i=0;i<n;i++){
//       for(int j=i;j<n;j++){
//          sum+=arr[j];
//          if(sum>target){
//             cout<<sum<<endl;
//          }
//       }
//       sum=0;
//    }
// }


// int main(){
//    int arr[]={1, 4, 45, 6, 0, 19};
//    int n=sizeof(arr)/sizeof(arr[0]);
//    int target=51;
//    SmallestSum(arr,n,target);
// }




// #include<iostream>
// using namespace std;

// void Smallest(int arr[],int n,int target){
//    int start=0, end=0,current_sum=0,min_len=n+1;
//    while(end<n){
//       current_sum+=arr[end++];
//       while(current_sum>target &&end<=n){
//             if(end-start<min_len){
//                min_len=end-start;
//             }
//             current_sum-=arr[start++];
//          }
//       }
//       cout<<min_len;
// }

// int main(){
//    int arr[]={1, 11, 100, 1, 0, 200, 3, 2, 1, 250};
//    int n=sizeof(arr)/sizeof(arr[0]);
//    int target=280;
//    Smallest(arr,n,target);

// }


//Maximum product subarray
// #include<iostream>
// using namespace std;
// void  maxProduct(int arr[],int n){
//    int ans=INT_MIN,product=1;
//    for(int i=0;i<n;i++){
//       for(int j=i;j<n;j++){
//          product*=arr[j]; 
//          ans=max(ans,product);
//       }
//       product=1;
//    }
//    cout<<ans<<endl;
// }

// int main(){
//    int arr[]={-2};
//    int n=sizeof(arr)/sizeof(arr[0]);
//    maxProduct(arr,n);
// }

//or

// // optimize solution
// #include<iostream>
// using namespace std;
// void  maxProduct(int arr[],int n){
//    int ans=arr[0];
//    int max_product=arr[0];
//    int min_product=arr[0];
//    for(int i=1;i<n;i++){
//     if(arr[i]<0)
//     {
//         swap(max_product,min_product);
//     }
//     max_product=max(arr[i],max_product*arr[i]);
//     min_product=min(arr[i],min_product*arr[i]);
//     ans=max(ans,max_product)
//    }
//    cout<<ans<<endl;
// }

// int main(){
//    int arr[]={-2};
//    int n=sizeof(arr)/sizeof(arr[0]);
//    maxProduct(arr,n);
// }








// #include<iostream>
// using namespace std;


// void maxproduct(int arr[],int n){
//    int sum,max_len=0;
//    for(int i=0;i<n;i++){
//       sum=0;
//       for(int j=i;j<n;j++){
//          sum+=arr[j]; 
//          if(sum==0){
//             max_len=max(max_len,j-i+1);
//          }
//       }
//    }
//    cout<<max_len;
// }


// int main(){
//    int arr[]={15,-2,2,-8,1,7,10,23};
//    int n=sizeof(arr)/sizeof(arr[0]);
//    maxproduct(arr,n);
// }




// arrange positive and negative in sequence

// #include<iostream>
// using namespace std;



// void arrange_num(int arr[],int n){
//    int k=0,t=0,a1[50],a2[50],pos=0,neg=0;
//    for(int i=0;i<n;i++){
//       if(0<=arr[i]){
//          a1[k++]=arr[i];
//       }
//    }
//    for(int j=0;j<n;j++){
//       if(0>arr[j]){
//          a2[k++]=arr[j];
//       }
//    }
   
// }

// int main(){
//    int arr[]={9, 4, -2, -1, 5, 0, -5, -3, 2};
//    int n=sizeof(arr)/sizeof(arr[0]);
//    arrange_num(arr,n);
// }







// Rearrange array in alternating positive & negative items


// #include <bits/stdc++.h>
// using namespace std;

// void rearrange(int arr[], int n)
// {
// 	int i = 0, j = n-1;

// 	while (i < j)
// 	{
// 		while(i < n and arr[i] > 0)
// 			i += 1;
// 		while (j >= 0 and arr[j] < 0)
// 			j -= 1;
// 		if (i < j)
// 			swap(arr[i], arr[j]);
// 	}

// 	// if (i == 0 || i == n)
// 	// 	return;

	
// 	// int k = 0;
// 	// while (k < n && i < n)
// 	// {
// 	// 	swap(arr[k], arr[i]);
// 	// 	i = i + 1;
// 	// 	k = k + 2;
// 	// }
// }

// // Utility function to print an array
// void printArray(int arr[], int n)
// {
// 	for (int i = 0; i < n; i++)
// 	cout << arr[i] << " ";
// 	cout << endl;
// }

// int main()
// {
// 	int arr[] = {9, 4, -2, -1, 5, 0, -5, -3, 2};

// 	int n = sizeof(arr)/sizeof(arr[0]);

	

// 	rearrange(arr, n);
//    cout << "Given array is \n";
// 	printArray(arr, n);
// 	return 0;
// }



// #include<iostream>
// using namespace std;

// void Move_zero(int arr[],int end){
//    for(int i=0;i<=end;i++){
//       if(arr[i]==0){
//          swap(arr[i],arr[end]);
//       }
//    }
//    for(int i=0;i<=end;i++){
//       cout<<arr[i];
//    }
   
// }




// int main(){
//    int arr[]={0, 0, 0, 4};
//    int end=(sizeof(arr)/sizeof(arr[0]))-1;
//    Move_zero(arr,end);
// }




// Stock buy and sell

// #include<iostream>
// using namespace std;


// void maxProfit(int arr[],int n){
//    int mini=arr[0],profit=0;
//    for(int i=0;i<n;i++){
//       int cost=arr[i]-mini;
//       profit=max(profit,cost);
//       mini=min(mini,arr[i]);
//    }
//    cout<<profit;
// }


// int main(){
//    int arr[]={7,1,5,3,6,4};
//    int n=sizeof(arr)/sizeof(arr[0]);
//    maxProfit(arr,n);
// }




// Kth smallest element

// #include<iostream>
// #include <bits/stdc++.h>
// using namespace std;

// void smallest(int arr[],int n){
//    int k=4,max_len=0;
//    sort(arr,arr+n);
//    for(int i=0;i<k;i++){
//       max_len=max(max_len,arr[i]);
//    }
//    cout<<max_len;
// }


// int main(){
//    int arr[]={7,10,4,20,15};
//    int n=sizeof(arr)/sizeof(arr[0]);
//    smallest(arr,n);
// }




// Array Subset of another array
// #include<iostream>
// #include <bits/stdc++.h>
// using namespace std;

// bool subset(int a1[],int a2[],int n,int m){
//    set<int> s;
//    int flag;
//    for(int i=0;i<n;i++){
//       s.insert(a1[i]);
//    }
//    for(int j=0;j<m;j++){
//       if(s.find(a2[j])==s.end()){
//          return false; 
//       }
//    }
//    return true;
// }


// int main(){
//    int a1[] = {1, 2, 3,4, 5, 6};
//    int a2[] = {1,2,4};
//    int n=sizeof(a1)/sizeof(a1[0]);
//    int m=sizeof(a2)/sizeof(a2[0]);
//    if(subset(a1,a2,n,m)){
//              cout << "arr2[] is subset of arr1[] "
//              << "\n";
//    }
//     else{
//         cout << "arr2[] is not a subset of arr1[] "
//              << "\n";
//    }
// }




// #include<iostream>
// #include <bits/stdc++.h>
// using namespace std;

// void swap(int* a, int* b)
// {
//     int t = *a;
//     *a = *b;
//     *b = t;
// }


// int partition(int a1[],int low,int high){

//    int pivot = a1[high]; 
//     int i = (low- 1); 
 
//     for (int j = low; j <= high - 1; j++) {

//         if (a1[j] < pivot) {
//             i++;
//             swap(a1[i], a1[j]);
//         }
//     }
//     swap(a1[i + 1], a1[high]);
//     return(i+1);
// }


// void quicksort(int a1[],int low,int high){
//    if (low < high) {

//         int pi = partition(a1, low, high);
//         quicksort(a1, low, pi - 1);
//         quicksort(a1, pi + 1, high);
//     }
  
// }

// void print(int a1[],int size){
//     int i;
//     for (i = 0; i < size; i++){
//         cout << a1[i] << " ";
//     }
      
// }

// int main(){
//    int a1[] ={ 4, 1, 3, 9, 7};
//    int n=sizeof(a1)/sizeof(a1[0]);
//    quicksort(a1,0,n-1);
//    print(a1,n);
// }




















// Majority Element
// #include <bits/stdc++.h>
// using namespace std;


// void findMajority(int arr[], int n)
// {
// 	int maxCount = 0;
// 	int index = -1;
// 	for (int i = 0; i < n; i++) {
// 		int count = 0;
// 		for (int j = 0; j < n; j++) {
// 			if (arr[i] == arr[j])
// 				count++;
// 		}
// 		if (count > maxCount) {
// 			maxCount = count;
// 			index = i;
// 		}
// 	}
// 	if (maxCount > n / 2)
// 		cout << arr[index] << endl;

// 	else
// 		cout << "No Majority Element" << endl;
// }

// int main()
// {
// 	int arr[] = {3, 3, 4, 2, 4, 4, 2, 4};
// 	int n = sizeof(arr) / sizeof(arr[0]);
// 	findMajority(arr, n);
// 	return 0;
// }



// Count Inversions

// #include<iostream>
// using namespace std;


// void count_inver(int arr[],int n){
//     int c=0;
//     for(int i=0;i<n;i++){
//       for(int j=i+1;j<n;j++){
//          if(arr[i]>arr[j]){
//             c++;
//          }
//       }
//    }
//    cout<<c;
// }


// int main(){
//     int arr[]={8, 4, 2, 1};
//     int n= sizeof(arr) / sizeof(arr[0]);
//     count_inver(arr,n);
// }



// Minimum platform

// #include<iostream>
// #include <bits/stdc++.h>
// using namespace std;



// void minimumplatform(int arr[],int dep[],int n){
//     int i=0,j=0,count=0,ans=0;
//     sort(arr,arr+n);
//     sort(dep,dep+n);
//     while(i<n){
//         if(arr[i]<=dep[j]){
//             count++;
//             ans=max(ans,count);
//             i++;
//         }
//         else if(arr[i]>dep[j]){
//             count--;
//             j++;
//         }
//     }
//     cout<<ans;

// }

// int main(){
//     int arr[] = {900, 1100, 1235};
//     int dep[] = {1000, 1200, 1240};
//     int n=2;
//     minimumplatform(arr,dep,n);
// }




// Find Missing And Repeating

// #include<iostream>
// using namespace std;


// void missandrepeat(int arr[],int n){
//     int orign_sum=0,current_sum=0,repeat,missing;
//     for(int i=0;i<n;i++){
//         orign_sum+=i+1;
//     }
//     for(int i=0;i<n;i++){
//         current_sum+=arr[i];
//     }
//     for(int i=0;i<n;i++){
//         if(arr[i]==arr[i+1]){
//             repeat=arr[i];
//         }
//     }
//     missing=orign_sum-(current_sum-repeat);
//     cout<<"missing element="<<missing<<endl;
//     cout<<"repeat element="<<repeat;

// }


// int main(){
//     int arr[]={2, 2};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     missandrepeat(arr,n);
// }




// #include<iostream>
// #include <bits/stdc++.h>
// using namespace std;


// void missandrepeat(int arr[],int n){
//     int z,a,k;
//     for(int i=0;i<n;i++){
//         if(arr[abs(arr[i])-1]<0){
//             a=abs(arr[i]);
//         }
//         else{
//             arr[abs(arr[i])-1]=-arr[abs(arr[i])-1];
//         }
//     }
//     cout<<a<<" ";
//     for(int i=0;i<n;i++){
//         if(arr[i]>0){
//             k=i+1;
//             break;
 
//         }
//     }
//     cout<<k;
// }


// int main(){
//     int arr[]={7, 3, 4, 5, 5, 6, 2 };
//     int n=sizeof(arr)/sizeof(arr[0]);
//     missandrepeat(arr,n);
// }



// Triplet Sum in Array

// #include<iostream>
// #include <bits/stdc++.h>
// using namespace std;

// void triplesum(int arr[],int end,int x){
//    sort(arr,arr+end);
//    for(int i=0;i<end;i++){
//       int low=i+1,high=end-1;
//    while(low<high){
//       if(arr[i]+arr[low]+arr[high]==x){
//          cout<<arr[i]<<" "<<arr[low]<<" "<<arr[high];
//          break;
//       }
//       else if(arr[i]+arr[low]+arr[high]<x){
//          low++;
//       }
//       else{
//          high--;
//       }
//    }

// }

// }


// int main(){
//    int arr[]={1, 4, 45, 6, 10, 8};
//    int x=22;
//    int end=sizeof(arr)/sizeof(arr[0]);
//    triplesum(arr,end,x);
// }





// maximum of all subarrays of size k
// #include<iostream>
// using namespace std;

// void maximumsub(int arr[],int n,int k){
//     int max;
//     for(int i=0;i<=n-k;i++){
//         max=arr[i];
//         for(int j=1;j<k;j++){
//             if(arr[i+j]>max){
//                 max=arr[i+j]; 
//             }
//         }
//         cout<<max<<" ";
//     }
// }



// int main(){
//     int arr[]={1,2 ,3, 1, 4, 5, 2, 3 ,6};
//     int k=3;
//     int n=sizeof(arr)/sizeof(arr[0]);
//     maximumsub(arr,n,k);
// }






// #include <bits/stdc++.h>
// using namespace std;
 
// void printTwoElements(int arr[], int n)
// {
//     int i,z,a;
//     cout << "The repeating element is ";
//      for(int i=0;i<n;i++){
//         z=abs(arr[i]);
//         if(arr[z-1]>0){
//             arr[z-1]=-arr[z-1];

//         }
//         else{
//             cout << abs(arr[i]) << "\n";
//         }
//     }
//     cout << "and the missing element is ";
//     for (i = 0; i <n ; i++) {
//         if (arr[i] > 0)
//             cout << (i + 1);
//     }
// }

// int main()
// {
//     int arr[] = {0,-10,1,3,-20};
//     int n = sizeof(arr) / sizeof(arr[0]);
//     printTwoElements(arr, n);
// }



// Find the smallest positive number missing
// #include <iostream>
// using namespace std;


// void smallestpositive(int arr[],int n){
//     int i=0;
//     while(i<n){
//         if(arr[i]>0 && arr[i]<=n && arr[i]!=arr[arr[i]-1]){
//              int other_index=arr[i]-1;
//              swap(arr[i],arr[other_index]);
//              }
//         else{
//             i++;
//             }
//         }
//     for(int i=0;i<=n;i++){
//         if(arr[i]!=i+1){
//             cout<<i+1;
//             break;
//         }
//     }
 
    
// }

// int main(){
//     int arr[] = {2, 3, -7, 6, 8, 1, -10, 15 };
//     int n=sizeof(arr)/sizeof(arr[0]);
//     smallestpositive(arr,n);
// }



// Print a given matrix in spiral form


// #include <bits/stdc++.h>
// #include <iostream>
// using namespace std;
// #define R 4
// #define C 4


// void spiralarr(int m,int n,int arr[R][C]){
//     int i;
//     int l=0;
//     int top=0;
//     int bottom=n-1;
//     int r=m-1;
//     while(l<r && top<bottom){
//         for(i=0;i<=r;i++){
//             cout<<arr[top][i]<<" ";
//             }
//             top++;
//         for(i=top; i<=bottom; i++){
//             cout<<arr[i][r]<<" ";
//         }
//         r--;
//         if(l<=r){
//             for(i=r;i>=l;i--){
//             cout<<arr[bottom][i]<<" ";
//             }
//         }
//         bottom--;
//         if(top<bottom){
//             for(i=bottom; i>=top; i--){
//                 cout<<arr[i][l]<<" ";
//                 }
//             }
//             l++;
//     }
   

// }


// int main()
// {
//     int arr[R][C]={{ 1, 2, 3, 4 },
//                    { 5, 6, 7, 8},
//                     {9, 10, 11, 12},
//                        {13, 14, 15, 16}};
    
//     spiralarr(R,C,arr);
// }






// Maximum Index

// #include <iostream>
// using namespace std;

// void maximum_index(int arr[],int n){
//     int sub,arr_len=0;
//     for(int i=0;i<n;i++){
//         for(int j=i+1;j<n;j++){
//             if(arr[i]<=arr[j]){
//                 sub=j-i;
//                 arr_len=max(arr_len,sub);
//             }
//         }
//     }
//     cout<<arr_len;
// }


// int main(){
//     int arr[]={82, 63, 44, 74, 82, 99, 82};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     maximum_index(arr,n);

// }

// or

// #include <iostream>
// using namespace std;

// void maximum_index(int arr[],int n){
//     int sub,arr_len=0;
//     for(int i=0;i<n;i++){
//         for(int j=n;j>i;j--){
//             if(arr[i]<arr[j]){
//                 sub=j-i;
//                 arr_len=max(arr_len,sub);
//             }
//         }
//     }
//     cout<<arr_len;
// }


// int main(){
//     int arr[]={1, 10};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     maximum_index(arr,n);

// }





// #include<iostream>
// #include <bits/stdc++.h>
// using namespace std;
// int main(){
//     int arr[]={1, 23, 12, 9, 30, 2, 50};
//     int k=3;
//     int n=sizeof(arr)/sizeof(arr[0]);
//     sort(arr,arr+n);

//     for(int i=0;i<n;i++){
//         for(int j=i+1;j<n;j++){
//             if(arr[i]<<arr[j]){
//                 swap(arr[i],arr[j]);
//             } 
//         }
//     }
//     for(int i=0;i<k;i++){
//         cout<<arr[i]<<" ";
//     }



// #include<iostream>
// #include <bits/stdc++.h>
// using namespace std;
// int main(){
//     int arr[]={54, 546, 548, 60};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     for(int i=0;i<n;i++){
//         for(int j=i+1;j<n;j++){
//             if(i<j){
//                 swap(arr[i],arr[j]);
//             } 
//         }
//     }
//     for(int i=0;i<n;i++){
//         cout<<arr[i];
//     }

// }



// peak element in array
// #include<iostream>
// using namespace std;

// void peak_element(int arr[],int n){
//     int low=0;
//     int high=n-1;
//     while(low<=high){
//         int mid=(low+high)/2;
//         if( (mid==0 || arr[mid]>=arr[mid-1]) && (mid==n-1 || arr[mid]>=arr[mid+1]))
//         {
//             cout<<mid;
//             break;
//         }
//         else if(arr[mid]<=arr[mid+1])
//         {
//             low=mid+1;
//         }
//         else{
//             high=mid-1;
//         }
//     }
// }

// int main(){
//     int arr[]={1,2,3,1};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     peak_element(arr,n);

// }

array_list = [1, 3, 20, 4, 1, 0]



// void peak_element(int arr[],int n){
// #include<iostream>
// using namespace std;


//     int low=0;
//     int high=n-1;
//     while(low<=high){
//         int mid=(low+high)/2;
//         if( (mid==0 || arr[mid]>=arr[mid-1]) && (mid==n-1 || arr[mid]>=arr[mid+1]))
//         {
//             cout<<mid;
//             break;
//         }
//         else if(arr[mid]<=arr[mid+1])
//         {
//             low=mid+1;
//         }
//         else{
//             high=mid-1;
//         }
//     }
// }

// int main(){
//     int arr[]={1,2,3,1};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     peak_element(arr,n);

// }







// #include<iostream>
// using namespace std;

// void  maxProfit(int arr[],int n){
//     int mini=arr[0],profit;
//     for(int i=0;i<n;i++){
//         int cost=arr[i]-mini;
//         profit=max(profit,cost);
//         mini=min(mini,arr[i]);
//     }
//     cout<<profit;
// }


// int main(){
//     int arr[]={100, 180, 260, 310, 40, 535, 695};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     maxProfit(arr,n);
// }




// miniumum number ofjump
// #include <iostream>
// using namespace std;

// int  minimum_jump(int arr[],int n){
//    int maxR=arr[0];
//    int step=arr[0];
//    int jump=1;
//    if(n==1){
//       return 0;
//    }
//    else if(arr[0]==0){
//       return -1;
//    }
//    else{
//       for(int i=1;i<n;i++){
//          if(i==n-1){
//             cout<<jump;
//          }
//          maxR=max(maxR,i+arr[i]);
//          step--;
//          if(step==0){
//             jump++;
//             if(i>maxR){
//                return -1;
//             }
//             step=maxR-i;
//          }
//       }
//    }
// }


// int main(){
//     int arr[] = {1, 4, 3, 2, 6, 7};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     minimum_jump(arr,n);
// }




// Minimum element in a sorted and rotated array

// #include<iostream>
// using namespace std;

// void findMin(int arr[],int n){
//    int arr_len;
//    if(n==0){
//       cout<<"-1";
//    }
//    if(n==1 || arr[0]<arr[n-1]){
//       cout<<arr[0];
//    }
//    if(n==2){
//       arr_len=min(arr[0],arr[1]);
//       cout<<arr_len;
//    }
//    int low=0, high=n-1;
//    while(low<high){
//       int mid=(low+high)/2;
//       if(mid>0 && arr[mid]<arr[mid-1]){
//          cout<<arr[mid];
//       }
//       else if(arr[mid]>arr[high]){
//          low=mid+1;
//       }
//       else if(arr[mid]<arr[high]){
//          high=mid-1;
//       }

//    }
// }

// int main(){
//    int arr[] = {11,13,15,17};
//    int n=sizeof(arr)/sizeof(arr[0]);
//    findMin(arr,n);

// }




// Longest consecutive subsequence

// #include <iostream>
// #include <bits/stdc++.h>
// using namespace std;



// int longestConsecutive(int nums[],int n) {
//         unordered_set<int> s;
//         for(int i=0;i<n;i++){
//             s.insert(nums[i]);
//         }
        
//         int ans=0;
//         for(int i=0;i<n;i++){
//             if(s.find(nums[i]-1)!=s.end()){
//                 continue;
            
//             }else{
//                 int count=0;
//                 int current=nums[i];
//                 while(s.find(current)!=s.end()){
//                     count++;
//                     current++;
//                 }
                
//                 ans=max(ans,count);
//             } 
//         }
//         cout<<ans;
        
// }


// int main(){
//    int nums[] = {2,6,1,9,4,5,3};
//    int n=sizeof(nums)/sizeof(nums[0]);
//    longestConsecutive(nums,n);
// }









// int longestConsecutive(int nums[],int n) {
// 	int i,j;
// 	for(int i=0;i<n;i++){
// 		for( j=0;j<n;j++){
// 			if(i!=j && nums[i]==nums[j] ){
// 				break;
// 			}
// 		}
// 		if (j == n){
// 		cout<<nums[i];
// 		}	
// 	}	
// }


// int main(){
//    int nums[] = { 9, 4, 9, 6, 7, 4};
//    int n=sizeof(nums)/sizeof(nums[0]);
//    longestConsecutive(nums,n);
// }



// Trapping Rain Water

// #include <iostream>
// #include <bits/stdc++.h>
// using namespace std;

// void maxWater(int arr[],int n){
// 	int left[n]={};
// 	int right[n]={};


// 	left[0]=arr[0];
// 	for(int i=1;i<n;i++){
// 		left[i]=max(left[i-1],arr[i]);
// 	}

// 	right[n-1]=arr[n-1];
// 	for(int i=n-2;i>=0;i--){
// 		cout<<i<<endl;
// 		right[i]=max(right[i+1],arr[i]);
// 	}
// 	int ans=0; 
// 	for(int i=0;i<n;i++){
// 		ans+=(min(left[i], right[i]) - arr[i]);
// 	}
// 	cout<<ans;
// }

// int main(){
//    int arr[] = {3,0,0,2,0,4};
//    int n=sizeof(arr)/sizeof(arr[0]);
//    maxWater(arr,n);
// }



// Partition problem


// #include <iostream>
// #include <bits/stdc++.h>
// using namespace std;

// bool subsetSum(int arr[],int n ,int sum){
//     int i=0;
//     if(sum==0){
//         return true;
//     }
//     if(n==0 && sum!=0){
//         return false;
//     }
//     if(0>sum){
//         return false;
//     }
//     if(i>n){
//         return false;
//     }

//     else{
//         return subsetSum(arr,i+1,sum-arr[i]) ||   subsetSum(arr,i+1,sum);
//     }
// }




// bool partition(int arr[],int n){
//     int sum=0;
//     for(int i=0;i<n;i++){
//         sum+=arr[i];
//     }
//     if(sum % 2 !=0){
//         return false;
//     }
//     return subsetSum(arr,n,sum/2);
// }




// int main(){
//     int arr[] = {1, 3, 5};
//     int n=sizeof(arr)/sizeof(arr[0]);
//     if (partition(arr, n) == true)
//         cout << "Can be divided into two subsets "
//                 "of equal sum";
//     else
//         cout << "Can not be divided into two subsets"
//                 " of equal sum";
//     return 0;

// }
    


// common elements

// #include <iostream>
// #include <bits/stdc++.h>
// using namespace std;



// void longestConsecutive(int ar1[],int ar2[],int ar3[],int n1,int n2,int n3) {
//      int i = 0, j = 0, k = 0;
 
//     // Declare three variables prev1, prev2, prev3 to track
//     // previous element
//     int prev1, prev2, prev3;
 
//     // Initialize prev1, prev2, prev3 with INT_MIN
//     prev1 = prev2 = prev3 = INT_MIN;
    
//     while(i < n1 && j < n2 && k < n3){
//         while(ar1[i]==prev1 && i<n1){
//             i++;
//         }
//         while(ar2[i]==prev2 && j<n2){
//             j++;
//         }
//         while(ar3[k]==prev3 && k<n3){
//             k++;
//         }
//         if(ar1[i] == ar2[j] && ar2[j] == ar3[k]){
//             cout<<ar1[i]<<" ";
//             prev1 = ar1[i++];
//             prev2 = ar2[j++];
//             prev3 = ar3[k++];
//         }
//         else if (ar1[i] < ar2[j])
//             prev1 = ar1[i++];
 
//         // If y < z, update prev2 and increment j
//         else if (ar2[j] < ar3[k])
//             prev2 = ar2[j++];
 
//         // We reach here when x > y and z < y, i.e., z is
//         // smallest update prev3 and increment k
//         else
//             prev3 = ar3[k++];
//     }
// }


// int main(){
//     int ar1[] = {1, 5, 5};
//     int ar2[] = {3, 4, 5, 5, 10};
//     int ar3[]= {5, 5, 10, 20};
//     int n1 = sizeof(ar1) / sizeof(ar1[0]);
//     int n2 = sizeof(ar2) / sizeof(ar2[0]);
//     int n3 = sizeof(ar3) / sizeof(ar3[0]);
//     longestConsecutive(ar1,ar2,ar3,n1,n2,n3);
// }




//////////////////////////////////////////////////////STRING QUESTIONS///////////////////////////////////////////////////////////////////


// Implement strstr


// #include <iostream>
// #include <bits/stdc++.h>
// #include<cstring>
// using namespace std;

// void strstr(string s1,string x)
// {
//     int lenS1= s1.length();
//     int lenS2=x.length();
//     int flag;
//     int i;

//     for(i=0;i<lenS1;i++){
//         if(s1[i]==x[0])
//         {
//             flag=0;
//             for(int j=0;j<lenS2;j++){
//                 if(s1[i+j]!=x[j]){
//                     flag=1;
//                     break;
//                 }
//             }
//             if(flag==0){
//                 cout<<"true";
//                 return;
//             }
//         }
//     }
//     cout<<"false";
// }

// int main(){
//     string s1="dzfzh";
//     string x="rbbvrwex";
//     strstr(s1,x);
// }



// Anagram Palindrome

// #include <iostream>
// #include <bits/stdc++.h>
// #include<cstring>
// using namespace std;

// int strstr(string s1)
// {
//     set<char> s;
//     int lenS=s1.length();
//     for(int i=0;i<lenS;i++){
//         if(s.count(s1[i])){
//             s.erase(s1[i]);
//         }
//         else{
//             s.insert(s1[i]);
//         }
//     }
//     if(s.size()==1){
//         cout<<"true";
//     }
//     else{
//         cout<<"false";
//     }
   
// }


// int main(){
//     string s1="geeksforgeeks";
//     strstr(s1);
// }




// Check for subsequence


// #include <iostream>
// #include <bits/stdc++.h>
// #include<cstring>
// using namespace std;

// void Subsequence(string A,string B){
//     int m=A.length();
//     int n=B.length();
//     int j=0;

//     for(int i=0;i<n;i++){
//         if(B[i]==A[j]){
//             j++;
//         }
//     }
//     if(j==m){
//         cout<<"true";
//     }
//     else{
//         cout<<"false";
//     }

// }


// int main(){
//     string A="gksrek";
//     string B="geeksforgeeks";
//     Subsequence(A,B);
// }




// Integer to Roman


// #include<iostream>
// using namespace std;

// void Roman(int num){
//     string s1[]={"M","CM","D","C","XC","L","X","V","IV","III","I"};
//     string s2;
//     int pos[]={1000,900,500,100,90,50,10,5,4,3,1};
//     for(int i=0; num>0; i++){
//         while(num>=pos[i]){
//             s2=s2+s1[i];
//             num=num-pos[i];
//         }
//     }
//     cout<<s2;
// }


// int main(){
//     int num =58;
//     Roman(num);
// }



// Reverse words in a given string

// #include <iostream>
// #include <bits/stdc++.h>
// #include<cstring>
// using namespace std;

// void reverse_string(string s1)
// {
//     int i=s1.length()-1;
//     string s2="";
//     while(i>=0){
//         while(i>=0 && s1[i]==' '){
//             i--;
//         }
//         int j=i;
//         if (i<0){
//             break;
//         }

//         while(i>=0 && s1[i]!=' '){
//             i--;
//         }
//         s2=s2+(s1.substr(i+1,j-i+1) + " ");
//     }
//     cout<<s2;
// }



// int main(){
//     string s1="hello world";
//     reverse_string(s1);
// }

// When i=23 and j=27 the index value of (i+1, j-i+1).....j-i+1=j-(i+1)+1 in the s1.substr(i+1,j-i+1) function call would be 24 to 5 (i.e. s1[24] to s1[28]).









// #include<iostream>
// #include <bits/stdc++.h>
// #include<unordered_map>
// using namespace std;


// bool isAnagram(string s1, string s2){
//     unordered_map<char,int> Map;

//     int t=s1.length();
//     int u=s2.length();

//     if(t!=u){
//         return false;
//     }

//     for(int i=0;i<t;i++){
//         Map[s1[i]]++;
//     }
//     for(int j=0;j<u;j++){
//         if(Map.find(s2[j])==Map.end()){
//         return false;
//         }
//         Map[s2[j]]--;
//     }
//     return true;
    
// }


// int main(){
//     string s1="allergy";
//     string s2="allergic";
//     if (isAnagram(s1,s2)){
//         cout << "The two strings are anagram of each other"<< "\n";
//    }
//    else{
//         cout << "The two strings are not anagram of each "
//                 "other"
//              << "\n";
//    }
// }








// string is palindrome
// #include<iostream>
// #include <bits/stdc++.h>
// using namespace std;

// bool palindrome(string s1){
//     int j=s1.length();
//     for(int i=0;i<s1.length()/2;i++){
//         if(s1[i]!=s1[j-i-1]){
//             return "No";
//         }
//     }
//     return "Yes";
// }



// int main(){
//     string s1="hq";
//     cout<<palindrome(s1);
// }




// Find first non-repeating character of given String
// #include <iostream>
// #include <unordered_map>
// using namespace std;


// char firstNonRepeating(string str) {

//     unordered_map<char, int> count;

//     for (int i=0;i<str.length();i++)
//         count[str[i]]++;

//     for (int i=0;i<str.length();i++)
//         if (count[str[i]] == 1)
//         {
//             return str[i];
//         }
//         return '_';
// }

// int main() {
//     string str = "zxvczbtxyzvy";
//     std::cout << "First non-repeating character: " << firstNonRepeating(str) << std::endl;
//     return 0;
// }






// Check if two strings are k-anagrams or not
// #include <iostream>
// #include <string>
// #include <unordered_map>

// using namespace std;



bool areKAnagrams(string str1, string str2, int k) {
    int n = str1.length();
    int m = str2.length();
    if (n != m) {
        return false;
    }
    
    unordered_map<char, int> freqMap;
    for (int c = 0; c < n; c++) {
        freqMap[str1[c]]++;
    }
    
    int count = 0;
    for (int i = 0; i < m; i++) {
        if (freqMap[str2[i]] > 0) {
            freqMap[str2[i]]--;
        } else {
            count++;
        }
    }

    return (count <= k);
}

int main() {
    string str1 = "geeks";
    string str2 = "eggkf";
    int k = 1;
    if (areKAnagrams(str1, str2, k)) {
        cout << "The strings are k-anagrams." << endl;
    } else {
        cout << "The strings are not k-anagrams." << endl;
    }
    return 0;
}




// Parenthesis Checker
// #include<iostream>
// #include <bits/stdc++.h>
// #include<cstring>
// using namespace std;

// bool ispar(string x){
//     stack<char> temp;
//     for(int i=0;i<x.length();i++){
//         if(temp.empty()){
//             temp.push(x[i]);
//             }
//         else if(('('==temp.top() && x[i]==')') || ('{'==temp.top() && x[i]=='}') || 
//         ('['==temp.top() && x[i]==']') )
//         {
//             temp.pop();
//         }
//         else{
//             temp.push(x[i]);
//         }
//     }
//     if(temp.empty()){
//         return true;
//     }
//     return false;
// }



// int main(){
//     string x="[(])";
//     if(ispar(x)){
//         cout<<"true";
//     }
//     else{
//         cout<<"false";
//     }
// }




// string reverse
// #include<iostream>
// #include <bits/stdc++.h>
// #include<cstring>
// #include<unordered_map>
// using namespace std;

// void ispar(string x){
//     unordered_set<char> s;
//     for(int i=0;i<x.length();i++){
//         if(s.find(x[i])==s.end()){
//             s.insert(x[i]);
//             cout<<x[i];
//         }
//     }
// }


// int main(){
//     string x="cbacdcbc";
//     ispar(x);
// }




// Look and Say Pattern
// #include<iostream>
// #include<cstring>
// using namespace std;

// string pattern(int n){
//     if(n==1){
//         return "1";
//     } 
//     string s=pattern(n-1);
//     int count=0;
//     string res="";
//     for(int i=0;i<s.length();i++){
//         count++;
//         if(i==s.length()-1 || s[i]!=s[i+1]){
//             res=res+to_string(count)+s[i];
//             count=0;
//         }
//     }
//     return res;
// }

// int main(){
//     int n=4;
//     cout<<pattern(n);
// }








// Match specific pattern

// #include<iostream>
// #include<unordered_map>
// #include <bits/stdc++.h>
// #include<cstring>
// using namespace std;

// string encode_string(string str){
//     unordered_map<char,int> map;
//     int i=0;
//     string res="";
//     for(int j=0;j<str.length();j++){
//         char ch=str[j];
//         if(map.find(ch)==map.end()){
//             map[ch]=i++;
//         }
//         res=res+to_string(map[ch]);
//     }
//     return res;
// }



// void match_string(unordered_set<string> dict , string pattern){
//     int  len=pattern.length();
//     string hash=encode_string(pattern);
//     for(string word:dict){
//         if(word.length()==len && encode_string(word)==hash){
//             cout<<word<<" ";
//         }
//     }
// }


// int main(){
//     unordered_set<string> dict = {"abb","abc","xyz","xyy"};
//     string pattern="foo";
//     match_string(dict,pattern);
// }







// String Permutations

// #include<iostream>
// #include <bits/stdc++.h>
// #include<cstring>
// using namespace std;



// void permute(string s,int l,int r){
//     if(l==r){
//         cout<<s<<" ";
//     }
//     else{
//         for(int i=l;i<r;i++){
//             swap(s[l],s[i]);
//             permute(s,l+1,r);
//             swap(s[l],s[i]);
//         }
//     }
// }


// int main(){
//     string s="ABSG";
//     int n=s.length();
//     permute(s,0,n);
// }




// Find next greater number with same set of digits


// #include<iostream>
// #include <bits/stdc++.h>
// #include<cstring>
// using namespace std;

// void next_element(char dig[],int n){
//     int i,j;
//     for( i=n-1;i>0;i--){
//         if(dig[i]>dig[i-1]){
//             break;
//         }
//     }

//     if(i==0){
//         cout<<"not possible";
//     }
//     int x=dig[i-1];
//     int smallest=i;
//     for(int j=i+1 ;j<n;j++){
//         if(dig[j]>x && dig[j]<dig[smallest])
//         smallest=j;
//     } 
//     swap(dig[i-1],dig[smallest]);
//     sort(dig+i,dig+n);
//     cout<<dig;
// }



// int main(){
//     char dig[]="534976";
//     int n=strlen(dig);
//     next_element(dig,n);
// }





// rotation of string

// #include<iostream>
// #include <bits/stdc++.h>
// #include <string>
// using namespace std;


// bool rotate(string s1 , string s2){
//     return (s1.length()==s2.length() && (s1+s1).find(s2)!=string::npos);

// }


// int main(){
//     string s1 ="abcde";
//     string s2  = "cdeab";
//     if(rotate(s1,s2)){
//         cout<<"true";
//     }
//     else{
//         cout<<"false";
//     }
// }



// Check if string is rotated by two places

// #include <iostream>
// #include <bits/stdc++.h>
// #include<cstring>
// using namespace std;


// void rotate(string s1 , string s2){
//     string a,b,c;
     
//     a=s2.substr(s2.length()-2,s2.length());
//     b=s2.substr(0,s2.length()-2);
//     c=a+b;
//     if(c==s1){
//         cout << "true\n";
 
//     }
//     a=s1.substr(2,s1.length());
//     b=s1.substr(0,2);
//     c=a+b;
//     if(c==s2){
//         cout << "true\n";

//     }
//     else{
//         cout<<"false\n";
//     }

// }


// int main(){
//     string s1 ="amazon";
//     string s2  = "azonam";
//     rotate(s1,s2);
   
// }





//longest palindrome string or substring


// #include <iostream>
// #include <bits/stdc++.h>
// #include<cstring>
// using namespace std;


// string longestPalin(string s1) {
//     int maxlen = 1;
//     int start=0;
//     int l;
//     int r;
//     int len;
//     int n=s1.length();


//     for (int i = 0; i < n-1; i++) {
//         //odd

//         if(s1.length()<=1){
//             return s1;
//         }


//         l=i;
//         r=i;

     
//         while (l >= 0 && r < n ) {
//             if (s1[l]==s1[r]) {
//                 l--;
//                 r++;
//             }
//             else{
//                 break;
//             }
//         }

//         len=r-l-1;
    
//         if(len>maxlen){
//             maxlen=len;
//             start=l+1;
//         }

//         l = i;
//         r = i+1;

//         //even
//         while (l >= 0 && r < n ) {
//             if (s1[l]==s1[r]) {
//                 l--;
//                 r++;
//             }
//             else{
//                 break;
//             }
//         }

//         len=r-l-1;

//         if(len>maxlen){
//             maxlen=len;
//             start=l+1;
//         }
//     }
//     return s1.substr(start,maxlen);
// }

// int main() {
//     string s1 = "abc";
//     string longest = longestPalin(s1);
//     cout << longest << endl;
//     return 0;
// }










// #include <iostream>
// #include <bits/stdc++.h>
// #include<cstring>
// using namespace std;


// void longestCommomSubstr(string s1  , string s2)
// {
//     int n=s1.length();
//     int m=s2.length();
//     int i=0;
//     int j=0;
//     int count=0;
//     int t=0;

//     while(i<n){
//         if(s1[i]==s2[j]){
//             i++;
//             j++;
//             count++;
//             t=max(t,count);
//         }
//         else{
//             j++;
//         }
//     }
//     cout<<t;

// }


// int main(){
//     string s1="ABCDGH";
//     string s2="ACDGHR";
//     longestCommomSubstr(s1,s2);
// }



// find_longest_common_substring
// #include <iostream>
// #include <cstring>
// using namespace std;

// int find_longest_common_substring(string s1, string s2, int n, int m) {

//     int table[n+1][m+1];
//     for (int i = 0; i <= n; i++) {
//         for (int j = 0; j <= m; j++) {
//             table[i][j] = 0;
            
//         }
//     }

//     int max_len = 0;
//     for (int i = 1; i <= n; i++) {
//         for (int j = 1; j <= m; j++) {
//             if (s1[i-1] == s2[j-1]) {
//                 table[i][j] = table[i-1][j-1] + 1;
//                 max_len=max(max_len,table[i][j]);
//             } else {
//                 table[i][j] = 0;
//             }
//         }
//     }
    
//     return max_len;
// }

// int main() {
//     string s1 = "ABCDGH";
//     string s2 = "ACDGHR";
//     int n = 6;
//     int m = 6;
//     cout << find_longest_common_substring(s1, s2, n, m) << endl; 
//     return 0;
// }




// find_longest_common_subsequence
// #include <iostream>
// #include <cstring>
// using namespace std;

// int find_longest_common_substring(string s1, string s2, int n, int m) {
//     int i;
//     int j;
//     int table[n+1][m+1];
//     for (int i = 0; i <= n; i++) {
//         for (int j = 0; j <= m; j++) {
//             table[i][j] = 0;
            
//         }
//     }

//     int max_len = 0;
//     for (int i = 1; i <= n; i++) {
//         for (int j = 1; j <= m; j++) {
//             if (s1[i-1] == s2[j-1]) {
//                 table[i][j] = table[i-1][j-1] + 1;
                
//             } else {
//                 table[i][j]=max(table[i-1][j],table[i][j-1]);
//             }
//         }
//     }
    
//     return table[n][m];
// }

// int main() {
//     string s1 = "ABCDGH";
//     string s2 = "ACDGHR";
//     int n = s1.length();
//     int m = s2.length();
//     cout << find_longest_common_substring(s1, s2, n, m) << endl; 
//     return 0;
// }





// String to Integer

// #include <iostream>
// #include <cstring>
// using namespace std;

// int myAtoi(string s1) {
//     int sign=+1;
//     long ans=0;
//     int i=0;
//     int MIN=INT_MIN;
//     int MAX=INT_MAX;


//     while(i<s1.length() && s1[i]==' '){
//         i++;
//     }


//     if(s1[i]=='-'){
//         sign=-1;
//         i++;
//     }

//     else if(s1[i]=='+'){
//         i++;
//     }
    
    
//     s1=s1.substr(i);

//     for(int i=0;i<s1.length();i++){
//         if(!isdigit(s1[i])){
//             break;
//         }


//         ans = ans * 10 + (s1[i] - '0');

//         if(sign==-1 &&  -1*ans<MIN){
//             return MIN;
//         }

//         if(sign==1 &&  ans>MAX){
//             return MAX;
//         }

//     }
    
//     return int(sign*ans);
// }


// int main() {
//     string s1="   -42";
//     cout<<myAtoi(s1);
// }




// FORM a palindrome

// #include <iostream>
// #include <cstring>
// #include <algorithm>
// using namespace std;

// int minInsertions(string s) {


//     string s1=s;
//     string s2=s;

//     int n=s1.length();
//     int m=s2.length();

//     int i;
//     int j;

//     reverse(s2.begin(),s2.end());

//     int table[n+1][m+1];
//     for (int i = 0; i <= n; i++) {
//         for (int j = 0; j <= m; j++) {
//             table[i][j] = 0;
            
//         }
//     }

//     int max_len = 0;
//     for (int i = 1; i <= n; i++) {
//         for (int j = 1; j <= m; j++) {
//             if (s1[i-1] == s2[j-1]) {
//                 table[i][j] = table[i-1][j-1] + 1;
                
//             } else {
//                 table[i][j]=max(table[i-1][j],table[i][j-1]);
//             }
//         }
//     }
    
//     int lcs =table[n][m];
//     return n-lcs;
// }

// int main() {
//     string s = "abcd";
//     cout << minInsertions(s) << endl; 
//     return 0;
// }



// prefix and sufeix
// #include <iostream>
// #include <cstring>
// #include <algorithm>
// using namespace std;

// int lps(string s){
//     int n=s.length();
//     int lps[n];
//     lps[0]=0;
//     int i=1;
//     int len=0;

//     while(i<n){
//         if(s[i]==s[len]){
//             len++;
//             lps[i]=len;
//             i++;
//         }
//         else if(len!=0){
//             len=lps[len-1];
//         }
//         else{
//             lps[i]=0;
//             i++;
//         }
//     }
//     return lps[n-1];
// }



// int main(){
//     string s = "aabaacaabaad";
//     cout<<lps(s);
// }




// Print Anagrams Together
// #include <iostream>
// #include<vector>
// #include <cstring>
// #include<unordered_map>
// #include <algorithm>
// using namespace std;

// vector<vector<string>> groupAnagrams(vector<string> word ){
//     string temp;
//     vector<vector<string>> ans;
//     unordered_map<string ,vector<string>> map;
//     for(int i=0;i<word.size();i++){
//         temp=word[i];
//         sort(temp.begin(),temp.end());
//         map[temp].push_back(word[i]);
       
//     }
//     for(auto itr=map.begin(); itr!=map.end();itr++){
//         ans.push_back(itr->second);
//     }
//     return ans;

// }

// int main(){
//     vector<string> word = {"act","god","cat","dog","tac"};
//     vector<vector<string>> anagrams = groupAnagrams(word);
//     for (const auto& anagram_group : anagrams) {
//         for (const auto& word : anagram_group) {
//             cout << word << " ";
//         }
//         cout << endl;
//     }
//     return 0;
// }








// #include <iostream>
// #include<vector>
// #include <cstring>
// #include<unordered_map>
// #include <algorithm>
// using namespace std;

// bool isInterleave(string s1,string s2,string s3,int i,int j,int k,vector<vector<int>> m){
//      if (m[i][j]=-1) {
//         return m[i][j];
//     }

//     if(i==s1.length() && j==s2.length() && k==s3.length()){
//         return true;
//     }

//     bool x=false, y =false;
//     if(i!=s1.length()){
//         if(s1[i]==s3[k]){
//             x=isInterleave(s1,s2,s3,i+1,j,k+1,m);
//         }
//     }
//     if(j!=s2.length()){
//         if(s2[j]==s3[k]){
//             y=isInterleave(s1,s2,s3,i,j+1,k+1,m);
//         }
//     }
//     return m[i][j]=x||y;
// }

// int main(){
//     string s1 = "XY"; 
//     string s2 = "X";
//     string s3 = "XXY";
//     int a=s1.length();
//     int b=s2.length();
//     vector<vector<int>> m(a+1,vector<int>(b+1,-1));
//     int i,j,k;
//     cout<< isInterleave(s1,s2,s3,0,0,0,m);
// }



// or 

// #include <iostream>
// #include <cstring>
// using namespace std;

// bool isInterleave(string s1, string s2, string s3, int i, int j, int k) {
//     if (i == s1.length() && j == s2.length() && k == s3.length()) {
//         return true;
//     }

//     bool x = false, y = false;
//     if (i != s1.length() && s1[i] == s3[k]) {
//         x = isInterleave(s1, s2, s3, i + 1, j, k + 1);
//     }

//     if (j != s2.length() && s2[j] == s3[k]) {
//         y = isInterleave(s1, s2, s3, i, j + 1, k + 1);
//     }

//     return x || y;
// }

// int main() {
//     string s1 = "aabcc";
//     string s2 = "dbbca";
//     string s3 = "aadbbbaccc";

//     if (isInterleave(s1, s2, s3, 0, 0, 0)) {
//         cout << "Yes, " << s3 << " can be formed by interleaving " << s1 << " and " << s2 << endl;
//     } else {
//         cout << "No, " << s3 << " cannot be formed by interleaving " << s1 << " and " << s2 << endl;
//     }

//     return 0;
// }







// Add Binary Strings



// #include <iostream>
// #include <cstring>
// #include <bits/stdc++.h>
// using namespace std;

// string  addBinary(string s1, string s2){
//     int i=0;
//     int carry=0;
//     string ans="";
//     while(i<s1.length()  ||  i<s2.length() || carry!=0){
//         int x=0;
      
//         if(i<s1.length()  && s1[s1.length()-i-1]=='1'){
//             x=1;
//         }
//         int y=0;
//         if(i<s2.length() && s2[s2.length()-i-1]=='1'){
//             y=1;
//         }

//         ans=to_string((x+y+carry)%2)+ans;
//         carry=(x+y+carry)/2;
//         i++;
//     }
//     return ans;
// }


// int main(){
//     string s1 = "1101";
//     string s2 = "111";
//     cout<<addBinary(s1,s2);
// }



//////////////////////////////////////////////////////////////////




// #include <iostream>
// #include <cstring>
// #include <bits/stdc++.h>
// using namespace std;

// string multiply(string s1,string s2){
//     int j=s1.length()-1;
//     int i=s2.length()-1;
//     int *result=new int [i+j];
//     int pf=0;

//     if(s1=="0" || s2=="0"){
//         return 0;
//     }

//     memset(result, 0, sizeof(int)*(i+j+1));
//     while(i>=0){
//         int ival=s2[i]-'0';
//         int k=i+j-pf;
//         i--;
//         int jval=s1[j]-'0';
//         int  carry=0;
//         while(j>=0 || carry!=0){
//             j--;
//             int product=  ival*jval+carry+result[k];
//             result[k]=product%10;
//             carry=product/10;
//             k--;
//         }
//         pf++;
//     }
//     //remove leading zero
//     string s3="";
//     bool flag=false;
//     for(int val=0; val<=i+j+1;val++){
//         if(val==0 && flag==false){
//             continue;
//         }
//         else{
//             flag=true;
//             s3+=to_string(result[val]);
//         }
//     }
//     return s3;

// }



// int main(){
//     string s1="123";
//     string s2="456";
//     cout<< multiply(s1,s2);
// }
















// #include <iostream>
// #include <cstring>
// #include <bits/stdc++.h>
// using namespace std;

// string multiply(string s1, string s2){
//     int j=s1.length();
//     int i=s2.length();
//     int *result=new int [i+j];
//     int pf=0;

//     if(s1=="0" || s2=="0"){
//         return 0;
//     }

//     while(i>=0){
//         int ival=s2[i]-'0';
//         i--;
//         int k=i+j-pf;
//         int jval=s1[j]-'0';
//         int  carry=0;
//         while(j>=0 || carry!=0){
//             int jval=j>=0 ? s2[j]-'0':0;
//             j--;
//             int product=  ival*jval+carry+result[k];
//             result[k]=product%10;
//             carry=product/10;
//             k--;
//         }
//         pf++;
//     }

//     //remove leading zero
//     string str="";
//     bool flag=false;
//     for(int val: result){
//         if(val==0 && flag==false){
//             continue;
//         }
//         else{
//             flag=true;
//             str+=to_string(val);
//         }
//     }

//     return str;
// }

// int main(){
//     string s1="123";
//     string s2="456";
//     cout<< multiply(s1,s2) << endl;
//     return 0;
// }









// #include <iostream>
// #include <cstring>
// #include <bits/stdc++.h>
// using namespace std;

// string multiply(string s1,string s2){
//     int j=s1.length()-1;
//     int i=s2.length()-1;
//     int *result=new int [i+j+1];
//     int pf=0;

//     if(s1=="0" || s2=="0"){
//         return "0";
//     }

//     memset(result, 0, sizeof(int)*(i+j+1));

//     while(i>=0){
//         int ival=s2[i]-'0';
//         int k=i+j-pf;
//         i--;
//         int jval=s1[j]-'0';
//         int  carry=0;
//         while(j>=-1 || carry!=0){
//             int jval=j>=0 ? s1[j]-'0':0;
//             j--;
//             int product=  ival*jval+carry+result[k];
//             result[k]=product%10;
//             carry=product/10;
//             k--;
//         }
//         pf++;
//         j=s1.length()-1;
//     }

//     //remove leading zero
//     string s3="";
//     bool flag=false;
//     for(int val=0; val<i+j+1;val++){
//         if(result[val]!=0 || flag==true){
//             flag=true;
//             s3+=to_string(result[val]);
//         }
//     }

//     delete[] result;

//     return s3;
// }

// int main(){
//     string s1="123";
//     string s2="456";
//     cout<< multiply(s1,s2);
//     return 0;
// }











// Largest number in K swaps

// #include <cstring>
// #include <bits/stdc++.h>
// using namespace std;

// void findMax(string str,int k,string& ans,int index)
// {



// 	if (k == 0) {
//         return;
//     }

	
// 	char maxm=str[index];
// 	for(int i=index+1;i<str.length();i++){
// 		if(maxm<str[i]){
// 			maxm=str[i];
// 		}
// 	}

// 	if(maxm!=str[index]){
// 		k--;
// 	}

// 	for(int j=str.length()-1;j>=index;j--){
// 		cout<<str[j]<<" "<<maxm<<endl;
// 		if(str[j]==maxm){
// 			swap(str[index],str[j]);
		
// 		if(str.compare(ans) > 0){
// 			ans=str;
// 		}
// 		findMax(str,k,ans,index+1);
// 		swap(str[index],str[j]);
// 		}
// 	}
// }


// int main(){
// 	string str="68543";
// 	int k=1;
// 	string ans=str;
// 	findMax(str,k,ans,0);
// 	cout<<ans;
// 	return 0;

// }




// Reverse each word in a given string

// #include <cstring>
// #include <bits/stdc++.h>
// using namespace std;


// string reverseWords(string s) {

// 	int l=0 ,r=0;
// 	while(l<s.length()){
// 		while(s[r]!=' '  &&  r<s.length()){
// 			r++;
// 		}
// 		reverse(s.begin()+l , s.begin()+r);
// 		l=r+1;
// 		r=l;
// 	}
// 	return s;

// }


// int main(){
// 	string s = "i like this program very much";
// 	cout<< reverseWords(s);
// }



// Column name from a given column number

// #include <cstring>
// #include <bits/stdc++.h>
// using namespace std;


// int reverseWords(string s) {
// 	int result=0;
//     for(int i=0;i<s.size();i++){
//         int d=s[i]-'A'+1;
// 		//"d" they will get numeric values
//         result=result*26+d;
//     }
//     return result;
// }


// int main(){
// 	string s = "ZY";
// 	cout<< reverseWords(s);
// }






// Anagram
// #include<iostream>
// #include<unordered_map>
// using namespace std;


// bool isAnagram(string s1, string s2){
//     unordered_map<char,int> map;
//     for(int i=0;i<s1.length();i++){
//         map[s1[i]]++;
//     }
    
//     for(int j=0;j<s2.length();j++){
//         if(map.find(s2[j])==map.end()){
//             return false;
//         }
//         map[s2[j]]--;
//         if(map[s2[j]]==0){
//             map.erase(s2[j]);
//         }
//     }
//     return map.empty();

// }


// int main(){
//     string s1 = "anagram";
//     string s2 = "nagaram";
//     bool result=isAnagram(s1,s2);
//     if (result) {
//         cout << s1 << " and " << s2 << " are anagrams." << endl;
//     } else {
//         cout << s1 << " and " << s2 << " are not anagrams." << endl;
//     }
    
// }







// remove all duplicate from string


// #include<iostream>
// #include <unordered_set>
// using namespace std;

// string removeDuplicates(string str) {
//     unordered_set<char> s;
//     string result = "";
//     for (int i = 0; i < str.length(); i++) {
//         if (s.find(str[i]) == s.end()) {
//             s.insert(str[i]);
//             result += str[i];
//         }
//     }
//     return result;
// }


// int main(){
//     string str="geeksforgeeks";
//     cout<<removeDuplicates(str);
// }




// length of encoding
// #include<iostream>
// using namespace std;
// string runLengthEncode(std::string s1){
  
//     string res="";
  
//     for(int i=0;i<s1.length();i++){
//         int count=1;
//         while(i<s1.length()-1 && s1[i]==s1[i+1]){
//             count++;
//             i++;
//         }
//         res+=to_string(count)+s1[i];
//     }
//     return res;
// }


// int main() {
//     std::string s1 = "AAAABBBCCCCDDDDEEEEEE";
//     std::string encodedStr = runLengthEncode(s1);
//     std::cout << "Original string: " << s1<< std::endl;
//     std::cout << "Encoded string: " << encodedStr << std::endl;
//     return 0;
// }





// #include <iostream>
// using namespace std;
// #include <string>

// void runLengthEncode(string str) {
//     int n=str.length();
//     int i;
//     for(int i=n-1;i>0;i--){
//         if(str[i]>str[i-1]){
//             break;
//         }
//     }
//     if(i==0){
//         cout<<"not possible";
//     }
//     int x=str[i-1];
//     int smallest=i;
//     for(int j=i+1;j<n;j++){
//         if(str[j]>x && str[j]<str[smallest]){
//             smallest=j;
//         }
//     }
//     swap(str[i-1],str[smallest]);
//     sort(str+i,str+n);
//     cout<<str;

// }

// int main() {
//     string str = "218765";
//     runLengthEncode(str);
// }







// #include <iostream>
// using namespace std;
// #include <bits/stdc++.h>
// #include<cstring>


// void runLengthEncode(char str[],int n) {
//     int i;
//     for(i=n-1; i > 0; i--){
//         if(str[i] > str[i-1]){
//             break;
//         }
//     }
//     if(i == 0){
//         cout << "not possible";
//         return;
//     }
//     int x = str[i-1];
//     int smallest = i;
//     for(int j = i+1; j < n; j++){
//         if(str[j] > x && str[j] < str[smallest]){
//             smallest = j;
//         }
//     }
//     swap(str[i-1], str[smallest]);
//     sort(str+i, str+n);
//     cout << str;

// }

// int main() {
//     char str[] = "218765";
//     int n=strlen(str);
//     runLengthEncode(str,n);
// }





// #include <iostream>
// using namespace std;
// #include<vector>
// #include <bits/stdc++.h>
// #include<cstring>



// bool longestCommonSubstr(string s1,string s2, string s3,int i,int j ,int k,vector<vector<int>> &dp){
//     if (dp[i][j]!=-1) {
//         return dp[i][j];
//     }

//     if(i==s1.length() && j==s2.length() && k==s3.length()){
//         return true;
//     }
//     bool x=false, y=false;
//         if(i!=s1.length()  && s1[i]==s3[k]){
//         x=longestCommonSubstr(s1,s2,s3,i+1,j,k+1,dp);
//     }
//     if(j!=s2.length() && s2[j]==s3[k]){
//         y=longestCommonSubstr(s1,s2,s3,i,j+1,k+1,dp);
//     }
//     return dp[i][j]=x||y;
// }


// int main(){
//     string s1="YX";
//     string s2="X";
//     string s3="XXY";
//     int m=s1.length();
//     int n=s2.length();
//     vector<vector<int>> dp(m+1,vector<int> (n+1,-1));
//     cout<<longestCommonSubstr(s1,s2,s3,0,0,0,dp);
// }






// #include<iostream>
// using namespace std;


// struct Node{
//     int data;
//     Node *next;
// };

// Node *head=NULL;
// Node *head2=NULL;


// void insert(int d)

// {
//     Node *first = new Node;
//     first->data=d;
//     first->next=NULL;
//     if(head==NULL){
//         head=first;
//     }
//     else{
//          Node *last=head;
//          while(last->next!=NULL){
//         last=last->next;
//         }
//         last->next=first;
//         }
   
// };



// void insert1(int u)

// {
//     Node *second = new Node;
//     second->data=u;
//     second->next=NULL;
//     if(head2==NULL){
//         head2=second;
//     }
//     else{
//          Node *last1=head2;
//          while(last1->next!=NULL){
//         last1=last1->next;
//         }
//         last1->next=second;
//         }
   
// };




// void reverse(){
//     Node *temp=NULL;
//     Node *temp2=NULL;
//     while(head!=NULL){
//         temp2=head->next;
//         head->next=temp;
//         temp=head;
//         head=temp2;
//     }
//     head=temp;
// }



// void search (int d){
//     Node *temp=head;
//     bool found=false;
//     while(temp!=NULL){
//         if(temp->data==d){
//             found=true;
           
//     }
//     temp=temp->next;
//     }
//     if(found==true){
//         cout<<"found";
//         cout<<endl;
//     }
//     else{
//         cout<<"not found";
//         cout<<endl;
//     }

// }



// void middel(){
//         Node *fast=head;
//         Node*slow=head;
//         while(fast!=NULL && fast->next!=NULL){
//             fast=fast->next->next;
//             slow=slow->next;
//         }
//         cout<<slow->data;
//         cout<<endl;
//     };

// void print(){
//     Node *temp=head;
//     while(temp!=NULL){
//         cout<<temp->data;
//         temp=temp->next;
//     }
//     cout<<endl;
// };

// void display(){
//     Node *temp1=head2;
//     while(temp1!=NULL){
//         cout<<temp1->data;
//         temp1=temp1->next;
//     }
//     cout<<endl;
// };


// Node *merge(Node *head, Node *head2){
//     Node *p1=head;
//     Node *p2=head2;
//     Node *dummy=new Node;
//     Node *p3=dummy;
//     dummy->next = NULL;
//     while(p1!=NULL && p2!=NULL){
//         if(p1->data<p2->data){
//             p3->next=p1;
//             p1=p1->next;
//         }
//          else{
//             p3->next=p2;
//             p2=p2->next;
//         }
//         p3=p3->next;
//     }
//     if (p1 != NULL) {
//         p3->next = p1;
//     }
//     if (p2 != NULL) {
//         p3->next = p2;
//     }
//     return dummy->next;
// }


// void print1(Node* head) {
//     Node* temp = head;
//     while (temp != NULL) {
//         cout << temp->data << " ";
//         temp = temp->next;
//     }
//     cout << endl;
// }

// void getNthFromLast()
// {
//     Node *first=head;
//     Node *second=head;
//     int n=5;

//     for(int i=1;i<n;i++){
//         second=second->next;
//         if(second==NULL){
//             cout<<"not found";
//             }
//             }
//         while(second!=NULL && second->next!=NULL){
//             first=first->next;
//             second=second->next;
//         }
//         cout<<first->data;

// }


// void detectloop()
// {
//     Node *fast=head;
//     Node *slow=head;
   
//         while(fast!=NULL && fast->next!=NULL){
//             slow=slow->next;
//             fast=fast->next->next;
//             if(slow==fast){
//                 cout<<slow->data;

//             }
//         }
        

// }

// void remove()
// {
//     Node *first=head;
//     Node *second=head;
//     int n=5;

//     for(int i=1;i<n;i++){
//         second=second->next;
//         if(second==NULL){
//             cout<<"not found";
//             }
//             }
//         while(second!=NULL && second->next!=NULL){
//             first=first->next;
//             second=second->next;
//         }
//         cout<<first->data;

// }



// int main(){
//     insert(5);
//     insert(10);
//     insert(15);
//     insert(40);
//     insert1(2);
//     insert1(3);
//     insert1(20);
//     Node* res = merge(head, head2);
//     print1(res);

//     print();
//     display();
//     reverse();
//     insert(5);
//     insert(6);
//     insert(7);
//     insert(8);
//     insert(9);
//     getNthFromLast();

//     search(3);
//     middel();
//     print();

// }












