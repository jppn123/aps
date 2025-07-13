from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from connection import SessionDep
from model.foto_ponto import FotoPonto, CreateFotoPonto, UpdateFotoPonto
from services.foto_ponto import valida_foto_ponto, valida_atualizar_foto_ponto
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated
from datetime import datetime

security = HTTPBearer()

router = APIRouter(
    prefix="/foto-ponto",
    tags=["FotoPonto"]
)

@router.post("/adicionar")
def adicionar_foto_ponto(
    foto_ponto: CreateFotoPonto,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    valida_foto_ponto(foto_ponto, session)
    
    # Se data_criacao não for fornecida, define automaticamente
    if not foto_ponto.data_criacao:
        foto_ponto.data_criacao = datetime.now().isoformat()
    
    nova_foto = FotoPonto.model_validate(foto_ponto)
    session.add(nova_foto)
    session.commit()
    session.refresh(nova_foto)
    return {"mensagem": "Foto adicionada com sucesso"}

@router.delete("/remover/{id_foto}")
def remover_foto_ponto(
    id_foto: int,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    foto = session.exec(select(FotoPonto).where(FotoPonto.id == id_foto)).first()
    if not foto:
        raise HTTPException(404, detail="Foto não encontrada")
    session.delete(foto)
    session.commit()
    return {"mensagem": "Foto removida com sucesso"}

@router.get("/getFotosPonto/{id_ponto}")
def get_fotos_ponto(
    id_ponto: int,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    fotos = session.exec(select(FotoPonto).where(FotoPonto.id_ponto == id_ponto)).all()
    return fotos

@router.get("/getFoto/{id_foto}")
def get_foto_ponto(
    id_foto: int,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    foto = session.exec(select(FotoPonto).where(FotoPonto.id == id_foto)).first()
    if not foto:
        raise HTTPException(404, detail="Foto não encontrada")
    return foto

@router.put("/atualizar/{id_foto}")
def atualizar_foto_ponto(
    id_foto: int,
    foto_ponto: UpdateFotoPonto,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    foto_obj = session.exec(select(FotoPonto).where(FotoPonto.id == id_foto)).first()
    if not foto_obj:
        raise HTTPException(404, detail="Foto não encontrada")
    valida_atualizar_foto_ponto(foto_ponto, session)
    foto_data = foto_ponto.model_dump(exclude_none=True)
    foto_obj.sqlmodel_update(foto_data)
    session.add(foto_obj)
    session.commit()
    session.refresh(foto_obj)
    return foto_obj 