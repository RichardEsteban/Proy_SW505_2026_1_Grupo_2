"""Caso de uso: Gestión de productos (CRUD)."""
from __future__ import annotations

from typing import List, Optional

from app.application.ports.repositorio_producto import RepositorioProducto
from app.domain.entities.producto import Producto


class GestionarProductos:
    def __init__(self, repo: RepositorioProducto) -> None:
        self._repo = repo

    def listar(self, solo_activos: bool = True) -> List[Producto]:
        return self._repo.listar(solo_activos=solo_activos)

    def buscar(self, termino: str, limit: int = 50) -> List[Producto]:
        return self._repo.buscar(termino=termino, limit=limit)

    def obtener(self, producto_id: int) -> Optional[Producto]:
        return self._repo.obtener_por_id(producto_id)

    def crear(
        self,
        sku: str,
        nombre: str,
        precio_compra: float,
        precio_venta: float,
        codigo_barra: Optional[str] = None,
        descripcion: Optional[str] = None,
        categoria_id: Optional[int] = None,
        proveedor_id: Optional[int] = None,
        unidad_medida: str = "UND",
        incluye_igv: bool = True,
    ) -> Producto:
        if self._repo.obtener_por_sku(sku):
            raise ValueError(f"SKU {sku} ya existe")
        producto = Producto(
            id=None,
            sku=sku,
            codigo_barra=codigo_barra,
            nombre=nombre,
            descripcion=descripcion,
            categoria_id=categoria_id,
            proveedor_id=proveedor_id,
            precio_compra=precio_compra,
            precio_venta=precio_venta,
            incluye_igv=incluye_igv,
            unidad_medida=unidad_medida,
        )
        return self._repo.crear(producto)

    def actualizar(self, producto: Producto) -> Producto:
        return self._repo.actualizar(producto)

    def eliminar(self, producto_id: int) -> None:
        self._repo.eliminar(producto_id)
