from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "mp_payment_id", "amount", "status", "mp_status", "created_at")
    list_filter = ("status", "mp_status", "method")
    search_fields = ("mp_payment_id",)
