# 个性化新闻推荐网站

本项目是基于**Django框架**的个性化新闻推荐网站，聚类改进的**基于肘部法则的K-means算法**，推荐算法采用**内容与协同过滤组合**的推荐方法。
网址: http://47.95.196.246:8005/

## 环境配置

### 运行系统环境

Ubuntu 16.04.6 LTS (GNU/Linux 4.4.0-93-generic x86_64)

### Python版本

Python3.6.5

### Python依赖包

#### 依赖包文件：requirement.txt

```python
absl-py==0.4.0
astor==0.7.1
Django==2.1
django-crontab==0.7.1
gast==0.2.0
grpcio==1.14.1
Markdown==2.6.11
numpy==1.15.1
pandas==0.23.4
protobuf==3.6.1
python-dateutil==2.7.3
pytz==2018.5
six==1.11.0
tensorboard==1.10.0
tensorflow==1.10.0
termcolor==1.1.0
Werkzeug==0.14.1
```

#### 生成依赖包文件方法

```python
pip freeze > requirements.txt
```

#### 安装依赖方法

在项目根目录打开Python终端，运行

```python
pip install -r requirements.txt
```

## 运行项目方法

1. 在IDE(如Pycharm)中运行

2. 进入`manage.py`文件目录下,然后运行：

   ```python
   python3 manage.py runserver 0.0.0.0:8005
   nohup python -u manage.py runserver 0.0.0.0:8005 > out.log 2>&1 &    # 后台运行
   ```