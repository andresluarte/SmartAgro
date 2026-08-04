from .tools_sensores import (
    tool_ultima_lectura_aire,
    tool_ultima_lectura_suelo,
    tool_tendencia_humedad_suelo,
    tool_sensores_sin_datos_recientes,
    tool_historico_aire,
    tool_historico_suelo,
)
from .tools_clima import tool_clima_actual, tool_clima_pronostico

from .tools_recomendacion import tool_resumen_sector
from .schemas import TOOLS_SCHEMA_SENSORES, TOOLS_SCHEMA_CLIMA, TOOLS_SCHEMA_ACCIONES,TOOLS_SCHEMA_RECOMENDACION
from .tools_acciones import tool_proponer_jornada, tool_listar_opciones_jornada
TOOLS_REGISTRY = {
    "ultima_lectura_aire":          {"funcion": tool_ultima_lectura_aire,          "categoria": "sensores"},
    "ultima_lectura_suelo":         {"funcion": tool_ultima_lectura_suelo,         "categoria": "sensores"},
    "tendencia_humedad_suelo":      {"funcion": tool_tendencia_humedad_suelo,      "categoria": "sensores"},
    "sensores_sin_datos_recientes": {"funcion": tool_sensores_sin_datos_recientes, "categoria": "sensores"},
    "historico_aire":               {"funcion": tool_historico_aire,               "categoria": "sensores"},
    "historico_suelo":              {"funcion": tool_historico_suelo,              "categoria": "sensores"},
    "clima_actual":                 {"funcion": tool_clima_actual,                 "categoria": "clima"},
    "clima_pronostico":             {"funcion": tool_clima_pronostico,             "categoria": "clima"},
    "proponer_jornada":             {"funcion": tool_proponer_jornada,             "categoria": "acciones"},
    "resumen_sector":               {"funcion": tool_resumen_sector, "categoria": "clima"},
    "listar_opciones_jornada":      {"funcion": tool_listar_opciones_jornada,      "categoria": "acciones"},
}

TOOLS_SCHEMA_TOTAL = TOOLS_SCHEMA_SENSORES + TOOLS_SCHEMA_CLIMA + TOOLS_SCHEMA_ACCIONES + TOOLS_SCHEMA_RECOMENDACION