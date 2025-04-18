from fastapi import APIRouter, HTTPException
from sqlmodel import select
from connection import SessionDep
from model.usuario import *
from services.token import *

router = APIRouter(
    prefix="/usuario",
    tags=[Usuario.__name__]
)


@router.post("/criar")
def criar_usuario(usu: CreateUsuario, session: SessionDep):

    usuario = Usuario.model_validate(usu)

    # session.add(usuario)
    # session.commit()
    session.refresh(usuario)
    return usuario


@router.get("/getUsuario/{id_usuario}")
def retorna_usuario(id_usuario, session: SessionDep):
    usu = session.exec(select(Usuario).where(Usuario.id == id_usuario)).first()
    if not usu:
        raise HTTPException(404, "Usuário não encontrado")
    
    return usu


@router.get("/criptografaSenha")
def criptografa_senha(senha):
    return criptografa(senha)