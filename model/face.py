from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class FaceData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    imagem: bytes 