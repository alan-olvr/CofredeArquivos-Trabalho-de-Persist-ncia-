import zipfile
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from models.documento import Equipamento, Experimento
from app.crud import buscar_documentos
from app.config import carregar_config

def criar_backup_seletivo(
    equipamento: Optional[Equipamento] = None,
    experimento: Optional[Experimento] = None,
) -> Path:
    if equipamento is None and experimento is None:
        raise ValueError("É necessário informar equipamento ou experimento.")

    if equipamento is not None and experimento is not None:
        raise ValueError("Informe apenas equipamento ou experimento, não os dois.")

    documentos = buscar_documentos(equipamento=equipamento, experimento=experimento)

    if not documentos:
        raise ValueError("Nenhum documento encontrado para esse filtro.")

    pasta_exports = Path("storage/exports")
    pasta_exports.mkdir(parents=True, exist_ok=True)

    filtro_valor = equipamento.value if equipamento else experimento.value
    filtro_nome = filtro_valor.replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    caminho_zip = pasta_exports / f"backup_seletivo_{filtro_nome}_{timestamp}.zip"

    metadados = [doc.model_dump(mode="json") for doc in documentos]

    config = carregar_config()
    diretorio_arquivos = Path(config["diretorio_armazenamento"])

    with zipfile.ZipFile(caminho_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("metadados.json", json.dumps(metadados, indent=2, ensure_ascii=False))

        for doc in documentos:
            caminho_arquivo_original = diretorio_arquivos / doc.nome_armazenado
            if caminho_arquivo_original.exists():
                zipf.write(caminho_arquivo_original, arcname=doc.nome_armazenado)

    return caminho_zip


