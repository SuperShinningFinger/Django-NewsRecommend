from django.db import models
from django.contrib.auth.models import AbstractUser
class article(models.Model):
    article_id = models.IntegerField(primary_key=True)
    title=models.CharField(max_length=50,default='无题')
    author=models.CharField(max_length=20)
    text=models.TextField(null=True)
    date=models.CharField(max_length=20)
    type=models.TextField(null=True)
    click=models.IntegerField(default=0,null=True)
    def __str__(self):
        return self.title

class User(AbstractUser):
    username=models.CharField(max_length=50,primary_key=True)
    password=models.CharField(max_length=20)
    sex=models.CharField(max_length=10,null=True)
    school=models.CharField(max_length=50,null=True)
    type=models.TextField(null=True)
    viewed=models.TextField(null=True)
    scored=models.TextField(null=True)
    recommend=models.TextField(null=True)

class Score(models.Model):
    user = models.ForeignKey('User',on_delete=models.CASCADE)
    article = models.ForeignKey('Article',on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=3, decimal_places=2)
# Create your models here.
