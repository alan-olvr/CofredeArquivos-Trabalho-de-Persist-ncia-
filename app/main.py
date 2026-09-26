from fastapi import FastAPI, File, UploadFile, Form
from datetime import date
from models.documento import Documento, DocumentoBase, Laboratorio, Equipamento, Experimento
from app.crud import criar_documento
from app.logger import logger

app = FastAPI(title="Cofre de Arquivos Digital - Laboratório")

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
    conteudo=await arquivo.read()

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

    documento=criar_documento(conteudo, arquivo.filename, dados)
    return documento

@app.on_event("startup")
def evento_inicializacao():
    logger.info("Sistema iniciado")