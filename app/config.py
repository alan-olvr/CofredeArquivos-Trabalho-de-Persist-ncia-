from pathlib import Path
import yaml

CAMINHO_CONFIG = Path("config/config.yaml")
VALORES_PADRAO = {"diretorio_armazenamento": "storage/documentos", "nivel_log": "INFO"}


def carregar_config() -> dict:
    if not CAMINHO_CONFIG.exists():
        print("Aviso: config/config.yaml não encontrado. Usando valores padrão.")
        return dict(VALORES_PADRAO)
    try:
        with open(CAMINHO_CONFIG, "r", encoding="utf-8") as arquivo:
            config = yaml.safe_load(arquivo)
    except (yaml.YAMLError, OSError):
        print("Aviso: config/config.yaml inválido. Usando valores padrão.")
        return dict(VALORES_PADRAO)
    if not isinstance(config, dict):
        print("Aviso: config/config.yaml vazio ou inválido. Usando valores padrão.")
        return dict(VALORES_PADRAO)
    return {**VALORES_PADRAO, **config}