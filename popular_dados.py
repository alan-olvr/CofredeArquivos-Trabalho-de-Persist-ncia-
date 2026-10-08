import csv
import io
import json
import random
import struct
import zlib
from datetime import date

from app.crud import criar_documento
from models.documento import DocumentoBase, Laboratorio, Equipamento, Experimento

AC, HE, MI = Laboratorio.ANALISES_CLINICAS, Laboratorio.HEMATOLOGIA, Laboratorio.MICROBIOLOGIA
CE, MO = Equipamento.CENTRIFUGA, Equipamento.MICROSCOPIO_OPTICO
AU, ES = Equipamento.AUTOANALISADOR_BIOQUIMICO, Equipamento.ESTUFA_CULTURA
HC, CB = Experimento.HEMOGRAMA_COMPLETO, Experimento.CULTURA_BACTERIANA
DG, UR = Experimento.DOSAGEM_GLICOSE, Experimento.URINALISE

# (arquivo, nome_original, categoria, descricao, laboratorio, equipamento, experimento, responsavel, data)
DOCUMENTOS = [
    ("relatorio_hemograma_01.pdf", "Relatório de Hemograma 01", "Relatório", "Hemograma da amostra 01", AC, CE, HC, "Alan", date(2026, 9, 2)),
    ("resultados_hemograma_01.csv", "Resultados de Hemograma 01", "Resultado", "Valores do hemograma 01", AC, AU, HC, "Daniel", date(2026, 9, 3)),
    ("microscopia_hemograma_01.png", "Microscopia de Hemograma 01", "Imagem", "Lâmina de sangue ao microscópio", HE, MO, HC, "Ana Lima", date(2026, 9, 4)),
    ("relatorio_hemograma_02.pdf", "Relatório de Hemograma 02", "Relatório", "Hemograma da amostra 02", HE, CE, HC, "Alan", date(2026, 9, 5)),
    ("planilha_contagem_celulas.csv", "Planilha de Contagem de Células", "Planilha", "Contagem diferencial de células", HE, AU, HC, "Daniel", date(2026, 9, 6)),
    ("cultura_placa_01.png", "Placa de Cultura 01", "Imagem", "Crescimento bacteriano em placa", MI, ES, CB, "Ana Lima", date(2026, 9, 8)),
    ("cultura_placa_02.png", "Placa de Cultura 02", "Imagem", "Colônias vistas ao microscópio", MI, MO, CB, "Ana Lima", date(2026, 9, 9)),
    ("relatorio_cultura_01.pdf", "Relatório de Cultura Bacteriana", "Relatório", "Resultado da cultura após 48h", MI, ES, CB, "Alan", date(2026, 9, 10)),
    ("resultados_cultura.csv", "Resultados da Cultura", "Resultado", "Contagem de colônias por placa", MI, ES, CB, "Daniel", date(2026, 9, 10)),
    ("protocolo_cultura.txt", "Protocolo de Cultura", "Manual", "Passo a passo do procedimento", MI, ES, CB, "Alan", date(2026, 9, 11)),
    ("glicose_calibracao.csv", "Calibração de Glicose", "Planilha", "Curva de calibração do autoanalisador", AC, AU, DG, "Daniel", date(2026, 9, 12)),
    ("relatorio_glicose.pdf", "Relatório de Dosagem de Glicose", "Relatório", "Dosagem de glicose em jejum", AC, AU, DG, "Alan", date(2026, 9, 13)),
    ("notas_glicose.txt", "Notas da Dosagem de Glicose", "Resultado", "Observações da bancada", AC, CE, DG, "Ana Lima", date(2026, 9, 14)),
    ("urinalise_resultados.csv", "Resultados de Urinálise", "Resultado", "Parâmetros físico-químicos", AC, MO, UR, "Daniel", date(2026, 9, 15)),
    ("sedimento_urinario.png", "Sedimento Urinário", "Imagem", "Imagem do sedimento ao microscópio", AC, MO, UR, "Ana Lima", date(2026, 9, 16)),
    ("manual_centrifuga.pdf", "Manual da Centrífuga", "Manual", "Instruções de operação", HE, CE, HC, "Alan", date(2026, 9, 17)),
    ("manual_autoanalisador.txt", "Manual do Autoanalisador", "Manual", "Rotina de manutenção", HE, AU, DG, "Daniel", date(2026, 9, 18)),
    ("manual_microscopio.txt", "Manual do Microscópio", "Manual", "Limpeza e ajuste de foco", MI, MO, CB, "Ana Lima", date(2026, 9, 19)),
    ("log_estufa.json", "Log da Estufa de Cultura", "Resultado", "Temperatura registrada por hora", MI, ES, CB, "Alan", date(2026, 9, 20)),
]


