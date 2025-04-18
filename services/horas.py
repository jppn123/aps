from datetime import datetime
import math

from routers.usuario import retorna_usuario

from model.horas import CreateHoras


def transforma_hora(segundos):
    horas = math.floor(segundos/3600)
    segundos -= horas * 3600
    minutos = math.floor(segundos/60)
    segundos -= minutos * 60    
    segundos = math.floor(segundos)
    hora = datetime.strptime(f"{horas}:{minutos}:{segundos}", "%H:%M:%S").strftime("%H:%M:%S")
    
    return hora


def edita_hora(entrada, saida):
    entrada = datetime.strptime(entrada, "%H:%M:%S")
    saida = datetime.strptime(saida, "%H:%M:%S")
    segundos = (saida - entrada).total_seconds()
    
    return transforma_hora(segundos)


def horas_restantes(entrada, saida, id_usuario, session):
    usu_horas = f"0{retorna_usuario(id_usuario, session).qtd_hrs}:00:00"
    hora = edita_hora(entrada, saida)
    
    usu_horas_aux = datetime.strptime(usu_horas, "%H:%M:%S")
    hora_aux = datetime.strptime(hora, "%H:%M:%S")

    if (hora_aux - usu_horas_aux).total_seconds() > 0:
        hora_final = "+" + edita_hora(usu_horas, hora) #extra
    else:
        hora_final = "-" + edita_hora(hora, usu_horas) #falta

    return hora_final


def cria_hora_atual():
    dia, entrada = edita_data_atual(datetime.now())
    hora = CreateHoras()
    hora.dia = dia
    hora.entrada = entrada

    return hora


def edita_data_atual(hora: datetime):
    dia = hora.strftime("%d/%m/%Y")
    hora = hora.strftime("%H:%M:%S")

    return dia, hora


def edita_hora_desconto(lista_desconto: list, horas):
    desconto = retorna_desconto(lista_desconto)
    desc_aux = ["0"+x if len(x) < 2 else x for x in desconto[1:].split(":")]
    desc_aux = ":".join(desc_aux)
    
    if horas[0] == desconto[0]:
        retorno = somar_horas(desc_aux, horas, desconto[0], horas[0])
    else:
        retorno = subtrair_horas(desc_aux, horas, desconto[0], horas[0])

    ret = ["0"+x if len(x) < 2 else x for x in retorno[1:].split(":")]
    ret = ":".join(ret)
    return retorno[0] + ret


def retorna_desconto(lista_desconto: list):
    #- paga hora
    #+ tem horas sobrando
    #sinais iguais soma, sinais diferentes subtrai
    total_desconto = "00:00:00"
    i = 0
    for x in lista_desconto:
        if x:
            acao = x[0]
            tempo = x[1:]
           
            if acao == "+":
                if i == 0:
                    total_desconto = somar_horas(total_desconto, tempo, acao, acao)
                    i+=1
                elif total_desconto[0] == acao:
                    total_desconto = somar_horas(total_desconto[1:], tempo, total_desconto[0], acao)
                else:
                    total_desconto = subtrair_horas(total_desconto[1:], tempo, total_desconto[0], acao)
            else:
                if i == 0:
                    total_desconto = subtrair_horas(total_desconto, tempo, acao, acao)
                    i+=1
                elif total_desconto[0] == acao:
                    total_desconto = somar_horas(total_desconto[1:], tempo, total_desconto[0], acao)
                else:
                    total_desconto = subtrair_horas(total_desconto[1:], tempo, total_desconto[0], acao)

    sinal = total_desconto[0]
    desconto = ["0"+x if len(x) < 2 else x for x in total_desconto[1:].split(":")]
    desconto = ":".join(desconto)

    return sinal + desconto


def somar_horas(tempoAnterior:str, tempoAtual:str, sinalAnterior, sinalAtual):
    tempoAnterior = tempoAnterior.split(":")
    tempoAtual = tempoAtual.split(":")

    s1 = int(tempoAnterior[0]) * 3600 + int(tempoAnterior[1]) * 60 + int(tempoAnterior[2])
    s2 = int(tempoAtual[0]) * 3600 + int(tempoAtual[1]) * 60 + int(tempoAtual[2])

    hora = int(tempoAnterior[0]) + int(tempoAtual[0])
    minuto = int(tempoAnterior[1]) + int(tempoAtual[1])
    segundo = int(tempoAnterior[2]) + int(tempoAtual[2])

    if minuto >= 60:
        hora += minuto//60
        minuto -= (minuto//60)*60
    
    if segundo >= 60:
        minuto += segundo//60
        segundo -=  (segundo//60)*60
    
    if s1 > s2:
        sinal = sinalAnterior
    else:
        sinal = sinalAtual


    return f"{sinal}{hora}:{minuto}:{segundo}"


def subtrair_horas(tempoAnterior:str, tempoAtual:str, sinalAnterior, sinalAtual):
    tempoAnterior = tempoAnterior.split(":")
    tempoAtual = tempoAtual.split(":")

    s1 = int(tempoAnterior[0]) * 3600 + int(tempoAnterior[1]) * 60 + int(tempoAnterior[2])
    s2 = int(tempoAtual[0]) * 3600 + int(tempoAtual[1]) * 60 + int(tempoAtual[2])
    
    if s1 > s2:
        segundos = s1 - s2
        sinal = sinalAnterior
    else:
        segundos = s2 - s1
        sinal = sinalAtual

    horas = segundos//3600
    segundos -= horas * 3600 
    minutos = segundos//60
    segundos -= minutos * 60
    
    return f"{sinal}{horas}:{minutos}:{segundos}"