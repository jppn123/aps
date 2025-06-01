from fastapi import APIRouter, HTTPException
from sqlmodel import select
from connection import SessionDep
from model.usuario import *

router = APIRouter(
    prefix="/usuario",
    tags=[Usuario.__name__]
)


@router.post("/criar")
def criar_usuario(usu: CreateUsuario, session: SessionDep):

    usua = session.exec(select(Usuario).where(Usuario.cpf == usu.cpf)).first()
    if usua:
        raise HTTPException(400, "CPF já cadastrado")
    
    usuario = Usuario.model_validate(usu)

    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.get("/getUsuario/{id_usuario}")
def retorna_usuario(id_usuario, session: SessionDep):
    usu = session.exec(select(Usuario).where(Usuario.id == id_usuario)).first()
    if not usu:
        raise HTTPException(404, "Usuário não encontrado")
    
    return usu


@router.put("/atualizar/{id_usuario}")
def criar_usuario(id_usuario, usu: UpdateUsuario, session: SessionDep):
    usuario = retorna_usuario(id_usuario, session) 
    usua = usu.model_dump(exclude_none=True)
    usuario.sqlmodel_update(usua)

    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario