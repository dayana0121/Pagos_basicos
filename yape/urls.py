from django.urls import path
from . import views

urlpatterns = [
    path('', views.yape_view, name='yape'),
    path('procesar_pago/', views.procesar_pago, name='procesar_pago'),
    path('webhook/', views.mp_webhook, name='mp_webhook'),
]
