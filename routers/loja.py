from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from connection import SessionDep
from model.loja import *
from services.loja import *
from services.token import valida_token
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated

security = HTTPBearer()

router = APIRouter(
    prefix="/loja",
    tags=[Loja.__name__]
)

@router.post("/criar")
def criar_loja(
    loja: CreateLoja, 
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """Cria uma nova loja - apenas coordenadores"""
    token_data = valida_token(credentials.credentials)
    valida_tipo_usuario_coord(token_data)
    
    valida_insere_loja(loja, session)
    
    nova_loja = Loja.model_validate(loja)
    session.add(nova_loja)
    session.commit()
    session.refresh(nova_loja)
    
    return nova_loja

@router.get("/listar")
def listar_lojas(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """Lista todas as lojas - apenas coordenadores"""
    token_data = valida_token(credentials.credentials)
    valida_tipo_usuario_coord(token_data)
    
    lojas = session.exec(select(Loja)).all()
    
    # Retorna apenas os campos id, nome e endereco
    lojas_simplificadas = []
    for loja in lojas:
        lojas_simplificadas.append({
            "id": loja.id,
            "nome": loja.nome,
            "endereco": loja.endereco
        })
    
    return lojas_simplificadas

@router.get("/getLoja/{id_loja}")
def retorna_loja(
    id_loja: int,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """Retorna uma loja específica - apenas coordenadores"""
    token_data = valida_token(credentials.credentials)
    valida_tipo_usuario_coord(token_data)
    
    loja = session.exec(select(Loja).where(Loja.id == id_loja)).first()
    if not loja:
        raise HTTPException(404, detail="Loja não encontrada")
    
    return loja

@router.put("/atualizar/{id_loja}")
def atualizar_loja(
    id_loja: int,
    loja: UpdateLoja,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """Atualiza uma loja - apenas coordenadores"""
    token_data = valida_token(credentials.credentials)
    valida_tipo_usuario_coord(token_data)
    
    loja_existente = session.exec(select(Loja).where(Loja.id == id_loja)).first()
    if not loja_existente:
        raise HTTPException(404, detail="Loja não encontrada")
    
    # Se o nome está sendo alterado, verifica se já existe outra loja com o mesmo nome
    if loja.nome and loja.nome != loja_existente.nome:
        loja_duplicada = session.exec(select(Loja).where(Loja.nome == loja.nome)).first()
        if loja_duplicada:
            raise HTTPException(400, detail="Já existe uma loja com este nome")
    
    # Atualiza apenas os campos fornecidos
    dados_atualizados = loja.model_dump(exclude_none=True)
    for campo, valor in dados_atualizados.items():
        setattr(loja_existente, campo, valor)
    
    session.add(loja_existente)
    session.commit()
    session.refresh(loja_existente)
    
    return loja_existente

@router.delete("/deletar/{id_loja}")
def deletar_loja(
    id_loja: int,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """Deleta uma loja - apenas coordenadores"""
    token_data = valida_token(credentials.credentials)
    valida_tipo_usuario_coord(token_data)
    
    loja = session.exec(select(Loja).where(Loja.id == id_loja)).first()
    if not loja:
        raise HTTPException(404, detail="Loja não encontrada")
    
    session.delete(loja)
    session.commit()
    
    return {"mensagem": "Loja deletada com sucesso"} 