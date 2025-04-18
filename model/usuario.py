from model import *
from model.login import *
from model.horas import *

class Usuario(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    nome: str | None = Field(default=None)
    cpf: str | None = Field(default=None)
    qtd_hrs: int | None = Field(default=None)
    id_login: int | None = Field(default=None, foreign_key="login.id")
   
    login: "Login" = Relationship(back_populates="usuario")
    horas: "Horas" = Relationship(back_populates="usuario")

class CreateUsuario(SQLModel):
    nome: str | None = Field(default=None)
    cpf: str | None = Field(default=None)
    qtd_hrs: int | None = Field(default=None)
    id_login: int | None = Field(default=None, foreign_key="login.id")