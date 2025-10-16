from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.conf import settings

def home(request):
    return render(request, 'yape.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('yape.urls')),
]
