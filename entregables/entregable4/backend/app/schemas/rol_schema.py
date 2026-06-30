from pydantic import BaseModel


class RolResponse(BaseModel):
    idRol: int
    nombreRol: str

    class Config:
        from_attributes = True