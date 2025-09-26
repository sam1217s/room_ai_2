# scripts/entrenar_modelo.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from app.core.ia_engine import MotorIA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("entrenar_modelo")

def main():
    logger.info("🚀 Entrenando modelo básico de compatibilidad...")
    motor = MotorIA()
    resultado = motor.entrenar_modelo_completo()
    logger.info("✅ Modelo entrenado y guardado en /models")
    logger.info(f"Métricas: {resultado}")

if __name__ == "__main__":
    main()