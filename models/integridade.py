import hashlib
from pathlib import Path
from typing import Optional
from app.crud import buscar_documentos_por_id
from app.config import carregar_config
from app.db import ler_documentos

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

def verificar_integridade_global() -> dict:
    documentos = ler_documentos()

    verificados = 0
    integros = 0
    alterados = 0
    nao_localizados = 0

    for doc in documentos:
        resultado = verificar_integridade(doc.id)
        verificados += 1

        if "motivo" in resultado:
            nao_localizados += 1
        elif resultado["integro"]:
            integros += 1
        else:
            alterados += 1

    return {
        "total_verificados": verificados,
        "integros": integros,
        "alterados": alterados,
        "nao_localizados": nao_localizados,
    }