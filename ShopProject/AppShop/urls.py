from django.contrib import admin
from django.urls import path,re_path
from AppShop.views import *

urlpatterns = [
    path('register/', register),
    path('registerajax/', registerajax),
    path('login/', login),
    path('index/', index),
    path('base/',base),
    path('register_store/',register_store),
    path('add_goods/',add_goods),
    path('list_goods/',list_goods),
    path('logout/',logout),
    path('edit_price/',edit_price),
    re_path(r"^goods/(?P<goods_id>\d+)",goods),
    re_path(r"edit_goods/(?P<goods_id>\d+)",edit_goods),
]
