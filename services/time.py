from fastapi import HTTPException
from sqlmodel import select
from connection import SessionDep
from model.time import Time, CreateTime

def valida_insere_time(time: CreateTime, session: SessionDep):
    """Valida os dados para inserção de um novo time"""
    
    if not time.nome or time.nome.strip() == "":
        raise HTTPException(400, detail="Nome do time é obrigatório")
    
    # Verifica se já existe um time com o mesmo nome
    time_existente = session.exec(select(Time).where(Time.nome == time.nome)).first()
    if time_existente:
        raise HTTPException(400, detail="Já existe um time com este nome")

def valida_tipo_usuario_coord(token_data: dict):
    """Valida se o usuário tem tipo 'coord'"""
    if token_data.get("tp_login") == "func":
        raise HTTPException(403, detail="Acesso negado. Apenas coordenadores podem acessar esta funcionalidade") 