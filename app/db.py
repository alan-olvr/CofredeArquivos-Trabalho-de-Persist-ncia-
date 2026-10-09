from pathlib import Path
import json
from pydantic import ValidationError
from app.logger import logger
from models.documento import Documento

CAMINHO_JSON = Path("storage/metadados.json")


class MetadadosInvalidosError(Exception):
    """O arquivo de metadados está corrompido ou fora do formato esperado."""


def ler_documentos() -> list[Documento]:
    if not CAMINHO_JSON.exists() or CAMINHO_JSON.stat().st_size == 0:
        return []
    try:
        with open(CAMINHO_JSON, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        return [Documento.model_validate(item) for item in dados]
    except (json.JSONDecodeError, ValidationError, TypeError) as erro:
        logger.error(f"Metadados inválidos em {CAMINHO_JSON}: {erro}")
        raise MetadadosInvalidosError(str(erro)) from erro


def salvar_documentos(documentos: list[Documento]) -> None:
    CAMINHO_JSON.parent.mkdir(parents=True, exist_ok=True)
    dados = [doc.model_dump(mode="json") for doc in documentos]
    with open(CAMINHO_JSON, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=2, ensure_ascii=False)