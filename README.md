# Cofre Digital de Arquivos

**Tema recebido:** Tema 14 — Cofre de Documentação de Laboratórios

Trabalho Prático 1 — QXD0099 Desenvolvimento de Software para Persistência
Universidade Federal do Ceará, Campus Quixadá — Prof. Francisco Victor da Silva Pinheiro

## Integrantes

- José Alan de Oliveira Silva
- Daniel Fernandes Ferreira

## Objetivo

Desenvolver, com Python e FastAPI, uma aplicação que armazena, consulta, atualiza, protege, exporta e faz backup de documentos digitais de laboratório (relatórios, resultados, imagens, planilhas e manuais), mantendo os metadados de cada arquivo.

O sistema integra JSON (metadados), CSV (exportação), YAML (configuração), logs e arquivos binários. Os metadados ficam em arquivo e os documentos em disco, **sem banco de dados**.

## Requisitos

- Python 3.10 ou superior
- `pip` e `venv` (já vêm com o Python)
- Git, para clonar o repositório
- Sistema operacional: Windows, Linux ou macOS

## Bibliotecas utilizadas

| Biblioteca | Uso |
|---|---|
| FastAPI | Criação da API REST e do Swagger UI |
| Uvicorn | Servidor para executar a API |
| Pydantic | Modelos e validação dos metadados |
| PyYAML | Leitura do arquivo de configuração |
| python-multipart | Recebimento de arquivos (upload) |

Da biblioteca padrão do Python: `json`, `csv`, `hashlib`, `zipfile`, `logging`, `mimetypes`, `uuid` e `pathlib`. Todas as dependências externas estão no `requirements.txt`.

## Instalação

1. Clone o repositório e entre na pasta:

```bash
   git clone https://github.com/alan-olvr/CofredeArquivos-Trabalho-de-Persist-ncia-.git
   cd CofredeArquivos-Trabalho-de-Persist-ncia-
```

2. Crie e ative o ambiente virtual:

```bash
   python -m venv venv
   # Windows (PowerShell)
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
```

   Se o PowerShell bloquear a ativação, rode antes `Set-ExecutionPolicy -Scope Process Bypass`.

3. Instale as dependências:

```bash
   pip install -r requirements.txt
```

## Execução

1. Na raiz do projeto, com o ambiente virtual ativo, inicie a API:

```bash
   uvicorn app.main:app --reload
```

2. Abra o Swagger UI em <http://127.0.0.1:8000/docs> para testar todos os endpoints.

3. (Opcional) Popule o sistema com dados de demonstração, em outro terminal:

```bash
   python popular_dados.py
```

   O script cadastra 19 documentos (5 extensões, 5 categorias, 3 laboratórios e 4 equipamentos) usando a mesma lógica do upload. Como o sistema recusa conteúdo duplicado (`409`), para repetir a carga apague antes `storage/metadados.json` e os arquivos de `storage/documentos/`.

## Estrutura do projeto

```
.
├── app/
│   ├── main.py          # rotas da API e tratamento de erros HTTP
│   ├── crud.py          # regras de documentos, backup geral e CSV
│   ├── db.py            # leitura e escrita do JSON de metadados
│   ├── config.py        # leitura do config.yaml
│   └── logger.py        # configuração do log
├── models/
│   ├── documento.py     # modelos Pydantic e enums
│   ├── estatisticas.py  # cálculo das estatísticas
│   ├── integridade.py   # verificação SHA-256
│   └── backup.py        # backup seletivo (F16)
├── config/
│   └── config.yaml      # configuração externa
├── storage/
│   ├── documentos/      # arquivos físicos
│   ├── metadados.json   # metadados dos documentos (persistência principal)
│   ├── logs/            # app.log
│   ├── backups/         # backups gerais (.zip)
│   └── exports/         # CSV e backups seletivos
├── popular_dados.py     # carga de dados de demonstração
└── requirements.txt
```

Cada pasta de `storage/` guarda um tipo de dado: arquivos originais, metadados, logs, backups e exportações. Elas são criadas automaticamente quando necessário.

## Configuração (`config/config.yaml`)

```yaml
diretorio_armazenamento: storage/documentos
nivel_log: INFO
```

- `diretorio_armazenamento`: pasta onde os arquivos físicos são gravados.
- `nivel_log`: nível do log (`DEBUG`, `INFO`, `WARNING`, `ERROR`).

Se o arquivo não existir, estiver vazio ou for inválido, a aplicação avisa no terminal e usa esses mesmos valores como padrão.

## Metadados dos documentos

### Campos gerais

| Campo | Descrição |
|---|---|
| `id` | UUID gerado no upload |
| `nome_original` | Nome de exibição do documento |
| `nome_armazenado` | Nome físico no disco (`<uuid><extensão>`), sem colisão |
| `extensao`, `tipo_mime`, `tamanho` | Calculados no upload (MIME desconhecido vira `application/octet-stream`) |
| `sha256` | Hash do conteúdo, calculado no upload |
| `categoria`, `descricao` | Classificação e descrição |
| `data_upload` | Data e hora do envio |

