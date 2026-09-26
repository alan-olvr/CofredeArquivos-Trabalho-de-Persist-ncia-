from fastapi import FastAPI, HTTPException
from crud import buscar_documentos, buscar_documento_por_id
from typing import Optional
from models.documento import Documento, DocumentoBase
from app.db import ler_documentos, salvar_documentos

app = FastAPI(title="Cofre Digital de Arquivos - Tema 14")

@app.get("/")
def raiz():
    return {"status": "ok", "projeto": "Cofre Digital de Arquivos"} 


@app.get("/documentos")
def consultar_documentos() -> list[Documento]:
    return buscar_documentos() 


@app.get("/documentos/{id}")
def consultar_documentos_por_id(id: str) -> Optional[Documento]:
    doc =  buscar_documento_por_id(id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Documento não encontrado."
        )
    return doc 