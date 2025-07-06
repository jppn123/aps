from sqlmodel import SQLModel, Field
from typing import Optional

class Ponto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuario.id")
    foto: str
    latitude: float
    longitude: float
    horario: str
    endereco: str
    tipo: str

class CreatePonto(SQLModel):
    id_usuario: int
    foto: str
    latitude: float
    longitude: float
    horario: str
    endereco: str
    tipo: str

class UpdatePonto(SQLModel):
    foto: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    horario: str | None = None
    endereco: str | None = None 
    tipo: str | None = None