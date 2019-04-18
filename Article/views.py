from django.template import Library
from django.template.defaultfilters import stringfilter
import pandas as pd
import numpy as np
import tensorflow as tf
import sqlite3
from django.shortcuts import render
from . import models
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.contrib import auth
from .models import User as User
from django.shortcuts import HttpResponse

basepath = os.getcwd() + '/Article/templates/'


def num2info(data):
    data_n = [str(i) for i in data]
    str_data = ",".join(data_n)
    str_data.strip('0')
    return str_data


def normalizeRarings(rating, record):
    m, n = rating.shape
    rating_mean = np.zeros((m, 1))
    rating_norm = np.zeros((m, n))
    for i in range(m):
        idx = record[i, :] != 0
        rating_mean[i] = np.mean(rating[i, idx])
        rating_norm[i, idx] -= rating_mean[i]
    return rating_norm, rating_mean


def user_recommend(request):
    # 读入数据
    conn = sqlite3.connect("news.sqlite")
    ratings_df = pd.read_sql_query("select * from Article_score;", conn)
    ratings_df.tail()
    # 初始化用户与新闻信息，将Id做数组保存
    userNo = ratings_df['user_id'].max() + 1
    pageNo = ratings_df['article_id'].max() + 1
    # 新闻评分矩阵，储存用户评价新闻的分数
    rating = np.zeros((pageNo, userNo))
    for index, row in ratings_df.iterrows():
        rating[int(row['article_id']), int(row['user_id'])] = row['score']
    record = rating > 0
    # 评分记录矩阵，用01记录有评分的记录
    record = np.array(record, dtype=int)
    # 标准化
    rating_norm, rating_mean = normalizeRarings(rating, record)
    rating_norm = np.nan_to_num(rating_norm)
    rating_mean = np.nan_to_num(rating_mean)
    num_features = 10
    x_p = tf.Variable(tf.random_normal([pageNo, num_features], stddev=0.35))
    theta_p = tf.Variable(tf.random_normal([userNo, num_features], stddev=0.35))
    loss = 1 / 2 * tf.reduce_sum(((tf.matmul(x_p, theta_p, transpose_b=True) - rating_norm) * record) ** 2) + \
           1 / 2 * (tf.reduce_sum(x_p ** 2) + tf.reduce_sum(theta_p ** 2))
    optimizer = tf.train.AdagradOptimizer(1e-4)
    train = optimizer.minimize(loss)
    tf.summary.scalar('loss', loss)
    summaryMarged = tf.summary.merge_all()
    filename = 'D:/page_t'
    writer = tf.summary.FileWriter(filename)
    sess = tf.Session()
    init = tf.global_variables_initializer()
    sess.run(init)
    saver = tf.train.Saver(max_to_keep=1)
    c_x_p, c_t_p = sess.run([x_p, theta_p])
    predicts = np.dot(c_x_p, c_t_p.T) + rating_mean
    errors = np.sqrt(np.sum((predicts - rating) ** 2))
    pages_df = pd.read_sql_query("select * from Article_article;", conn)
    user_id = request.user_id
    print(predicts)
    sortedResult = predicts[int(user_id), :].argsort()[::-1]
    predicts = np.transpose(predicts)
    # 推荐完毕
    return sortedResult


def fix_recommend(request):
    Viewed = []
    Recommend = []
    Result1 = []
    Result2 = []
    Result3 = []
    Result4 = []
    Result5 = []
    articles = models.article.objects.filter(type=1).order_by("-date")
    for n in range(0, len(articles)):
        Result1.append(articles[n])
    articles = models.article.objects.filter(type=2).order_by("-date")
    for n in range(0, len(articles)):
        Result2.append(articles[n])
    articles = models.article.objects.filter(type=3).order_by("-date")
    for n in range(0, len(articles)):
        Result3.append(articles[n])
    articles = models.article.objects.filter(type=4).order_by("-date")
    for n in range(0, len(articles)):
        Result4.append(articles[n])
    articles = models.article.objects.filter(type=5).order_by("-date")
    for n in range(0, len(articles)):
        Result5.append(articles[n])
    # 上一次点击的type
    last_type = 0
    viewed = request.viewed
    if request.viewed:
        article_list_id = viewed.split(',')
        for article_id in article_list_id:
            article = models.article.objects.get(article_id=int(article_id))
            Viewed.append(article)
            if len(Viewed) > 9:
                Viewed = Viewed[0:10]
        last_type = Viewed[0].type
    # 将上次点击的类型3个加入结果
    index = 0
    while index < 3:
        j = 0
        if last_type == '1':
            while (Result1[j] in Recommend):
                j += 1
            Recommend.append(Result1[j])
        if last_type == '2':
            while (Result2[j] in Recommend):
                j += 1
            Recommend.append(Result2[j])
        if last_type == '3':
            while (Result3[j] in Recommend):
                j += 1
            Recommend.append(Result3[j])
        if last_type == '4':
            while (Result4[j] in Recommend):
                j += 1
            Recommend.append(Result4[j])
        if last_type == '5':
            while (Result5[j] in Recommend):
                j += 1
            Recommend.append(Result5[j])
        index += 1
    # 协同过滤
    index = 0
    recommend_id = user_recommend(request)
    for i in recommend_id:
        article = models.article.objects.get(article_id=int(i))
        Recommend.append(article)
        index += 1
        if index == 3:
            break
    print("user_recommend compelete")
    # 喜欢的类型
    type = request.type
    type_num = 0
    if request.type:
        type = type.split(',')
        for i in type:
            j = 0
            type_num += 1
            if i == '1':
                while (Result1[j] in Recommend):
                    j += 1
                Recommend.append(Result1[j])
            if i == '2':
                while (Result2[j] in Recommend):
                    j += 1
                Recommend.append(Result2[j])
            if i == '3':
                while (Result3[j] in Recommend):
                    j += 1
                Recommend.append(Result3[j])
            if i == '4':
                while (Result4[j] in Recommend):
                    j += 1
                Recommend.append(Result4[j])
            if i == '5':
                while (Result5[j] in Recommend):
                    j += 1
                Recommend.append(Result5[j])
    # 热门新闻
    hot = models.article.objects.all().order_by("-click")
    j = 0
    for i in hot:
        if i not in Recommend:
            Recommend.append(i)
            j += 1
        if j == 4 - type_num:
            break
    j = 0
    recommend_id2 = []
    for i in Recommend:
        if (not models.article.objects.get(article_id=int(i.article_id))):
            print("推荐出错了")
        recommend_id2.append(i.article_id)
        j += 1

    return recommend_id2


