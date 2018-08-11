from django.contrib import admin
from .models import article
from .models import User

class articleadmin(admin.ModelAdmin):
    list_display = ('title','author','date')
admin.site.register(article,articleadmin)
admin.site.register(User)

# Register your models here.
