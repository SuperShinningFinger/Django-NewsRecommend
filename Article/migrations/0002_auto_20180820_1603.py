# Generated by Django 2.0.5 on 2018-08-20 08:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Article', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.DecimalField(decimal_places=2, max_digits=3)),
            ],
        ),
        migrations.RemoveField(
            model_name='article',
            name='id',
        ),
        migrations.RemoveField(
            model_name='user',
            name='id',
        ),
        migrations.RemoveField(
            model_name='user',
            name='user_name',
        ),
        migrations.AddField(
            model_name='user',
            name='recommend',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='scored',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='viewed',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='article_id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='score',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Article.article'),
        ),
        migrations.AddField(
            model_name='score',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
