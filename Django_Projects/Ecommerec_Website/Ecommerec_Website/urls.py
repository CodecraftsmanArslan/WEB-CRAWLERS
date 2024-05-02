from django.urls import path
from . import views

urlpatterns=[
    path('',views.user_login,name='login'),
    path('registration',views.registration_form,name='registration_form'),
    path('item',views.add_item,name='item'),

]