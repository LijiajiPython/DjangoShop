from django.db import models

# Create your models here.
class Buyer(models.Model):
    username=models.CharField(max_length=32,verbose_name="用户名")
    password=models.CharField(max_length=32,verbose_name="密码")
    email=models.EmailField(verbose_name="用户邮箱")
    phone=models.CharField(max_length=32,verbose_name="联系电话",null=True,blank=True)
    connect_address = models.TextField(verbose_name="联系地址",null=True,blank=True)

class Address(models.Model):
    address = models.TextField(verbose_name="收货地址")
    recver = models.CharField(max_length=32,verbose_name="接收人")
    recv_phone=models.CharField(max_length=32,verbose_name="接收人电话")
    post_number = models.CharField(max_length=32,verbose_name="邮编")
    buyer_id = models.ForeignKey(to=Buyer,on_delete=models.CASCADE,verbose_name="用户id")

class Order(models.Model):
    order_id = models.CharField(max_length=32,verbose_name="id订单编号")
    goods_count = models.IntegerField(verbose_name="商品数量")
    order_user = models.ForeignKey(to=Buyer,on_delete=models.CASCADE,verbose_name="订单编号")
    order_address = models.ForeignKey(to = Address,on_delete=models.CASCADE,verbose_name="订单地址",blank=True,null=True)
    order_price = models.FloatField(verbose_name="订单总价")

class OrderDetail(models.Model):
    order_id = models.ForeignKey(to=Order,on_delete=models.CASCADE,verbose_name="订单编号(多对一)")
    goods_id = models.IntegerField(verbose_name="商品id")
    goods_name=models.CharField(max_length=32,verbose_name="商品名称")
    goods_price = models.FloatField(verbose_name="商品价格")
    goods_number = models.IntegerField(verbose_name="商品购买数量")
    goods_total = models.FloatField(verbose_name="商品总价")
    goods_store = models.IntegerField(verbose_name="店铺id")
    goods_image=models.ImageField(verbose_name="商品图片")
    # 订单状态：1未支付，2已支付未发货，3已发货，4已接收，0已退货
    goods_status = models.IntegerField(default=1,verbose_name="订单状态")