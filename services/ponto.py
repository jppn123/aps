from fastapi import HTTPException
from sqlmodel import select
from connection import SessionDep
from model.ponto import CreatePonto, UpdatePonto
from model.usuario import Usuario
from model.loja import Loja

def valida_registrar_ponto(ponto: CreatePonto, session: SessionDep):
    # Verifica se o usuário existe
    usuario = session.exec(select(Usuario).where(Usuario.id == ponto.id_usuario)).first()
    if not usuario:
        raise HTTPException(400, detail="Usuário não encontrado")
    
    # Verifica se a loja existe (apenas se id_loja for fornecido)
    if ponto.id_loja is not None:
        loja = session.exec(select(Loja).where(Loja.id == ponto.id_loja)).first()
        if not loja:
            raise HTTPException(400, detail="Loja não encontrada")

def valida_atualizar_ponto(ponto: UpdatePonto, session: SessionDep):
    # Se id_loja está sendo atualizado, verifica se a loja existe
    if ponto.id_loja is not None:
        loja = session.exec(select(Loja).where(Loja.id == ponto.id_loja)).first()
        if not loja:
            raise HTTPException(400, detail="Loja não encontrada")
