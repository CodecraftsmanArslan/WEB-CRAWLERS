from django.urls import path
from . import views

urlpatterns=[
    path('', views.translated_text, name='addpost'),
]




