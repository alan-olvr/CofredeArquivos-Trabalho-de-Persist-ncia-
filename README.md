# 🏛️ Cofre Digital de Arquivos - Tema 14

Sistema de gerenciamento, armazenamento e verificação de integridade de documentos digitais de laboratórios desenvolvido com **Python** e **FastAPI**.

---

## 🚀 Funcionalidades

- **CRUD de Documentos**: Upload, consulta por filtros (laboratório, equipamento, experimento), busca por ID e download do arquivo físico.
- **Exportação de Dados**: Geração de relatórios em formato CSV.
- **Gerenciamento de Backups**: Backup total compactado em `.zip` e backups seletivos por filtro.
- **Integridade & Segurança**: Validação de hashes SHA256 dos arquivos físicos contra registros em metadados.
- **Estatísticas**: Métricas automatizadas sobre uso de armazenamento e quantidade de arquivos por categoria.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3.10+
- **Framework**: FastAPI
- **Servidor ASGI**: Uvicorn
- **Validação de Dados**: Pydantic
- **Persistência**: Arquivos locais e `storage/metadados.json`

---

