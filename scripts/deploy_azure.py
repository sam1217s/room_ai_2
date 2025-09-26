# scripts/deploy_azure.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import subprocess
from app.core.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deploy_azure")

def main():
    logger.info("🚀 Iniciando despliegue en Azure...")

    try:
        # Verificar si las variables están configuradas
        if not hasattr(config, 'AZURE_CONTAINER_APP'):
            logger.error("❌ Variables Azure no configuradas en .env")
            return

        subprocess.run([
            "az", "containerapp", "update",
            "--name", config.AZURE_CONTAINER_APP,
            "--resource-group", config.AZURE_RESOURCE_GROUP,
            "--image", f"{config.AZURE_CONTAINER_REGISTRY}.azurecr.io/roommatchai:latest"
        ], check=True)

        logger.info("✅ Despliegue en Azure completado")

    except Exception as e:
        logger.error(f"❌ Error en despliegue: {e}")

if __name__ == "__main__":
    main()