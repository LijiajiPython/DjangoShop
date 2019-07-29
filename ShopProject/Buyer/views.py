import hashlib
import time

from alipay import AliPay
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect

from Buyer.models import *
from AppShop.models import *
# Create your views here.

def loginVilid(fun):
    def inner(request,*args,**kwargs):
        cookie_name=request.COOKIES.get("username")
        session_name=request.session.get("username")
        if cookie_name and session_name:
            user=Buyer.objects.filter(username=cookie_name).first()
            if user and cookie_name==session_name:
                return fun(request,*args,**kwargs)
        return HttpResponseRedirect("/Buyer/login/")
    return inner


def set_password(password):
    md5=hashlib.md5()
    md5.update(password.encode())
    return md5.hexdigest()

def setOrderId(user_id,goods_id,store_id):
    timenum=time.strftime("%Y%m%d%H%M%S",time.localtime())
    order_id = timenum+user_id+goods_id+store_id
    return order_id


def base(request):
    return render(request,"buyer/base.html")



def index(request):
    GoodstypeList = GoodsType.objects.all()

    return render(request,"buyer/index.html",locals())

def register(request):
    if request.method=="POST":
        username=request.POST.get("user_name")
        password=request.POST.get("pwd")
        cpassword=request.POST.get("cpwd")
        email=request.POST.get("email")
        if username and password and cpassword and email:
            if password==cpassword:
                buyer=Buyer.objects.filter(username=username).first()
                if not buyer:
                    newbuyer=Buyer()
                    newbuyer.username=username
                    newbuyer.password=set_password(password)
                    newbuyer.email=email
                    newbuyer.save()
                    return HttpResponseRedirect("/Buyer/login/")
    return render(request,"buyer/register.html")

def login(request):
    response=render(request,"buyer/login.html")
    response.set_cookie("login_form","login_page")
    if request.method=="POST":
        username=request.POST.get("username")
        password=request.POST.get("pwd")
        print(username,password)
        if username and password:
            buyer=Buyer.objects.filter(username=username).first()
            if buyer:
                cookies=request.COOKIES.get("login_form")
                if cookies=="login_page" and set_password(password)==buyer.password:
                    response=HttpResponseRedirect("/Buyer/index/")
                    response.set_cookie("username",username)
                    response.set_cookie("userid",buyer.id)
                    request.session["username"]=username
                    return response
    return response




def logout(request):
    response =HttpResponseRedirect("/Buyer/index/")
    for key in request.COOKIES:
        response.delete_cookie(key)
    del request.session["username"]
    return response

def buyer_list_goods(request):
    typeid=request.GET.get("typeid")
    # if typeid:
    goods_list = Goods.objects.filter(goodstype_id=typeid,goods_under=1)
    return render(request,"buyer/buyer_list_goods.html",locals())


