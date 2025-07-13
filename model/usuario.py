from model import *
from model.login import *
from model.horas import *
from typing import List

class Usuario(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: int | None = Field(primary_key=True, default=None)
    nome: str | None = Field(default=None)
    cpf: str | None = Field(default=None)
    data_nascimento: str | None = Field(default=None)
    qtd_hrs: int | None = Field(default=None)
    telefone: str | None = Field(default=None)
    id_login: int | None = Field(default=None, foreign_key="login.id")
   
    login: "Login" = Relationship(back_populates="usuario")
    horas: "Horas" = Relationship(back_populates="usuario")
    usuario_times: List["UsuarioTime"] = Relationship(back_populates="usuario")
    usuario_lojas: List["UsuarioLoja"] = Relationship(back_populates="usuario")

class CreateUsuario(SQLModel):
    nome: str | None = Field(default=None)
    cpf: str | None = Field(default=None)
    id_login: int | None = Field(default=None, foreign_key="login.id")

class UpdateUsuario(SQLModel):
    nome: str | None = Field(default=None)
    cpf: str | None = Field(default=None)   
    data_nascimento: str | None = Field(default=None)
    telefone: str | None = Field(default=None)

class AddUsuarioTime(SQLModel):
    id_usuario: int = Field(foreign_key="usuario.id")
    id_time: int = Field(foreign_key="time.id")

class RemoveUsuarioTime(SQLModel):
    id_usuario: int = Field(foreign_key="usuario.id")
    id_time: int = Field(foreign_key="time.id")