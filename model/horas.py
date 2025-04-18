from model import *
from model.usuario import *

class Horas(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    dia: str | None = Field(default=None, unique_items=True)
    entrada: str | None = Field(default=None)
    saida: str | None = Field(default=None)
    falta: str | None = Field(default=None)
    id_usuario: int | None = Field(default=None, foreign_key="usuario.id")
    usuario: "Usuario" = Relationship(back_populates="horas")


class CreateHoras(SQLModel):
    dia: str | None = Field(default=None, unique=True)
    entrada: str | None = Field(default=None)


class UpdateFaltaHoras(SQLModel):
    id: int | None = Field( default=None)
    falta: str | None = Field(default=None)