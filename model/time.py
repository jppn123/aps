from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Time(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(default=None)
    descricao: str = Field(default=None)
    deletado: int = Field(default=None)
    
    usuario_times: List["UsuarioTime"] = Relationship(back_populates="time")

class CreateTime(SQLModel):
    nome: str = Field(default=None)
    descricao: str = Field(default=None)
    deletado: int = 0

class UpdateTime(SQLModel):
    nome: Optional[str] = Field(default=None)
    descricao: Optional[str] = Field(default=None)
    deletado: Optional[int] = Field(default=None)
