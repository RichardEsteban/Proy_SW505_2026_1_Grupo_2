from pydantic import BaseModel


class UbicacionCreate(BaseModel):
    idEmpresa: int
    nombreUbicacion: str
    tipoUbicacion: str
    direccion: str


class UbicacionResponse(BaseModel):
    idUbicacion: int
    idEmpresa: int
    nombreUbicacion: str
    tipoUbicacion: str
    direccion: str
    isActivo: bool

    class Config:
        from_attributes = True