from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqladmin import Admin, ModelView
from models import Base, Empresa, NotaFiscal, NotaStatus, TipoNota
from routes import router
import os

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
# Na Vercel, o sistema de arquivos é somente leitura. 
# Se não houver DATABASE_URL, usamos o SQLite na pasta /tmp (única pasta com permissão de escrita)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Dados da Umbler fornecidos pelo usuário
    DATABASE_URL = "mysql+pymysql://apinfepy:k7m2y9u4@mysql741.umbler.com:41890/apinfepy"
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
elif DATABASE_URL.startswith("mysql://"):
    # Garante o uso do driver pymysql para MySQL
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# Configuração do Engine
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(
    DATABASE_URL, 
    connect_args=connect_args,
    pool_pre_ping=True  # Ajuda a manter a conexão viva com MySQL externo
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar as tabelas na inicialização
Base.metadata.create_all(bind=engine)

# --- INICIALIZAÇÃO DO APP ---
app = FastAPI(
    title="API de Notas Fiscais (NFe/NFCe)",
    description="API para emissão de Notas Fiscais Eletrônicas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Incluir rotas da API
app.include_router(router)

# --- CONFIGURAÇÃO DO ADMIN ---
admin = Admin(app, engine, title="Admin NFe")

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

@app.get("/")
def read_root():
    return {
        "message": "API de Notas Fiscais ativa",
        "admin_url": "/admin",
        "docs_url": "/docs",
        "database": "SQLite (Temporário)" if "sqlite" in DATABASE_URL else "Externo"
    }

# Para rodar localmente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
