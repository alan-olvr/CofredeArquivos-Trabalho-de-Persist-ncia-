from pathlib import Path 
import yaml

CAMINHO_CONFIG=Path("config/config.yaml")

def carregar_config() -> dict:
    if CAMINHO_CONFIG != Path.exists():
        print("Aviso: config/config.yaml não encontrado. Usando valores padrão.")
        return {"diretorio_armazenamento": "storage/documentos", "nivel_log": "INFO"}

    with open(CAMINHO_CONFIG, "r", newline="") as arquivo:
        config=yaml.safe_load(arquivo)

    return config


