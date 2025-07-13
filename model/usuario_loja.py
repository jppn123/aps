from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class UsuarioLoja(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuario.id")
    id_loja: int = Field(foreign_key="loja.id")
    # Relacionamentos
    usuario: "Usuario" = Relationship(back_populates="usuario_lojas")
    loja: "Loja" = Relationship(back_populates="usuario_lojas")

class CreateUsuarioLoja(SQLModel):
    id_usuario: int = Field(foreign_key="usuario.id")
    id_loja: int = Field(foreign_key="loja.id") 