def ali_pay(request):
    alipay_public_key_string = """-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAjM7nNA0g+FaXNvpYieFk4em9kmoGSno1PsUEuJKK6ydoDVHxH6KJHXrjbgQeMmMeGx11R9Ajbq3wXPrMECYEAqgzgjZ/vf+gB3ka1ZY2bB5me/lpeKH3LkyC8YdmfodMc6U+Zx4/QuuZlAn3p7zKidpPnrKzhghU4jntvXB2IWEjDUK56A4cKvDo35v7MzsAFBqzpFlkTS4+oM7WR5q4+fybCGnulfYiSnE/Q2Hh2uoRiY2vEuGFsh00wTdfYy09H6nSBGR+uyzkRgvQb5IAB7bjh4w6TvYroNUhOaqDjk/ErWd8WFPGRdTGhXAXMQyI7Yd6nuqRUU9Uk2JIPFx+yQIDAQAB
    -----END PUBLIC KEY-----"""

    app_private_key_string = """-----BEGIN RSA PRIVATE KEY-----
    MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCMzuc0DSD4Vpc2+liJ4WTh6b2SagZKejU+xQS4korrJ2gNUfEfookdeuNuBB4yYx4bHXVH0CNurfBc+swQJgQCqDOCNn+9/6AHeRrVljZsHmZ7+Wl4ofcuTILxh2Z+h0xzpT5nHj9C65mUCfenvMqJ2k+esrOGCFTiOe29cHYhYSMNQrnoDhwq8Ojfm/szOwAUGrOkWWRNLj6gztZHmrj5/JsIae6V9iJKcT9DYeHa6hGJja8S4YWyHTTBN19jLT0fqdIEZH67LORGC9BvkgAHtuOHjDpO9iug1SE5qoOOT8StZ3xYU8ZF1MaFcBcxDIjth3qe6pFRT1STYkg8XH7JAgMBAAECggEAYWj5dX7noiV1Mul5utkcy1TCermyZG+qyiPOIknupMN8LkrTvojYxnYvQ/rBUSZUu3ljmyyYdocKU6iE518FQzlNePVu5egjs0fKkpv6Rk25pGZk2rlhoLv5klGTTFEZSJ+2TewU45zNgCZtF7N5gmhu0GDb5Qt6fY6Js5ZLgscAV2ZdCfIP1tTMD2kcyvUx3mw5+NXML+tOv2U7iMBj1ytupPc0MhXy+ivFjkBPK6v0LKz/7S/d9YsdOf7hVMrA89TtodkQwAiqyaVFCNOEwg3/7q8dD+ywPSwLiMpHLAjqfdp7YNYRJWXWDVrKnxiylvJnbkTuGEG3tjJoCrjNAQKBgQDeYXI4YJSnVECM8TLBOptuQ+eZ6hiqDbekW7RroIQQ6op3HyJBPkZJ3BU2RtdNo9i/UlK0X0iqM6Nr7YCp6CBCYQBLvT4crni+GH22FH7XZ/3x4gQfyb9P7PgpcZPmkhatL4fpzDmK2Z54hHJd3Km1UX74fquW/rFWavnY/u/QmQKBgQCiGHLfpJe+zWzSe8rOxy7OBKekPa56XYFiNS4j4TyB0ysNW2KGdB8qVpVnpNdLlxi67ofv+OFrYYO3ynycRtH/cHhv5BKpgVc0Fs+Nlqol2Sd09Qz9PkAyUgISkzc9IP4Mmdcp3YzmoH4y4fy4EMGh+p4PDASuePgWkt2wHJGNsQKBgQCmyiujAT09a0Gm9Fj++HgPcbrJg/zPvs4X5fgiKRgkn+UOhzln+c86Iml+dg+R2ev9Qz9orXaQwX42usGfrcxUPPC93cgyNuG0oiXXZPPll8etnbk+JlDpH3DZlKg7bSK47kdgIZ6e962V8rDcmV5n8iHrOwZzj79uc3nFOSChMQKBgGjOMggUHeFKZWA6lkjYVJT0QYhaMWQA7VUYWXrtePfgF2gNfEi+8B+p1/QpiuLfEShcbhxk6StK46WEEMniqIjmqZh++OoMLNwLG6vKjLzoCTD/+KQNCej/SUPFV+P4Xwq6tXnmO+IqRy6TG5nPi8M1jdjgxm4g3ReLYjcqYZohAoGBAL+nZyP+VAuh7ClyjZY9f9pwAOMx9lqfgsKxOggXQlU4OhxNtk+xGIs17UIFg6VLxXCRikqcaxnYzaGmZ75lJXBEkd1x8h5v9RXfNhhOwPwp1u5ewecvbTlCQK/ct7ATtfBtfFCfhXJ/IS7waz6thyfLg98TWD+gwdM11oApplg1
    -----END RSA PRIVATE KEY-----"""

    # 实例化支付应用
    alipay = AliPay(
        appid="2016092900624238",
        app_notify_url=None,
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2"
    )

    # 发起支付请求
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no="21202",  # 订单号
        total_amount=str(199789),  # 支付金额
        subject="奇怪的交易",  # 交易主题
        return_url="http://127.0.0.1:8000/Buyer/pay_result/",
        notify_url="http://127.0.0.1:8000/Buyer/pay_result/"
    )
    return HttpResponseRedirect("https://openapi.alipaydev.com/gateway.do?" + order_string)


