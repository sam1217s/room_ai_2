import sys
import os
import logging

# 👇 Agregar la raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("limpiar_inquilinos")

# Valores por defecto
DEFAULTS = {
    "fumador": "no",
    "mascotas": "sin mascotas",
    "orden": "desordenada",
    "deporte": "no",
    "bioritmo": "madrugador",
    "visitas": "no",
    "personalidad": "indefinido",
    "nivel_educativo": "indefinido",
    "musica_tipo": "indefinido",
    "plan_perfecto": "indefinido",
    "instrumento": "no",
    "rol": "inquilino"
}

def limpiar_inquilinos():
    """
    Analiza todos los documentos en MongoDB e inserta valores por defecto
    donde encuentre null o campos faltantes.
    """
    collection = db_manager.inquilinos_collection
    inquilinos = list(collection.find({}))

    logger.info(f"🔎 Analizando {len(inquilinos)} inquilinos...")

    total_campos_corregidos = 0
    actualizados = 0

    for inq in inquilinos:
        cambios = {}
        for campo, valor_def in DEFAULTS.items():
            if campo not in inq or inq[campo] in (None, "", "null", "None"):
                cambios[campo] = valor_def
        if cambios:
            collection.update_one({"_id": inq["_id"]}, {"$set": cambios})
            actualizados += 1
            total_campos_corregidos += len(cambios)
            logger.info(f"✅ Inquilino {inq.get('id_inquilino')} actualizado con {cambios}")

    logger.info(f"✨ Limpieza completada. {actualizados} inquilinos actualizados.")
    logger.info(f"📊 Total de campos corregidos: {total_campos_corregidos}")

if __name__ == "__main__":
    limpiar_inquilinos()
