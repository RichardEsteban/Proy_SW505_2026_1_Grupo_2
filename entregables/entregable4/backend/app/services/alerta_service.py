from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import Roles
from app.models.alerta_stock import AlertaStock
from app.models.usuario import Usuario
from app.repositories.alerta_repository import AlertaRepository
from app.schemas.alerta_schema import AlertaStockResponse


class AlertaService:

    @staticmethod
    def _usuario_es_global(usuario: Usuario) -> bool:
        return usuario.rol.nombreRol in (Roles.ADMIN, Roles.SUPERVISOR_ALMACEN)

    @staticmethod
    def _validar_acceso_ubicacion(usuario: Usuario, id_ubicacion: int):
        if AlertaService._usuario_es_global(usuario):
            return

        if usuario.idUbicacion != id_ubicacion:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes consultar alertas de tu ubicación",
            )

    @staticmethod
    def _response(alerta: AlertaStock) -> AlertaStockResponse:
        return AlertaStockResponse(
            idAlerta=alerta.idAlerta,
            idUbicacion=alerta.idUbicacion,
            ubicacion=alerta.ubicacion.nombreUbicacion,
            idProducto=alerta.idProducto,
            producto=alerta.producto.nombreProducto,
            tipoAlerta=alerta.tipoAlerta,
            cantidadActual=alerta.cantidadActual,
            stockReferencia=alerta.stockReferencia,
            estado=alerta.estado,
            fechaCreacion=alerta.fechaCreacion,
            fechaLeida=alerta.fechaLeida,
        )

    @staticmethod
    def listar(
        db: Session,
        usuario_actual: Usuario,
        id_ubicacion: int | None = None,
        estado: str | None = "PENDIENTE",
    ) -> list[AlertaStockResponse]:
        if estado is not None and estado not in ("PENDIENTE", "LEIDA"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estado de alerta inválido",
            )

        if not AlertaService._usuario_es_global(usuario_actual):
            if id_ubicacion is not None and id_ubicacion != usuario_actual.idUbicacion:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Solo puedes consultar alertas de tu ubicación",
                )
            id_ubicacion = usuario_actual.idUbicacion

        alertas = AlertaRepository.obtener_todas(
            db=db,
            id_ubicacion=id_ubicacion,
            estado=estado,
        )
        return [AlertaService._response(alerta) for alerta in alertas]

    @staticmethod
    def marcar_como_leida(
        db: Session,
        id_alerta: int,
        usuario_actual: Usuario,
    ) -> AlertaStockResponse:
        alerta = AlertaRepository.obtener_por_id(db, id_alerta)

        if not alerta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alerta no encontrada",
            )

        AlertaService._validar_acceso_ubicacion(usuario_actual, alerta.idUbicacion)
        alerta.estado = "LEIDA"
        alerta.fechaLeida = datetime.utcnow()
        AlertaRepository.guardar(db, alerta)
        db.commit()

        alerta_actualizada = AlertaRepository.obtener_por_id(db, id_alerta)
        return AlertaService._response(alerta_actualizada)
