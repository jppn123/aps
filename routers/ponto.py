from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from sqlalchemy import desc
from sqlmodel import select
from connection import SessionDep
from model.ponto import Ponto, CreatePonto, UpdatePonto
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

@router.get("/getPonto/{id_usuario}")
def get_ponto_by_day(id_usuario:int,data:str, session:SessionDep):

    
    # pontos:Ponto = session.exec(select(Ponto).where(formatar_data(Ponto.horario) == '03/07/2025')).first()
    pontos:Ponto = session.exec(select(Ponto).where(Ponto.id_usuario == id_usuario).order_by(desc(Ponto.horario))).first()
    return pontos
    # if not pontos:
    #     raise HTTPException(404, "Ponto não encontrado")
    
    # if len(pontos) == 2:
    #     possuiEntrada = False
    #     possuiSaida = False
    #     for x in pontos:
    #         if x.tipo == "entrada":
    #             possuiEntrada = True
    #         if x.tipo == "saida":
    #             possuiSaida = True
    # else:
    #     return "Usuário não finalizou a jornada no dia " + data
    
    # if possuiEntrada and possuiSaida:
    #     return pontos
    # else:
    #     return "Houve um erro"

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

@router.put("/atualizar/{id_ponto}", response_model=Ponto)
def atualizar_ponto(id_ponto: int, ponto: UpdatePonto, session: SessionDep):
    ponto_obj = session.exec(select(Ponto).where(Ponto.id == id_ponto)).first()
    if not ponto_obj:
        raise HTTPException(404, "Ponto não encontrado")
    ponto_data = ponto.model_dump(exclude_none=True)
    ponto_obj.sqlmodel_update(ponto_data)
    session.add(ponto_obj)
    session.commit()
    session.refresh(ponto_obj)
    return ponto_obj 