from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class UsuarioTime(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuario.id")
    id_time: int = Field(foreign_key="time.id")
    
    # Relacionamentos
    usuario: "Usuario" = Relationship(back_populates="usuario_times")
    time: "Time" = Relationship(back_populates="usuario_times")

class CreateUsuarioTime(SQLModel):
    id_usuario: int = Field(foreign_key="usuario.id")
    id_time: int = Field(foreign_key="time.id") 