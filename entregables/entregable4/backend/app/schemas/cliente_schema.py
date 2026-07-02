from typing import Literal

from pydantic import BaseModel, EmailStr, Field, model_validator


TipoCliente = Literal["PERSONA", "EMPRESA"]


class ClienteCreateRequest(BaseModel):
    tipoCliente: TipoCliente
    telefono: str | None = Field(default=None, max_length=20)
    correoElectronico: EmailStr | None = None

    documentoIdentidad: str | None = Field(default=None, max_length=12)
    nombres: str | None = Field(default=None, max_length=100)
    apellidos: str | None = Field(default=None, max_length=100)

    identificacionFiscal: str | None = Field(default=None, max_length=11)
    razonSocial: str | None = Field(default=None, max_length=150)
    direccionFiscal: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validar_datos_por_tipo(self):
        if self.tipoCliente == "PERSONA":
            if not self.documentoIdentidad or not self.nombres or not self.apellidos:
                raise ValueError("Para PERSONA debes enviar documentoIdentidad, nombres y apellidos")
        if self.tipoCliente == "EMPRESA":
            if not self.identificacionFiscal or not self.razonSocial:
                raise ValueError("Para EMPRESA debes enviar identificacionFiscal y razonSocial")
        return self


class ClienteUpdateRequest(BaseModel):
    isActivo: bool | None = None
    telefono: str | None = Field(default=None, max_length=20)
    correoElectronico: EmailStr | None = None

    documentoIdentidad: str | None = Field(default=None, max_length=12)
    nombres: str | None = Field(default=None, max_length=100)
    apellidos: str | None = Field(default=None, max_length=100)

    identificacionFiscal: str | None = Field(default=None, max_length=11)
    razonSocial: str | None = Field(default=None, max_length=150)
    direccionFiscal: str | None = Field(default=None, max_length=255)


class ClienteResponse(BaseModel):
    idCliente: int
    tipoCliente: str
    telefono: str | None
    correoElectronico: str | None
    documentoIdentidad: str | None = None
    nombres: str | None = None
    apellidos: str | None = None
    identificacionFiscal: str | None = None
    razonSocial: str | None = None
    direccionFiscal: str | None = None
    nombreMostrar: str
    isActivo: bool = True