def pay_result(request):
    order_id=request.GET.get("order_id")
    orderid=Order.objects.get(order_id=order_id)
    goods=OrderDetail.objects.filter(order_id_id=orderid)
    print(goods)
    for i in goods:
        i.goods_status=2
        i.save()
    # total_amount=199789.00
    # out_trade_no=21202
    # timestamp=2019-07-26+20%3A36%3A18
    return render(request,"buyer/pay_result.html",locals())


def pay_order(request):
    money=request.GET.get("money")
    order_id=request.GET.get("order_id")
    alipay_public_key_string = """-----BEGIN PUBLIC KEY-----
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAjM7nNA0g+FaXNvpYieFk4em9kmoGSno1PsUEuJKK6ydoDVHxH6KJHXrjbgQeMmMeGx11R9Ajbq3wXPrMECYEAqgzgjZ/vf+gB3ka1ZY2bB5me/lpeKH3LkyC8YdmfodMc6U+Zx4/QuuZlAn3p7zKidpPnrKzhghU4jntvXB2IWEjDUK56A4cKvDo35v7MzsAFBqzpFlkTS4+oM7WR5q4+fybCGnulfYiSnE/Q2Hh2uoRiY2vEuGFsh00wTdfYy09H6nSBGR+uyzkRgvQb5IAB7bjh4w6TvYroNUhOaqDjk/ErWd8WFPGRdTGhXAXMQyI7Yd6nuqRUU9Uk2JIPFx+yQIDAQAB
        -----END PUBLIC KEY-----"""

    app_private_key_string = """-----BEGIN RSA PRIVATE KEY-----
        MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCMzuc0DSD4Vpc2+liJ4WTh6b2SagZKejU+xQS4korrJ2gNUfEfookdeuNuBB4yYx4bHXVH0CNurfBc+swQJgQCqDOCNn+9/6AHeRrVljZsHmZ7+Wl4ofcuTILxh2Z+h0xzpT5nHj9C65mUCfenvMqJ2k+esrOGCFTiOe29cHYhYSMNQrnoDhwq8Ojfm/szOwAUGrOkWWRNLj6gztZHmrj5/JsIae6V9iJKcT9DYeHa6hGJja8S4YWyHTTBN19jLT0fqdIEZH67LORGC9BvkgAHtuOHjDpO9iug1SE5qoOOT8StZ3xYU8ZF1MaFcBcxDIjth3qe6pFRT1STYkg8XH7JAgMBAAECggEAYWj5dX7noiV1Mul5utkcy1TCermyZG+qyiPOIknupMN8LkrTvojYxnYvQ/rBUSZUu3ljmyyYdocKU6iE518FQzlNePVu5egjs0fKkpv6Rk25pGZk2rlhoLv5klGTTFEZSJ+2TewU45zNgCZtF7N5gmhu0GDb5Qt6fY6Js5ZLgscAV2ZdCfIP1tTMD2kcyvUx3mw5+NXML+tOv2U7iMBj1ytupPc0MhXy+ivFjkBPK6v0LKz/7S/d9YsdOf7hVMrA89TtodkQwAiqyaVFCNOEwg3/7q8dD+ywPSwLiMpHLAjqfdp7YNYRJWXWDVrKnxiylvJnbkTuGEG3tjJoCrjNAQKBgQDeYXI4YJSnVECM8TLBOptuQ+eZ6hiqDbekW7RroIQQ6op3HyJBPkZJ3BU2RtdNo9i/UlK0X0iqM6Nr7YCp6CBCYQBLvT4crni+GH22FH7XZ/3x4gQfyb9P7PgpcZPmkhatL4fpzDmK2Z54hHJd3Km1UX74fquW/rFWavnY/u/QmQKBgQCiGHLfpJe+zWzSe8rOxy7OBKekPa56XYFiNS4j4TyB0ysNW2KGdB8qVpVnpNdLlxi67ofv+OFrYYO3ynycRtH/cHhv5BKpgVc0Fs+Nlqol2Sd09Qz9PkAyUgISkzc9IP4Mmdcp3YzmoH4y4fy4EMGh+p4PDASuePgWkt2wHJGNsQKBgQCmyiujAT09a0Gm9Fj++HgPcbrJg/zPvs4X5fgiKRgkn+UOhzln+c86Iml+dg+R2ev9Qz9orXaQwX42usGfrcxUPPC93cgyNuG0oiXXZPPll8etnbk+JlDpH3DZlKg7bSK47kdgIZ6e962V8rDcmV5n8iHrOwZzj79uc3nFOSChMQKBgGjOMggUHeFKZWA6lkjYVJT0QYhaMWQA7VUYWXrtePfgF2gNfEi+8B+p1/QpiuLfEShcbhxk6StK46WEEMniqIjmqZh++OoMLNwLG6vKjLzoCTD/+KQNCej/SUPFV+P4Xwq6tXnmO+IqRy6TG5nPi8M1jdjgxm4g3ReLYjcqYZohAoGBAL+nZyP+VAuh7ClyjZY9f9pwAOMx9lqfgsKxOggXQlU4OhxNtk+xGIs17UIFg6VLxXCRikqcaxnYzaGmZ75lJXBEkd1x8h5v9RXfNhhOwPwp1u5ewecvbTlCQK/ct7ATtfBtfFCfhXJ/IS7waz6thyfLg98TWD+gwdM11oApplg1
        -----END RSA PRIVATE KEY-----"""

    # 实例化支付应用
    alipay = AliPay(
        appid="2016092900624238",
        app_notify_url=None,
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2"
    )

    # 发起支付请求
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id,  # 订单号
        total_amount=str(money),  # 支付金额
        subject="奇怪的交易",  # 交易主题
        return_url="http://127.0.0.1:8000/Buyer/pay_result/?order_id=%s"%(order_id),
        notify_url="http://127.0.0.1:8000/Buyer/pay_result/?order_id=%s"%(order_id)
    )
    return HttpResponseRedirect("https://openapi.alipaydev.com/gateway.do?" + order_string)

