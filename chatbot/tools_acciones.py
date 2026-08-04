# chatbot/tools_acciones.py

import unicodedata
from datetime import datetime, time as time_type
from agrosmartiotweb.models import Sector, Trabajador, Huerto, Lote, Jornada

# Copia exacta de las opciones de tu modelo Jornada
MANODEOBRACHOICES = [
    ('PODA', 'Poda'),
    ('DESHOJE', 'Deshoje (sacar hojas)'),
    ('DESBROTE', 'Desbrote'),
    ('PESTICIDAS', 'Aplicación de pesticidas'),
    ('FERTILIZANTES', 'Aplicación de fertilizantes'),
    ('COSECHA', 'Cosecha'),
    ('AMARRE_GUIAS', 'Amarre de guías'),
    ('LIMPIEZA_MALEZA', 'Limpieza de maleza'),
    ('RIEGO', 'Riego'),
    ('PREPARACION_SUELO', 'Preparación del suelo'),
    ('PLANTACION', 'Plantación de cultivos'),
    ('ABONADO', 'Abonado'),
    ('LABRANZA', 'Labranza'),
    ('CONTROL_PLAGAS', 'Control manual de plagas'),
    ('DESINFECCION_SUELOS', 'Desinfección de suelos'),
    ('MONITOREO_CULTIVOS', 'Monitoreo de cultivos'),
    ('INSTALACION_RIEGO', 'Instalación de sistemas de riego'),
    ('RECOLECCION_RESIDUOS', 'Recolección de residuos'),
    ('INSTALACION_TUTORES', 'Instalación de tutores'),
    ('PODA_FORMACION', 'Poda de formación'),
    ('PODA_MANTENIMIENTO', 'Poda de mantenimiento'),
    ('ENTRESACADO_FRUTOS', 'Entresacado de frutos'),
    ('REPARACION_CERCAS', 'Reparación de cercas'),
    ('INSTALACION_RED_PROTECCION', 'Instalación de redes de protección'),
    ('MANEJO_POST_COSECHA', 'Manejo post-cosecha'),
    ('CLASIFICACION_UVAS', 'Clasificación de uvas'),
    ('TRANSPORTE_CARGA', 'Transporte de carga'),
    ('MANTENIMIENTO_MAQUINARIA', 'Mantenimiento de maquinaria'),
    ('REPLANTE_PLANTAS', 'Replante de plantas'),
    ('ACARREO_INSUMOS', 'Acarreo de insumos'),
    ('MANTENIMIENTO_RIEGO', 'Mantenimiento de sistemas de riego'),
    ('CONTROL_EROSION', 'Control de erosión'),
    ('CUBIERTA_ORGANICA', 'Colocación de cubierta orgánica'),
    ('APLICACION_BIOESTIMULANTES', 'Aplicación de bioestimulantes'),
    ('FERTIRRIGACION', 'Fertirrigación'),
    ('INSTALACION_SOMBREADO', 'Instalación de sistemas de sombreado'),
    ('DESINFECCION_HERRAMIENTAS', 'Desinfección de herramientas'),
    ('CAPACITACION_PERSONAL', 'Capacitación del personal'),
]


def _quitar_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')


def _normalizar_tarea(texto):
    return _quitar_acentos(texto).lower().strip()


def _match_tarea(texto):
    """Compara el texto libre del usuario contra código y etiqueta de cada tarea válida."""
    objetivo = _normalizar_tarea(texto)
    for codigo, label in MANODEOBRACHOICES:
        if objetivo == _normalizar_tarea(codigo) or objetivo == _normalizar_tarea(label):
            return codigo
    for codigo, label in MANODEOBRACHOICES:
        label_norm = _normalizar_tarea(label)
        if objetivo in label_norm or label_norm in objetivo:
            return codigo
    return None


def _parsear_fecha_simple(fecha_str):
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _parsear_hora_simple(hora_str, default=None):
    if not hora_str:
        return default
    try:
        h, m = map(int, hora_str.split(":"))
        return time_type(h, m)
    except (ValueError, AttributeError):
        return default


