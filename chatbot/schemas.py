# chatbot/schemas.py

TOOLS_SCHEMA_SENSORES = [
    {
        "name": "ultima_lectura_aire",
        "description": "Obtiene la última lectura de temperatura y humedad de los sensores de aire del usuario. Úsala cuando pregunten cómo está el clima/temperatura ahora mismo en un sector.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector_nombre": {"type": "string", "description": "Nombre del sector a filtrar, ej: 'Norte'. Opcional, si no se especifica trae todos."}
            }
        }
    },
    {
        "name": "ultima_lectura_suelo",
        "description": "Obtiene la última lectura de humedad y temperatura del suelo. Úsala para preguntas sobre estado del suelo o riego actual.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector_nombre": {"type": "string", "description": "Nombre del sector a filtrar. Opcional."}
            }
        }
    },
    {
        "name": "tendencia_humedad_suelo",
        "description": "Calcula si la humedad del suelo está subiendo, bajando o estable en un periodo reciente. Úsala para responder si se necesita regar pronto.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector_nombre": {"type": "string", "description": "Nombre del sector, obligatorio."},
                "horas": {"type": "integer", "description": "Ventana de horas hacia atrás a analizar, por defecto 72."}
            },
            "required": ["sector_nombre"]
        }
    },
    {
        "name": "sensores_sin_datos_recientes",
        "description": "Lista sensores que llevan tiempo sin reportar datos, indicando posible falla o desconexión. Úsala cuando pregunten por alertas o estado general de los sensores.",
        "input_schema": {
            "type": "object",
            "properties": {
                "horas": {"type": "integer", "description": "Umbral en horas para considerar un sensor como 'sin datos recientes', por defecto 6."}
            }
        }
    },
    
    {
        "name": "historico_aire",
        "description": "Obtiene un resumen estadístico (promedio, máximo, mínimo) de las lecturas de un sensor de aire específico en un rango de fechas. Úsala cuando pregunten por datos históricos de un sensor entre dos fechas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sensor_nombre": {"type": "string", "description": "Nombre o parte del nombre del sensor de aire, ej: 'nodo aire 01'."},
                "fecha_inicio": {"type": "string", "description": "Fecha de inicio en formato YYYY-MM-DD."},
                "fecha_fin": {"type": "string", "description": "Fecha de fin en formato YYYY-MM-DD."}
            },
            "required": ["sensor_nombre", "fecha_inicio", "fecha_fin"]
        }
    },
    {
        "name": "historico_suelo",
        "description": "Obtiene un resumen estadístico (promedio, máximo, mínimo) de las lecturas de un sensor de suelo específico en un rango de fechas. Úsala cuando pregunten por datos históricos de un sensor entre dos fechas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sensor_nombre": {"type": "string", "description": "Nombre o parte del nombre del sensor de suelo, ej: 'nodo suelo 01'."},
                "fecha_inicio": {"type": "string", "description": "Fecha de inicio en formato YYYY-MM-DD."},
                "fecha_fin": {"type": "string", "description": "Fecha de fin en formato YYYY-MM-DD."}
            },
            "required": ["sensor_nombre", "fecha_inicio", "fecha_fin"]
        }
    },
]

