from datetime import datetime, timedelta
from fastapi import HTTPException
import jwt
import cryptocode


KEY = "secret"

def cria_token(id_usuario = None, params = None, minutos = 60):
    date = datetime.now() + timedelta(minutes=minutos)
    json = {
        "exp": date.strftime("%Y%m%d%H%M%S")
    }
    if id_usuario:
        json.update({"id_usu": id_usuario})
    if params:
        json.update(**params)
    
    jwtToken = jwt.encode(json, key=KEY)

    return jwtToken

def obtem_dados_token(token):
    header_data = jwt.get_unverified_header(token)
    tokenData = jwt.decode(token, key=KEY, algorithms=[header_data['alg'],])
    return tokenData

def valida_token(token):
    tokenData = obtem_dados_token(token)
    if(tokenData["exp"] < datetime.now().strftime("%Y%m%d%H%M%S")):
        raise HTTPException(400, "Token Expirado")
    return tokenData
    
def expira_token(token):
    tokenData = obtem_dados_token(token)
    tokenData["exp"] = datetime.now().strftime("%Y%m%d%H%M%S")
    return tokenData

def criptografa(senha):
    return cryptocode.encrypt(senha, KEY)

def descriptografa(senha):
    return cryptocode.decrypt(senha, KEY)
