from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Ponto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuario.id")
    id_loja: Optional[int] = Field(default=None, foreign_key="loja.id")
    latitude: float
    longitude: float
    horario: str
    endereco: str
    tipo: str
    # Relacionamento com fotos
    fotos: List["FotoPonto"] = Relationship(back_populates="ponto")

class CreatePonto(SQLModel):
    id_usuario: int
    id_loja: Optional[int] = None
    latitude: float
    longitude: float
    horario: str
    endereco: str
    tipo: str

class UpdatePonto(SQLModel):
    id_loja: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    horario: str | None = None
    endereco: str | None = None 
    tipo: str | None = None