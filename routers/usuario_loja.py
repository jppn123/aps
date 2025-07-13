from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from connection import SessionDep
from model.usuario_loja import *
from model.usuario import Usuario
from model.loja import Loja
from model.login import Login
from services.usuario_loja import *
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated

security = HTTPBearer()

router = APIRouter(
    prefix="/usuario-loja",
    tags=["UsuarioLoja"]
)

@router.post("/adicionar")
def adicionar_usuario_loja(
    usuario_loja: CreateUsuarioLoja,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    valida_insere_usuario_loja(usuario_loja, session)
    novo_relacionamento = UsuarioLoja.model_validate(usuario_loja)
    session.add(novo_relacionamento)
    session.commit()
    session.refresh(novo_relacionamento)
    return {"mensagem": "Usuário adicionado à loja com sucesso"}

@router.delete("/remover")
def remover_usuario_loja(
    id_usuario: int,
    id_loja: int,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    valida_remove_usuario_loja(id_usuario, id_loja, session)
    relacionamento = session.exec(
        select(UsuarioLoja).where(
            UsuarioLoja.id_usuario == id_usuario,
            UsuarioLoja.id_loja == id_loja
        )
    ).first()
    session.delete(relacionamento)
    session.commit()
    return {"mensagem": "Usuário removido da loja com sucesso"}

@router.get("/getUsuariosLoja/{id_loja}")
def get_usuarios_loja(
    id_loja: int,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    loja = session.exec(select(Loja).where(Loja.id == id_loja)).first()
    if not loja:
        raise HTTPException(404, detail="Loja não encontrada")
    relacionamentos = session.exec(
        select(UsuarioLoja).where(UsuarioLoja.id_loja == id_loja)
    ).all()
    usuarios = []
    for rel in relacionamentos:
        usuario = session.exec(select(Usuario).where(Usuario.id == rel.id_usuario)).first()
        if usuario:
            login = session.exec(select(Login).where(Login.id == usuario.id_login)).first()
            tipo_usuario = login.tipo if login else None
            usuarios.append({
                "id": usuario.id,
                "nome": usuario.nome,
                "cpf": usuario.cpf,
                "telefone": usuario.telefone,
                "tipo": tipo_usuario
            })
    def sort_key(u):
        if u["tipo"] == "admin":
            return 0
        elif u["tipo"] == "coord":
            return 1
        else:
            return 2
    usuarios.sort(key=sort_key)
    return {
        "loja": {
            "id": loja.id,
            "nome": loja.nome,
            "endereco": loja.endereco
        },
        "usuarios": usuarios
    }

@router.get("/getLojasUsuario/{id_usuario}")
def get_lojas_usuario(
    id_usuario: int,
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    usuario = session.exec(select(Usuario).where(Usuario.id == id_usuario)).first()
    if not usuario:
        raise HTTPException(404, detail="Usuário não encontrado")
    relacionamentos = session.exec(
        select(UsuarioLoja).where(UsuarioLoja.id_usuario == id_usuario)
    ).all()
    lojas = []
    for rel in relacionamentos:
        loja = session.exec(select(Loja).where(Loja.id == rel.id_loja)).first()
        if loja:
            lojas.append({
                "id": loja.id,
                "nome": loja.nome,
                "endereco": loja.endereco
            })
    return {
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "cpf": usuario.cpf
        },
        "lojas": lojas
    } 