# scripts/generar_dataset.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from app.core.database import DatabaseManager
from app.core.inquilino_schema import generar_inquilino_demo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("generar_dataset_demo")

def main():
    if len(sys.argv) < 2:
        logger.error("❌ Debes indicar cuántos inquilinos generar. Ej: python scripts/generar_dataset.py 500")
        sys.exit(1)

    cantidad = int(sys.argv[1])
    db = DatabaseManager()

    # Limpieza de la colección antes de generar datos nuevos
    db.inquilinos_collection.delete_many({})
    logger.info("🧹 Colección limpiada antes de insertar nuevos datos")

    logger.info(f"🎯 Generando {cantidad} inquilinos demo...")
    insertados = 0
    for _ in range(cantidad):
        try:
            inquilino = generar_inquilino_demo()
            db.insertar_inquilino(inquilino)
            insertados += 1
        except Exception as e:
            logger.warning(f"⚠️ Inquilino descartado: {e}")

    logger.info(f"✅ Dataset demo generado exitosamente. Total insertados: {insertados}")

if __name__ == "__main__":
    main()




