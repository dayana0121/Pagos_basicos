from django.http import HttpResponse
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def home(request):
    return HttpResponse("Camishop: listo para integrar pagos 💳")

@csrf_exempt
def pagos_webhook(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            payload = {}
        print("Webhook recibido:", payload)
        return JsonResponse({"ok": True})
    return JsonResponse({"detail": "Método no permitido"}, status=405)
