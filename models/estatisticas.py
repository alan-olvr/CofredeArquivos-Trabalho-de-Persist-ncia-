from app.db import ler_documentos
from collections import Counter

def calcular_estatisticas():
    documentos = ler_documentos()

    extensoes = Counter(doc.extensao for doc in documentos)
    categorias = Counter(doc.categoria for doc in documentos)
    laboratorios = Counter(doc.laboratorio for doc in documentos)
    equipamentos = Counter(doc.equipamento for doc in documentos)

    total_documentos = len(documentos)
    tamanho_total_bytes = sum(doc.tamanho for doc in documentos)

    return{
        "total_documentos": total_documentos,
        "tamanho_total_bytes": tamanho_total_bytes,
        "quantidade_por_extensao": dict(extensoes),
        "quantidade_por_categoria": dict(categorias),
        "quantidade_por_laboratorio": dict(laboratorios),
        "quantidade_por_equipamento": dict(equipamentos),
    }