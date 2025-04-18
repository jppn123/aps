from fastapi import APIRouter, HTTPException, Depends, security
from sqlmodel import select
from connection import SessionDep
from model.login import *
from model.usuario import *
from services.token import *
from services.login import *
from services.email import *
from fastapi.security import HTTPAuthorizationCredentials
from typing import Annotated

securit = security.HTTPBearer()

router = APIRouter(
    prefix="/login",
    tags=[Login.__name__]
    
)

@router.get("/validarToken")
def validar_token(token: Annotated[HTTPAuthorizationCredentials, Depends(securit)]):
    return valida_token(token.credentials)

#adm
@router.post("/criar", dependencies=[Depends(securit)])
def criar_login(log: CreateLogin, session: SessionDep):
    login = Login.model_validate(log)
    valida_insere_email(log.email, session)
    valida_insere_senha(log.senha, log.conf_senha)
    login.senha = criptografa(log.senha)

    session.add(login)
    session.commit()
    session.refresh(login)
    
    return {"mensagem": "Login criado com sucesso"}


#sem token
@router.post("/entrar")
def entrar(log:EntrarLogin, session: SessionDep):

    login = session.exec(select(Login).where(Login.email == log.email)).first()
    if not login:
        raise HTTPException(404, detail="Login inválido")
    
    print(log.senha)
    validar_senha(log.senha, login.senha)
    usuario = session.exec(select(Usuario).where(Usuario.id_login == login.id)).first()
    if not usuario:
        token = cria_token(params={"id_login":login.id})
    else:
        token = cria_token(usuario.id)

    return {"token": token}

'''
envia o token para o frontend realizar a validação, posteriormente irei tratar isso no backend com redis

email: email da pessoa que vai solicitar a troca da senha
'''
@router.post('/enviarEmail')
async def enviar_email(rec:RecuperarSenha, session: SessionDep):
    nomeUsuario = ""

    login = session.exec(select(Login).where(Login.email == rec.email)).first()
    if not login:
        raise HTTPException(400, detail="Email inexistente")
    
    usuario = session.exec(select(Usuario).where(Usuario.id_login == login.id)).first()
    if usuario:
        nomeUsuario = usuario.nome
    
    codigoAutenticacao = await send_email_async('Redefinição de senha', login.email, nomeUsuario)
    
    
    return {"token": cria_token(params={"id_login": login.id, "codigoAutenticacao": str(codigoAutenticacao)})}


@router.post('/validarCodigo')
def validar_codigo(cod: VerificarCodigo, token: Annotated[HTTPAuthorizationCredentials, Depends(securit)]):
    tokenData = validar_token(token)
    
    if tokenData["codigoAutenticacao"] != cod.codigo:
        raise HTTPException(400, detail="Código inválido")


@router.post("/mudarSenha")
def mudar_senha(senha: MudarSenha, session: SessionDep, token: Annotated[HTTPAuthorizationCredentials, Depends(securit)]):
    #validar o tempo do token 10min e coletar o id_login para fazer a troca da senha caso todos os passos sejam atendidos
    tokenData = validar_token(token)
    
    login = session.exec(select(Login).where(Login.id == tokenData["id_login"])).first()
    #nunca chega aqui, é pra teste
    if not login:
        raise HTTPException(404, detail="login inexistente")
    
    valida_insere_senha(senha.senhaNova, senha.senhaNovaConfirmada)
    validar_senha(senha.senhaAntiga, login.senha)

    login.senha = criptografa(senha.senhaNova)
    session.add(login)
    session.commit()
    session.refresh(login)
    return login

