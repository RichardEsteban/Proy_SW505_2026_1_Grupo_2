from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import Roles, TiposUbicacion
from app.models.inventario_ubicacion import InventarioUbicacion
from app.models.movimiento_inventario import MovimientoInventario
from app.models.solicitud_reposicion import DetalleSolicitudReposicion, SolicitudReposicion
from app.models.ubicacion import Ubicacion
from app.models.usuario import Usuario
from app.repositories.empresa_repository import EmpresaRepository
from app.repositories.inventario_repository import InventarioRepository
from app.repositories.movimiento_repository import MovimientoRepository
from app.repositories.producto_repository import ProductoRepository
from app.repositories.reposicion_repository import ReposicionRepository
from app.repositories.ubicacion_repository import UbicacionRepository
from app.schemas.reposicion_schema import (
    SolicitudReposicionCreateRequest,
    SolicitudReposicionDetalleResponse,
    SolicitudReposicionGestionRequest,
    SolicitudReposicionResponse,
)
from app.services.inventario_service import InventarioService


class ReposicionService:

    @staticmethod
    def _usuario_es_global(usuario: Usuario) -> bool:
        return usuario.rol.nombreRol in (Roles.ADMIN, Roles.SUPERVISOR_ALMACEN)

    @staticmethod
    def _detalle_response(detalle: DetalleSolicitudReposicion) -> SolicitudReposicionDetalleResponse:
        return SolicitudReposicionDetalleResponse(
            idDetalleSolicitud=detalle.idDetalleSolicitud,
            idProducto=detalle.idProducto,
            codigoBarras=detalle.producto.codigoBarras,
            nombreProducto=detalle.producto.nombreProducto,
            cantidadSolicitada=detalle.cantidadSolicitada,
            cantidadDespachada=detalle.cantidadDespachada,
        )

    @staticmethod
    def _response(solicitud: SolicitudReposicion) -> SolicitudReposicionResponse:
        return SolicitudReposicionResponse(
            idSolicitud=solicitud.idSolicitud,
            idUbicacionOrigen=solicitud.idUbicacionOrigen,
            ubicacionOrigen=solicitud.ubicacion_origen.nombreUbicacion,
            idUbicacionDestino=solicitud.idUbicacionDestino,
            ubicacionDestino=solicitud.ubicacion_destino.nombreUbicacion,
            idUsuarioSolicitante=solicitud.idUsuarioSolicitante,
            usuarioSolicitante=solicitud.usuario_solicitante.correoElectronico,
            idUsuarioDespachador=solicitud.idUsuarioDespachador,
            usuarioDespachador=(solicitud.usuario_despachador.correoElectronico if solicitud.usuario_despachador else None),
            idUsuarioReceptor=solicitud.idUsuarioReceptor,
            usuarioReceptor=(solicitud.usuario_receptor.correoElectronico if solicitud.usuario_receptor else None),
            fechaSolicitud=solicitud.fechaSolicitud,
            fechaDespacho=solicitud.fechaDespacho,
            fechaRecepcion=solicitud.fechaRecepcion,
            fechaAperturaRevision=solicitud.fechaAperturaRevision,
            estado=solicitud.estado,
            observacion=solicitud.observacion,
            detalles=[ReposicionService._detalle_response(detalle) for detalle in solicitud.detalles],
        )

    @staticmethod
    def _actualizar_enviado_a_revision_si_corresponde(db: Session):
        empresa = EmpresaRepository.obtener_primera(db)
        if not empresa:
            return
        minutos = int(empresa.timer_revision_minutos or 60)
        limite_revision = datetime.now() - timedelta(minutes=minutos)
        solicitudes = db.execute(
            select(SolicitudReposicion).where(
                SolicitudReposicion.estado == "ENVIADO",
                SolicitudReposicion.fechaSolicitud <= limite_revision,
            )
        ).scalars().all()
        for solicitud in solicitudes:
            solicitud.estado = "EN_REVISION"
            solicitud.fechaAperturaRevision = datetime.now()
            ReposicionRepository.guardar(db, solicitud)
        if solicitudes:
            db.commit()

    @staticmethod
    def _obtener_almacen_principal(db: Session) -> Ubicacion:
        stmt = (
            select(Ubicacion)
            .where(Ubicacion.tipoUbicacion == TiposUbicacion.ALMACEN, Ubicacion.isActivo.is_(True))
            .order_by(Ubicacion.idUbicacion)
            .limit(1)
        )
        almacen = db.execute(stmt).scalar_one_or_none()
        if not almacen:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No existe un almacén activo para atender reposiciones")
        return almacen

    @staticmethod
    def _validar_ubicacion(db: Session, id_ubicacion: int, tipo_requerido: str, mensaje_tipo: str) -> Ubicacion:
        ubicacion = UbicacionRepository.obtener_por_id(db, id_ubicacion)
        if not ubicacion or not ubicacion.isActivo:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La ubicación no existe o está inactiva")
        if ubicacion.tipoUbicacion != tipo_requerido:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=mensaje_tipo)
        return ubicacion

    @staticmethod
    def _validar_acceso_solicitud(usuario: Usuario, solicitud: SolicitudReposicion):
        if ReposicionService._usuario_es_global(usuario):
            return
        if solicitud.idUbicacionDestino != usuario.idUbicacion:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes consultar reposiciones de tu propia sucursal")

    @staticmethod
    def crear(db: Session, datos: SolicitudReposicionCreateRequest, usuario_actual: Usuario) -> SolicitudReposicionResponse:
        id_ubicacion_origen = datos.idUbicacionOrigen or ReposicionService._obtener_almacen_principal(db).idUbicacion
        id_ubicacion_destino = datos.idUbicacionDestino or usuario_actual.idUbicacion

        ReposicionService._validar_ubicacion(db, id_ubicacion_origen, TiposUbicacion.ALMACEN, "La ubicación origen debe ser un almacén")
        ReposicionService._validar_ubicacion(db, id_ubicacion_destino, TiposUbicacion.SUCURSAL, "La ubicación destino debe ser una sucursal")
        if id_ubicacion_origen == id_ubicacion_destino:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La ubicación origen y destino no pueden ser iguales")
        if not ReposicionService._usuario_es_global(usuario_actual) and id_ubicacion_destino != usuario_actual.idUbicacion:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes solicitar reposición para tu propia sucursal")

        detalles_por_producto: dict[int, int] = {}
        for detalle in datos.detalles:
            producto = ProductoRepository.obtener_por_id(db, detalle.idProducto)
            if not producto or not producto.isActivo:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El producto {detalle.idProducto} no existe o está inactivo")
            detalles_por_producto[detalle.idProducto] = detalles_por_producto.get(detalle.idProducto, 0) + detalle.cantidadSolicitada

        solicitud = SolicitudReposicion(
            idUbicacionOrigen=id_ubicacion_origen,
            idUbicacionDestino=id_ubicacion_destino,
            idUsuarioSolicitante=usuario_actual.idUsuario,
            estado="ENVIADO",
            observacion=datos.observacion,
        )
        ReposicionRepository.guardar(db, solicitud)
        for id_producto, cantidad in detalles_por_producto.items():
            db.add(DetalleSolicitudReposicion(idSolicitud=solicitud.idSolicitud, idProducto=id_producto, cantidadSolicitada=cantidad, cantidadDespachada=0))
        db.commit()
        return ReposicionService._response(ReposicionRepository.obtener_por_id(db, solicitud.idSolicitud))


    @staticmethod
    def editar(db: Session, id_solicitud_reposicion: int, datos: SolicitudReposicionCreateRequest, usuario_actual: Usuario) -> SolicitudReposicionResponse:
        solicitud = ReposicionRepository.obtener_por_id(db, id_solicitud_reposicion)
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de reposición no encontrada")
        if solicitud.estado != "ENVIADO":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Solo se pueden editar solicitudes en estado ENVIADO")
        if not ReposicionService._usuario_es_global(usuario_actual) and solicitud.idUbicacionDestino != usuario_actual.idUbicacion:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes editar solicitudes de tu propia sucursal")

        empresa = EmpresaRepository.obtener_primera(db)
        minutos_edicion = int(empresa.timer_revision_minutos or 60) if empresa else 60
        fecha_limite = solicitud.fechaSolicitud + timedelta(minutes=minutos_edicion)
        if datetime.now() > fecha_limite:
            solicitud.estado = "EN_REVISION"
            solicitud.fechaAperturaRevision = datetime.now()
            ReposicionRepository.guardar(db, solicitud)
            db.commit()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El tiempo permitido de edición ya venció. La solicitud pasó a revisión.")

        if datos.idUbicacionOrigen is not None:
            ReposicionService._validar_ubicacion(db, datos.idUbicacionOrigen, TiposUbicacion.ALMACEN, "La ubicación origen debe ser un almacén")
            solicitud.idUbicacionOrigen = datos.idUbicacionOrigen

        if datos.idUbicacionDestino is not None:
            ReposicionService._validar_ubicacion(db, datos.idUbicacionDestino, TiposUbicacion.SUCURSAL, "La ubicación destino debe ser una sucursal")
            if not ReposicionService._usuario_es_global(usuario_actual) and datos.idUbicacionDestino != usuario_actual.idUbicacion:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes editar solicitudes de tu propia sucursal")
            solicitud.idUbicacionDestino = datos.idUbicacionDestino

        if solicitud.idUbicacionOrigen == solicitud.idUbicacionDestino:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La ubicación origen y destino no pueden ser iguales")

        detalles_por_producto: dict[int, int] = {}
        for detalle in datos.detalles:
            producto = ProductoRepository.obtener_por_id(db, detalle.idProducto)
            if not producto or not producto.isActivo:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El producto {detalle.idProducto} no existe o está inactivo")
            detalles_por_producto[detalle.idProducto] = detalles_por_producto.get(detalle.idProducto, 0) + detalle.cantidadSolicitada

        solicitud.observacion = datos.observacion
        solicitud.detalles.clear()
        db.flush()
        for id_producto, cantidad in detalles_por_producto.items():
            solicitud.detalles.append(DetalleSolicitudReposicion(idProducto=id_producto, cantidadSolicitada=cantidad, cantidadDespachada=0))

        ReposicionRepository.guardar(db, solicitud)
        db.commit()
        return ReposicionService._response(ReposicionRepository.obtener_por_id(db, id_solicitud_reposicion))

    @staticmethod
    def listar(db: Session, usuario_actual: Usuario, id_ubicacion_origen: int | None = None, id_ubicacion_destino: int | None = None, estado: str | None = None, desde: datetime | None = None, hasta: datetime | None = None, limite: int = 100) -> list[SolicitudReposicionResponse]:
        ReposicionService._actualizar_enviado_a_revision_si_corresponde(db)
        if not ReposicionService._usuario_es_global(usuario_actual):
            if id_ubicacion_destino is not None and id_ubicacion_destino != usuario_actual.idUbicacion:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes listar reposiciones de tu propia sucursal")
            id_ubicacion_destino = usuario_actual.idUbicacion
        solicitudes = ReposicionRepository.obtener_todas(db, id_ubicacion_origen, id_ubicacion_destino, estado, desde, hasta, limite)
        return [ReposicionService._response(solicitud) for solicitud in solicitudes]

    @staticmethod
    def obtener_por_id(db: Session, id_solicitud_reposicion: int, usuario_actual: Usuario) -> SolicitudReposicionResponse:
        ReposicionService._actualizar_enviado_a_revision_si_corresponde(db)
        solicitud = ReposicionRepository.obtener_por_id(db, id_solicitud_reposicion)
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de reposición no encontrada")
        ReposicionService._validar_acceso_solicitud(usuario_actual, solicitud)
        return ReposicionService._response(solicitud)

    @staticmethod
    def abrir_revision(db: Session, id_solicitud_reposicion: int, datos: SolicitudReposicionGestionRequest, usuario_actual: Usuario) -> SolicitudReposicionResponse:
        solicitud = ReposicionRepository.obtener_por_id(db, id_solicitud_reposicion)
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de reposición no encontrada")
        if solicitud.estado != "ENVIADO":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Solo se pueden abrir en revisión solicitudes enviadas")
        solicitud.estado = "EN_REVISION"
        solicitud.fechaAperturaRevision = datetime.now()
        if datos.observacion:
            solicitud.observacion = datos.observacion
        ReposicionRepository.guardar(db, solicitud)
        db.commit()
        return ReposicionService._response(ReposicionRepository.obtener_por_id(db, id_solicitud_reposicion))

    @staticmethod
    def aceptar(db: Session, id_solicitud_reposicion: int, datos: SolicitudReposicionGestionRequest, usuario_actual: Usuario) -> SolicitudReposicionResponse:
        solicitud = ReposicionRepository.obtener_por_id(db, id_solicitud_reposicion)
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de reposición no encontrada")
        if solicitud.estado not in ("ENVIADO", "EN_REVISION"):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Solo se pueden aceptar solicitudes enviadas o en revisión")
        solicitud.estado = "ACEPTADO"
        if solicitud.fechaAperturaRevision is None:
            solicitud.fechaAperturaRevision = datetime.now()
        if datos.observacion:
            solicitud.observacion = datos.observacion
        ReposicionRepository.guardar(db, solicitud)
        db.commit()
        return ReposicionService._response(ReposicionRepository.obtener_por_id(db, id_solicitud_reposicion))

    aprobar = aceptar

    @staticmethod
    def rechazar(db: Session, id_solicitud_reposicion: int, datos: SolicitudReposicionGestionRequest, usuario_actual: Usuario) -> SolicitudReposicionResponse:
        solicitud = ReposicionRepository.obtener_por_id(db, id_solicitud_reposicion)
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de reposición no encontrada")
        if solicitud.estado not in ("ENVIADO", "EN_REVISION"):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Solo se pueden rechazar solicitudes enviadas o en revisión")
        solicitud.estado = "RECHAZADA"
        if datos.observacion:
            solicitud.observacion = datos.observacion
        ReposicionRepository.guardar(db, solicitud)
        db.commit()
        return ReposicionService._response(ReposicionRepository.obtener_por_id(db, id_solicitud_reposicion))

    @staticmethod
    def enviar(db: Session, id_solicitud_reposicion: int, datos: SolicitudReposicionGestionRequest, usuario_actual: Usuario) -> SolicitudReposicionResponse:
        solicitud = ReposicionRepository.obtener_por_id(db, id_solicitud_reposicion)
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de reposición no encontrada")
        if solicitud.estado != "ACEPTADO":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Solo se pueden despachar solicitudes aceptadas")

        inventarios_origen: dict[int, InventarioUbicacion] = {}
        for detalle in solicitud.detalles:
            inventario_origen = InventarioRepository.obtener_por_ubicacion_producto(db, solicitud.idUbicacionOrigen, detalle.idProducto)
            if not inventario_origen or inventario_origen.stockDisponible < detalle.cantidadSolicitada:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Stock insuficiente en almacén para {detalle.producto.nombreProducto}")
            inventarios_origen[detalle.idProducto] = inventario_origen

        for detalle in solicitud.detalles:
            inventario_origen = inventarios_origen[detalle.idProducto]
            cantidad = detalle.cantidadSolicitada
            inventario_origen.stockDisponible -= cantidad
            detalle.cantidadDespachada = cantidad
            InventarioRepository.guardar(db, inventario_origen)
            MovimientoRepository.guardar(db, MovimientoInventario(
                idUbicacion=solicitud.idUbicacionOrigen,
                idProducto=detalle.idProducto,
                idUsuario=usuario_actual.idUsuario,
                cantidad=cantidad,
                tipoMovimiento="SALIDA",
                motivoMovimiento="REPOSICION_ENVIADA",
                tipoReferencia="SOLICITUD_REPOSICION",
                idReferencia=solicitud.idSolicitud,
            ))
            InventarioService._crear_alerta_si_corresponde(db, inventario_origen)

        solicitud.estado = "EN_TRANSITO"
        solicitud.fechaDespacho = datetime.now()
        solicitud.idUsuarioDespachador = usuario_actual.idUsuario
        if datos.observacion:
            solicitud.observacion = datos.observacion
        ReposicionRepository.guardar(db, solicitud)
        db.commit()
        return ReposicionService._response(ReposicionRepository.obtener_por_id(db, id_solicitud_reposicion))

    @staticmethod
    def recibir(db: Session, id_solicitud_reposicion: int, datos: SolicitudReposicionGestionRequest, usuario_actual: Usuario) -> SolicitudReposicionResponse:
        solicitud = ReposicionRepository.obtener_por_id(db, id_solicitud_reposicion)
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de reposición no encontrada")
        if solicitud.estado != "EN_TRANSITO":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Solo se pueden recibir solicitudes en tránsito")
        if not ReposicionService._usuario_es_global(usuario_actual) and solicitud.idUbicacionDestino != usuario_actual.idUbicacion:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes recibir reposiciones de tu propia sucursal")

        for detalle in solicitud.detalles:
            cantidad = detalle.cantidadDespachada or detalle.cantidadSolicitada
            inventario_destino = InventarioRepository.obtener_por_ubicacion_producto(db, solicitud.idUbicacionDestino, detalle.idProducto)
            if not inventario_destino:
                inventario_destino = InventarioUbicacion(idUbicacion=solicitud.idUbicacionDestino, idProducto=detalle.idProducto, stockDisponible=0, stockMinimo=0)
                InventarioRepository.guardar(db, inventario_destino)
            inventario_destino.stockDisponible += cantidad
            InventarioRepository.guardar(db, inventario_destino)
            MovimientoRepository.guardar(db, MovimientoInventario(
                idUbicacion=solicitud.idUbicacionDestino,
                idProducto=detalle.idProducto,
                idUsuario=usuario_actual.idUsuario,
                cantidad=cantidad,
                tipoMovimiento="INGRESO",
                motivoMovimiento="REPOSICION_RECIBIDA",
                tipoReferencia="SOLICITUD_REPOSICION",
                idReferencia=solicitud.idSolicitud,
            ))

        solicitud.estado = "RECIBIDA"
        solicitud.fechaRecepcion = datetime.now()
        solicitud.idUsuarioReceptor = usuario_actual.idUsuario
        if datos.observacion:
            solicitud.observacion = datos.observacion
        ReposicionRepository.guardar(db, solicitud)
        db.commit()
        return ReposicionService._response(ReposicionRepository.obtener_por_id(db, id_solicitud_reposicion))

    @staticmethod
    def cancelar(db: Session, id_solicitud_reposicion: int, datos: SolicitudReposicionGestionRequest, usuario_actual: Usuario) -> SolicitudReposicionResponse:
        solicitud = ReposicionRepository.obtener_por_id(db, id_solicitud_reposicion)
        if not solicitud:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de reposición no encontrada")
        if ReposicionService._usuario_es_global(usuario_actual):
            if solicitud.estado not in ("ENVIADO", "EN_REVISION"):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Solo se pueden cancelar solicitudes antes de ser aceptadas")
        else:
            if solicitud.estado != "ENVIADO":
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Solo puedes cancelar solicitudes en estado ENVIADO")
            if solicitud.idUbicacionDestino != usuario_actual.idUbicacion:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes cancelar reposiciones de tu propia sucursal")
        solicitud.estado = "CANCELADA"
        if datos.observacion:
            solicitud.observacion = datos.observacion
        ReposicionRepository.guardar(db, solicitud)
        db.commit()
        return ReposicionService._response(ReposicionRepository.obtener_por_id(db, id_solicitud_reposicion))

    anular = cancelar
