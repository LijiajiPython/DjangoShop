import hashlib

from django.shortcuts import render,HttpResponse,HttpResponseRedirect

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
                    request.session["username"]=username
                    return response
    return response

@loginVilid
def index(request):
    return render(request,"appshop/index.html",locals())

def base(request):
    return render(request,"appshop/base.html")