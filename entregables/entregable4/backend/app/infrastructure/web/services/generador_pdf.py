"""Generador de PDF para comprobantes de venta."""
from __future__ import annotations

import io
import logging
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.application.ports.generador_pdf import GeneradorPDF
from app.infrastructure.web.services.minio_service import MinioService

log = logging.getLogger(__name__)


class GeneradorPDFService(GeneradorPDF):
    def __init__(self, minio: Optional[MinioService] = None) -> None:
        self._minio = minio

    def generar_comprobante_venta(self, venta_id: int) -> bytes:
        # En un sistema real, aquí cargaríamos la venta desde el repo.
        # Para mantener el servicio aislado, lo resolvemos via session:
        from app.infrastructure.persistence.sqlalchemy.database import SessionLocal
        from app.infrastructure.persistence.sqlalchemy.models import (
            ClienteModel,
            ProductoModel,
            SucursalModel,
            UsuarioModel,
            VentaModel,
        )
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        db = SessionLocal()
        try:
            stmt = (
                select(VentaModel)
                .options(selectinload(VentaModel.detalles))
                .where(VentaModel.id == venta_id)
            )
            venta = db.execute(stmt).scalar_one_or_none()
            if not venta:
                raise ValueError(f"Venta {venta_id} no encontrada")

            cliente = db.get(ClienteModel, venta.cliente_id) if venta.cliente_id else None
            sucursal = db.get(SucursalModel, venta.sucursal_id)
            usuario = db.get(UsuarioModel, venta.usuario_id)

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm,
                topMargin=15 * mm, bottomMargin=15 * mm,
            )
            styles = getSampleStyleSheet()
            elems = []

            # Encabezado
            elems.append(Paragraph(f"<b>{sucursal.nombre if sucursal else 'Sistema Inventario'}</b>", styles["Title"]))
            elems.append(Paragraph(f"{venta.tipo_comprobante} &nbsp; {venta.serie}-{venta.numero}", styles["Heading2"]))
            elems.append(Paragraph(f"Fecha: {venta.fecha.strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
            if cliente:
                elems.append(Paragraph(f"Cliente: {cliente.nombre} ({cliente.tipo_documento}: {cliente.numero_documento})", styles["Normal"]))
            elems.append(Paragraph(f"Atendido por: {usuario.nombre_completo if usuario else ''}", styles["Normal"]))
            elems.append(Spacer(1, 8 * mm))

            # Tabla de items
            data = [["Cant.", "Producto", "P.Unit", "IGV", "Total"]]
            for d in venta.detalles:
                prod = db.get(ProductoModel, d.producto_id)
                nombre = prod.nombre if prod else f"#{d.producto_id}"
                data.append([
                    f"{d.cantidad:.2f}",
                    nombre,
                    f"S/ {d.precio_unitario:.2f}",
                    f"S/ {d.igv:.2f}",
                    f"S/ {d.total:.2f}",
                ])
            t = Table(data, colWidths=[20 * mm, 80 * mm, 25 * mm, 20 * mm, 25 * mm])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            ]))
            elems.append(t)
            elems.append(Spacer(1, 5 * mm))

            # Totales
            elems.append(Paragraph(f"<b>Subtotal:</b> S/ {venta.subtotal:.2f}", styles["Normal"]))
            elems.append(Paragraph(f"<b>IGV (18%):</b> S/ {venta.igv:.2f}", styles["Normal"]))
            elems.append(Paragraph(f"<b>TOTAL:</b> S/ {venta.total:.2f}", styles["Heading2"]))
            elems.append(Spacer(1, 5 * mm))
            elems.append(Paragraph("<i>Gracias por su compra</i>", styles["Italic"]))

            doc.build(elems)
            return buffer.getvalue()
        finally:
            db.close()

    def guardar(self, contenido: bytes, nombre_archivo: str) -> str:
        if self._minio is None:
            return f"/tmp/{nombre_archivo}"
        return self._minio.subir(contenido, nombre_archivo)
