from sqlmodel import SQLModel, create_engine, Session
from fastapi import Depends
from typing import Annotated
import os

# Pegar DATABASE_URL do ambiente (Railway fornece isso)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Se for PostgreSQL do Railway, ajustar a URL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]