def gerar_pdf(titulo: str, linhas: list[str]) -> bytes:
    def esc(t: str) -> str:
        return t.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    partes = [f"BT /F1 14 Tf 50 790 Td ({esc(titulo)}) Tj"]
    partes += [f"0 -22 Td ({esc(l)}) Tj" for l in linhas]
    partes.append("ET")
    stream = "\n".join(partes).encode("cp1252")
    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ]
    saida = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objetos, start=1):
        offsets.append(len(saida))
        saida += b"%d 0 obj\n" % i + obj + b"\nendobj\n"
    xref = len(saida)
    saida += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objetos) + 1)
    for off in offsets:
        saida += b"%010d 00000 n \n" % off
    saida += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objetos) + 1, xref)
    return bytes(saida)


def gerar_png(semente: int, largura: int = 160, altura: int = 100) -> bytes:
    linhas = bytearray()
    for y in range(altura):
        linhas.append(0)
        for x in range(largura):
            linhas += bytes(((x * 2 + semente * 37) % 256, (y * 3 + semente * 61) % 256, (x + y + semente * 17) % 256))

    def chunk(tipo: bytes, dados: bytes) -> bytes:
        corpo = tipo + dados
        return struct.pack(">I", len(dados)) + corpo + struct.pack(">I", zlib.crc32(corpo) & 0xFFFFFFFF)

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", largura, altura, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(linhas)))
        + chunk(b"IEND", b"")
    )


def gerar_conteudo(indice: int, item: tuple) -> bytes:
    arquivo, nome, categoria, descricao, lab, equip, exp, resp, data = item
    extensao = arquivo.rsplit(".", 1)[-1]
    rng = random.Random(indice)
    cabecalho = [descricao, lab.value, equip.value, exp.value, f"Responsável: {resp}", f"Data: {data.isoformat()}"]

    if extensao == "pdf":
        return gerar_pdf(nome, cabecalho)
    if extensao == "png":
        return gerar_png(indice)
    if extensao == "csv":
        saida = io.StringIO()
        escritor = csv.writer(saida)
        escritor.writerow(["amostra", "valor", "unidade"])
        for n in range(1, 9):
            escritor.writerow([f"{indice:02d}-{n:02d}", round(rng.uniform(1, 200), 2), "mg/dL"])
        return saida.getvalue().encode("utf-8")
    if extensao == "json":
        registros = [{"hora": f"{h:02d}:00", "temperatura_c": round(rng.uniform(35.5, 37.5), 1)} for h in range(8)]
        return json.dumps({"documento": nome, "registros": registros}, ensure_ascii=False, indent=2).encode("utf-8")
    texto = [nome, "=" * len(nome), *cabecalho, "", f"Registro interno nº {indice}, código {rng.randint(10000, 99999)}."]
    return "\n".join(texto).encode("utf-8")


def main() -> None:
    for indice, item in enumerate(DOCUMENTOS, start=1):
        arquivo, nome, categoria, descricao, lab, equip, exp, resp, data = item
        dados = DocumentoBase(
            nome_original=nome, categoria=categoria, descricao=descricao,
            laboratorio=lab, equipamento=equip, experimento=exp,
            responsavel=resp, data=data,
        )
        doc = criar_documento(gerar_conteudo(indice, item), arquivo, dados)
        print(f"[{indice:02d}] {doc.nome_original} -> {doc.extensao} ({doc.tamanho} bytes)")
    print(f"\n{len(DOCUMENTOS)} documentos cadastrados.")


if __name__ == "__main__":
    main()