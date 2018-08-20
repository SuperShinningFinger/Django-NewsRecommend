from django.template import Library
from django.template.defaultfilters import stringfilter
import pandas as pd
import numpy as np
import tensorflow as tf
import sqlite3

register = Library()
@stringfilter
def normalizeRarings(rating,record):
    m,n=rating.shape
    rating_mean = np.zeros((m,1))
    rating_norm = np.zeros((m,n))
    for i in range(m):
        idx = record[i,:]!=0
        rating_mean[i] = np.mean(rating[i,idx])
        rating_norm[i,idx] -= rating_mean[i]
    return rating_norm,rating_mean
register.filter(normalizeRarings)


@stringfilter
def recommend():
    # 读入数据
    conn = sqlite3.connect("news.sqlite")
    ratings_df = pd.read_sql_query("select * from Article_score;", conn)
    ratings_df.tail()
    # 初始化用户与新闻信息，将Id做数组保存
    userNo = ratings_df['user_id'].max()+1
    pageNo = ratings_df['article_id'].max()+1
    # 新闻评分矩阵，储存用户评价新闻的分数
    rating = np.zeros((pageNo,userNo))
    for index,row in ratings_df.iterrows():
        rating[int(row['article_id']),int(row['user_id'])] = row['score']
    record = rating > 0
    # 评分记录矩阵，用01记录有评分的记录
    record = np.array(record,dtype=int)
    # 标准化
    rating_norm,rating_mean = normalizeRarings(rating,record)
    rating_norm = np.nan_to_num(rating_norm)
    rating_mean = np.nan_to_num(rating_mean)
    num_features = 10
    x_p = tf.Variable(tf.random_normal([pageNo,num_features],stddev = 0.35))
    theta_p = tf.Variable(tf.random_normal([userNo,num_features],stddev = 0.35))
    loss = 1/2*tf.reduce_sum(((tf.matmul(x_p,theta_p,transpose_b=True)-rating_norm)*record)**2)+\
        1/2*(tf.reduce_sum(x_p**2)+tf.reduce_sum(theta_p**2))
    optimizer = tf.train.AdagradOptimizer(1e-4)
    train = optimizer.minimize(loss)
    tf.summary.scalar('loss',loss)
    summaryMarged = tf.summary.merge_all()
    filename = 'D:/page_t'
    writer = tf.summary.FileWriter(filename)
    sess = tf.Session()
    init = tf.global_variables_initializer()
    sess.run(init)
    for i in range(5000):
        _,movie_summary = sess.run([train,summaryMarged])
        writer.add_summary(movie_summary,i)
    c_x_p,c_t_p = sess.run([x_p,theta_p])
    predicts = np.dot(c_x_p,c_t_p.T) + rating_mean
    errors = np.sqrt(np.sum((predicts-rating)**2))
    pages_df = pd.read_sql_query("select * from Article_article;", conn)
    user_id = input('推荐id')
    sortedResult = predicts[:,int(user_id)].argsort()[::-1]
    idx = 0
    print('为用户推荐的20篇文章'.center(80,'='))
    for i in sortedResult:
        print('喜欢观看程度:%.2f,文章名:%s'%(predicts[i,int(user_id)],pages_df.iloc[i]['head']))
        idx += 1
        if idx == 20:
            break
register.filter(recommend)