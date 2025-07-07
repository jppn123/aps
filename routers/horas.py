from fastapi import APIRouter, HTTPException
from sqlmodel import select
from connection import SessionDep
from datetime import datetime, timedelta

from services.horas import *
from model.horas import *

router = APIRouter(
    prefix="/horas",
    tags=[Horas.__name__]
)

@router.post("/inicia/{id_usuario}")
def inicia_turno(id_usuario, session: SessionDep):
    data = cria_hora_atual()
    horas = session.exec(select(Horas).where(Horas.dia == data.dia and Horas.id_usuario == id_usuario)).first() 
    if horas:
        raise HTTPException(status_code=400, detail="Período já iniciado")

    hora = Horas.model_validate(data)
    hora.id_usuario = id_usuario
    session.add(hora)
    session.commit()
    session.refresh(hora)
    return hora


@router.post("/termina/{id_usuario}")
def termina_turno(id_usuario, session: SessionDep):
    data = cria_hora_atual()
    hora = session.exec(select(Horas).where(Horas.dia == data.dia and Horas.id_usuario == id_usuario)).first()
    if not hora:
        raise HTTPException(status_code=404, detail="Período não iniciado")
    if hora.saida:
        raise HTTPException(status_code=400, detail="Período já finalizado")
        
    hora.saida = edita_data_atual(datetime.now())[1]
    hora.falta = horas_restantes(hora.entrada, hora.saida, id_usuario, session)
    
    session.add(hora)
    session.commit()
    session.refresh(hora)
    return hora

@router.get("/horasRestantes")
def horas_restantes_diario(session: SessionDep, id_usuario = 1):
    data = cria_hora_atual()
    hora = session.exec(select(Horas).where(Horas.dia == data.dia and Horas.id_usuario == id_usuario)).first()
    if not hora:
        raise HTTPException(status_code=404, detail="Período não iniciado")
    
    horas = horas_restantes(hora.entrada, edita_data_atual(datetime.now())[1], id_usuario, session)
    data_sem_dia = data.dia[len(data.dia.split("/")[0]):]
    lista_desconto = session.exec(select(Horas.falta).where(Horas.id_usuario == id_usuario and Horas.dia[len(Horas.dia.split("/")[0]):] == data_sem_dia)).all()
    desc = retorna_desconto(lista_desconto)
    a = subtrair_horas(horas, desc, horas[0], desc[0])
    desconto = ["0"+x if len(x) < 2 else x for x in a[1:].split(":")]
    desconto = ":".join(desconto)
    return {
        "hrs": horas,
        #"a":a[0] + desconto,
        "desc": desc
    }
    # {
    #         "horas_restantes": horas, 
    #         "horas_restantes_com_desconto":edita_hora_desconto(lista_desconto, horas),
    #         "desconto":retorna_desconto(lista_desconto)
    #         }