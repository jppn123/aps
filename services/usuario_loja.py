from fastapi import HTTPException
from sqlmodel import select
from connection import SessionDep
from model.usuario_loja import UsuarioLoja, CreateUsuarioLoja
from model.usuario import Usuario
from model.loja import Loja

def valida_insere_usuario_loja(usuario_loja: CreateUsuarioLoja, session: SessionDep):
    usuario = session.exec(select(Usuario).where(Usuario.id == usuario_loja.id_usuario)).first()
    if not usuario:
        raise HTTPException(400, detail="Usuário não encontrado")
    loja = session.exec(select(Loja).where(Loja.id == usuario_loja.id_loja)).first()
    if not loja:
        raise HTTPException(400, detail="Loja não encontrada")
    relacionamento_existente = session.exec(
        select(UsuarioLoja).where(
            UsuarioLoja.id_usuario == usuario_loja.id_usuario,
            UsuarioLoja.id_loja == usuario_loja.id_loja
        )
    ).first()
    if relacionamento_existente:
        raise HTTPException(400, detail="Usuário já pertence a esta loja")

def valida_remove_usuario_loja(id_usuario: int, id_loja: int, session: SessionDep):
    relacionamento = session.exec(
        select(UsuarioLoja).where(
            UsuarioLoja.id_usuario == id_usuario,
            UsuarioLoja.id_loja == id_loja
        )
    ).first()
    if not relacionamento:
        raise HTTPException(400, detail="Usuário não pertence a esta loja") 