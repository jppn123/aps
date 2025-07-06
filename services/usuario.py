from fastapi import HTTPException
from sqlmodel import select
from connection import SessionDep
from services.token import *
from model.usuario import Usuario, CreateUsuario   

def valida_insere_usuario(usu:Usuario, session:SessionDep):
    NOME_INVALIDO = "Nome Inválido"
    EMAIL_CADASTRADO = "Email já cadastrado"
    EMAIL_INVALIDO = "Email inválido"

    if usu.nome == "" or usu.cpf == "" or usu.data_nascimento == "":
        raise HTTPException(400, detail="Dados inválidos")
    
    
    usua = session.exec(select(Usuario).where(Usuario.cpf == usu.cpf)).first()
    if usua:
        raise HTTPException(400, "CPF já cadastrado")