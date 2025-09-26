# app/core/config.py
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    """Configuración central de RoomMatchAI"""

    # Base de datos
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB: str = os.getenv("MONGO_DB", "roommatch")
    MONGO_COLLECTION: str = os.getenv("MONGO_COLLECTION", "inquilinos")

    # Modelos
    MODEL_PATH: str = os.getenv("MODEL_PATH", "models/")

    # Parámetros de entrenamiento IA
    N_ESTIMATORS: int = int(os.getenv("N_ESTIMATORS", 100))
    MAX_DEPTH: int = int(os.getenv("MAX_DEPTH", 10))
    TEST_SIZE: float = float(os.getenv("TEST_SIZE", 0.2))
    CV_FOLDS: int = int(os.getenv("CV_FOLDS", 5))

    # Rendimiento
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", 3600))
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", 4))

    # Debug / Logs
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Streamlit
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", 8501))
    STREAMLIT_HOST: str = os.getenv("STREAMLIT_HOST", "0.0.0.0")

    # Business rules
    ALTA_COMPATIBILIDAD: float = float(os.getenv("ALTA_COMPATIBILIDAD", 80.0))
    MEDIA_COMPATIBILIDAD: float = float(os.getenv("MEDIA_COMPATIBILIDAD", 60.0))
    BAJA_COMPATIBILIDAD: float = float(os.getenv("BAJA_COMPATIBILIDAD", 40.0))

    MIN_ACCURACY: float = float(os.getenv("MIN_ACCURACY", 0.85))
    MIN_F1_SCORE: float = float(os.getenv("MIN_F1_SCORE", 0.80))
    MIN_CROSS_VAL: float = float(os.getenv("MIN_CROSS_VAL", 0.75))

    # Backups
    BACKUP_PATH: str = os.getenv("BACKUP_PATH", "backups/")
    AUTO_BACKUP_HOURS: int = int(os.getenv("AUTO_BACKUP_HOURS", 24))
    MAX_BACKUP_FILES: int = int(os.getenv("MAX_BACKUP_FILES", 10))
    
    # Ética y Sesgos
    BIAS_MONITORING_ENABLED: bool = os.getenv("BIAS_MONITORING_ENABLED", "true").lower() == "true"
    DEMOGRAPHIC_PARITY_THRESHOLD: float = float(os.getenv("DEMOGRAPHIC_PARITY_THRESHOLD", 0.1))
    EQUALIZED_ODDS_THRESHOLD: float = float(os.getenv("EQUALIZED_ODDS_THRESHOLD", 0.1))
    SELECTION_RATE_THRESHOLD: float = float(os.getenv("SELECTION_RATE_THRESHOLD", 0.15))
    ETHICS_SCORE_MINIMUM: float = float(os.getenv("ETHICS_SCORE_MINIMUM", 80.0))

    # Explicabilidad
    SHAP_EXPLAINER_TYPE: str = os.getenv("SHAP_EXPLAINER_TYPE", "tree")
    EXPLANATION_MAX_FEATURES: int = int(os.getenv("EXPLANATION_MAX_FEATURES", 10))
    HUMAN_EXPLANATIONS_ENABLED: bool = os.getenv("HUMAN_EXPLANATIONS_ENABLED", "true").lower() == "true"

    # Azure Deploy
    AZURE_CONTAINER_APP: str = os.getenv("AZURE_CONTAINER_APP", "roommatchai-app")
    AZURE_RESOURCE_GROUP: str = os.getenv("AZURE_RESOURCE_GROUP", "senasoft-2025")
    AZURE_CONTAINER_REGISTRY: str = os.getenv("AZURE_CONTAINER_REGISTRY", "senasoft2025.azurecr.io")

    # Monitoreo
    HEALTH_CHECK_ENABLED: bool = os.getenv("HEALTH_CHECK_ENABLED", "true").lower() == "true"
    PREDICTION_LOGGING_ENABLED: bool = os.getenv("PREDICTION_LOGGING_ENABLED", "true").lower() == "true"

# Instancia global de configuración
config = Config()
