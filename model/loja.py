from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Loja(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(default=None)
    endereco: str = Field(default=None)
    imagem: str = Field(default=None)  # varchar para URL ou caminho da imagem

class CreateLoja(SQLModel):
    nome: str = Field(default=None)
    endereco: str = Field(default=None)
    imagem: str = Field(default=None)

class UpdateLoja(SQLModel):
    nome: Optional[str] = Field(default=None)
    endereco: Optional[str] = Field(default=None)
    imagem: Optional[str] = Field(default=None) 