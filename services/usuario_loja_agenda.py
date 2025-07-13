from fastapi import HTTPException
from sqlmodel import select
from connection import SessionDep
from model.usuario_loja_agenda import UsuarioLojaAgenda
from model.usuario import Usuario
from model.loja import Loja

def valida_usuario_loja_agenda(data, session: SessionDep):
    usuario = session.exec(select(Usuario).where(Usuario.id == data.id_usuario)).first()
    if not usuario:
        raise HTTPException(400, detail="Usuário não encontrado")
    loja = session.exec(select(Loja).where(Loja.id == data.id_loja)).first()
    if not loja:
        raise HTTPException(400, detail="Loja não encontrada")
    # Não permitir duplicidade de agenda para mesmo usuário, loja, dia da semana e período
    agenda_existente = session.exec(
        select(UsuarioLojaAgenda).where(
            UsuarioLojaAgenda.id_usuario == data.id_usuario,
            UsuarioLojaAgenda.id_loja == data.id_loja,
            UsuarioLojaAgenda.dia_semana == data.dia_semana,
            UsuarioLojaAgenda.periodo == data.periodo
        )
    ).first()
    if agenda_existente:
        raise HTTPException(400, detail="Agenda já cadastrada para este usuário, loja, dia da semana e período") 