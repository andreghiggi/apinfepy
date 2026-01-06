import os
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware

# Importações locais
from models import Base, Empresa, NotaFiscal
from routes import router

# 1. Configuração do Banco de Dados (MySQL Umbler Forçado)
# Usamos mysql+pymysql para garantir o driver correto
DATABASE_URL = "mysql+pymysql://apinfepy:k7m2y9u4@mysql741.umbler.com:41890/apinfepy"

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    pool_recycle=3600
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Inicialização do FastAPI
app = FastAPI(title="API NFe")
app.add_middleware(SessionMiddleware, secret_key="uma-chave-muito-secreta-123")
app.include_router(router)

# 3. Autenticação do Admin
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form.get("username"), form.get("password")
        if username == "admin" and password == "admin123":
            request.session.update({"token": "ok"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return "token" in request.session

auth_backend = AdminAuth(secret_key="uma-chave-muito-secreta-123")

# 4. Configuração do SQLAdmin
admin = Admin(app, engine, authentication_backend=auth_backend, title="Painel NFe")

class EmpresaAdmin(ModelView, model=Empresa):
    column_list = [Empresa.id, Empresa.razao_social, Empresa.cnpj]
    name = "Empresa"
    name_plural = "Empresas"

class NotaFiscalAdmin(ModelView, model=NotaFiscal):
    column_list = [NotaFiscal.id, NotaFiscal.numero, NotaFiscal.status]
    name = "Nota Fiscal"
    name_plural = "Notas Fiscais"

admin.add_view(EmpresaAdmin)
admin.add_view(NotaFiscalAdmin)

@app.get("/")
async def root():
    return {"status": "online", "admin": "/admin"}
