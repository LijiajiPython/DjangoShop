from django.contrib import admin
from django.urls import path,re_path
from Buyer.views import *

urlpatterns = [
    path("base/",base),
    path("index/",index),
    path("register/",register),
    path("login/",login),
    path("logout/",logout),
    path("buyer_list_goods/",buyer_list_goods),
    path("ali_pay/",ali_pay),
    path("pay_result/",pay_result),
    path("pay_order/",pay_order),
    path("buyer_list_goods/",buyer_list_goods),
    path("detail/",detail),
    path("place_order/",place_order),
]