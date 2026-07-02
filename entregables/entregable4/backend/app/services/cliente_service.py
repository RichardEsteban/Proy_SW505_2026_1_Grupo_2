from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.cliente import Cliente, EmpresaCliente, Persona
from app.repositories.cliente_repository import ClienteRepository
from app.schemas.cliente_schema import ClienteCreateRequest, ClienteResponse, ClienteUpdateRequest


class ClienteService:

    @staticmethod
    def nombre_mostrar(cliente: Cliente) -> str:
        if cliente.tipoCliente == "PERSONA" and cliente.persona:
            return f"{cliente.persona.nombres} {cliente.persona.apellidos}".strip()
        if cliente.tipoCliente == "EMPRESA" and cliente.empresa_cliente:
            return cliente.empresa_cliente.razonSocial
        return f"Cliente {cliente.idCliente}"

    @staticmethod
    def _response(cliente: Cliente) -> ClienteResponse:
        persona = cliente.persona
        empresa = cliente.empresa_cliente
        return ClienteResponse(
            idCliente=cliente.idCliente,
            tipoCliente=cliente.tipoCliente,
            telefono=cliente.telefono,
            correoElectronico=cliente.correoElectronico,
            documentoIdentidad=persona.documentoIdentidad if persona else None,
            nombres=persona.nombres if persona else None,
            apellidos=persona.apellidos if persona else None,
            identificacionFiscal=empresa.identificacionFiscal if empresa else None,
            razonSocial=empresa.razonSocial if empresa else None,
            direccionFiscal=empresa.direccionFiscal if empresa else None,
            nombreMostrar=ClienteService.nombre_mostrar(cliente),
            isActivo=cliente.isActivo,
        )

    @staticmethod
    def listar(db: Session, incluir_inactivos: bool = False) -> list[ClienteResponse]:
        clientes = ClienteRepository.obtener_todos(db=db, incluir_inactivos=incluir_inactivos)
        return [ClienteService._response(cliente) for cliente in clientes]

    @staticmethod
    def obtener_por_id(db: Session, id_cliente: int) -> ClienteResponse:
        cliente = ClienteRepository.obtener_por_id(db, id_cliente)
        if not cliente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
        return ClienteService._response(cliente)

    @staticmethod
    def crear(db: Session, datos: ClienteCreateRequest) -> ClienteResponse:
        documento = datos.documentoIdentidad if datos.tipoCliente == "PERSONA" else datos.identificacionFiscal
        if documento and ClienteRepository.obtener_por_documento(db, documento):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un cliente con ese documento")

        cliente = Cliente(
            tipoCliente=datos.tipoCliente,
            telefono=datos.telefono,
            correoElectronico=datos.correoElectronico,
            isActivo=True,
        )
        ClienteRepository.guardar(db, cliente)

        if datos.tipoCliente == "PERSONA":
            db.add(Persona(
                idCliente=cliente.idCliente,
                documentoIdentidad=datos.documentoIdentidad,
                nombres=datos.nombres,
                apellidos=datos.apellidos,
            ))
        else:
            db.add(EmpresaCliente(
                idCliente=cliente.idCliente,
                identificacionFiscal=datos.identificacionFiscal,
                razonSocial=datos.razonSocial,
                direccionFiscal=datos.direccionFiscal,
            ))

        db.commit()
        cliente_creado = ClienteRepository.obtener_por_id(db, cliente.idCliente)
        return ClienteService._response(cliente_creado)

    @staticmethod
    def actualizar(db: Session, id_cliente: int, datos: ClienteUpdateRequest) -> ClienteResponse:
        cliente = ClienteRepository.obtener_por_id(db, id_cliente)
        if not cliente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

        cambios = datos.model_dump(exclude_unset=True)

        if "telefono" in cambios:
            cliente.telefono = cambios["telefono"]
        if "correoElectronico" in cambios:
            cliente.correoElectronico = cambios["correoElectronico"]
        if "isActivo" in cambios and cambios["isActivo"] is not None:
            cliente.isActivo = cambios["isActivo"]

        if cliente.tipoCliente == "PERSONA":
            persona = cliente.persona
            if not persona:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cliente persona incompleto")
            if "documentoIdentidad" in cambios and cambios["documentoIdentidad"] != persona.documentoIdentidad:
                existente = ClienteRepository.obtener_por_documento(db, cambios["documentoIdentidad"])
                if existente and existente.idCliente != id_cliente:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe otro cliente con ese documento")
                persona.documentoIdentidad = cambios["documentoIdentidad"]
            if "nombres" in cambios:
                persona.nombres = cambios["nombres"]
            if "apellidos" in cambios:
                persona.apellidos = cambios["apellidos"]

        if cliente.tipoCliente == "EMPRESA":
            empresa = cliente.empresa_cliente
            if not empresa:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cliente empresa incompleto")
            if "identificacionFiscal" in cambios and cambios["identificacionFiscal"] != empresa.identificacionFiscal:
                existente = ClienteRepository.obtener_por_documento(db, cambios["identificacionFiscal"])
                if existente and existente.idCliente != id_cliente:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe otro cliente con ese documento")
                empresa.identificacionFiscal = cambios["identificacionFiscal"]
            if "razonSocial" in cambios:
                empresa.razonSocial = cambios["razonSocial"]
            if "direccionFiscal" in cambios:
                empresa.direccionFiscal = cambios["direccionFiscal"]

        ClienteRepository.guardar(db, cliente)
        db.commit()
        cliente_actualizado = ClienteRepository.obtener_por_id(db, id_cliente)
        return ClienteService._response(cliente_actualizado)
