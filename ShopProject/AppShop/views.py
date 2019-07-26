import hashlib

from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from django.core.paginator import Paginator
from django.http import JsonResponse

from AppShop.models import *
# Create your views here.

def loginVilid(fun):
    def inner(request,*args,**kwargs):
        cookie_name=request.COOKIES.get("username")
        session_name=request.session.get("username")
        if cookie_name and session_name:
            user=Seller.objects.filter(username=cookie_name).first()
            if user and cookie_name==session_name:
                return fun(request,*args,**kwargs)
        return HttpResponseRedirect("/AppShop/login/")
    return inner


def set_password(password):
    md5=hashlib.md5()
    md5.update(password.encode())
    return md5.hexdigest()

def register(request):
    if request.method=="POST":
        username=request.POST.get("username")
        password=request.POST.get("password")
        if username and password:
            sellers=Seller()
            sellers.username=username
            sellers.password=set_password(password)
            sellers.nickname=username
            sellers.save()
            return HttpResponseRedirect("/AppShop/login/")
    return render(request,"appshop/register.html")

def registerajax(request):
    result={"status":"error","content":""}
    username=request.GET.get("username")
    if username:
        name=Seller.objects.filter(username=username).first()
        if name:
            result["content"]="用户名已存在"
        else:
            result["status"]="success"
            result["content"]="可以使用的用户名"
    else:
        result["content"]="用户名不能为空"
    return JsonResponse(result)

def login(request):
    response = render(request,"appshop/login.html")
    response.set_cookie("login_from","login_page")
    if request.method == "POST":
        username=request.POST.get("username")
        password=request.POST.get("password")
        if username and password:
            user=Seller.objects.filter(username=username).first()
            if user:
                cookies = request.COOKIES.get("login_from")
                if user.password == set_password(password) and cookies=="login_page":
                    response=HttpResponseRedirect("/AppShop/index/")
                    response.set_cookie("username",username)
                    response.set_cookie("userid",user.id)
                    request.session["username"]=username
                    return response
    return response


def logout(request):
    response =HttpResponseRedirect("/AppShop/login/")
    for key in request.COOKIES:
        response.delete_cookie(key)
    # response.delete_cookie("username")
    # response.delete_cookie("userid")
    # response.delete_cookie("login_from")
    # response.delete_cookie("is_store")
    del request.session["username"]
    return response


@loginVilid
def index(request):
    cookie_id = request.COOKIES.get("userid")
    if cookie_id:
        cookie_id=int(cookie_id)
    else:
        cookie_id=0
    store=Store.objects.filter(user_id=cookie_id).first()
    if store:
        is_store=store.id
    else:
        is_store=""
    response = render(request, "appshop/index.html",{"is_store":is_store})
    response.set_cookie("is_store", is_store)
    print(is_store)
    return response
    # request.session["is_store"] = is_store
    # return render(request,"appshop/index.html")

def base(request):
    return render(request,"appshop/base.html")

@loginVilid
def register_store(request):
    typeList=StoreType.objects.all()
    if request.method=="POST":
        # userid=request.COOKIES.get("userid")
        store_name=request.POST.get("store_name")
        store_descripton=request.POST.get("store_descripton")
        store_phone=request.POST.get("store_phone")
        store_money=request.POST.get("store_money")
        store_address=request.POST.get("store_address")
        user_id=int(request.COOKIES.get("userid"))
        type_lists=request.POST.getlist("store_type")
        store_logo=request.FILES.get("store_logo")
        store=Store()
        store.store_name=store_name
        store.store_descripton=store_descripton
        store.store_phone=store_phone
        store.store_money=store_money
        store.store_address=store_address
        store.user_id=user_id
        store.store_logo=store_logo
        store.save()
        for i in type_lists:
            store_type=StoreType.objects.get(id = i)
            store.type.add(store_type)
        store.save()
        return HttpResponseRedirect("/AppShop/index/")
    return render(request,"appshop/register_store.html",locals())

@loginVilid
def add_goods(request):
    # userid=request.COOKIES.get("userid")
    # store=Store.objects.filter(user_id=userid).first()
    goodstypelist=GoodsType.objects.all()
    storeid=request.COOKIES.get("is_store")
    if request.method=="POST":
        goods_name=request.POST.get("goods_name")
        goods_price=request.POST.get("goods_price")
        goods_image=request.FILES.get("goods_image")
        goods_number=request.POST.get("goods_number")
        goods_description=request.POST.get("goods_description")
        goods_date=request.POST.get("goods_date")
        goods_safeDate=request.POST.get("goods_safeDate")
        goods_type=request.POST.get("goods_type")
        # store_id=request.POST.get("store_id")
        store_id=storeid
        print(goods_name,goods_price,store_id)
        goods=Goods()
        goods.goods_name=goods_name
        goods.goods_price=goods_price
        goods.goods_image=goods_image
        goods.goods_number=goods_number
        goods.goods_description=goods_description
        goods.goods_date=goods_date
        goods.goods_safeDate=goods_safeDate
        goods.goodstype_id_id=goods_type
        goods.save()
        goods.store_id.add(
            Store.objects.get(id=int(store_id))
        )
        print(Store.objects.get(id=int(store_id)))
        goods.save()
        return HttpResponseRedirect("/AppShop/list_goods/up/")
    return render(request,"appshop/add_goods.html",locals())


