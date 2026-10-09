from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status, Query
from datetime import date
from typing import Optional
from models.documento import Documento, DocumentoBase, DocumentoUpdate, Laboratorio, Equipamento, Experimento
from app.crud import (
    DocumentoDuplicadoError,
    criar_documento,
    buscar_documentos,
    buscar_documentos_por_id,
    atualizar_documento,
    apagar_documento,
    listar_backups,
    exportar_documentos_csv,
    criar_backup_zip,
    obter_caminho_documento,
)
from app.logger import logger
from models.estatisticas import calcular_estatisticas
from models.integridade import verificar_integridade, verificar_integridade_global
from models.backup import criar_backup_seletivo
from fastapi.responses import FileResponse

app = FastAPI(
    title="Cofre Digital de Arquivos - Tema 14",
    description="API para gerenciamento, armazenamento seguro, exportação e verificação de integridade de documentos de laboratório.",
    version="1.0.0",
)

def erro_404(recurso: str):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{recurso} não encontrado.",
    )

@app.on_event("startup")
def evento_inicializacao():
    logger.info("Sistema iniciado")

@app.get("/", tags=["Status"])
def raiz():
    """
    Verifica a disponibilidade do serviço.

    - **Retorna**: Um objeto indicando o status operacional do sistema.
    """
    return {"status": "ok", "projeto": "Cofre Digital de Arquivos"}


@app.post("/documentos", response_model=Documento, status_code=status.HTTP_201_CREATED, tags=["Documentos"])
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
    """
    Realiza o upload de um novo arquivo físico e grava seus metadados.

    - **arquivo**: Arquivo físico a ser enviado.
    - **nome_original**: Nome de exibição do documento.
    - **categoria**: Categoria do arquivo (ex: Relatório, Exame, Protocolo).
    - **descricao**: Descrição detalhada opcional.
    - **laboratorio**: Laboratório de origem (enum).
    - **equipamento**: Equipamento associado (enum).
    - **experimento**: Experimento relacionado (enum).
    - **responsavel**: Nome do operador/responsável.
    - **data**: Data de realização/registro do documento.
    - **Retorna**: O objeto `Documento` cadastrado com ID, hash SHA256 e metadados.
    """
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

    try:
        documento = criar_documento(conteudo, arquivo.filename, dados)
    except DocumentoDuplicadoError as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe um documento com o mesmo conteúdo (id={erro}).",
        )
    return documento


@app.get("/documentos", response_model=list[Documento], tags=["Documentos"])
def consultar_documentos(
    categoria: Optional[str] = Query(default=None, description="Filtrar por categoria"),
    laboratorio: Optional[Laboratorio] = Query(default=None, description="Filtrar por laboratório de origem"),
    equipamento: Optional[Equipamento] = Query(default=None, description="Filtrar por equipamento associado"),
    experimento: Optional[Experimento] = Query(default=None, description="Filtrar por experimento associado"),
) -> list[Documento]:
    """
    Consulta os documentos cadastrados utilizando filtros opcionais.

    - **categoria**: Filtrar por categoria.
    - **laboratorio**: Filtrar por laboratório de origem.
    - **equipamento**: Filtrar por equipamento associado.
    - **experimento**: Filtrar por experimento associado.
    - **Retorna**: Uma lista contendo os documentos que correspondem aos critérios passados.
    """
    return buscar_documentos(
        categoria=categoria,
        laboratorio=laboratorio,
        equipamento=equipamento,
        experimento=experimento,
    )


@app.get("/documentos/estatisticas", tags=["Estatísticas"])
def consultar_estatisticas():
    """
    Retorna métricas e estatísticas gerais do cofre digital.

    - **Retorna**: Quantidade total de documentos, tamanho acumulado dos arquivos e distribuições por categoria e laboratório.
    """
    return calcular_estatisticas()


@app.get("/documentos/{id}", response_model=Documento, tags=["Documentos"])
def consultar_documento_por_id(id: str) -> Optional[Documento]:
    """
    Busca os metadados de um documento específico pelo ID.

    - **id**: UUID do documento cadastrado.
    - **Retorna**: Os metadados detalhados do documento.
    """
    doc = buscar_documentos_por_id(id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado."
        )
    return doc

