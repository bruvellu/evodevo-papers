from django.contrib import admin
from django.urls import path
from django_distill import distill_path
from bot.views import home, feeds

urlpatterns = [
    distill_path('', home, name='home'),
    distill_path('feeds', feeds, name='feeds'),
    path('admin/', admin.site.urls),
]
