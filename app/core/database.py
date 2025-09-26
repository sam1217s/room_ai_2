# app/core/database.py
import logging
from pymongo import MongoClient, ASCENDING
from .config import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor de conexión y operaciones en MongoDB"""

    def __init__(self):
        try:
            self.client = MongoClient(config.MONGO_URI)
            self.db = self.client[config.MONGO_DB]
            self.inquilinos_collection = self.db[config.MONGO_COLLECTION]
            self._crear_indices()
            logger.info(f"✅ Conectado a MongoDB: {config.MONGO_DB}.{config.MONGO_COLLECTION}")
        except Exception as e:
            logger.error(f"❌ Error conectando a MongoDB: {e}")
            raise

    def _crear_indices(self):
        """Crea índices para optimizar consultas"""
        try:
            self.inquilinos_collection.create_index([("nombre", ASCENDING)])
            self.inquilinos_collection.create_index([("edad", ASCENDING)])
            logger.info("📇 Índices creados exitosamente")
        except Exception as e:
            logger.warning(f"⚠️ Error creando índices: {e}")

    # CRUD ==============================
    def insertar_inquilino(self, inquilino: dict) -> str:
        """Inserta un nuevo inquilino"""
        try:
            result = self.inquilinos_collection.insert_one(inquilino)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"❌ Error insertando inquilino: {e}")
            return None

    def obtener_todos_inquilinos(self) -> list:
        """Devuelve todos los inquilinos"""
        try:
            return list(self.inquilinos_collection.find())
        except Exception as e:
            logger.error(f"❌ Error obteniendo inquilinos: {e}")
            return []

    def obtener_estadisticas_db(self) -> dict:
        """Estadísticas rápidas de la base de datos"""
        try:
            total = self.inquilinos_collection.count_documents({})
            fumadores = self.inquilinos_collection.count_documents({"fumador": "si"})
            mascotas = self.inquilinos_collection.count_documents({"mascotas": "con mascotas"})
            return {
                "total_inquilinos": total,
                "fumadores": fumadores,
                "con_mascotas": mascotas
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}

# Instancia global
db_manager = DatabaseManager()

# Alias para facilitar importaciones
insertar_inquilino = db_manager.insertar_inquilino
obtener_todos_inquilinos = db_manager.obtener_todos_inquilinos
obtener_estadisticas_db = db_manager.obtener_estadisticas_db
