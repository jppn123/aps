from sqlalchemy import create_engine, URL
from sqlmodel import Session
from model import SQLModel
from fastapi import Depends
from typing import Annotated

SERVER = "DESKTOP-GDKM6AQ"
DATABASE = "banco-de-horas"
USERNAME = "pyodbc"
PASSWORD = "1q2w3e!Q@W#E"

connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Trusted_Connection=yes'
connectionURL = URL.create(
    "mssql+pyodbc", query={"odbc_connect": connectionString}
)
connect_args = {"check_same_thread": False}
engine = create_engine(connectionURL, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]