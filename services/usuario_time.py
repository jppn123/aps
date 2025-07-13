from fastapi import HTTPException
from sqlmodel import select
from connection import SessionDep
from model.usuario_time import UsuarioTime, CreateUsuarioTime
from model.usuario import Usuario
from model.time import Time

def valida_insere_usuario_time(usuario_time: CreateUsuarioTime, session: SessionDep):
    
    # Verifica se o usuário existe
    usuario = session.exec(select(Usuario).where(Usuario.id == usuario_time.id_usuario)).first()
    if not usuario:
        raise HTTPException(400, detail="Usuário não encontrado")
    
    # Verifica se o time existe
    time = session.exec(select(Time).where(Time.id == usuario_time.id_time)).first()
    if not time:
        raise HTTPException(400, detail="Time não encontrado")
    
    # Verifica se já existe o relacionamento
    relacionamento_existente = session.exec(
        select(UsuarioTime).where(
            UsuarioTime.id_usuario == usuario_time.id_usuario,
            UsuarioTime.id_time == usuario_time.id_time
        )
    ).first()
    
    if relacionamento_existente:
        raise HTTPException(400, detail="Usuário já pertence a este time")

def valida_remove_usuario_time(id_usuario: int, id_time: int, session: SessionDep):
    
    # Verifica se o relacionamento existe
    relacionamento = session.exec(
        select(UsuarioTime).where(
            UsuarioTime.id_usuario == id_usuario,
            UsuarioTime.id_time == id_time
        )
    ).first()
    
    if not relacionamento:
        raise HTTPException(400, detail="Usuário não pertence a este time")

def valida_tipo_usuario_coord(token_data: dict):
    if token_data.get("tp_login") == "func":
        raise HTTPException(403, detail="Acesso negado. Apenas coordenadores podem acessar esta funcionalidade") 