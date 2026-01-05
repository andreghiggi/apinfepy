from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqladmin import Admin, ModelView
from models import Base, Empresa, NotaFiscal, NotaStatus, TipoNota
from routes import router
import uvicorn

import os

# Na Vercel, o SQLite não é persistente. 
# Para produção, você deve usar uma variável de ambiente DATABASE_URL (PostgreSQL/MySQL)
# Se não houver, ele usa o SQLite local (apenas para teste, os dados somem ao reiniciar)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nfe.db")

if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar as tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Notas Fiscais (NFe/NFCe)",
    description="API para emissão de Notas Fiscais Eletrônicas (NFe) e Notas Fiscais de Consumidor Eletrônicas (NFCe)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Incluir rotas da API
app.include_router(router)

# Configuração do SQLAdmin (Interface Web de Administração)
admin = Admin(app, engine)

class EmpresaAdmin(ModelView, model=Empresa):
    column_list = [Empresa.id, Empresa.razao_social, Empresa.cnpj, Empresa.ambiente]
    form_columns = [Empresa.razao_social, Empresa.cnpj, Empresa.inscricao_estadual, Empresa.certificado_senha, Empresa.ambiente]
    name = "Empresa"
    name_plural = "Empresas"
    icon = "fa-solid fa-building"

class NotaFiscalAdmin(ModelView, model=NotaFiscal):
    column_list = [NotaFiscal.id, NotaFiscal.tipo, NotaFiscal.status, NotaFiscal.numero, NotaFiscal.data_emissao, NotaFiscal.valor_total]
    name = "Nota Fiscal"
    name_plural = "Notas Fiscais"
    icon = "fa-solid fa-file-invoice-dollar"

admin.add_view(EmpresaAdmin)
admin.add_view(NotaFiscalAdmin)

# Dependência para obter a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "message": "API de Notas Fiscais ativa",
        "admin_url": "/admin",
        "docs_url": "/docs",
        "versao": "1.0.0"
    }
if __name__ == "__main__":
    print("\n" + "="*60)
    print("API de Notas Fiscais iniciada com sucesso!")
    print("="*60)
    print("\n📍 Acesse:")
    print("   - API Docs (Swagger): http://localhost:8000/docs")
    print("   - Admin Panel: http://localhost:8000/admin")
    print("   - API Root: http://localhost:8000")
    print("\n" + "="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
