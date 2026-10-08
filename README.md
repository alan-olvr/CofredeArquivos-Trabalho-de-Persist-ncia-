# Cofre Digital de Arquivos — Tema 14 (Documentação de Laboratórios)

Trabalho Prático 1 — QXD0099 Desenvolvimento de Software para Persistência (UFC Quixadá).

API REST em **FastAPI** para armazenar, consultar, verificar a integridade, exportar e fazer backup de documentos de laboratório (relatórios, resultados, imagens, planilhas, manuais). Os metadados ficam em um arquivo JSON e os arquivos físicos em disco, sem banco de dados.

## Integrantes

- José Alan de Oliveira Silva
- Daniel Fernandes Ferreira

## Tecnologias

- Python 3.10 ou superior
- FastAPI e Uvicorn
- Pydantic (validação e modelos)
- PyYAML (arquivo de configuração)
- python-multipart (upload de arquivos)

## Estrutura do projeto

```
.
├── app/
│   ├── main.py          # rotas da API
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
│   ├── metadados.json   # metadados dos documentos
│   ├── logs/            # app.log
│   ├── backups/         # backups gerais (.zip)
│   └── exports/         # CSV e backups seletivos
└── requirements.txt
```

As pastas de `storage/` são criadas automaticamente quando necessário.

## Como instalar e executar

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

3. Instale as dependências:

```bash
   pip install -r requirements.txt
```

4. Inicie a API a partir da raiz do projeto:

```bash
   uvicorn app.main:app --reload
```

5. Abra a documentação interativa (Swagger UI) em <http://127.0.0.1:8000/docs>.

## Configuração (`config/config.yaml`)

```yaml
diretorio_armazenamento: storage/documentos
nivel_log: INFO
```

- `diretorio_armazenamento`: pasta onde os arquivos físicos são gravados.
- `nivel_log`: nível do log (`DEBUG`, `INFO`, `WARNING`, `ERROR`).

Se o arquivo não existir, a aplicação usa esses mesmos valores como padrão.

## Metadados dos documentos

| Campo | Descrição |
|---|---|
| `id` | UUID gerado no upload |
| `nome_original` | Nome de exibição do documento |
| `nome_armazenado` | Nome físico no disco (`<uuid><extensão>`), sem colisão |
| `extensao`, `tipo_mime`, `tamanho` | Calculados no upload (MIME desconhecido vira `application/octet-stream`) |
| `sha256` | Hash do conteúdo, calculado no upload |
| `categoria`, `descricao` | Classificação e descrição |
| `laboratorio`, `equipamento`, `experimento` | Metadados do domínio (listas fechadas, abaixo) |
| `responsavel` | Responsável pelo documento |
| `data` | Data do experimento ou relatório |
| `data_upload` | Data e hora do envio |

### Valores aceitos (enums)

Os valores são **exatos**, com maiúsculas e acentos. No Swagger, escolha na lista suspensa.

- **Laboratório:** `Laboratório de Análises Clínicas`, `Laboratório de Hematologia`, `Laboratório de Microbiologia`
- **Equipamento:** `Centrífuga`, `Microscópio Óptico`, `Autoanalisador Bioquímico`, `Estufa de Cultura`
- **Experimento:** `Hemograma Completo`, `Cultura Bacteriana`, `Dosagem de Glicose`, `Urinálise`

## Endpoints

| Requisito | Método e rota | Descrição |
|---|---|---|
| F1 | `POST /documentos` | Upload do arquivo (multipart) com metadados |
| F2, F7 | `GET /documentos` | Lista documentos; filtros combináveis `categoria`, `laboratorio`, `equipamento`, `experimento` |
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

- **F5 (atualização):** só os campos enviados são alterados. `sha256`, `tamanho`, `nome_armazenado` e o arquivo físico não são modificados. A alteração é gravada no JSON e registrada no log.
- **F6 (exclusão):** remove o registro do JSON **e** o arquivo físico. Se o arquivo físico já não existir, o registro é removido mesmo assim. A resposta é `204 No Content`.
- **F14 (backup geral):** cada backup recebe um nome com data e hora (`backup_AAAAMMDD_HHMMSS.zip`), então um novo backup não sobrescreve os anteriores. Fica em `storage/backups/` e contém todo o conteúdo de `storage/`, exceto os backups anteriores.
- **F15 (listagem):** lista apenas os backups gerais de `storage/backups/`. Os backups seletivos ficam em `storage/exports/`.
- **F16 (backup seletivo):** informe **apenas um** filtro, `equipamento` ou `experimento`. O `.zip` é salvo em `storage/exports/` com os arquivos correspondentes e um `metadados.json` só com esses documentos.

## Tratamento de erros (F17)

| Código | Quando ocorre |
|---|---|
| `201` | Documento criado |
| `204` | Documento removido |
| `400` | Backup seletivo sem filtro, com os dois filtros ou sem documentos correspondentes |
| `404` | Documento, arquivo físico ou recurso não encontrado |
| `422` | Dados inválidos: enum fora da lista, campo obrigatório ausente, texto fora do tamanho permitido |

## Logs

Os eventos ficam em `storage/logs/app.log`: inicialização, upload, atualização, exclusão, backups e exportação CSV.

## Como demonstrar (roteiro rápido)

1. `GET /documentos`: listar os documentos populados.
2. `GET /documentos?equipamento=Centrífuga`: filtrar por equipamento.
3. `GET /documentos/estatisticas`: ver as métricas.
4. `PUT /documentos/{id}` e depois `GET /documentos/{id}`: ver a atualização.
5. `GET /documentos/{id}/integridade` e `GET /integridade`.
6. `GET /exportar/csv`.
7. `POST /backup` e `GET /backups`.
8. **F16:** `POST /backup/seletivo?experimento=Cultura Bacteriana` e conferir o `.zip` em `storage/exports/`.
9. `DELETE /documentos/{id}` e confirmar que o arquivo sumiu de `storage/documentos/`.

## Decisões de projeto

- **JSON no lugar de banco de dados:** o enunciado não permite banco. `app/db.py` cumpre o papel da camada de dados.
- **Enums no lugar de chaves estrangeiras:** garantem valores sempre válidos para laboratório, equipamento e experimento e deixam os filtros (F7) e o F16 consistentes.
- **SHA-256:** serve para a verificação de integridade (F9 e F10).
- **Nome de armazenamento com UUID:** evita colisão entre arquivos com o mesmo nome original.

## Limitações conhecidas

- Cada operação lê e regrava o JSON inteiro, e isso não é atômico. Dois envios simultâneos podem fazer um registro se perder. Com um banco de dados, uma transação resolveria isso.
- A listagem de documentos não tem paginação.
