from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from connection import SessionDep
from model.usuario_time import *
from model.usuario import Usuario
from model.time import Time
from model.login import Login
from services.usuario_time import *
from services.token import valida_token
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated

security = HTTPBearer()

router = APIRouter(
    prefix="/usuario-time",
    tags=["UsuarioTime"]
)

@router.post("/adicionar")
def adicionar_usuario_time(
    usuario_time: CreateUsuarioTime,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """Adiciona um usuário a um time - apenas coordenadores"""
    token_data = valida_token(credentials.credentials)
    valida_tipo_usuario_coord(token_data)
    
    valida_insere_usuario_time(usuario_time, session)
    
    novo_relacionamento = UsuarioTime.model_validate(usuario_time)
    session.add(novo_relacionamento)
    session.commit()
    session.refresh(novo_relacionamento)
    
    return {"mensagem": "Usuário adicionado ao time com sucesso"}

@router.delete("/remover")
def remover_usuario_time(
    id_usuario: int,
    id_time: int,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """Remove um usuário de um time - apenas coordenadores"""
    token_data = valida_token(credentials.credentials)
    valida_tipo_usuario_coord(token_data)
    
    valida_remove_usuario_time(id_usuario, id_time, session)
    
    relacionamento = session.exec(
        select(UsuarioTime).where(
            UsuarioTime.id_usuario == id_usuario,
            UsuarioTime.id_time == id_time
        )
    ).first()
    
    session.delete(relacionamento)
    session.commit()
    
    return {"mensagem": "Usuário removido do time com sucesso"}

@router.get("/getUsuariosTime/{id_time}")
def get_usuarios_time(
    id_time: int,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    token_data = valida_token(credentials.credentials)
    
    # Verifica se o time existe
    time = session.exec(select(Time).where(Time.id == id_time)).first()
    if not time:
        raise HTTPException(404, detail="Time não encontrado")
    
    # Busca relacionamentos do time
    relacionamentos = session.exec(
        select(UsuarioTime).where(UsuarioTime.id_time == id_time)
    ).all()
    
    # Busca dados dos usuários
    usuarios = []
    for rel in relacionamentos:
        usuario = session.exec(select(Usuario).where(Usuario.id == rel.id_usuario)).first()
        if usuario:
            # Busca o tipo do usuário na tabela de login
            login = session.exec(select(Login).where(Login.id == usuario.id_login)).first()
            tipo_usuario = login.tipo if login else None
            usuarios.append({
                "id": usuario.id,
                "nome": usuario.nome,
                "cpf": usuario.cpf,
                "telefone": usuario.telefone,
                "tipo": tipo_usuario
            })
    
    def sort_key(u):
        if u["tipo"] == "admin":
            return 0
        elif u["tipo"] == "coord":
            return 1
        else:
            return 2
    usuarios.sort(key=sort_key)
    return {
        "time": {
            "id": time.id,
            "nome": time.nome,
            "descricao": time.descricao
        },
        "usuarios": usuarios
    }

@router.get("/getTimesUsuario/{id_usuario}")
def get_times_usuario(
    id_usuario: int,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    token_data = valida_token(credentials.credentials)
    
    # Verifica se o usuário existe
    usuario = session.exec(select(Usuario).where(Usuario.id == id_usuario)).first()
    if not usuario:
        raise HTTPException(404, detail="Usuário não encontrado")
    
    # Busca relacionamentos do usuário
    relacionamentos = session.exec(
        select(UsuarioTime).where(UsuarioTime.id_usuario == id_usuario)
    ).all()
    
    # Busca dados dos times
    times = []
    for rel in relacionamentos:
        time = session.exec(select(Time).where(Time.id == rel.id_time)).first()
        if time and time.deletado != 1:
            times.append({
                "id": time.id,
                "nome": time.nome,
                "descricao": time.descricao
            })
    
    return {
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "cpf": usuario.cpf
        },
        "times": times
    } 