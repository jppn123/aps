from fastapi import APIRouter, HTTPException
from sqlmodel import select
from connection import SessionDep
from model.usuario import *
from services.usuario import *
from model.login import Login

router = APIRouter(
    prefix="/usuario",
    tags=[Usuario.__name__]
)


@router.post("/criar")
def criar_usuario(usu: CreateUsuario, session: SessionDep):

    valida_insere_usuario(usu, session)

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

@router.get("/getUsuarioPorEmail/{email}")
def retorna_usuario_por_email(email: str, session: SessionDep):    
    
    # Primeiro busca o login pelo email
    login = session.exec(select(Login).where(Login.email == email)).first()
    if not login:
        raise HTTPException(404, "Usuário não encontrado")
    
    # Depois busca o usuário pelo id_login
    usuario = session.exec(select(Usuario).where(Usuario.id_login == login.id)).first()
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado")
    
    return usuario

@router.get("/getLoginUsuario/{id_usuario}")
def get_email_usuario(id_usuario: int, session: SessionDep):
    usuario = session.exec(select(Usuario).where(Usuario.id == id_usuario)).first()
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado")
    login = session.exec(select(Login).where(Login.id == usuario.id_login)).first()
    if not login:
        raise HTTPException(404, "Login não encontrado para este usuário")
    return {"email": login.email, "tipo": login.tipo}

