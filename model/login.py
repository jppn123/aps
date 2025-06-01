from model import *
from model.usuario import *

class Login(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    tipo: str | None = Field(default=None)
    email: str | None = Field(default=None)
    senha: str | None = Field(default=None)
    usuario: "Usuario" = Relationship(back_populates="login")

class CreateLogin(SQLModel):
    tipo: str | None = Field(default=None)
    email: str | None = Field(default=None)
    senha: str | None = Field(default=None)
    conf_senha: str | None = Field(default=None)
    
class EntrarLogin(SQLModel):
    email: str | None = Field(default=None)
    senha: str | None = Field(default=None)


class RecuperarSenha(SQLModel):
    email: str | None = Field(default=None)

class MudarSenha(SQLModel):
    senhaAntiga: str | None = Field(default=None)
    senhaNova: str | None = Field(default=None)
    senhaNovaConfirmada: str | None = Field(default=None)

class VerificarCodigo(SQLModel):
    codigo: str | None = Field(default=None)