def detail(request):
    goods_id=int(request.GET.get("goods_id"))
    if goods_id:
        goods=Goods.objects.filter(id=goods_id).first()
        if goods:
            return render(request,"buyer/detail.html",locals())
    return HttpResponse("商品不存在")


def place_order(request):
    if request.method == "POST":
        #post数据
        count = int(request.POST.get("count"))
        goods_id = request.POST.get("goods_id")
        #cookie的数据
        user_id = request.COOKIES.get("userid")
        #数据库的数据
        goods = Goods.objects.get(id = goods_id)
        print(goods.store_id_id)
        store_id = goods.store_id_id
        print(store_id)
        price = goods.goods_price

        order = Order()
        order.order_id = setOrderId(str(user_id),str(goods_id),str(store_id))
        order.goods_count = count
        order.order_user = Buyer.objects.get(id = user_id)
        order.order_price = count*price
        order.save()

        order_detail = OrderDetail()
        order_detail.order_id= order
        order_detail.goods_id = goods_id
        order_detail.goods_name = goods.goods_name
        order_detail.goods_price = goods.goods_price
        order_detail.goods_number = count
        order_detail.goods_total = count*goods.goods_price
        order_detail.goods_store = store_id
        order_detail.goods_image = goods.goods_image
        order_detail.save()

        detail = [order_detail]

        return render(request,"buyer/place_order.html",locals())
    else:
        return HttpResponse("非法请求")