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

---

Yape + Mercado Pago — Paso 3.1 (Revisión de integración y requisitos)

🎯 Objetivo
- Procesar pagos con Yape desde Django usando Mercado Pago como intermediario, contemplando credenciales, generación del pago, confirmaciones y manejo de errores.

📚 Documentación de referencia
- “Yape — Configuración de la integración” (Mercado Pago).
- Token/flujo Yape: generación con OTP + número de celular, luego creación del pago con ese token.
- Condiciones: modo sandbox, credenciales públicas/privadas, habilitación del método de pago en la cuenta de Mercado Pago.

✅ Estado actual del repositorio
- Frontend (`templates/yape.html`):
  - Formulario con campos obligatorios: `phone` (celular Yape) y `otp` (código OTP).
  - Carga del SDK JS de Mercado Pago (`https://sdk.mercadopago.com/js/v2`).
  - Inicialización con la clave pública `{{ public_key }}`.
  - Envío del token (actualmente simulado) al backend `POST /procesar_pago/` con protección CSRF.
- Backend (`yape/views.py`):
  - `yape_view`: lee `MP_PUBLIC_KEY` del `.env` y renderiza `yape.html`.
  - `procesar_pago`: recibe `token`, usa `MP_ACCESS_TOKEN` para crear el pago vía `POST https://api.mercadopago.com/v1/payments` con `payment_method_id: "yape"`.
- Configuración (`pagos_basico/settings.py`):
  - Variables de entorno: `MP_PUBLIC_KEY`, `MP_ACCESS_TOKEN` ya soportadas.
- Rutas (`yape/urls.py`):
  - `"/"` → `yape_view` y `"/procesar_pago/"` → `procesar_pago`.

⚠️ Nota sobre el token Yape
- En el flujo actual se simula el token en `yape.html` para probar end‑to‑end.
- Para producción, reemplazar la simulación por el flujo oficial de generación de token Yape (OTP + celular) según documentación vigente de Mercado Pago.

🧩 Requisitos y condiciones para pruebas (sandbox)
- Habilitar modo sandbox en Mercado Pago.
- Configurar credenciales en `.env`:
  - `MP_PUBLIC_KEY` (clave pública, usada en el frontend).
  - `MP_ACCESS_TOKEN` (token privado, usado en el backend para crear el pago).
- Asegurarse de que Yape esté habilitado como medio de pago en la cuenta.

📋 Campos obligatorios (flujo Yape)
- Número de teléfono del pagador (Yape).
- Código OTP enviado por Yape.
- Credenciales de Mercado Pago: pública (frontend) y privada (backend).

🚀 Cómo probar el flujo actual
1. Crear y completar el archivo `.env` siguiendo `Pagos_basicos/.env.example`.
2. Iniciar el servidor de Django: `python manage.py runserver`.
3. Abrir la página principal (renderiza `yape.html`).
4. Ingresar teléfono y OTP (de prueba), generar token simulado y enviar.
5. Ver la respuesta del backend y el payload a la API de Mercado Pago.

🔜 Próximos pasos (sugeridos)
- Sustituir el token simulado por el token real de Yape (según SDK/API oficial).
- Agregar manejo robusto de errores y estados del pago.
- Implementar webhook de confirmación de pago (si aplica al método Yape) y actualizar estados en BD.

---

Paso 3.2 — Registrar aplicación / credenciales en Mercado Pago

🎯 Meta
- Obtener credenciales públicas y privadas, y activar Yape en la cuenta.

🛠️ Acciones en el Dashboard de Mercado Pago
1. Ingresar al Dashboard de Desarrolladores (Mercado Pago → Developers).
2. Crear una nueva aplicación (si no existe) y seleccionar “Pagos online”.
3. En métodos de pago, habilitar Yape para Perú (si tu cuenta y país lo permiten).
4. Ir a “Credenciales” y copiar las claves en modo sandbox:
   - Public key → usar como `MP_PUBLIC_KEY` (frontend).
   - Access token (privado) → usar como `MP_ACCESS_TOKEN` (backend).
5. (Opcional) Configurar Webhooks: apuntar a tu endpoint, por ejemplo `https://<tu_dominio>/webhook/`.

📎 Sobre verificación de Webhooks
- A diferencia de Stripe, normalmente Mercado Pago no requiere un “webhook secret” universal para verificar firma.
- La validación recomendada es recuperar el pago por `id` con tu `MP_ACCESS_TOKEN` usando la API.
- Si tu cuenta ofrece configuración de firma/cabecera para webhooks, habilítala y valida según documentación; en este repo dejamos verificación por consulta a la API.

🔧 Configuración en este proyecto
- Variables en `.env` (ver `Pagos_basicos/.env.example`):
  - `MP_PUBLIC_KEY=...`
  - `MP_ACCESS_TOKEN=...`
- Endpoint de Webhook (creado en `yape/urls.py`): `POST /webhook/`
  - Recibe notificaciones y consulta el pago por `id` en la API de Mercado Pago.

✅ Checklist rápido
- Cuenta de Mercado Pago en modo sandbox.
- App “Pagos online” creada.
- Yape habilitado en métodos de pago.
- `MP_PUBLIC_KEY` y `MP_ACCESS_TOKEN` configurados.
- Webhook apuntando a tu entorno (si lo vas a usar para confirmaciones).