### Campos específicos do domínio (laboratórios)

| Campo | Descrição |
|---|---|
| `laboratorio` | Laboratório de origem (lista fechada) |
| `equipamento` | Equipamento associado (lista fechada) |
| `experimento` | Experimento relacionado (lista fechada) |
| `responsavel` | Responsável pelo documento |
| `data` | Data do experimento ou relatório (diferente de `data_upload`) |

### Valores aceitos (enums)

Os valores são **exatos**, com maiúsculas e acentos. No Swagger, escolha na lista suspensa.

- **Laboratório:** `Laboratório de Análises Clínicas`, `Laboratório de Hematologia`, `Laboratório de Microbiologia`
- **Equipamento:** `Centrífuga`, `Microscópio Óptico`, `Autoanalisador Bioquímico`, `Estufa de Cultura`
- **Experimento:** `Hemograma Completo`, `Cultura Bacteriana`, `Dosagem de Glicose`, `Urinálise`

## Principais endpoints

| Requisito | Método e rota | Descrição |
|---|---|---|
| F1 | `POST /documentos` | Upload do arquivo (multipart) com metadados |
| F2, F7 | `GET /documentos` | Lista documentos; filtros combináveis: `categoria`, `laboratorio`, `equipamento`, `experimento` |
| F3 | `GET /documentos/{id}` | Metadados de um documento |
| F4 | `GET /documentos/{id}/download` | Baixa o arquivo físico, idêntico ao enviado |
| F5 | `PUT /documentos/{id}` | Atualiza metadados (só os campos enviados); não altera o arquivo |
| F6 | `DELETE /documentos/{id}` | Remove o registro e o arquivo físico |
| F8 | `GET /documentos/estatisticas` | Total, tamanho total e quantidade por extensão, categoria, laboratório e equipamento |
| F9 | `GET /documentos/{id}/integridade` | Recalcula o SHA-256 e compara com o salvo |
| F10 | `GET /integridade` | Auditoria global: verificados, íntegros, alterados e não localizados |
| F13 | `GET /exportar/csv` | Exporta os metadados em CSV |
| F14 | `POST /backup` | Backup geral compactado (`.zip`) |
| F15 | `GET /backups` | Lista os backups gerais disponíveis |
| F16 | `POST /backup/seletivo` | Backup só dos documentos de um equipamento **ou** experimento |

### Comportamentos importantes

- **F1 (upload):** gera UUID, preserva o nome original, grava o arquivo como `<uuid><extensão>` (dois arquivos com o mesmo nome não se sobrescrevem), calcula tamanho, MIME e SHA-256 e registra no JSON e no log.
- **Duplicidade:** um upload cujo conteúdo já existe (mesmo SHA-256) é recusado com `409`, e o arquivo não é gravado.
- **F5 (atualização):** só os campos enviados são alterados. `sha256`, `tamanho`, `nome_armazenado` e o arquivo físico não são modificados. A alteração é gravada no JSON e registrada no log.
- **F6 (exclusão):** remove o registro do JSON **e** o arquivo físico. Se o arquivo físico já não existir, o registro é removido mesmo assim. A resposta é `204 No Content`.
- **F14 (backup geral):** cada backup recebe um nome com data e hora (`backup_AAAAMMDD_HHMMSS.zip`), então um novo backup não sobrescreve os anteriores. Fica em `storage/backups/` e contém todo o conteúdo de `storage/`, exceto os backups anteriores.
- **F15 (listagem):** lista apenas os backups gerais de `storage/backups/`. Os backups seletivos ficam em `storage/exports/`.

## Funcionalidade específica do tema (F16): backup seletivo

Gera um `.zip` com **apenas** os documentos relacionados a um equipamento ou a um experimento, separado do backup geral.

- **Endpoint:** `POST /backup/seletivo?equipamento=...` ou `POST /backup/seletivo?experimento=...` (apenas um dos dois).
- **Dados usados:** os metadados `equipamento` e `experimento` realmente persistidos em `storage/metadados.json`.
- **Saída:** `storage/exports/backup_seletivo_<filtro>_<data>.zip`, com os arquivos filtrados e um `metadados.json` só com esses documentos.
- **Erros:** `400` se nenhum filtro for informado, se forem informados os dois, ou se nenhum documento corresponder.

## Exemplos de utilização

O jeito mais simples é o Swagger UI em `/docs`. Os exemplos abaixo usam `curl` (Linux, macOS ou Git Bash; no PowerShell, use `curl.exe` nos comandos sem JSON e o Swagger para o `PUT`).

