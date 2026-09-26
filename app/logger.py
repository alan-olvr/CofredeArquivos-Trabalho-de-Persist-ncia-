import logging
from pathlib import Path
from app.config import carregar_config

def configurar_logger() -> logging.Logger:
    config = carregar_config()
    nivel = config.get("nivel_log", "INFO")

    diretorio_logs = Path("storage/logs")
    diretorio_logs.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("cofre_digital")
    logger.setLevel(nivel)

    if not logger.handlers:
        handler = logging.FileHandler(diretorio_logs/"app.log", encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

logger = configurar_logger()