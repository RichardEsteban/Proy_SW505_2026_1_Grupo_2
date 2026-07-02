from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.solicitud_reposicion import DetalleSolicitudReposicion, SolicitudReposicion


class ReposicionRepository:

    @staticmethod
    def obtener_todas(
        db: Session,
        id_ubicacion_origen: int | None = None,
        id_ubicacion_destino: int | None = None,
        estado: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        limite: int = 100,
    ) -> list[SolicitudReposicion]:
        stmt = (
            select(SolicitudReposicion)
            .options(
                joinedload(SolicitudReposicion.ubicacion_origen),
                joinedload(SolicitudReposicion.ubicacion_destino),
                joinedload(SolicitudReposicion.usuario_solicitante),
                joinedload(SolicitudReposicion.usuario_despachador),
                joinedload(SolicitudReposicion.usuario_receptor),
                joinedload(SolicitudReposicion.detalles).joinedload(DetalleSolicitudReposicion.producto),
            )
            .order_by(SolicitudReposicion.fechaSolicitud.desc(), SolicitudReposicion.idSolicitud.desc())
            .limit(limite)
        )
        if id_ubicacion_origen is not None:
            stmt = stmt.where(SolicitudReposicion.idUbicacionOrigen == id_ubicacion_origen)
        if id_ubicacion_destino is not None:
            stmt = stmt.where(SolicitudReposicion.idUbicacionDestino == id_ubicacion_destino)
        if estado is not None:
            stmt = stmt.where(SolicitudReposicion.estado == estado)
        if desde is not None:
            stmt = stmt.where(SolicitudReposicion.fechaSolicitud >= desde)
        if hasta is not None:
            stmt = stmt.where(SolicitudReposicion.fechaSolicitud <= hasta)
        return list(db.execute(stmt).unique().scalars().all())

    @staticmethod
    def obtener_por_id(db: Session, id_solicitud: int) -> SolicitudReposicion | None:
        stmt = (
            select(SolicitudReposicion)
            .options(
                joinedload(SolicitudReposicion.ubicacion_origen),
                joinedload(SolicitudReposicion.ubicacion_destino),
                joinedload(SolicitudReposicion.usuario_solicitante),
                joinedload(SolicitudReposicion.usuario_despachador),
                joinedload(SolicitudReposicion.usuario_receptor),
                joinedload(SolicitudReposicion.detalles).joinedload(DetalleSolicitudReposicion.producto),
            )
            .where(SolicitudReposicion.idSolicitud == id_solicitud)
        )
        return db.execute(stmt).unique().scalar_one_or_none()

    @staticmethod
    def guardar(db: Session, solicitud_reposicion: SolicitudReposicion) -> SolicitudReposicion:
        db.add(solicitud_reposicion)
        db.flush()
        db.refresh(solicitud_reposicion)
        return solicitud_reposicion
