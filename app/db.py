from pathlib import Path
import json
from models.documento import Documento

CAMINHO_JSON=Path("storage/metadados.json")

def ler_documentos() -> list[Documento]:
    if not CAMINHO_JSON.exists():
        return []

    with open(CAMINHO_JSON, "r", encoding="utf-8") as arquivo:
        try:
            dados = json.load(arquivo)
        except json.JSONDecodeError:
            return []

    return [Documento.model_validate(item) for item in dados]

def salvar_documentos(documentos: list[Documento]) -> None:
    CAMINHO_JSON.parent.mkdir(parents=True, exist_ok=True)

    dados = [doc.model_dump(mode="json") for doc in documentos]
    with open(CAMINHO_JSON, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=2, ensure_ascii=False)
    
    
    