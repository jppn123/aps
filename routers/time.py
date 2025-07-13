from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from connection import SessionDep
from model.time import *
from services.time import *
from services.token import valida_token
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated

security = HTTPBearer()

router = APIRouter(
    prefix="/time",
    tags=[Time.__name__]
)

@router.post("/criar")
def criar_time(
    time: CreateTime, 
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    token_data = valida_token(credentials.credentials)
    valida_tipo_usuario_coord(token_data)
    
    valida_insere_time(time, session)
    
    novo_time = Time.model_validate(time)
    session.add(novo_time)
    session.commit()
    session.refresh(novo_time)
    
    return novo_time

@router.get("/listar")
def listar_times(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    token_data = valida_token(credentials.credentials)
    valida_tipo_usuario_coord(token_data)
    
    times = session.exec(select(Time).where(Time.deletado != 1)).all()
    
    # Retorna apenas os campos id, nome e descricao
    times_simplificados = []
    for time in times:
        times_simplificados.append({
            "id": time.id,
            "nome": time.nome,
        })
    
    return times_simplificados

@router.get("/getTime/{id_time}")
def retorna_time(
    id_time: int,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    token_data = valida_token(credentials.credentials)
    valida_tipo_usuario_coord(token_data)
    
    time = session.exec(select(Time).where(Time.id == id_time)).first()
    if not time:
        raise HTTPException(404, detail="Time não encontrado")
    
    return time

@router.put("/atualizar/{id_time}")
def atualizar_time(
    id_time: int,
    time: UpdateTime,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    token_data = valida_token(credentials.credentials)
    valida_tipo_usuario_coord(token_data)
    
    time_existente = session.exec(select(Time).where(Time.id == id_time)).first()
    if not time_existente:
        raise HTTPException(404, detail="Time não encontrado")
    
    # Se o nome está sendo alterado, verifica se já existe outro time com o mesmo nome
    if time.nome and time.nome != time_existente.nome:
        time_duplicado = session.exec(select(Time).where(Time.nome == time.nome)).first()
        if time_duplicado:
            raise HTTPException(400, detail="Já existe um time com este nome")
    
    # Atualiza apenas os campos fornecidos
    dados_atualizados = time.model_dump(exclude_none=True)
    for campo, valor in dados_atualizados.items():
        setattr(time_existente, campo, valor)
    
    session.add(time_existente)
    session.commit()
    session.refresh(time_existente)
    
    return time_existente

@router.delete("/deletar/{id_time}")
def deletar_time(
    id_time: int,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    token_data = valida_token(credentials.credentials)
    valida_tipo_usuario_coord(token_data)
    
    time = session.exec(select(Time).where(Time.id == id_time)).first()
    if not time:
        raise HTTPException(404, detail="Time não encontrado")
    
    session.delete(time)
    session.commit()
    
    return {"mensagem": "Time deletado com sucesso"}

 