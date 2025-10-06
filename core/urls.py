from django.urls import path
from .views import home, pagos_webhook

urlpatterns = [
    path('', home, name='home'),
    path('webhook/pagos/', pagos_webhook, name='pagos_webhook'),
]