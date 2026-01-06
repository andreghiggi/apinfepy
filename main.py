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

# Criar as tabelas na inicialização (Apenas se não estiver na Vercel para evitar timeout)
if not os.getenv("VERCEL"):
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

# --- CONFIGURAÇÃO DO ADMIN (Comentado temporariamente para isolar erro 500) ---
# admin = Admin(app, engine, title="Admin NFe")
# admin.add_view(EmpresaAdmin)
# admin.add_view(NotaFiscalAdmin)

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
