# chatbot/permisos.py

from .registry import TOOLS_REGISTRY, TOOLS_SCHEMA_TOTAL

PERMISOS_CHAT = {
    'admin': {
        'consultar': '*',
        'accion': '*',
    },
    'superuser':   {'consultar': [], 'accion': []},
    'agricultor':  {'consultar': [], 'accion': []},
    'colaborador': {'consultar': [], 'accion': []},
    'ayudante':    {'consultar': [], 'accion': []},
}


def usuario_puede_consultar(user_type, categoria):
    permisos = PERMISOS_CHAT.get(user_type, {})
    consultar = permisos.get('consultar', [])
    return consultar == '*' or categoria in consultar


def usuario_puede_ejecutar_accion(user_type, accion):
    permisos = PERMISOS_CHAT.get(user_type, {})
    acciones = permisos.get('accion', [])
    return acciones == '*' or accion in acciones


def usuario_tiene_acceso_chat(user_type):
    permisos = PERMISOS_CHAT.get(user_type, {})
    consultar = permisos.get('consultar', [])
    return consultar == '*' or len(consultar) > 0


def filtrar_tools_por_rol(user_type):
    schema_filtrado = []
    for tool_schema in TOOLS_SCHEMA_TOTAL:
        nombre = tool_schema["name"]
        categoria = TOOLS_REGISTRY[nombre]["categoria"]
        if usuario_puede_consultar(user_type, categoria):
            schema_filtrado.append(tool_schema)
    return schema_filtrado