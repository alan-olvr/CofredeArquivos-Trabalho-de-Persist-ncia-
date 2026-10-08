from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import date, datetime


class Laboratorio(str, Enum):
    ANALISES_CLINICAS = "Laboratório de Análises Clínicas"
    HEMATOLOGIA = "Laboratório de Hematologia"
    MICROBIOLOGIA = "Laboratório de Microbiologia"


class Equipamento(str, Enum):
    CENTRIFUGA = "Centrífuga"
    MICROSCOPIO_OPTICO = "Microscópio Óptico"
    AUTOANALISADOR_BIOQUIMICO = "Autoanalisador Bioquímico"
    ESTUFA_CULTURA = "Estufa de Cultura"


class Experimento(str, Enum):
    HEMOGRAMA_COMPLETO = "Hemograma Completo"
    CULTURA_BACTERIANA = "Cultura Bacteriana"
    DOSAGEM_GLICOSE = "Dosagem de Glicose"
    URINALISE = "Urinálise"


class DocumentoBase(BaseModel):
    nome_original: str
    categoria: str
    descricao: Optional[str] = None
    laboratorio: Laboratorio
    equipamento: Equipamento
    experimento: Experimento    
    responsavel: str
    data: date

class DocumentoUpdate(BaseModel):
    nome_original: Optional[str] = Field(default=None, min_length=3, max_length=120)
    categoria: Optional[str] = Field(default=None, min_length=3, max_length=60)
    descricao: Optional[str] = Field(default=None, max_length=300)
    laboratorio: Optional[Laboratorio] = None
    equipamento: Optional[Equipamento] = None
    experimento: Optional[Experimento] = None
    responsavel: Optional[str] = Field(default=None, min_length=2, max_length=80)
    data: Optional[date] = None


class Documento(DocumentoBase):
    id: str
    nome_armazenado: str
    extensao: str
    tipo_mime: str
    tamanho: int
    sha256: str
    data_upload: datetime = Field(default_factory=datetime.now)