TOOLS_SCHEMA_CLIMA = [
    {
        "name": "clima_actual",
        "description": "Obtiene el clima actual (temperatura, humedad, condición) de un sector específico, basado en sus coordenadas reales. Úsala cuando pregunten cómo está el clima/tiempo ahora mismo en un sector.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector_nombre": {"type": "string", "description": "Nombre del sector, ej: 'Norte'."}
            },
            "required": ["sector_nombre"]
        }
    },
    {
        "name": "clima_pronostico",
        "description": "Obtiene el pronóstico del clima de los próximos días (hasta 5) para un sector, incluyendo temperaturas y estimación de lluvia. Úsala para preguntas sobre el clima futuro o si se necesita regar según lluvia esperada.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector_nombre": {"type": "string", "description": "Nombre del sector, ej: 'Norte'."}
            },
            "required": ["sector_nombre"]
        }
    },
]
TOOLS_SCHEMA_ACCIONES = [
    {
        "name": "proponer_jornada",
        "description": "Prepara una propuesta de jornada laboral (NO la crea, solo la propone para confirmación). Úsala cuando el usuario pida crear/agendar una jornada o tarea para un trabajador.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector_nombre": {"type": "string", "description": "Nombre del sector donde se realizará la jornada."},
                "trabajador_nombre": {"type": "string", "description": "Nombre del trabajador a asignar."},
                "tarea": {"type": "string", "description": "Tipo de tarea, ej: 'poda', 'riego', 'cosecha'."},
                "fecha": {"type": "string", "description": "Fecha en formato YYYY-MM-DD."}
            },
            "required": ["sector_nombre", "trabajador_nombre", "tarea", "fecha"]
        }
    },
]
TOOLS_SCHEMA_RECOMENDACION = [
    {
        "name": "resumen_sector",
        "description": "Obtiene un panorama completo de un sector: histórico reciente de sus sensores de suelo (pasado) más el pronóstico del clima (futuro). Úsala SIEMPRE que te pidan una recomendación sobre un sector, o un resumen combinado de cómo ha estado y cómo estará el clima/suelo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector_nombre": {"type": "string", "description": "Nombre del sector, ej: 'Invernadero'."},
                "dias_historial": {"type": "integer", "description": "Cuántos días hacia atrás revisar en el histórico de sensores, por defecto 7."}
            },
            "required": ["sector_nombre"]
        }
    },
]
TOOLS_SCHEMA_ACCIONES = [
    {
        "name": "listar_opciones_jornada",
        "description": "Obtiene las opciones reales disponibles para crear una jornada: sectores, trabajadores y tareas válidas del sistema. Úsala al INICIO de cualquier creación de jornada, antes de preguntar nada, para ofrecer opciones reales en vez de adivinar nombres.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector_nombre": {"type": "string", "description": "Si ya se sabe el sector, filtra también los huertos de ese sector. Opcional."}
            }
        }
    },
    {
        "name": "proponer_jornada",
        "description": "Prepara una propuesta de jornada COMPLETA para confirmación del usuario. Solo llama esta tool cuando ya tengas TODOS los datos obligatorios reunidos conversando: sector, trabajador, fecha, y al menos una tarea con su horario. No inventes ningún dato, pregunta lo que falte antes de llamarla.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector_nombre": {"type": "string", "description": "Nombre del sector."},
                "trabajador_nombre": {"type": "string", "description": "Nombre del trabajador a asignar."},
                "fecha": {"type": "string", "description": "Fecha en formato YYYY-MM-DD."},
                "tareas": {
                    "type": "array",
                    "description": "Lista de 1 a 3 tareas a realizar, cada una con su horario.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "tarea": {"type": "string", "description": "Nombre de la tarea, debe coincidir con una de las tareas_disponibles."},
                            "hora_inicio": {"type": "string", "description": "Hora de inicio, formato HH:MM."},
                            "hora_fin": {"type": "string", "description": "Hora de término, formato HH:MM."}
                        },
                        "required": ["tarea", "hora_inicio", "hora_fin"]
                    }
                },
                "huerto_nombre": {"type": "string", "description": "Nombre del huerto dentro del sector. Opcional."},
                "lote_nombre": {"type": "string", "description": "Nombre del lote. Opcional."},
                "extras": {
                    "type": "array",
                    "description": "Gastos extra opcionales (máx 3), ej: colación, combustible, con su monto.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "nombre": {"type": "string"},
                            "monto": {"type": "number"}
                        },
                        "required": ["nombre", "monto"]
                    }
                },
                "observacion": {"type": "string", "description": "Observación adicional opcional."}
            },
            "required": ["sector_nombre", "trabajador_nombre", "fecha", "tareas"]
        }
    },
]