def add_info(request, infos, data):
    if data:
        article_list_id = data.split(',')
        if str(infos.article_id) not in article_list_id:
            article_list_id.insert(0, str(infos.article_id))
        else:
            article_list_id.remove(str(infos.article_id))
            article_list_id.insert(0, str(infos.article_id))
        data = ",".join(article_list_id)
        print(data)
    else:
        data = str(infos.article_id)
    return data


def detail(request, id):
    hot_articles = models.article.objects.all().order_by("-click")
    hot_articles = hot_articles[0:10]
    try:
        infos = models.article.objects.get(article_id=id)
    except Exception as e:
        return HttpResponse('404')
    else:
        infos.click += 1
        infos.save()
    if not request.user.is_authenticated:
        return render(request, 'pages/news.html', {'news': infos, 'selected': -1, 'hot_news': hot_articles})
    viewed = request.user.viewed
    request.user.viewed = add_info(request, infos, viewed)
    request.user.save()
    scored = request.user.scored
    if request.POST.get('score'):
        request.user.scored = add_info(request, infos, scored)
        score = models.Score.objects.create(user=request.user, article=infos, score=float(request.POST.get('score')))
        score.save()
        request.user.save()
        return render(request, 'pages/news.html', {'news': infos, 'selected': 1, 'hot_news': hot_articles})
    if not scored or not str(id) in scored:
        return render(request, 'pages/news.html', {'news': infos, 'selected': 0, 'hot_news': hot_articles})
    return render(request, 'pages/news.html', {'news': infos, 'selected': 1, 'hot_news': hot_articles})


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
    keyword = request.POST.get('searchtext')
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
    page = request.POST.get('page', 1)
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
    response = index(request)
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
            request.user.school = request.POST.get('school')
            request.user.type = request.POST.get('label')
            request.user.sex = request.POST.get('sex-radio')
            request.user.save()
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


def recommend1(request):
    temp = fix_recommend(request.user)
    request.user.recommend = num2info(temp)
    request.user.save()


def index(request):

    Viewed = []
    Recommend = []
    Result1 = []
    Result2 = []
    Result3 = []
    Result4 = []
    Result5 = []
    articles = models.article.objects.filter(type=1).order_by("-date")
    for n in range(0, len(articles)):
        Result1.append(articles[n])
    articles = models.article.objects.filter(type=2).order_by("-date")
    for n in range(0, len(articles)):
        Result2.append(articles[n])
    articles = models.article.objects.filter(type=3).order_by("-date")
    for n in range(0, len(articles)):
        Result3.append(articles[n])
    articles = models.article.objects.filter(type=4).order_by("-date")
    for n in range(0, len(articles)):
        Result4.append(articles[n])
    articles = models.article.objects.filter(type=5).order_by("-date")
    for n in range(0, len(articles)):
        Result5.append(articles[n])

    Result1 = Result1[0:10]
    Result2 = Result2[0:6]
    Result3 = Result3[0:6]
    Result4 = Result4[0:8]
    Result5 = Result5[0:8]
    if not request.user.is_authenticated:
        return render(request, 'pages/index.html',
                      {"type1": Result1, "type2": Result2, "type3": Result3, "type4": Result4, "type5": Result5})

    recommend1(request)    
    # 浏览记录
    viewed = request.user.viewed
    if request.user.viewed:
        article_list_id = viewed.split(',')
        for article_id in article_list_id:
            article = models.article.objects.get(article_id=int(article_id))
            Viewed.append(article)
            if len(Viewed) > 9:
                Viewed = Viewed[0:10]

    # 推荐新闻
    recommend = request.user.recommend
    if request.user.recommend:
        article_list_id = recommend.split(',')
        for article_id in article_list_id:
            article = models.article.objects.get(article_id=int(article_id))
            Recommend.append(article)
    return render(request, 'pages/index.html',
                  {"type1": Result1, "type2": Result2, "type3": Result3, "type4": Result4, "type5": Result5,
                   "viewed": Viewed, "recommend": Recommend})
