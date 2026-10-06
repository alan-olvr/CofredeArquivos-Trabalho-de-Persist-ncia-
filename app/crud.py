import uuid
import hashlib 
import mimetypes
from pathlib import Path
from typing import Optional
from app.logger import logger
from app.db import ler_documentos, salvar_documentos
from app.config import carregar_config
from models.documento import Documento, DocumentoBase, Laboratorio, Equipamento, Experimento
import csv
import zipfile
from datetime import datetime

def criar_documento(conteudo: bytes, nome: str, dados: DocumentoBase) -> Documento:
    id_documento=str(uuid.uuid4())
    extensao=Path(nome).suffix

    nome_armazenado=f"{id_documento}{extensao}"
    sha256=hashlib.sha256(conteudo).hexdigest()
    tipo, _ = mimetypes.guess_type(nome)
    tamanho=len(conteudo)

    documento = Documento(
        **dados.model_dump(),
        id=id_documento,
        nome_armazenado=nome_armazenado,
        extensao=extensao,
        tipo_mime=tipo,
        tamanho=tamanho,
        sha256=sha256,
    )

    config = carregar_config()
    diretorio = Path(config["diretorio_armazenamento"])
    diretorio.mkdir(parents=True, exist_ok=True)

    caminho_arquivo = diretorio / nome_armazenado
    caminho_arquivo.write_bytes(conteudo)

    documentos = ler_documentos()
    documentos.append(documento)
    salvar_documentos(documentos)

    logger.info(f"Upload realizado: {documento.nome_original} (id={documento.id})")

    return documento


def buscar_documentos(
        categoria: Optional[str] = None,
        laboratorio: Optional[Laboratorio] = None,
        equipamento: Optional[Equipamento] = None,
        experimento: Optional[Experimento] = None,
) -> list[Documento]:
    documentos = ler_documentos()

    if categoria is not None:
        documentos = [doc for doc in documentos if doc.categoria == categoria]

    if laboratorio is not None:
        documentos = [doc for doc in documentos if doc.laboratorio == laboratorio]

    if equipamento is not None:
        documentos = [doc for doc in documentos if doc.equipamento == equipamento]

    if experimento is not None:
        documentos = [doc for doc in documentos if doc.experimento == experimento]

    return documentos

def buscar_documentos_por_id(id: str) -> Optional[Documento]:
    documento = ler_documentos()
    for doc in documento:
        if doc.id == id:
            return doc
   
    return None



def exportar_documentos_csv():
    documentos = ler_documentos()

    pasta_exports = Path("storage/exports")
    pasta_exports.mkdir(parents=True, exist_ok=True)
    caminho_csv = pasta_exports / "documentos_exportados.csv"

    with open(caminho_csv, mode="w", newline="", encoding="utf-8") as arquivo_csv:
        campos = [
            "id", "nome_original", "categoria", "descricao",
            "laboratorio", "equipamento", "experimento", "responsavel",
            "data", "tamanho", "sha256"
        ]

        escritor = csv.DictWriter(arquivo_csv, fieldnames=campos)
        escritor.writeheader()

        for doc in documentos:
            dados_doc = doc.model_dump(mode="json")
            linha = {campo: dados_doc.get(campo) for campo in campos}
            escritor.writerow(linha)

    logger.info("Exportação em CSV realizada com sucesso.")
    return caminho_csv


def criar_backup_zip()->Path:
    pasta_storage = Path("storage").resolve()
    pasta_backups = pasta_storage / "backups"
    pasta_backups.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = pasta_backups / f"backup_{timestamp}.zip"
    print(f"--> GUARDANDO BACKUP EM: {caminho_zip}")

    

    with zipfile.ZipFile(caminho_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for arquivo in pasta_storage.rglob("*"):
            if "backups" in arquivo.parts:
                continue
            if arquivo.is_file():
                zipf.write(arquivo, arcname=arquivo.relative_to(pasta_storage))

    logger.info(f"Backup criado com sucesso: {caminho_zip.name}")
    return caminho_zip

def obter_caminho_documento(id: str) -> tuple[Path, Documento] | None:
    doc = buscar_documentos_por_id(id)
    if not doc:
        return None

    config = carregar_config()
    diretorio = Path(config.get("diretorio_armazenamento", "storage/documentos"))
    caminho_arquivo = diretorio / doc.nome_armazenado

    if not caminho_arquivo.exists():
        return None

    return caminho_arquivo, doc