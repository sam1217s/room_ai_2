import logging
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv
import os

load_dotenv()
logger = logging.getLogger("app.core.database")

class DatabaseManager:
    def __init__(self):
        try:
            self.client = MongoClient(os.getenv("MONGO_URI"))
            self.db = self.client[os.getenv("MONGO_DB")]
            self.inquilinos_collection = self.db[os.getenv("MONGO_COLLECTION")]

            # Crear índices
            self.inquilinos_collection.create_index([("id_inquilino", ASCENDING)], unique=True)
            logger.info("📇 Índices creados exitosamente")
            logger.info(f"✅ Conectado a MongoDB: {os.getenv('MONGO_DB')}.{os.getenv('MONGO_COLLECTION')}")
        except Exception as e:
            logger.error(f"❌ Error conectando a MongoDB: {e}")

    def insertar_inquilino(self, inquilino, log_individual=False):
        try:
            if not isinstance(inquilino, dict):
                inquilino = inquilino.dict()

            self.inquilinos_collection.insert_one(inquilino)

            if log_individual:
                logger.info(f"✅ Inquilino insertado: {inquilino.get('nombre')}")
        except Exception as e:
            logger.error(f"❌ Error insertando inquilino: {e}")

    def buscar_inquilino(self, filtro):
        try:
            return self.inquilinos_collection.find_one(filtro)
        except Exception as e:
            logger.error(f"❌ Error buscando inquilino: {e}")
            return None

    def obtener_todos_inquilinos(self):
        """🔹 Devuelve todos los inquilinos de la colección"""
        try:
            return list(self.inquilinos_collection.find({}))
        except Exception as e:
            logger.error(f"❌ Error obteniendo inquilinos: {e}")
            return []

    def limpiar_inquilinos(self):
        try:
            self.inquilinos_collection.delete_many({})
            logger.info("🧹 Colección limpiada correctamente")
        except Exception as e:
            logger.error(f"❌ Error limpiando colección: {e}")

# ✅ Instancia global para usar directo en otros módulos
db_manager = DatabaseManager()