def _calcular_cobro_tarea(hora_inicio, hora_fin, cobro_por_hora):
    """Misma fórmula que usa tu JornadaForm.save(): horas trabajadas × tarifa/hora del trabajador."""
    if hora_inicio and hora_fin and cobro_por_hora:
        hi = hora_inicio.hour + hora_inicio.minute / 60
        hf = hora_fin.hour + hora_fin.minute / 60
        horas = hf - hi
        return round(horas * float(cobro_por_hora), 2)
    return None


def tool_listar_opciones_jornada(user, sector_nombre=None):
    """
    Devuelve las opciones REALES disponibles para crear una jornada: sectores, trabajadores
    y tareas válidas. Úsala al INICIO de una creación de jornada para presentarle al usuario
    las opciones existentes, en vez de adivinar nombres.
    """
    sectores = list(Sector.objects.filter(user=user).values_list('nombre', flat=True))
    trabajadores = list(Trabajador.objects.filter(user=user).values_list('nombre', flat=True))
    tareas = [label for _, label in MANODEOBRACHOICES]

    resultado = {
        "sectores": sectores,
        "trabajadores": trabajadores,
        "tareas_disponibles": tareas,
    }

    if sector_nombre:
        sector = Sector.objects.filter(user=user, nombre__icontains=sector_nombre).first()
        if sector:
            resultado["huertos_del_sector"] = list(
                Huerto.objects.filter(user=user, sector=sector).values_list('nombre', flat=True)
            )

    return resultado


def tool_proponer_jornada(user, sector_nombre, trabajador_nombre, fecha, tareas,
                           huerto_nombre=None, lote_nombre=None, extras=None, observacion=None):
    """
    Prepara una PROPUESTA de jornada completa (hasta 3 tareas, cada una con su horario;
    hasta 3 extras opcionales) para que el usuario la confirme. NO guarda nada todavía.
    'tareas' es una lista de objetos {tarea, hora_inicio, hora_fin}, 1 a 3 elementos.
    'extras' es una lista de objetos {nombre, monto}, hasta 3 elementos, opcional.
    """
    if not tareas or len(tareas) < 1:
        return {"mensaje": "Debes especificar al menos una tarea con su horario."}
    if len(tareas) > 3:
        return {"mensaje": "Solo se pueden registrar hasta 3 tareas por jornada."}

    sector = Sector.objects.filter(user=user, nombre__icontains=sector_nombre).first()
    if not sector:
        return {"mensaje": f"No se encontró el sector '{sector_nombre}'."}

    trabajador = Trabajador.objects.filter(user=user, nombre__icontains=trabajador_nombre).first()
    if not trabajador:
        return {"mensaje": f"No se encontró un trabajador llamado '{trabajador_nombre}'."}

    fecha_parseada = _parsear_fecha_simple(fecha)
    if not fecha_parseada:
        return {"mensaje": "No pude interpretar la fecha, usa formato YYYY-MM-DD."}

    huerto = None
    if huerto_nombre:
        huerto = Huerto.objects.filter(user=user, nombre__icontains=huerto_nombre, sector=sector).first()
        if not huerto:
            return {"mensaje": f"No se encontró el huerto '{huerto_nombre}' en el Sector {sector.nombre}."}

    lote = None
    if lote_nombre:
        lote = Lote.objects.filter(user=user, nombre__icontains=lote_nombre).first()
        if not lote:
            return {"mensaje": f"No se encontró el lote '{lote_nombre}'."}

    tareas_procesadas = []
    for t in tareas:
        codigo = _match_tarea(t.get("tarea", ""))
        if not codigo:
            return {"mensaje": f"'{t.get('tarea')}' no es una tarea reconocida. Usa 'listar_opciones_jornada' para ver las opciones válidas."}

        hi = _parsear_hora_simple(t.get("hora_inicio"))
        hf = _parsear_hora_simple(t.get("hora_fin"))
        if not hi or not hf:
            return {"mensaje": f"Falta un horario válido (HH:MM) para la tarea '{t.get('tarea')}'."}

        cobro = _calcular_cobro_tarea(hi, hf, trabajador.cobro)
        tareas_procesadas.append({
            "codigo": codigo,
            "hora_inicio": hi.strftime("%H:%M"),
            "hora_fin": hf.strftime("%H:%M"),
            "cobro": cobro,
        })

    extras_procesados = []
    if extras:
        if len(extras) > 3:
            return {"mensaje": "Solo se pueden registrar hasta 3 gastos extra."}
        for e in extras:
            nombre_extra = e.get("nombre")
            monto = e.get("monto")
            if nombre_extra and monto is not None:
                extras_procesados.append({"nombre": nombre_extra, "monto": monto})

    total_tareas = sum(t["cobro"] or 0 for t in tareas_procesadas)
    total_extras = sum(e["monto"] or 0 for e in extras_procesados)
    total_general = total_tareas + total_extras

    resumen_tareas = ", ".join(f"{t['codigo']} ({t['hora_inicio']}-{t['hora_fin']})" for t in tareas_procesadas)
    resumen = (
        f"Jornada para {trabajador.nombre} en el Sector {sector.nombre}, el {fecha_parseada}. "
        f"Tareas: {resumen_tareas}. Gasto estimado: ${total_general:,.0f}"
    )
    if extras_procesados:
        resumen += f" (extras: {', '.join(e['nombre'] for e in extras_procesados)})"
    if not trabajador.cobro:
        resumen += " ⚠️ El trabajador no tiene tarifa/hora configurada, el cobro quedará en blanco."

    return {
        "requiere_confirmacion": True,
        "accion": "crear_jornada",
        "resumen": resumen,
        "detalle": {
            "sector_id": sector.id,
            "trabajador_id": trabajador.id,
            "huerto_id": huerto.id if huerto else None,
            "lote_id": lote.id if lote else None,
            "fecha": str(fecha_parseada),
            "tareas": tareas_procesadas,
            "extras": extras_procesados,
            "observacion": observacion,
        }
    }


