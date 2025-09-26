# scripts/probar_prediccion.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from app.core.ia_engine import MotorIA
from app.core.inquilino_schema import generar_inquilino_demo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("probar_prediccion")

def main():
    logger.info("🚀 Cargando modelo entrenado...")
    motor = MotorIA()
    motor.cargar_modelos()

    # Generar un inquilino de prueba
    inquilino_demo = generar_inquilino_demo()
    logger.info(f"🧑 Inquilino demo generado: {inquilino_demo}")

    # Realizar predicción usando explicabilidad
    if motor.is_trained:
        explicacion = motor.obtener_explicacion_prediccion(inquilino_demo)
        logger.info(f"🔮 Resultado predicción: {explicacion}")
    else:
        logger.warning("⚠️ Modelo no entrenado")

if __name__ == "__main__":
    main()
