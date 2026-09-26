import uuid
import hashlib 
import mimetypes
from pathlib import Path
from models.documento import Documento, DocumentoBase
from app.db import ler_documentos, salvar_documentos
from app.config import carregar_config
from app.logger import logger

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


