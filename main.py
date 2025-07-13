from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from connection import create_db_and_tables
from routers import *
from routers.face import router as face_router
from routers.loja import router as loja_router
from routers.time import router as time_router
from routers.usuario_time import router as usuario_time_router
from routers.usuario_loja import router as usuario_loja_router


def lifespan(app:FastAPI):
    create_db_and_tables()

    yield #todo codigo depois dessa linha será executado após a finalização da api, assim como todo codigo antes será executado antes do start da api

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.include_router(horas.router)
app.include_router(usuario.router)
app.include_router(login.router)
app.include_router(utils.router)
app.include_router(ponto.router)
app.include_router(face_router)
app.include_router(loja_router)
app.include_router(time_router)
app.include_router(usuario_time_router)
app.include_router(usuario_loja_router)

