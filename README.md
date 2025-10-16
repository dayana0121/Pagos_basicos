PROYECTO: PAGOS EN LINEA CON TARJETA

🎯 OBJETIVO:
Integrar un flujo completo de pagos con tarjeta en Django: desde la creación de la orden, redirección al checkout de Stripe, hasta la confirmación del pago mediante webhook y actualización de la orden en la base de datos.

📦 ESTRUCTURA DEL PROYECTO:

core/ – App principal

models.py – Modelo Orden con campos: producto, monto, estado, checkout_id

views.py – Funciones:

home() – Página de inicio

crear_orden() – Crea orden y sesión de pago Stripe

success_view() – Página de pago exitoso

cancel_view() – Página de pago cancelado

stripe_webhook() – Webhook que valida la firma y marca la orden como pagada

urls.py – Rutas:

/ → home

/crear-orden/ → crear_orden

/success/ → success_view

/cancel/ → cancel_view

/webhook/pagos/ → stripe_webhook

templates/ – Plantillas HTML (home.html, success.html, cancel.html)

.env – Variables de entorno:

STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

⚙️ Pasos realizados
1️. Crear cuenta y credenciales de prueba en Stripe

Registré cuenta en Stripe.

Copié las API Keys (pública y secreta) en .env.

Habilité modo prueba.

2️. Instalar Stripe en Django
pip install stripe


Configuré la clave secreta en settings.py usando .env.

3️. Crear modelo Orden
class Orden(models.Model):
    producto = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, default='pendiente')
    checkout_id = models.CharField(max_length=255, blank=True, null=True)


Ejecuté migraciones:

python manage.py makemigrations
python manage.py migrate

4️. Crear endpoint /crear-orden/

En views.py, la función crear_orden():

Crea una orden en la BD.

Llama a Stripe para crear sesión de checkout.

Guarda checkout_id en la orden.

Redirige al usuario a la URL de checkout.

5️. Vistas de éxito y cancelación

/success/ → success_view()

/cancel/ → cancel_view()

6️. Configurar webhook /webhook/pagos/

Endpoint que recibe POST de Stripe.

Valida firma usando STRIPE_WEBHOOK_SECRET.

Actualiza orden a estado='pagado' si evento checkout.session.completed.

Uso de ngrok para pruebas locales:

ngrok http 8000
stripe listen --forward-to http://<ngrok_id>.ngrok.io/webhook/pagos/


Permite que los webhooks de Stripe lleguen con firma válida a local.

7️. Manejo de errores y logs

Captura errores de Stripe (ValueError, SignatureVerificationError) y muestra mensajes claros.

Logs en consola:

Creación de sesión

Recepción de webhook

Orden marcada como pagada

🧩 PROBLEMAS ENCONTRADOS:
- Error con la verificación de firma del webhook de Stripe
Durante la integración del webhook, Django mostraba el siguiente mensaje en la consola:
Error procesando webhook: No signatures found matching the expected signature for payload

Causa del problema:
Stripe verifica que los webhooks realmente provengan de su sistema mediante una firma secreta (Stripe-Signature).
Esta firma se valida en el código usando la variable STRIPE_WEBHOOK_SECRET.
El error se produjo porque la URL del webhook en Stripe había cambiado (ya que cada vez que se reinicia ngrok cambia el dominio público) y por lo tanto la firma generada por Stripe no coincidía con la que el servidor esperaba.

Solución aplicada:
1. Se ejecutó nuevamente ngrok http 8000 para obtener una nueva URL pública.
2. En el panel de Stripe (Developers → Webhooks), se actualizó el endpoint con esa nueva URL (https://xxxx-xxx.ngrok-free.app/webhook/pagos/).
3. Stripe generó una nueva clave de firma (whsec_...), la cual se copió en el archivo .env.
4. Se reinició el servidor Django y ngrok.
5. Después de esto, los eventos checkout.session.completed fueron recibidos y verificados correctamente, marcando la orden como “pagada” en el sistema.