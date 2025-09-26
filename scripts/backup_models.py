# scripts/backup_models.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import shutil
import logging
from datetime import datetime
from app.core.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backup_models")

def main():
    src = config.MODEL_PATH
    dst = os.path.join(config.BACKUP_PATH, f"models_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    os.makedirs(dst, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True)

    logger.info(f"✅ Backup completado en {dst}")

if __name__ == "__main__":
    main()

