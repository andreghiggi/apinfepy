from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TipoNotaSchema(str, Enum):
    NFE = "nfe"
    NFCE = "nfce"

class NotaStatusSchema(str, Enum):
    PENDENTE = "pendente"
    EMITIDA = "emitida"
    CANCELADA = "cancelada"
    ERRO = "erro"

class ItemNotaSchema(BaseModel):
    descricao: str = Field(..., description="Descrição do produto/serviço")
    quantidade: float = Field(..., gt=0, description="Quantidade")
    valor_unitario: float = Field(..., gt=0, description="Valor unitário")
    valor_total: float = Field(..., gt=0, description="Valor total do item")
    ncm: Optional[str] = Field(None, description="Código NCM")
    cfop: str = Field(..., description="CFOP")

class DestinatarioSchema(BaseModel):
    nome: str = Field(..., description="Nome ou Razão Social")
    cpf_cnpj: str = Field(..., description="CPF ou CNPJ")
    endereco: str = Field(..., description="Endereço")
    numero: str = Field(..., description="Número")
    complemento: Optional[str] = None
    bairro: str = Field(..., description="Bairro")
    cidade: str = Field(..., description="Cidade")
    uf: str = Field(..., min_length=2, max_length=2, description="UF")
    cep: str = Field(..., description="CEP")
    email: Optional[str] = None
    telefone: Optional[str] = None

class CriarNotaFiscalSchema(BaseModel):
    empresa_id: int = Field(..., description="ID da empresa emissora")
    tipo: TipoNotaSchema = Field(default=TipoNotaSchema.NFE, description="Tipo de nota")
    serie: int = Field(..., gt=0, description="Série da nota")
    numero: int = Field(..., gt=0, description="Número da nota")
    data_emissao: Optional[datetime] = None
    destinatario: DestinatarioSchema
    itens: List[ItemNotaSchema] = Field(..., min_items=1)
    desconto: Optional[float] = 0
    frete: Optional[float] = 0
    observacoes: Optional[str] = None

class NotaFiscalResponseSchema(BaseModel):
    id: int
    tipo: TipoNotaSchema
    status: NotaStatusSchema
    numero: int
    serie: int
    chave_acesso: Optional[str]
    data_emissao: datetime
    valor_total: float
    erro_mensagem: Optional[str]

    class Config:
        from_attributes = True

class EmpresaSchema(BaseModel):
    id: int
    razao_social: str
    cnpj: str
    inscricao_estadual: Optional[str]
    ambiente: int

    class Config:
        from_attributes = True

class CriarEmpresaSchema(BaseModel):
    razao_social: str = Field(..., description="Razão Social")
    cnpj: str = Field(..., description="CNPJ")
    inscricao_estadual: Optional[str] = None
    certificado_senha: str = Field(..., description="Senha do certificado")
    ambiente: int = Field(default=2, description="1=Produção, 2=Homologação")
