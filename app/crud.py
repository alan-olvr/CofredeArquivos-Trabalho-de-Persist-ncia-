import uuid
import hashlib 
import mimetypes
from pathlib import Path
from typing import Optional
from app.logger import logger
from models.documento import Documento, DocumentoBase
from app.db import ler_documentos, salvar_documentos
from app.config import carregar_config
from models.documento import Documento, DocumentoBase, Laboratorio, Equipamento, Experimento

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

