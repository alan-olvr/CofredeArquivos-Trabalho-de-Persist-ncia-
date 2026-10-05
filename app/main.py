from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status
from datetime import date
from typing import Optional
from models.documento import Documento, DocumentoBase, Laboratorio, Equipamento, Experimento
from app.crud import criar_documento, buscar_documentos, buscar_documentos_por_id, exportar_documentos_csv, criar_backup_zip
from app.logger import logger
from models.estatisticas import calcular_estatisticas
from models.integridade import verificar_integridade, verificar_integridade_global
from models.backup import criar_backup_seletivo
from fastapi.responses import FileResponse



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

@app.get("/documentos/estatisticas")
def consultar_estatisticas():
    return calcular_estatisticas()

@app.get("/documentos/{id}")
def consultar_documento_por_id(id: str) -> Optional[Documento]:
    doc = buscar_documentos_por_id(id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado."
        )
    return doc

@app.get("/documentos/{id}/integridade")
def consultar_integridade(id: str):
    resultado = verificar_integridade(id)

    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado."
        )
    return resultado

@app.get("/integridade")
def consultar_integridade_global():
    return verificar_integridade_global()

@app.get("/exportar/csv")
def exportar_csv():
    caminho_arquivo = exportar_documentos_csv()
    return FileResponse(
        path=caminho_arquivo,
        filename="relatorio_documentos.csv",
        media_type="text/csv"
    )


@app.post("/backup")
def realizar_backup():
    caminho_backup = criar_backup_zip()
    return {
        "mensagem": "Backup realizado com sucesso!",
        "arquivo": caminho_backup.name
    }

@app.post("/backup/seletivo")
def realizar_backup_seletivo(
    equipamento: Optional[Equipamento] = None,
    experimento: Optional[Experimento] = None,
):
    try:
        caminho_zip = criar_backup_seletivo(equipamento=equipamento, experimento=experimento)
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro))

    return {
        "mensagem": "Backup seletivo realizado com sucesso.",
        "arquivo": caminho_zip.name,
    }