from django.shortcuts import render
from . import models
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.contrib import auth
from .models import User as User

basepath = os.getcwd() + '\\Article\\templates\\'


def detail(request, id):
    news = models.article.objects.get(pk=id)
    return render(request, 'pages/news.html', {'news': news})


def list(request):
    limit = 20  # 这里是，每页限制的信息条数
    articles_list = models.article.objects.all()
    paginator = Paginator(articles_list, limit)  # 设置分页信息；
    page = request.GET.get('page', 1)
    try:
        article = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        article = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        article = paginator.page(paginator.num_pages)
    loaded = paginator.page(page)
    return render(request, 'pages/index.html', {'articles': article})


def search(request):
    limit = 20  # 这里是，每页限制的信息条数
    keyword = request.GET['searchtext']
    allArticle = models.article.objects.all().order_by("-date")
    SearchResult = []
    for article in allArticle:
        if keyword in article.title:
            SearchResult.append(article)
        elif keyword in article.text:
            SearchResult.append(article)
        elif keyword in article.author:
            SearchResult.append(article)
    #  elif keyword in article.type:
    #   SearchResult.append(article)
    SearchStatus = "Error" if len(SearchResult) == 0 else "Success"
    ResultAmount = len(SearchResult)
    paginator = Paginator(SearchResult, limit)  # 设置分页信息；
    page = request.GET.get('page', 1)
    try:
        article = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        article = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        article = paginator.page(paginator.num_pages)
    loaded = paginator.page(page)
    return render(request, 'pages/search.html',
                  {"keyword": keyword, "SearchResult": article, "SearchStatus": SearchStatus,
                   "ResultAmount": ResultAmount})


def homepage(request):
    response = render(request, basepath + "pages/hello.html")
    return response


# 用户注册
@csrf_exempt
def register(request):
    errors = []
    account = None
    password = None
    password2 = None
    CompareFlag = False

    if request.method == 'POST':
        if not request.POST.get('account'):
            errors.append('用户名不能为空')
        else:
            account = request.POST.get('account')

        if not request.POST.get('password'):
            errors.append('密码不能为空')
        else:
            password = request.POST.get('password')
        if not request.POST.get('password2'):
            errors.append('确认密码不能为空')
        else:
            password2 = request.POST.get('password2')

        if password is not None:
            if password == password2:
                CompareFlag = True
            else:
                errors.append('两次输入密码不一致')

        if account is not None and password is not None and password2 is not None and CompareFlag:
            User.objects.create_user(username=account, password=password)
            userlogin = auth.authenticate(username=account, password=password)
            auth.login(request, userlogin)
            return HttpResponseRedirect('/pages/index/')

    return render(request, 'pages/register.html', {'errors': errors})


# 用户登录
@csrf_exempt
def login(request):
    errors = []
    account = None
    password = None
    if request.method == "POST":
        if not request.POST.get('account'):
            errors.append('用户名不能为空')
        else:
            account = request.POST.get('account')

        if not request.POST.get('password'):
            errors = request.POST.get('密码不能为空')
        else:
            password = request.POST.get('password')

        if account is not None and password is not None:
            user = auth.authenticate(username=account, password=password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect('/pages/index/')
                else:
                    errors.append('用户名错误')
            else:
                errors.append('用户名或密码错误')
    return render(request, 'pages/login.html', {'errors': errors})


# 用户退出
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/pages/index/')


# Create your views here.


def type(request, t):
    limit = 20  # 这里是，每页限制的信息条数
    articles = models.article.objects.filter(type=t).order_by("-date")
    ResultAmount = len(articles)
    paginator = Paginator(articles, limit)  # 设置分页信息；
    page = request.GET.get('page', 1)
    try:
        article = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        article = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        article = paginator.page(paginator.num_pages)
    loaded = paginator.page(page)
    return render(request, 'pages/type.html', {"type": t, "SearchResult": article, "ResultAmount": ResultAmount})


def index(request):
    Result1 = []
    Result2 = []
    Result3 = []
    Result4 = []
    Result5 = []
    articles = models.article.objects.filter(type=1).order_by("-date")
    for n in range(0, 10):
        Result1.append(articles[n])
    articles = models.article.objects.filter(type=2).order_by("-date")
    for n in range(0, 6):
        Result2.append(articles[n])
    articles = models.article.objects.filter(type=3).order_by("-date")
    for n in range(0, 6):
        Result3.append(articles[n])
    articles = models.article.objects.filter(type=4).order_by("-date")
    for n in range(0, 8):
        Result4.append(articles[n])
    articles = models.article.objects.filter(type=5).order_by("-date")
    for n in range(0, 8):
        Result5.append(articles[n])
    return render(request, 'pages/index.html',{"type1":Result1,"type2":Result2,"type3":Result3,"type4":Result4,"type5":Result5})
