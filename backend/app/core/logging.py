import logging
import os
from logging.handlers import RotatingFileHandler
from app.core.config import settings

def setup_logging():
    os.makedirs(settings.LOGS_DIR, exist_ok=True)
    log_file = os.path.join(settings.LOGS_DIR, "rag_app.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("rag_app")
