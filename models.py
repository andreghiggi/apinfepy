from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
# Removido import incorreto de create_all
import enum
from datetime import datetime

Base = declarative_base()

class NotaStatus(enum.Enum):
    PENDENTE = "pendente"
    EMITIDA = "emitida"
    CANCELADA = "cancelada"
    ERRO = "erro"

class TipoNota(enum.Enum):
    NFE = "nfe"
    NFCE = "nfce"

class Empresa(Base):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True, index=True)
    razao_social = Column(String(255), nullable=False)
    cnpj = Column(String(14), unique=True, index=True, nullable=False)
    inscricao_estadual = Column(String(20))
    certificado_pfx = Column(Text)  # Base64 do certificado
    certificado_senha = Column(String(100))
    ambiente = Column(Integer, default=2)  # 1=Produção, 2=Homologação

    notas = relationship("NotaFiscal", back_populates="empresa")

class NotaFiscal(Base):
    __tablename__ = "notas_fiscais"
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    tipo = Column(Enum(TipoNota), default=TipoNota.NFE)
    status = Column(Enum(NotaStatus), default=NotaStatus.PENDENTE)
    numero = Column(Integer)
    serie = Column(Integer)
    chave_acesso = Column(String(44), unique=True, index=True)
    xml_envio = Column(Text)
    xml_retorno = Column(Text)
    erro_mensagem = Column(Text)
    data_emissao = Column(DateTime, default=datetime.utcnow)
    valor_total = Column(Float)

    empresa = relationship("Empresa", back_populates="notas")
