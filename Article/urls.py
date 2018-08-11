"""NewRecommand URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path,include
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name='Article'
urlpatterns = [
    path('news/<int:id>/', views.detail,name='news'),
    path('index/', views.list,name='index'),
    path('master/', views.search,name='master'),
    path('search/', views.search,name='search'),
    path('login/', views.login,name='login'),
    path('register/',views.register,name='register'),
]
urlpatterns += staticfiles_urlpatterns()
