from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from sqlalchemy import desc
from sqlmodel import select
from connection import SessionDep
from model.ponto import Ponto, CreatePonto, UpdatePonto
from model.loja import Loja
from services.ponto import valida_registrar_ponto, valida_atualizar_ponto
from services.token import valida_token
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


securit = HTTPBearer()

router = APIRouter(
    prefix="/ponto",
    tags=[Ponto.__name__],
    #dependencies=[Depends(securit)]
)


@router.post("/registrar", response_model=Ponto)
def registrar_ponto(ponto: CreatePonto, session: SessionDep):
    valida_registrar_ponto(ponto, session)
    ponto_obj = Ponto.model_validate(ponto)
    session.add(ponto_obj)
    session.commit()
    session.refresh(ponto_obj)
    return ponto_obj

def formatar_data(horario:str):
    timeSplit = horario.split("T")
    data = timeSplit[0].split("-")
    dia = data[2]
    mes = data[1]
    ano = data[0]

    return f"{dia}/{mes}/{ano}"

@router.get("/getPontos/{id_usuario}")
def get_ponto_by_day(id_usuario: int, data: str, session: SessionDep):
    pontos = session.exec(select(Ponto).where(Ponto.id_usuario == id_usuario)).all()
    pontos_do_dia = [p for p in pontos if formatar_data(p.horario) == data]
    return pontos_do_dia


@router.get("/getPonto/{id_ponto}", response_model=Ponto)
def get_ponto(id_ponto: int, session: SessionDep):
    ponto = session.exec(select(Ponto).where(Ponto.id == id_ponto)).first()
    if not ponto:
        raise HTTPException(404, "Ponto não encontrado")
    return ponto

@router.get("/usuario/{id_usuario}", response_model=list[Ponto])
def get_pontos_usuario(id_usuario: int, session: SessionDep):
    pontos = session.exec(select(Ponto).where(Ponto.id_usuario == id_usuario)).all()
    return pontos   

@router.get("/loja/{id_loja}", response_model=list[Ponto])
def get_pontos_loja(id_loja: int, session: SessionDep):
    # Verifica se a loja existe
    loja = session.exec(select(Loja).where(Loja.id == id_loja)).first()
    if not loja:
        raise HTTPException(404, "Loja não encontrada")
    pontos = session.exec(select(Ponto).where(Ponto.id_loja == id_loja)).all()
    return pontos

@router.get("/loja/{id_loja}/data/{data}")
def get_pontos_loja_data(id_loja: int, data: str, session: SessionDep):
    # Verifica se a loja existe
    loja = session.exec(select(Loja).where(Loja.id == id_loja)).first()
    if not loja:
        raise HTTPException(404, "Loja não encontrada")
    pontos = session.exec(select(Ponto).where(Ponto.id_loja == id_loja)).all()
    pontos_do_dia = [p for p in pontos if formatar_data(p.horario) == data]
    return pontos_do_dia

@router.put("/atualizar/{id_ponto}", response_model=Ponto)
def atualizar_ponto(id_ponto: int, ponto: UpdatePonto, session: SessionDep):
    ponto_obj = session.exec(select(Ponto).where(Ponto.id == id_ponto)).first()
    if not ponto_obj:
        raise HTTPException(404, "Ponto não encontrado")
    valida_atualizar_ponto(ponto, session)
    ponto_data = ponto.model_dump(exclude_none=True)
    ponto_obj.sqlmodel_update(ponto_data)
    session.add(ponto_obj)
    session.commit()
    session.refresh(ponto_obj)
    return ponto_obj 