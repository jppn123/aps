from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from connection import create_db_and_tables
from routers import *


def lifespan(app:FastAPI):
    create_db_and_tables()

    yield #todo codigo depois dessa linha será executado após a finalização da api, assim como todo codigo antes será executado antes do start da api

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, 
    allow_origins="*", 
    allow_methods="*",
    allow_headers="*"
)

app.include_router(horas.router)
app.include_router(usuario.router)
app.include_router(login.router)

