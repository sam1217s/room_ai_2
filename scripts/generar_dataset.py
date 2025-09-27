import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from dotenv import load_dotenv
from tqdm import tqdm  # 🔥 Barra de progreso
from app.core.database import DatabaseManager
from app.core.inquilino_schema import generar_inquilino_demo

# Cargar variables del .env
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("generar_dataset_demo")

def main():
    # 🔹 Leer cantidad desde argumento o desde .env
    if len(sys.argv) > 1:
        cantidad = int(sys.argv[1])
    else:
        cantidad = int(os.getenv("DATASET_SIZE", 100))  # default = 100

    db = DatabaseManager()

    # Limpieza de la colección antes de generar datos nuevos
    db.inquilinos_collection.delete_many({})
    logger.info("🧹 Colección limpiada antes de insertar nuevos datos")

    logger.info(f"🎯 Generando {cantidad} inquilinos demo...")

    insertados = 0
    # 🔥 Usamos tqdm para mostrar barra de progreso
    for _ in tqdm(range(cantidad), desc="Progreso", unit="inquilinos"):
        try:
            inquilino = generar_inquilino_demo()
            db.insertar_inquilino(inquilino, log_individual=False)
            insertados += 1
        except Exception as e:
            logger.warning(f"⚠️ Inquilino descartado: {e}")

    logger.info(f"✅ Dataset demo generado exitosamente. Total insertados: {insertados}")

if __name__ == "__main__":
    main()
