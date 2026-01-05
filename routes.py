from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import Empresa, NotaFiscal, NotaStatus, TipoNota
from schemas import (
    CriarNotaFiscalSchema,
    NotaFiscalResponseSchema,
    EmpresaSchema,
    CriarEmpresaSchema,
)
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/v1", tags=["API"])

# Dependência para obter a sessão (será importada do main.py)
def get_db_dependency():
    from main import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============= ENDPOINTS DE EMPRESAS =============

@router.post("/empresas", response_model=EmpresaSchema, status_code=status.HTTP_201_CREATED)
def criar_empresa(empresa_data: CriarEmpresaSchema, db: Session = Depends(get_db_dependency)):
    """Criar uma nova empresa emissora de notas fiscais."""
    # Verificar se CNPJ já existe
    empresa_existente = db.query(Empresa).filter(Empresa.cnpj == empresa_data.cnpj).first()
    if empresa_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ já cadastrado no sistema"
        )
    
    nova_empresa = Empresa(
        razao_social=empresa_data.razao_social,
        cnpj=empresa_data.cnpj,
        inscricao_estadual=empresa_data.inscricao_estadual,
        certificado_senha=empresa_data.certificado_senha,
        ambiente=empresa_data.ambiente,
    )
    db.add(nova_empresa)
    db.commit()
    db.refresh(nova_empresa)
    return nova_empresa

@router.get("/empresas", response_model=List[EmpresaSchema])
def listar_empresas(db: Session = Depends(get_db_dependency)):
    """Listar todas as empresas cadastradas."""
    empresas = db.query(Empresa).all()
    return empresas

@router.get("/empresas/{empresa_id}", response_model=EmpresaSchema)
def obter_empresa(empresa_id: int, db: Session = Depends(get_db_dependency)):
    """Obter detalhes de uma empresa específica."""
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    return empresa

# ============= ENDPOINTS DE NOTAS FISCAIS =============

@router.post("/notas-fiscais", response_model=NotaFiscalResponseSchema, status_code=status.HTTP_201_CREATED)
def criar_nota_fiscal(nota_data: CriarNotaFiscalSchema, db: Session = Depends(get_db_dependency)):
    """
    Criar uma nova nota fiscal (NFe ou NFCe).
    
    Este endpoint recebe os dados da nota e a registra no sistema.
    A emissão efetiva será processada em segundo plano.
    """
    # Verificar se a empresa existe
    empresa = db.query(Empresa).filter(Empresa.id == nota_data.empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    # Calcular valor total
    valor_total = sum(item.valor_total for item in nota_data.itens)
    valor_total -= nota_data.desconto or 0
    valor_total += nota_data.frete or 0
    
    # Criar a nota fiscal
    nova_nota = NotaFiscal(
        empresa_id=nota_data.empresa_id,
        tipo=TipoNota(nota_data.tipo.value),
        status=NotaStatus.PENDENTE,
        numero=nota_data.numero,
        serie=nota_data.serie,
        data_emissao=nota_data.data_emissao or datetime.utcnow(),
        valor_total=valor_total,
    )
    
    db.add(nova_nota)
    db.commit()
    db.refresh(nova_nota)
    
    return NotaFiscalResponseSchema.model_validate(nova_nota)

@router.get("/notas-fiscais", response_model=List[NotaFiscalResponseSchema])
def listar_notas_fiscais(
    empresa_id: int = None,
    status_filtro: str = None,
    db: Session = Depends(get_db_dependency)
):
    """Listar notas fiscais com filtros opcionais."""
    query = db.query(NotaFiscal)
    
    if empresa_id:
        query = query.filter(NotaFiscal.empresa_id == empresa_id)
    
    if status_filtro:
        try:
            status_enum = NotaStatus(status_filtro)
            query = query.filter(NotaFiscal.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status inválido: {status_filtro}"
            )
    
    notas = query.all()
    return [NotaFiscalResponseSchema.model_validate(nota) for nota in notas]

@router.get("/notas-fiscais/{nota_id}", response_model=NotaFiscalResponseSchema)
def obter_nota_fiscal(nota_id: int, db: Session = Depends(get_db_dependency)):
    """Obter detalhes de uma nota fiscal específica."""
    nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
    if not nota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota fiscal não encontrada"
        )
    return NotaFiscalResponseSchema.model_validate(nota)

@router.post("/notas-fiscais/{nota_id}/emitir")
def emitir_nota_fiscal(nota_id: int, db: Session = Depends(get_db_dependency)):
    """
    Emitir uma nota fiscal pendente.
    
    Este endpoint inicia o processo de emissão da nota junto à SEFAZ.
    """
    nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
    if not nota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota fiscal não encontrada"
        )
    
    if nota.status != NotaStatus.PENDENTE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nota já foi processada. Status atual: {nota.status.value}"
        )
    
    # TODO: Integrar com PyNFe para emissão real
    # Por enquanto, apenas simulamos a emissão
    nota.status = NotaStatus.EMITIDA
    nota.chave_acesso = "35250100000000000000550010000000011234567890"  # Exemplo
    db.commit()
    db.refresh(nota)
    
    return {
        "id": nota.id,
        "status": nota.status.value,
        "chave_acesso": nota.chave_acesso,
        "mensagem": "Nota fiscal emitida com sucesso"
    }

@router.post("/notas-fiscais/{nota_id}/cancelar")
def cancelar_nota_fiscal(nota_id: int, db: Session = Depends(get_db_dependency)):
    """Cancelar uma nota fiscal emitida."""
    nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
    if not nota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota fiscal não encontrada"
        )
    
    if nota.status != NotaStatus.EMITIDA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas notas emitidas podem ser canceladas"
        )
    
    nota.status = NotaStatus.CANCELADA
    db.commit()
    db.refresh(nota)
    
    return {
        "id": nota.id,
        "status": nota.status.value,
        "mensagem": "Nota fiscal cancelada com sucesso"
    }

@router.get("/notas-fiscais/{nota_id}/xml")
def obter_xml_nota(nota_id: int, db: Session = Depends(get_db_dependency)):
    """Obter o XML da nota fiscal."""
    nota = db.query(NotaFiscal).filter(NotaFiscal.id == nota_id).first()
    if not nota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota fiscal não encontrada"
        )
    
    return {
        "id": nota.id,
        "xml_envio": nota.xml_envio,
        "xml_retorno": nota.xml_retorno,
    }