@app.put("/documentos/{id}", response_model=Documento, tags=["Documentos"])
def atualizar_metadados(id: str, dados: DocumentoUpdate):
    """
    Atualiza os metadados de um documento. O arquivo físico não é alterado.
    - **id**: UUID do documento.
    - **Retorna**: O documento com os metadados atualizados.
    """
    documento = atualizar_documento(id, dados)
    if documento is None:
        erro_404("Documento")
    return documento

@app.delete("/documentos/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Documentos"])
def remover_documento(id: str):
    """
    Remove o registro do JSON e o arquivo físico do documento.
    - **id**: UUID do documento.
    """
    if not apagar_documento(id):
        erro_404("Documento")

@app.get("/backups", tags=["Exportação e Backup"])
def consultar_backups():
    """
    Lista os backups `.zip` gerados na pasta de backups.
    - **Retorna**: Nome, tamanho e data de criação de cada backup.
    """
    return listar_backups()

@app.get("/documentos/{id}/integridade", tags=["Integridade"])
def consultar_integridade(id: str):
    """
    Verifica a integridade do arquivo físico de um documento comparando seu hash SHA256 atual com o gravado.

    - **id**: UUID do documento a ser auditado.
    - **Retorna**: Status informando se o arquivo está íntegro, alterado ou ausente.
    """
    resultado = verificar_integridade(id)

    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado."
        )
    return resultado


@app.get("/integridade", tags=["Integridade"])
def consultar_integridade_global():
    """
    Executa a auditoria de integridade SHA256 em todos os documentos cadastrados no cofre.

    - **Retorna**: Relatório consolidado com documentos íntegros, corrompidos e ausentes.
    """
    return verificar_integridade_global()


@app.get("/exportar/csv", tags=["Exportação e Backup"])
def exportar_csv():
    """
    Gera e disponibiliza o download de uma planilha em formato CSV com todos os metadados dos documentos.

    - **Retorna**: Arquivo `relatorio_documentos.csv` para download direto.
    """
    caminho_arquivo = exportar_documentos_csv()
    return FileResponse(
        path=caminho_arquivo,
        filename="relatorio_documentos.csv",
        media_type="text/csv"
    )

@app.post("/backup", tags=["Exportação e Backup"])
def realizar_backup():
    """
    Cria um backup compactado em `.zip` contendo todos os dados e arquivos armazenados no cofre.

    - **Retorna**: Mensagem de confirmação e o nome do arquivo ZIP gerado na pasta de backups.
    """
    caminho_backup = criar_backup_zip()
    return {
        "mensagem": "Backup realizado com sucesso!",
        "arquivo": caminho_backup.name
    }

@app.post("/backup/seletivo", tags=["Exportação e Backup"])
def realizar_backup_seletivo(
    equipamento: Optional[Equipamento] = None,
    experimento: Optional[Experimento] = None,
):
    """
    Gera um pacote de backup em formato `.zip` filtrado por equipamento e/ou experimento.

    - **equipamento**: Equipamento para filtrar os arquivos (opcional).
    - **experimento**: Experimento para filtrar os arquivos (opcional).
    - **Retorna**: Mensagem de sucesso e o nome do pacote de backup seletivo gerado.
    """
    try:
        caminho_zip = criar_backup_seletivo(equipamento=equipamento, experimento=experimento)
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro))

    return {
        "mensagem": "Backup seletivo realizado com sucesso.",
        "arquivo": caminho_zip.name,
    }


@app.get("/documentos/{id}/download", tags=["Documentos"])
def download_documento(id: str):
    """
    Realiza o download do arquivo físico associado a um documento.

    - **id**: UUID do documento cadastrado.
    - **Retorna**: O arquivo para download direto no navegador.
    """
    resultado = obter_caminho_documento(id)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento ou arquivo físico não encontrado."
        )

    caminho_arquivo, doc = resultado

    return FileResponse(
        path=caminho_arquivo,
        filename=doc.nome_original,
        media_type=doc.tipo_mime or "application/octet-stream"
    )

