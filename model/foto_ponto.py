from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class FotoPonto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_ponto: int = Field(foreign_key="ponto.id")
    foto: str  # base64 ou URL da foto
    data_criacao: Optional[str] = Field(default=None)  # timestamp da criação
    # Relacionamento com ponto
    ponto: "Ponto" = Relationship(back_populates="fotos")

class CreateFotoPonto(SQLModel):
    id_ponto: int = Field(foreign_key="ponto.id")
    foto: str
    data_criacao: Optional[str] = Field(default=None)

class UpdateFotoPonto(SQLModel):
    foto: str | None = None 