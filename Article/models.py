from django.db import models
from django.contrib.auth.models import AbstractUser
class article(models.Model):
    article_id = models.IntegerField()
    title=models.CharField(max_length=50,default='无题')
    author=models.CharField(max_length=20)
    text=models.TextField(null=True)
    date=models.CharField(max_length=20)
    type=models.TextField(null=True)
    click=models.IntegerField(default=0,null=True)
    def __str__(self):
        return self.title

class User(AbstractUser):
    user_name=models.CharField(max_length=50)
    password=models.CharField(max_length=20)
    sex=models.CharField(max_length=10,null=True)
    school=models.CharField(max_length=50,null=True)
    type=models.TextField(null=True)
    viewed=models.TextField(null=True)
    like=models.TextField(null=True)
    dislike=models.TextField(null=True)
# Create your models here.