```bash
# F1 - Upload
curl -X POST "http://127.0.0.1:8000/documentos" -F "arquivo=@relatorio.pdf" -F "nome_original=Relatório de Hemograma" -F "categoria=Relatório" -F "laboratorio=Laboratório de Hematologia" -F "equipamento=Centrífuga" -F "experimento=Hemograma Completo" -F "responsavel=Alan" -F "data=2026-09-10"

# F7 - Filtros combinados
curl "http://127.0.0.1:8000/documentos?experimento=Cultura%20Bacteriana&equipamento=Estufa%20de%20Cultura"

# F5 - Atualização de metadados
curl -X PUT "http://127.0.0.1:8000/documentos/<id>" -H "Content-Type: application/json" -d '{"categoria": "Resultado"}'

# F4 - Download
curl -o arquivo_baixado "http://127.0.0.1:8000/documentos/<id>/download"

# F9 - Integridade individual
curl "http://127.0.0.1:8000/documentos/<id>/integridade"

# F16 - Backup seletivo
curl -X POST "http://127.0.0.1:8000/backup/seletivo?experimento=Cultura%20Bacteriana"
```

Exemplo de resposta do `GET /documentos/estatisticas` (valores ilustrativos; os reais dependem dos dados cadastrados):

```json
{
  "total_documentos": 19,
  "tamanho_total_bytes": 123456,
  "quantidade_por_extensao": {".pdf": 5, ".csv": 5, ".png": 4, ".txt": 4, ".json": 1},
  "quantidade_por_categoria": {"Relatório": 5, "Imagem": 4},
  "quantidade_por_laboratorio": {"Laboratório de Hematologia": 5},
  "quantidade_por_equipamento": {"Centrífuga": 4}
}
```

## Tratamento de erros (F17)

| Código | Quando ocorre |
|---|---|
| `200` | Operação realizada com sucesso |
| `201` | Documento criado |
| `204` | Documento removido |
| `400` | Backup seletivo sem filtro, com os dois filtros ou sem documentos correspondentes |
| `404` | Documento, arquivo físico ou recurso não encontrado |
| `409` | Upload de arquivo com conteúdo já cadastrado (SHA-256 duplicado) |
| `422` | Dados inválidos: enum fora da lista, campo obrigatório ausente, texto fora do tamanho permitido |
| `500` | `metadados.json` corrompido ou erro de leitura/escrita no armazenamento |

Outros casos tratados:

- `config.yaml` inexistente, vazio ou inválido: a aplicação usa os valores padrão.
- Arquivo físico ausente: a verificação de integridade aponta o documento como não localizado.
- Arquivo sem extensão ou com extensão desconhecida: o MIME vira `application/octet-stream`.

## Logs

Os eventos ficam em `storage/logs/app.log`, com data, hora, nível e mensagem.

| Nível | Eventos |
|---|---|
| `INFO` | Inicialização, upload, consulta, download, atualização, exclusão, verificação de integridade (individual e global), backups (geral e seletivo), exportação CSV |
| `WARNING` | Documento inexistente, upload duplicado recusado |
| `ERROR` | Metadados inválidos ou corrompidos, erro de leitura ou escrita |

Exemplo de linha: `2026-09-25 14:30:12,345 - INFO - Upload realizado: Relatório de Hemograma (id=...)`.

## Como demonstrar (roteiro rápido)

1. `GET /documentos`: listar os documentos populados.
2. `GET /documentos?equipamento=Centrífuga`: filtrar por equipamento.
3. `GET /documentos/estatisticas`: ver as métricas.
4. `PUT /documentos/{id}` e depois `GET /documentos/{id}`: ver a atualização.
5. `GET /documentos/{id}/integridade` e `GET /integridade`.
6. `GET /exportar/csv`.
7. `POST /backup` e `GET /backups`.
8. **F16:** `POST /backup/seletivo?experimento=Cultura Bacteriana` e conferir o `.zip` em `storage/exports/`.
9. Enviar o mesmo arquivo duas vezes: o segundo retorna `409`.
10. `DELETE /documentos/{id}` e confirmar que o arquivo sumiu de `storage/documentos/`.

## Decisões de projeto

- **JSON no lugar de banco de dados:** o enunciado não permite banco. `app/db.py` cumpre o papel da camada de dados.
- **Enums no lugar de chaves estrangeiras:** garantem valores sempre válidos para laboratório, equipamento e experimento e deixam os filtros (F7) e o F16 consistentes.
- **SHA-256:** serve para a verificação de integridade (F9 e F10) e para impedir documentos duplicados (`409`).
- **Nome de armazenamento com UUID:** evita colisão entre arquivos com o mesmo nome original.
- **Estrutura de pastas própria:** `storage/metadados.json` no lugar de `storage/metadata/documentos.json`, com uma pasta para cada tipo de dado.

## Limitações conhecidas

- Cada operação lê e regrava o JSON inteiro, e isso não é atômico. Dois envios simultâneos podem fazer um registro se perder. Com um banco de dados, uma transação resolveria isso.
- A listagem de documentos não tem paginação.
- Não há criptografia de arquivos.