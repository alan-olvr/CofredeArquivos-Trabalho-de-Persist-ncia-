from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status
from datetime import date
from typing import Optional
from models.documento import Documento, DocumentoBase, Laboratorio, Equipamento, Experimento
from app.crud import criar_documento, buscar_documentos, buscar_documentos_por_id
from app.logger import logger

app = FastAPI(title="Cofre Digital de Arquivos - Tema 14")


@app.on_event("startup")
def evento_inicializacao():
    logger.info("Sistema iniciado")


@app.get("/")
def raiz():
    return {"status": "ok", "projeto": "Cofre Digital de Arquivos"}


@app.post("/documentos", response_model=Documento)
async def upload_documento(
    arquivo: UploadFile = File(...),
    nome_original: str = Form(...),
    categoria: str = Form(...),
    descricao: str | None = Form(None),
    laboratorio: Laboratorio = Form(...),
    equipamento: Equipamento = Form(...),
    experimento: Experimento = Form(...),
    responsavel: str = Form(...),
    data: date = Form(...),
):
    conteudo = await arquivo.read()

    dados = DocumentoBase(
        nome_original=nome_original,
        categoria=categoria,
        descricao=descricao,
        laboratorio=laboratorio,
        equipamento=equipamento,
        experimento=experimento,
        responsavel=responsavel,
        data=data,
    )

    documento = criar_documento(conteudo, arquivo.filename, dados)
    return documento


@app.get("/documentos")
def consultar_documentos(
    categoria: Optional[str] = None,
    laboratorio: Optional[Laboratorio] = None,
    equipamento: Optional[Equipamento] = None,
    experimento: Optional[Experimento] = None,
) -> list[Documento]:
    return buscar_documentos(
        categoria=categoria,
        laboratorio=laboratorio,
        equipamento=equipamento,
        experimento=experimento,
    )


@app.get("/documentos/{id}")
def consultar_documento_por_id(id: str) -> Optional[Documento]:
    doc = buscar_documentos_por_id(id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado."
        )
    return doc