def ejecutar_creacion_jornada(user, detalle):
    """Esta función SÍ guarda en la base de datos. Solo se llama tras confirmación explícita."""
    sector = Sector.objects.filter(id=detalle["sector_id"], user=user).first()
    trabajador = Trabajador.objects.filter(id=detalle["trabajador_id"], user=user).first()
    if not sector or not trabajador:
        return {"error": "Sector o trabajador ya no existen."}

    huerto = Huerto.objects.filter(id=detalle["huerto_id"], user=user).first() if detalle.get("huerto_id") else None
    lote = Lote.objects.filter(id=detalle["lote_id"], user=user).first() if detalle.get("lote_id") else None

    campos = {
        "user": user,
        "created_by": user,
        "sector": sector,
        "huerto": huerto,
        "lote": lote,
        "asignado": trabajador,
        "fecha": detalle["fecha"],
        "observacion": detalle.get("observacion") or None,
    }

    tareas = detalle.get("tareas", [])
    detalle_gasto_tareas = 0
    for i, t in enumerate(tareas[:3], start=1):
        hi = _parsear_hora_simple(t["hora_inicio"], time_type(8, 0))
        hf = _parsear_hora_simple(t["hora_fin"], time_type(17, 0))
        campos[f"nombre_tarea_{i}"] = t["codigo"]
        campos[f"hora_inicio_tarea_{i}"] = hi
        campos[f"hora_fin_tarea_{i}"] = hf
        campos[f"cobro_tarea_{i}"] = t["cobro"]
        detalle_gasto_tareas += t["cobro"] or 0

    extras = detalle.get("extras", [])
    detalle_gastos_extras = 0
    for i, e in enumerate(extras[:3], start=1):
        campos[f"nombre_extra_{i}"] = e["nombre"]
        campos[f"gasto_extra_{i}"] = e["monto"]
        detalle_gastos_extras += e["monto"] or 0

    campos["detalle_gasto_total_tareas"] = detalle_gasto_tareas
    campos["detalle_gastos_total_extras"] = detalle_gastos_extras
    campos["total_gasto_jornada"] = detalle_gasto_tareas + detalle_gastos_extras

    jornada = Jornada.objects.create(**campos)
    return {"exito": True, "jornada_id": jornada.id, "mensaje": "Jornada creada correctamente."}