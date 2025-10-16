from django.shortcuts import render
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from dotenv import load_dotenv
import requests
from decimal import Decimal
from .models import Payment
import logging

load_dotenv()
logger = logging.getLogger(__name__)

def yape_view(request):
    public_key = os.getenv('MP_PUBLIC_KEY')  # 🔹 toma del .env
    return render(request, 'yape.html', {'public_key': public_key})

def procesar_pago(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except Exception:
            data = {}

        token = data.get("token")
        amount_str = data.get("amount") or data.get("monto") or "1.00"
        phone = data.get("phone")
        otp = data.get("otp")

        try:
            amount = Decimal(str(amount_str))
        except Exception:
            amount = Decimal("1.00")

        if not token:
            logger.warning("Token ausente en solicitud de pago")
            return JsonResponse({"message": "Token requerido"}, status=400)

        if not settings.MP_ACCESS_TOKEN:
            logger.error("MP_ACCESS_TOKEN no configurado")
            return JsonResponse({"message": "Falta configurar MP_ACCESS_TOKEN en el servidor"}, status=500)

        # Aquí usas tu ACCESS_TOKEN privado
        headers = {
            "Authorization": f"Bearer {settings.MP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        # Crea registro local con estado 'pendiente'
        payment = Payment.objects.create(
            amount=amount,
            description="Pago con Yape",
            method="yape",
            status="pendiente",
            token=token,
            phone=phone,
            otp=otp,
        )

        

        payload = {
            "transaction_amount": float(amount),
            "token": token,
            "description": payment.description,
            "installments": 1,
            "payment_method_id": "yape",
        }

        logger.info(f"Creando pago MP: amount={amount}, phone={phone}, otp={otp}")
        try:
            response = requests.post("https://api.mercadopago.com/v1/payments", headers=headers, json=payload)
            resp_data = response.json()
        except Exception as e:
            logger.exception("Error llamando a API de MP")
            payment.status = "fallido"
            payment.mp_status = "error"
            payment.save()
            return JsonResponse({"message": "Error al crear el pago en MP", "error": str(e)}, status=502)

        # Sincroniza información de MP en el registro local (se mantiene 'pendiente' hasta confirmación)
        mp_id = resp_data.get("id")
        mp_status = resp_data.get("status")
        payment.mp_payment_id = mp_id
        payment.mp_status = mp_status
        payment.save()

        # Manejo de errores de MP (status HTTP o contenido)
        if response.status_code >= 400 or resp_data.get("error"):
            logger.error(f"Pago MP rechazado: status={response.status_code}, body={resp_data}")
            payment.status = "fallido"
            payment.save()
            return JsonResponse({
                "message": "Pago rechazado o inválido",
                "payment_id": payment.id,
                "mp_payment_id": mp_id,
                "mp_status": mp_status,
                "local_status": payment.status,
                "data": resp_data,
            }, status=400)

        return JsonResponse({
            "message": "Pago creado en Mercado Pago (pendiente de confirmación)",
            "payment_id": payment.id,
            "mp_payment_id": mp_id,
            "mp_status": mp_status,
            "local_status": payment.status,
            "data": resp_data,
        })

    return JsonResponse({"message": "Método no permitido"}, status=405)

@csrf_exempt
def mp_webhook(request):
    if request.method in ("POST", "GET"):
        try:
            payload = json.loads(request.body) if request.method == "POST" else {}
        except Exception:
            payload = {}

        payment_id = None
        if isinstance(payload, dict):
            data_obj = payload.get("data")
            if isinstance(data_obj, dict) and data_obj.get("id"):
                payment_id = data_obj.get("id")
            elif payload.get("id"):
                payment_id = payload.get("id")
            elif payload.get("resource"):
                resource = payload.get("resource")
                try:
                    payment_id = str(resource).rstrip("/").split("/")[-1]
                except Exception:
                    payment_id = None

        if not payment_id:
            payment_id = request.GET.get("id")

        payment_info = None
        if payment_id:
            headers = {"Authorization": f"Bearer {settings.MP_ACCESS_TOKEN}"}
            try:
                logger.info(f"Consultando pago MP por webhook: id={payment_id}")
                resp = requests.get(f"https://api.mercadopago.com/v1/payments/{payment_id}", headers=headers)
                payment_info = resp.json()
            except Exception as e:
                logger.exception("Error consultando pago en MP desde webhook")
                payment_info = {"error": str(e)}
            # Actualiza estado local según estado en MP
            try:
                mp_status = payment_info.get("status")
                if mp_status == "approved":
                    local_status = "pagado"
                elif mp_status in ("pending", "in_process"):
                    local_status = "pendiente"
                else:
                    local_status = "fallido"

                Payment.objects.filter(mp_payment_id=payment_id).update(status=local_status, mp_status=mp_status)
            except Exception:
                pass

            logger.info(f"Webhook procesado: id={payment_id}, mp_status={mp_status}")
            return JsonResponse({"received": True, "payment_id": payment_id, "payment": payment_info})

        return JsonResponse({"received": True, "payment_id": None, "payment": None}, status=400)

    return JsonResponse({"message": "Método no permitido"}, status=405)