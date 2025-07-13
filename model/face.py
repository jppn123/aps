from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Face(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    imagem: bytes
    embedding: Optional[str] = Field(default=None)