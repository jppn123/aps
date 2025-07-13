from fastapi import HTTPException
from sqlmodel import select
from connection import SessionDep
from model.loja import Loja, CreateLoja

def valida_insere_loja(loja: CreateLoja, session: SessionDep):
    """Valida os dados para inserção de uma nova loja"""
    
    if not loja.nome or loja.nome.strip() == "":
        raise HTTPException(400, detail="Nome da loja é obrigatório")
    
    if not loja.endereco or loja.endereco.strip() == "":
        raise HTTPException(400, detail="Endereço da loja é obrigatório")
    
    # Verifica se já existe uma loja com o mesmo nome
    loja_existente = session.exec(select(Loja).where(Loja.nome == loja.nome)).first()
    if loja_existente:
        raise HTTPException(400, detail="Já existe uma loja com este nome")

def valida_tipo_usuario_coord(token_data: dict):
    """Valida se o usuário tem tipo 'coord'"""
    if token_data.get("tp_login") == "func":
        raise HTTPException(403, detail="Acesso negado. Apenas coordenadores podem acessar esta funcionalidade") 