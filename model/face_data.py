from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class FaceData(SQLModel, table=True):
    __tablename__ = "face_data"
    __table_args__ = {"extend_existing": True}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    imagem: bytes
    embedding: Optional[str] = Field(default=None)  # Embedding serializado para comparação mais rápida 