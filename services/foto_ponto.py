from fastapi import HTTPException
from sqlmodel import select
from connection import SessionDep
from model.foto_ponto import CreateFotoPonto, UpdateFotoPonto
from model.ponto import Ponto

def valida_foto_ponto(foto_ponto: CreateFotoPonto, session: SessionDep):
    # Verifica se o ponto existe
    ponto = session.exec(select(Ponto).where(Ponto.id == foto_ponto.id_ponto)).first()
    if not ponto:
        raise HTTPException(400, detail="Ponto não encontrado")

def valida_atualizar_foto_ponto(foto_ponto: UpdateFotoPonto, session: SessionDep):
    # Validações específicas para atualização, se necessário
    pass 