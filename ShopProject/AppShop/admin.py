from django.contrib import admin
from .models import *
from Buyer.models import *
# Register your models here.
admin.site.register(Seller)
admin.site.register(StoreType)
admin.site.register(Store)
admin.site.register(GoodsType)
admin.site.register(Goods)
admin.site.register(GoodsImg)
admin.site.register(Buyer)
admin.site.register(Address)