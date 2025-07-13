from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from connection import SessionDep
from model.usuario_loja_agenda import UsuarioLojaAgenda
from services.usuario_loja_agenda import valida_usuario_loja_agenda
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated

security = HTTPBearer()

router = APIRouter(
    prefix="/usuario-loja-agenda",
    tags=["UsuarioLojaAgenda"]
)

@router.post("/adicionar")
def adicionar_agenda(
    agenda: UsuarioLojaAgenda,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    valida_usuario_loja_agenda(agenda, session)
    nova_agenda = UsuarioLojaAgenda.model_validate(agenda)
    session.add(nova_agenda)
    session.commit()
    session.refresh(nova_agenda)
    return {"mensagem": "Agenda adicionada com sucesso"}

@router.delete("/remover")
def remover_agenda(
    id_usuario: int,
    id_loja: int,
    dia_semana: int,
    periodo: int,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    agenda = session.exec(select(UsuarioLojaAgenda).where(
        UsuarioLojaAgenda.id_usuario == id_usuario,
        UsuarioLojaAgenda.id_loja == id_loja,
        UsuarioLojaAgenda.dia_semana == dia_semana,
        UsuarioLojaAgenda.periodo == periodo
    )).first()
    if not agenda:
        raise HTTPException(404, detail="Agenda não encontrada")
    session.delete(agenda)
    session.commit()
    return {"mensagem": "Agenda removida com sucesso"}

@router.get("/getAgendaUsuarioLoja/{id_usuario}/{id_loja}")
def get_agenda_usuario_loja(
    id_usuario: int,
    id_loja: int,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    agenda = session.exec(select(UsuarioLojaAgenda).where(
        UsuarioLojaAgenda.id_usuario == id_usuario,
        UsuarioLojaAgenda.id_loja == id_loja
    )).all()
    return agenda

@router.get("/getUsuariosLojaDiaSemana/{id_loja}/{dia_semana}/{periodo}")
def get_usuarios_loja_dia_semana(
    id_loja: int,
    dia_semana: int,
    periodo: int,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    agendas = session.exec(select(UsuarioLojaAgenda).where(
        UsuarioLojaAgenda.id_loja == id_loja,
        UsuarioLojaAgenda.dia_semana == dia_semana,
        UsuarioLojaAgenda.periodo == periodo
    )).all()
    return agendas 