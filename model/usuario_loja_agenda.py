from sqlmodel import SQLModel, Field
from typing import Optional

class UsuarioLojaAgenda(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuario.id")
    id_loja: int = Field(foreign_key="loja.id")
    dia_semana: int = Field()  # 0=segunda, 1=terça, ..., 6=domingo 
    periodo: int = Field()  # 1, 2, 3, 4 (espaços de tempo no dia) 