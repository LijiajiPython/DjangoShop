import hashlib

from django.shortcuts import render
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