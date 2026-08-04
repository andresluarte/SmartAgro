# chatbot/views.py

import json
import requests
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render

from agrosmartiotweb.models import ChatConversacion, ChatMensaje
from .permisos import usuario_tiene_acceso_chat, usuario_puede_ejecutar_accion, filtrar_tools_por_rol
from .registry import TOOLS_REGISTRY
from .tools_acciones import ejecutar_creacion_jornada

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
MODELO = "claude-haiku-4-5-20251001"

HEADERS = {
    "x-api-key": settings.ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

EJECUTORES_ACCIONES = {
    "crear_jornada": ejecutar_creacion_jornada,
}


@login_required
def chat_view(request):
    return render(request, 'chatbot/chat.html')


def _llamar_claude(historial, tools_schema, system_prompt):
    payload = {
        "model": MODELO,
        "max_tokens": 1024,
        "system": system_prompt,
        "messages": historial,
    }
    if tools_schema:
        payload["tools"] = tools_schema

    respuesta = requests.post(ANTHROPIC_URL, headers=HEADERS, json=payload)
    respuesta.raise_for_status()
    return respuesta.json()


def _ejecutar_tool(nombre_tool, input_data, user):
    print(f"🔧 TOOL LLAMADA: {nombre_tool} con input: {input_data}")
    tool_info = TOOLS_REGISTRY.get(nombre_tool)
    if not tool_info:
        return {"error": f"Tool '{nombre_tool}' no encontrada"}

    funcion = tool_info["funcion"]
    try:
        resultado = funcion(user=user, **input_data)
        print(f"✅ RESULTADO: {resultado}")  # ← 
        return resultado
    except Exception as e:
        print(f"❌ ERROR EN TOOL: {e}")  # ← temporal, para debug
        return {"error": f"Error ejecutando la consulta: {str(e)}"}


def procesar_mensaje(user, historial, tools_schema):
    system_prompt = (
        "CREACIÓN DE JORNADAS — sigue este proceso paso a paso, como un formulario conversacional:\n"
    "1. Cuando el usuario quiera crear una jornada, llama primero a 'listar_opciones_jornada' "
    "para conocer los sectores, trabajadores y tareas REALES del sistema.\n"
    "2. Pregunta uno o varios datos a la vez (lo que sea natural), mostrando las opciones reales "
    "cuando sea útil (ej: 'tenemos estos sectores: X, Y, Z, ¿cuál es?'). Necesitas: sector, "
    "trabajador, fecha, y al menos una tarea con su horario (hora_inicio y hora_fin, formato HH:MM).\n"
    "3. Puedes preguntar si quiere agregar más de una tarea (hasta 3), y si hay gastos extra "
    "(ej: colación, combustible) con su monto — ambos son opcionales, ofrécelos sin insistir.\n"
    "4. Huerto y lote son opcionales, solo pregúntalos si el usuario los menciona o quiere precisar más.\n"
    "5. Solo cuando tengas sector, trabajador, fecha y al menos una tarea completa, llama a "
    "'proponer_jornada'. Esto le mostrará un resumen con el costo calculado para que confirme.\n"
    "6. Nunca inventes nombres de sectores, trabajadores o tareas — usa siempre los que "
    "'listar_opciones_jornada' te devolvió."
    "7. IMPORTANTE: tú NUNCA creas la jornada directamente ni confirmas su creación en texto. "
    "Solo el botón 'Confirmar' que aparece en el resumen ejecuta la creación real en el sistema. "
    "Si el usuario te dice 'sí', 'confirmo', 'dale' o similar EN TEXTO después de ver el resumen, "
    "NUNCA digas que la jornada fue creada — no lo sabes y no lo has hecho. En su lugar, dile "
    "explícitamente: 'Para crearla de verdad, por favor haz clic en el botón Confirmar que "
    "aparece arriba en el resumen.' Solo el sistema (no tú) confirma el éxito real de la creación."
    )

    accion_pendiente = None
    respuesta = _llamar_claude(historial, tools_schema, system_prompt)

    intentos = 0
    while respuesta.get("stop_reason") == "tool_use" and intentos < 5:
        intentos += 1
        bloques_tool_result = []
        historial.append({"role": "assistant", "content": respuesta["content"]})

        for bloque in respuesta["content"]:
            if bloque["type"] == "tool_use":
                resultado = _ejecutar_tool(bloque["name"], bloque["input"], user)

                if isinstance(resultado, dict) and resultado.get("requiere_confirmacion"):
                    accion_pendiente = resultado

                bloques_tool_result.append({
                    "type": "tool_result",
                    "tool_use_id": bloque["id"],
                    "content": json.dumps(resultado, default=str, ensure_ascii=False),
                })

        historial.append({"role": "user", "content": bloques_tool_result})
        respuesta = _llamar_claude(historial, tools_schema, system_prompt)

    texto_final = next(
        (b["text"] for b in respuesta["content"] if b["type"] == "text"),
        "No pude generar una respuesta."
    )
    return texto_final, accion_pendiente


@login_required
@require_POST
def chat_endpoint(request):
    user = request.user

    if not usuario_tiene_acceso_chat(user.user_type):
        return JsonResponse({"error": "Tu rol aún no tiene acceso al chatbot."}, status=403)

    try:
        data = json.loads(request.body)
        mensaje_usuario = data.get("mensaje", "").strip()
        conversacion_id = data.get("conversacion_id")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    if not mensaje_usuario:
        return JsonResponse({"error": "El mensaje no puede estar vacío"}, status=400)

    if conversacion_id:
        conversacion = ChatConversacion.objects.filter(id=conversacion_id, user=user).first()
        if not conversacion:
            return JsonResponse({"error": "Conversación no encontrada"}, status=404)
    else:
        conversacion = ChatConversacion.objects.create(user=user, titulo=mensaje_usuario[:50])

    ChatMensaje.objects.create(conversacion=conversacion, rol='user', contenido=mensaje_usuario)

    mensajes_previos = conversacion.mensajes.order_by('creado_en')
    historial = [{"role": m.rol, "content": m.contenido} for m in mensajes_previos if m.rol in ('user', 'assistant')]

    tools_schema = filtrar_tools_por_rol(user.user_type)

    try:
        texto_final, accion_pendiente = procesar_mensaje(user, historial, tools_schema)
    except requests.exceptions.HTTPError:
        return JsonResponse({"error": "Error al conectar con el asistente. Intenta de nuevo."}, status=502)

    ChatMensaje.objects.create(conversacion=conversacion, rol='assistant', contenido=texto_final)

    return JsonResponse({
        "respuesta": texto_final,
        "conversacion_id": conversacion.id,
        "accion_pendiente": accion_pendiente,
    })


@login_required
@require_POST
def confirmar_accion(request):
    user = request.user

    if not usuario_puede_ejecutar_accion(user.user_type, "crear_jornada"):
        return JsonResponse({"error": "No tienes permiso para ejecutar esta acción."}, status=403)

    try:
        data = json.loads(request.body)
        accion = data.get("accion")
        detalle = data.get("detalle")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    ejecutor = EJECUTORES_ACCIONES.get(accion)
    if not ejecutor:
        return JsonResponse({"error": f"Acción '{accion}' no reconocida."}, status=400)

    resultado = ejecutor(user, detalle)
    return JsonResponse(resultado)