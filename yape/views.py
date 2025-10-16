from django.shortcuts import render
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from dotenv import load_dotenv
import requests

load_dotenv()

def yape_view(request):
    public_key = os.getenv('MP_PUBLIC_KEY')  # 🔹 toma del .env
    return render(request, 'yape.html', {'public_key': public_key})

@csrf_exempt
def procesar_pago(request):
    if request.method == "POST":
        data = json.loads(request.body)
        token = data.get("token")

        # Aquí usas tu ACCESS_TOKEN privado
        headers = {
            "Authorization": f"Bearer {settings.MP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        payload = {
            "transaction_amount": 1.00,  # monto de prueba
            "token": token,
            "description": "Pago de prueba con Yape",
            "installments": 1,
            "payment_method_id": "yape",
        }

        response = requests.post("https://api.mercadopago.com/v1/payments", headers=headers, json=payload)
        resp_data = response.json()

        return JsonResponse({"message": "✅ Pago procesado correctamente", "data": resp_data})

    return JsonResponse({"message": "Método no permitido"}, status=405)