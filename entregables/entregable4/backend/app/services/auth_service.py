from datetime import datetime, timedelta
import random
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.codigo_verificacion import CodigoVerificacion
from app.models.sesion_usuario import SesionUsuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auth_schema import (
    CambiarContrasenaRequest,
    LoginRequest,
    MensajeResponse,
    RecuperarContrasenaRequest,
    TokenResponse,
    UsuarioAuthResponse,
    VerificarCodigoRequest,
)
from app.services.email_service import EmailService
from app.utils.jwt import crear_access_token
from app.utils.password import generar_hash_contrasena, verificar_contrasena


class AuthService:

    @staticmethod
    def _crear_usuario_response(usuario) -> UsuarioAuthResponse:
        return UsuarioAuthResponse(
            idUsuario=usuario.idUsuario,
            correoElectronico=usuario.correoElectronico,
            idRol=usuario.idRol,
            rol=usuario.rol.nombreRol,
            idUbicacion=usuario.idUbicacion,
            ubicacion=usuario.ubicacion.nombreUbicacion,
            tipoUbicacion=usuario.ubicacion.tipoUbicacion,
            isContrasenaTemporal=usuario.isContrasenaTemporal
        )

    @staticmethod
    def _cerrar_sesiones_expiradas(db: Session, id_usuario: int) -> None:
        # Limpieza preventiva antes de bloquear un nuevo login por sesión activa.
        # Cubre tanto inactividad normal como cierres bruscos del navegador/equipo.
        settings = get_settings()
        ahora = datetime.utcnow()
        limite_inactividad = ahora - timedelta(minutes=settings.session_inactivity_minutes)
        limite_heartbeat = ahora - timedelta(minutes=settings.session_heartbeat_grace_minutes)

        sesiones_expiradas = db.query(SesionUsuario).filter(
            SesionUsuario.idUsuario == id_usuario,
            SesionUsuario.isActiva == True,  # noqa: E712
            SesionUsuario.fechaUltimaActividad < limite_inactividad,
        ).all()

        for sesion in sesiones_expiradas:
            sesion.isActiva = False
            sesion.fechaCierre = ahora
            sesion.motivoCierre = "INACTIVIDAD"

        sesiones_sin_heartbeat = db.query(SesionUsuario).filter(
            SesionUsuario.idUsuario == id_usuario,
            SesionUsuario.isActiva == True,  # noqa: E712
            SesionUsuario.fechaUltimaActividad < limite_heartbeat,
        ).all()

        for sesion in sesiones_sin_heartbeat:
            sesion.isActiva = False
            sesion.fechaCierre = ahora
            sesion.motivoCierre = "SIN_HEARTBEAT"

    @staticmethod
    def _obtener_sesion_activa(db: Session, id_usuario: int) -> SesionUsuario | None:
        return db.query(SesionUsuario).filter(
            SesionUsuario.idUsuario == id_usuario,
            SesionUsuario.isActiva == True,  # noqa: E712
        ).order_by(SesionUsuario.fechaUltimaActividad.desc()).first()

    @staticmethod
    def _cerrar_sesiones_activas_usuario(db: Session, id_usuario: int, motivo: str) -> None:
        ahora = datetime.utcnow()
        sesiones_activas = db.query(SesionUsuario).filter(
            SesionUsuario.idUsuario == id_usuario,
            SesionUsuario.isActiva == True,  # noqa: E712
        ).all()

        for sesion in sesiones_activas:
            sesion.isActiva = False
            sesion.fechaCierre = ahora
            sesion.motivoCierre = motivo

    @staticmethod
    def cerrar_sesion(db: Session, token_id: str | None, motivo: str = "LOGOUT") -> MensajeResponse:
        if not token_id:
            return MensajeResponse(mensaje="Sesión cerrada.")

        sesion = db.query(SesionUsuario).filter(
            SesionUsuario.tokenId == token_id,
            SesionUsuario.isActiva == True,  # noqa: E712
        ).first()

        if sesion:
            ahora = datetime.utcnow()
            sesion.isActiva = False
            sesion.fechaCierre = ahora
            sesion.motivoCierre = motivo
            db.commit()

        return MensajeResponse(mensaje="Sesión cerrada correctamente.")

    @staticmethod
    def login(db: Session, datos: LoginRequest) -> TokenResponse:
        settings = get_settings()
        usuario = UsuarioRepository.obtener_por_correo(
            db=db,
            correo=str(datos.correoElectronico).strip().lower()
        )

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )

        if not verificar_contrasena(datos.contrasena, usuario.contrasenaHash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )

        if not usuario.isActivo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario está inactivo"
            )

        ahora = datetime.utcnow()
        AuthService._cerrar_sesiones_expiradas(db, usuario.idUsuario)

        if settings.single_active_session:
            sesion_activa = AuthService._obtener_sesion_activa(db, usuario.idUsuario)
            if sesion_activa:
                # Mantiene la regla de una sola sesión, pero permite recuperar cuentas colgadas.
                if datos.forzarCierreSesion:
                    AuthService._cerrar_sesiones_activas_usuario(
                        db,
                        usuario.idUsuario,
                        "CIERRE_FORZADO_NUEVO_LOGIN",
                    )
                    db.flush()
                else:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            "Esta cuenta ya tiene una sesión activa. "
                            "Puedes cerrar la sesión anterior y volver a ingresar si quedó abierta por error."
                        )
                    )

        token_id = str(uuid4())
        sesion = SesionUsuario(
            idUsuario=usuario.idUsuario,
            tokenId=token_id,
            isActiva=True,
            fechaInicio=ahora,
            fechaUltimaActividad=ahora,
        )
        db.add(sesion)
        db.flush()

        access_token = crear_access_token({
            "sub": str(usuario.idUsuario),
            "sid": token_id,
            "correo": usuario.correoElectronico,
            "rol": usuario.rol.nombreRol,
            "idRol": usuario.idRol,
            "idUbicacion": usuario.idUbicacion,
            "tipoUbicacion": usuario.ubicacion.tipoUbicacion
        })

        db.commit()

        return TokenResponse(
            access_token=access_token,
            usuario=AuthService._crear_usuario_response(usuario)
        )

    @staticmethod
    def solicitar_codigo_recuperacion(db: Session, datos: RecuperarContrasenaRequest) -> MensajeResponse:
        settings = get_settings()
        correo = str(datos.correoElectronico).strip().lower()

        usuario = UsuarioRepository.obtener_por_correo(db=db, correo=correo)

        if not usuario or not usuario.isActivo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El correo no pertenece a una cuenta registrada y activa."
            )

        ahora = datetime.utcnow()
        ultimo_codigo = db.query(CodigoVerificacion).filter(
            CodigoVerificacion.idUsuario == usuario.idUsuario,
            CodigoVerificacion.isUsado == False,  # noqa: E712
        ).order_by(CodigoVerificacion.idCodigo.desc()).first()

        if ultimo_codigo and ultimo_codigo.fechaCreacion:
            segundos_desde_ultimo = (ahora - ultimo_codigo.fechaCreacion).total_seconds()
            if segundos_desde_ultimo < settings.reset_code_resend_seconds:
                segundos_restantes = int(settings.reset_code_resend_seconds - segundos_desde_ultimo)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Espera {segundos_restantes} segundos antes de reenviar el código."
                )

        db.query(CodigoVerificacion).filter(
            CodigoVerificacion.idUsuario == usuario.idUsuario,
            CodigoVerificacion.isUsado == False,  # noqa: E712
        ).update({
            "isUsado": True,
            "fechaUso": ahora,
        })

        codigo = f"{random.SystemRandom().randint(0, 999999):06d}"
        codigo_verificacion = CodigoVerificacion(
            idUsuario=usuario.idUsuario,
            codigoHash=generar_hash_contrasena(codigo),
            isUsado=False,
            intentos=0,
            fechaCreacion=ahora,
            fechaExpiracion=ahora + timedelta(minutes=settings.reset_code_expire_minutes),
        )
        db.add(codigo_verificacion)

        try:
            EmailService.enviar_codigo_recuperacion(destinatario=usuario.correoElectronico, codigo=codigo)
        except Exception as error:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"No se pudo enviar el código de verificación: {error}"
            ) from error

        db.commit()
        return MensajeResponse(
            mensaje=f"Código enviado. Revisa tu correo. El código vence en {settings.reset_code_expire_minutes} minutos."
        )

    @staticmethod
    def _obtener_codigo_activo(db: Session, usuario, codigo: str) -> CodigoVerificacion:
        settings = get_settings()
        ahora = datetime.utcnow()
        codigo_verificacion = db.query(CodigoVerificacion).filter(
            CodigoVerificacion.idUsuario == usuario.idUsuario,
            CodigoVerificacion.isUsado == False,  # noqa: E712
            CodigoVerificacion.fechaExpiracion >= ahora,
        ).order_by(CodigoVerificacion.idCodigo.desc()).first()

        if not codigo_verificacion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código no existe o ya venció. Solicita uno nuevo."
            )

        if codigo_verificacion.intentos >= settings.reset_code_max_attempts:
            codigo_verificacion.isUsado = True
            codigo_verificacion.fechaUso = ahora
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Se superó el número máximo de intentos. Solicita un nuevo código."
            )

        if not codigo_verificacion.codigoHash or not verificar_contrasena(codigo, codigo_verificacion.codigoHash):
            codigo_verificacion.intentos += 1
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código inválido."
            )

        return codigo_verificacion

    @staticmethod
    def verificar_codigo_recuperacion(db: Session, datos: VerificarCodigoRequest) -> MensajeResponse:
        correo = str(datos.correoElectronico).strip().lower()
        usuario = UsuarioRepository.obtener_por_correo(db=db, correo=correo)

        if not usuario or not usuario.isActivo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código no existe o ya venció. Solicita uno nuevo."
            )

        AuthService._obtener_codigo_activo(db, usuario, datos.codigo)
        return MensajeResponse(mensaje="Código verificado correctamente.")

    @staticmethod
    def cambiar_contrasena_con_codigo(db: Session, datos: CambiarContrasenaRequest) -> MensajeResponse:
        if datos.nuevaContrasena != datos.confirmarContrasena:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las contraseñas no coinciden."
            )

        correo = str(datos.correoElectronico).strip().lower()
        usuario = UsuarioRepository.obtener_por_correo(db=db, correo=correo)

        if not usuario or not usuario.isActivo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código no existe o ya venció. Solicita uno nuevo."
            )

        codigo_verificacion = AuthService._obtener_codigo_activo(db, usuario, datos.codigo)
        ahora = datetime.utcnow()

        usuario.contrasenaHash = generar_hash_contrasena(datos.nuevaContrasena)
        usuario.isContrasenaTemporal = False
        codigo_verificacion.isUsado = True
        codigo_verificacion.fechaUso = ahora

        db.query(SesionUsuario).filter(
            SesionUsuario.idUsuario == usuario.idUsuario,
            SesionUsuario.isActiva == True,  # noqa: E712
        ).update({
            "isActiva": False,
            "fechaCierre": ahora,
            "motivoCierre": "CAMBIO_CONTRASENA",
        })

        db.commit()
        return MensajeResponse(mensaje="Contraseña actualizada correctamente. Ya puedes iniciar sesión.")
