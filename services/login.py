from fastapi import HTTPException
from sqlmodel import select
from connection import SessionDep
from services.token import *
from model.login import Login

def validar_senha(senhaInserida, senhaAtual):
    SENHA_INVALIDA = "Senha inválida"
    senhaAtual = descriptografa(senhaAtual)
    if senhaAtual != senhaInserida:
        raise HTTPException(400, detail=SENHA_INVALIDA)


def valida_insere_senha(senha, conf_senha):
    MIN_SENHA = 5
    TAMANHO_INVALIDO_SENHA = f"A senha deve ter no mínimo {MIN_SENHA} caracteres"
    SENHAS_DIFERENTES = "Senhas diferentes"
    if len(senha) < MIN_SENHA:
        raise HTTPException(400, detail=TAMANHO_INVALIDO_SENHA)
    if senha != conf_senha:
        raise HTTPException(400, detail=SENHAS_DIFERENTES)

def valida_insere_email(email, session:SessionDep):
    MIN_LOGIN = 2
    MAX_LOGIN = 15
    EMAIL_INVALIDO = "Email inválido"
    EMAIL_CADASTRADO = "Email já cadastrado"
    if not "@" in email:
        raise HTTPException(400, detail=EMAIL_INVALIDO)
    
    emailSplitted = email.split("@")
    if len(emailSplitted[0]) < MIN_LOGIN:
        raise HTTPException(400, detail=EMAIL_INVALIDO)
    elif len(emailSplitted[0]) > MAX_LOGIN:
        raise HTTPException(400, detail=EMAIL_INVALIDO)
    
    emailSplitted = emailSplitted[1].split(".")
    if len(emailSplitted) < 1:
        raise HTTPException(400, detail=EMAIL_INVALIDO)
    if len(emailSplitted[0]) < MIN_LOGIN:
        raise HTTPException(400, detail=EMAIL_INVALIDO)

    login = session.exec(select(Login).where(Login.email == email)).first()
    if login:
        raise HTTPException(400, detail=EMAIL_CADASTRADO)