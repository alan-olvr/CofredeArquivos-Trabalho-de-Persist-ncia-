import hashlib
from pathlib import Path
from typing import Optional
from app.crud import buscar_documentos_por_id
from app.config import carregar_config

def verificar_integridade(id: str) -> Optional[dict]:
    documento = buscar_documentos_por_id(id)

    if not documento:
        return None

    config = carregar_config()
    diretorio = Path(config["diretorio_armazenamento"])
    caminho_arquivo = diretorio / documento.nome_armazenado

    if not caminho_arquivo.exists():
        return {
            "id": documento.id,
            "integro": False,
            "motivo": "Arquivo físico não encontrado",
        }

    conteudo_atual = caminho_arquivo.read_bytes()
    sha256_atual = hashlib.sha256(conteudo_atual).hexdigest()

    return {
        "id": documento.id,
        "integro":  sha256_atual == documento.sha256,
        "sha256_original": documento.sha256,
        "sha256_atual": sha256_atual
    }
