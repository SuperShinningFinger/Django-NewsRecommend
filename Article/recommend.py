import pandas as pd
import numpy as np
import tensorflow as tf
import sqlite3
from Article import models


def num2info(data):
    str_data=""
    for i in data:
        str_data = ",".join(i)
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
    for i in range(5000):
        _, movie_summary = sess.run([train, summaryMarged])
        writer.add_summary(movie_summary, i)
    c_x_p, c_t_p = sess.run([x_p, theta_p])
    predicts = np.dot(c_x_p, c_t_p.T) + rating_mean
    errors = np.sqrt(np.sum((predicts - rating) ** 2))
    pages_df = pd.read_sql_query("select * from Article_article;", conn)
    user_id = request.user_id
    sortedResult = predicts[:, int(user_id)].argsort()[::-1]
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
    return Recommend


def recommend():
    user = models.User.objects.all()
    for i in user:
        i.recommend = num2info(fix_recommend(i))
    print("推荐完毕，写入DB")
