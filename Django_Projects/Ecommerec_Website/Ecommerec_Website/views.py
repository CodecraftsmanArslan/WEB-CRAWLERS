from django.contrib.auth.models import User
from .models import Product
from .models import CardItem
from django.http import HttpResponse,HttpResponseNotAllowed
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404



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
        data_list.append({'id': product.pk, 'title': title, 'price': price, 'image': image})  # Include product ID
    return render(request, 'item.html', {'infos': data_list})


def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = Product.objects.get(pk=product_id)
        existing_item = CardItem.objects.filter(title=product.title, price=product.price).first()
        if not existing_item:
            card_item = CardItem(title=product.title, price=product.price)
            card_item.save()
        return redirect('item')

    cart_data = CardItem.objects.all()
    info_data = [{'title': item.title, 'price': item.price} for item in cart_data]
    return render(request, 'add_item.html', {'items': info_data})

# def quantity_increase(request):
#     return render(request,'add_item.html')







    







