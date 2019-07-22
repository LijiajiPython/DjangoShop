from django.contrib import admin
from django.urls import path
from AppShop.views import *

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('index/', index),
    path('base',base)
]