@loginVilid
def list_goods(request,state):
    try:
        if state == "up":
            state_num=1
        else:
            state_num=0
        # userid=request.COOKIES.get("userid")
        # store=Store.objects.filter(user_id=userid).first()
        storeid=request.COOKIES.get("is_store")
        # print(store.id)
        keywords=request.GET.get("keywords","")
        page_num=request.GET.get("page_num","1")
        if keywords:
            good_list=Goods.objects.filter(store_id=storeid,goods_under=state_num,goods_name__contains=keywords)
        else:
            good_list=Goods.objects.filter(store_id=storeid,goods_under=state_num)
        paginator=Paginator(good_list,2)
        page=paginator.page(int(page_num))
        page_list=paginator.page_range
        return render(request,"appshop/list_goods.html",locals())
    except:
        if state == "up":
            state_num=1
        else:
            state_num=0
        # userid=request.COOKIES.get("userid")
        # store=Store.objects.filter(user_id=userid).first()
        storeid=request.COOKIES.get("is_store")
        # print(store.id)
        keywords=request.GET.get("keywords","")
        page_num=int(request.GET.get("page_num","1"))-1
        if keywords:
            good_list=Goods.objects.filter(store_id=storeid,goods_under=state_num,goods_name__contains=keywords)
        else:
            good_list=Goods.objects.filter(store_id=storeid,goods_under=state_num)
        paginator=Paginator(good_list,2)
        page=paginator.page(page_num)
        page_list=paginator.page_range
        return HttpResponseRedirect("/AppShop/list_goods/%s/?keywords=%s&page_num=%s" % (state,keywords,page_num))
        # return render(request,"appshop/404.html")

@loginVilid
def edit_price(request):
    if request.method == "POST":
        goods_id = request.POST.get("goods_id")
        goods_price = request.POST.get("goods_price")
        goods_state=request.POST.get("state")
        print(goods_id, goods_price)
        Goods.objects.filter(id=goods_id).update(goods_price=goods_price)
    # return render(request, "appshop/list_goods.html", locals())
        return HttpResponseRedirect("/AppShop/list_goods/%s"%goods_state)

@loginVilid
def goods(request,goods_id):
    good=Goods.objects.filter(id=goods_id).first()
    return render(request,"appshop/goods.html",locals())
@loginVilid
def edit_goods(request,goods_id):
    good=Goods.objects.filter(id=goods_id).first()
    if request.method=="POST":
        goods_name=request.POST.get("goods_name")
        goods_price=request.POST.get("goods_price")
        goods_number=request.POST.get("goods_number")
        goods_date=request.POST.get("goods_date")
        goods_safeDate=request.POST.get("goods_safeDate")
        goods_description=request.POST.get("goods_description")
        goods_image=request.FILES.get("goods_image")
        goods=Goods.objects.get(id=int(goods_id))
        goods.goods_name=goods_name
        goods.goods_price=goods_price
        goods.goods_number=goods_number
        goods.goods_date=goods_date
        goods.goods_safeDate=goods_safeDate
        goods.goods_description=goods_description
        if goods_image:
            goods.goods_image=goods_image
        goods.save()
        return HttpResponseRedirect("/AppShop/list_goods/up/")
    return render(request,"appshop/edit_goods.html",locals())

def set_goods(request,state):
    if state =="up":
        state_num=1
    else:
        state_num=0
    id=request.GET.get("id")
    referer=request.META.get("HTTP_REFERER")
    if id:
        goods=Goods.objects.filter(id=id).first()
        if state =="delete":
            goods.delete()
        else:
            goods.goods_under=state_num
            goods.save()
    return HttpResponseRedirect(referer)


def list_goodstype(request):
    goods_type_list=GoodsType.objects.all()
    if request.method=="POST":
        name=request.POST.get("name")
        description=request.POST.get("description")
        image=request.FILES.get("picture")
        if name and description and image:
            goodstype=GoodsType()
            goodstype.goodstype_name=name
            goodstype.goodstype_description=description
            goodstype.goodstype_image=image
            goodstype.save()
    return render(request,"appshop/list_goodstype.html",locals())

def delete_goodstype(request):
    goodstype_id=request.GET.get("id")
    if goodstype_id:
        delgoodstype=GoodsType.objects.get(id=goodstype_id)
        delgoodstype.delete()
    return HttpResponseRedirect("/AppShop/list_goodstype")

# def edit_goodstype(request):
#     goodstype_id = request.GET.get("id")
#     if goodstype_id:
#         goodstype = GoodsType.objects.get(id=goodstype_id)
#     if request.method=="POST":
#         id=request.POST.get("id")
#         name = request.POST.get("name")
#         description = request.POST.get("description")
#         image = request.FILES.get("picture")
#         if id and name and description and image:
#             goodstype = GoodsType.objects.get(id=id)
#             goodstype.goodstype_name = name
#             goodstype.goodstype_description = description
#             goodstype.goodstype_image = image
#             goodstype.save()
#             return HttpResponseRedirect("/AppShop/list_goodstype")
#     return render(request, "appshop/edit_goodstype.html", locals())

def edit_goodstype(request):
    if request.method=="POST":
        id = request.POST.get("id")
        name = request.POST.get("name")
        description = request.POST.get("description")
        image = request.FILES.get("picture")
        print(id,name,description,image)
        if id:
            goodstype = GoodsType.objects.get(id=id)
            goodstype.goodstype_name = name
            goodstype.goodstype_description = description
            goodstype.goodstype_image = image
            goodstype.save()
    return HttpResponseRedirect("/AppShop/list_goodstype")