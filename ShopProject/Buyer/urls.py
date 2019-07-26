from django.contrib import admin
from django.urls import path,re_path
from Buyer.views import *

urlpatterns = [
    path("base/",base),
    path("index/",index),
    path("register/",register),
    path("login/",login),
    path("logout/",logout),
]