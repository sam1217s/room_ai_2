# scripts/entrenar_modelo_completo.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from app.core.ia_engine import MotorIA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("entrenar_modelo_completo")

def main():
    logger.info("🚀 Entrenamiento completo iniciado...")
    motor = MotorIA()
    metricas = motor.entrenar_modelo_completo()

    logger.info("📊 Métricas del modelo:")
    for k, v in metricas.items():
        if isinstance(v, (int, float)):
            logger.info(f"   {k}: {v:.3f}")
        else:
            logger.info(f"   {k}: {v}")

    logger.info("✅ Entrenamiento completo finalizado")

if __name__ == "__main__":
    main()
