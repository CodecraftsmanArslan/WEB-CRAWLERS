from django.contrib.auth.models import User
from .models import Product
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password= request.POST.get('password')
        data=authenticate(request,username=username,password=password)
        if data is not None:
            login(request,data)
            messages.success(request, 'login successfully')
        else:
            messages.error(request, 'Username and Password are incorrect.')

    return render (request,'index.html')


def registration_form(request):
    if request.method == "POST":
        user_name = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists. Please use a different email.')
        else:
            user_info = User(username=user_name, email=email)
            user_info.set_password(password)  
            user_info.save()
            messages.success(request, 'Account created successfully')
            return redirect('/')
 
    return render(request, 'reg.html')



def add_item(request):
    item_info = Product.objects.all()  
    data_list = []
    for product in item_info:
        title = product.title
        price = f"${product.price}"
        image = product.header_image.url
        print(image)
        data_list.append({'title': title, 'price': price, 'image': image})

    return render(request,'item.html',{'infos':data_list})



