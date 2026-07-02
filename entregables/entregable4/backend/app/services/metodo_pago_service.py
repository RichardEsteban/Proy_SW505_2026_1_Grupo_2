from sqlalchemy.orm import Session

from app.models.metodo_pago import MetodoPago
from app.repositories.metodo_pago_repository import MetodoPagoRepository
from app.schemas.metodo_pago_schema import MetodoPagoResponse


class MetodoPagoService:

    @staticmethod
    def _response(metodo_pago: MetodoPago) -> MetodoPagoResponse:
        return MetodoPagoResponse(
            idMetodoPago=metodo_pago.idMetodoPago,
            nombreMetodo=metodo_pago.nombreMetodo,
            isActivo=metodo_pago.isActivo,
        )

    @staticmethod
    def listar(db: Session, incluir_inactivos: bool = False) -> list[MetodoPagoResponse]:
        metodos = MetodoPagoRepository.obtener_todos(
            db=db,
            incluir_inactivos=incluir_inactivos,
        )
        return [MetodoPagoService._response(metodo) for metodo in metodos]
