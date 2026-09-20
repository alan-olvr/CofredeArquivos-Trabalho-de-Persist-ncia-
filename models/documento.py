import enum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import date, datetime

class Laboratorio(str, enum):
    ANALISES_CLINICAS="Laboratório de Análises Clínicas.",
    HEMATOLOGIA="Laboratório de Hematologia.",
    MICROBIOLOGIA="Laboratório de Microbiologia."

class Equipamento(str, enum):
    CENTRIFUGA="Centrífuga.",
    MICROSCOPIO_OPTICO="Microscópio Óptico.",
    AUTOANALISADOR_BIOQUIMICO="Autoanalisador Bioquímico."

class Experimento(str, enum):
    HEMOGRAMA_COMPLETO="Hemograma completo.",
    CULTURA_BACTERIANA="Cultura bacteriana.",
    DOSAGEM_GLICOSE="Dosagem de glicose.",
    URINALISE="Urinálise."

def DocumentoBase(BaseModel):
    nome: str
    categoria: str
    descricao: Optional[str] = None
    laboratorio: Laboratorio
    equipamento: Equipamento
    experimento: Experimento
    responsavel: str
    data: date

def Documento(DocumentoBase):
    id: str
    nome: str
    extensao: str
    tipo: str
    tamanho: int
    sha256: str
    data_upload: datetime=Field(default_factory=datetime.now)


