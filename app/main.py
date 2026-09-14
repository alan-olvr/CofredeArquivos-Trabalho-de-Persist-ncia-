from fastapi import FastAPI

app = FastAPI(title="Cofre Digital de Arquivos - Tema 14")

@app.get("/")
def raiz():
    return {"status": "ok", "projeto": "Cofre Digital de Arquivos"} 