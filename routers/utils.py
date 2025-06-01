from fastapi import APIRouter
from services.login import criptografa, descriptografa

router = APIRouter(
    prefix="/utils",
    tags=["Utils"]
)


@router.get("/codificarSenha")
def codificar_senha(senha):
    
    return criptografa(senha)

@router.get("/decodificarSenha")
def codificar_senha(senha):
    
    return descriptografa(senha)

    
    