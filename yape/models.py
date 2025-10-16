from django.db import models


class Payment(models.Model):
    METHOD_CHOICES = (
        ("yape", "Yape"),
    )

    STATUS_CHOICES = (
        ("pendiente", "Pendiente"),
        ("pagado", "Pagado"),
        ("fallido", "Fallido"),
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, default="Pago con Yape")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="yape")

    # Estado local de negocio
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendiente")

    # Datos auxiliares
    token = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    otp = models.CharField(max_length=10, blank=True, null=True)

    # Datos sincronizados con Mercado Pago
    mp_payment_id = models.CharField(max_length=64, blank=True, null=True)
    mp_status = models.CharField(max_length=32, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"MP:{self.mp_payment_id or 'sin_id'} | {self.status} | {self.amount}"
