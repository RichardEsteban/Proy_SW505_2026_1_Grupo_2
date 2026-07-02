from fastapi import APIRouter

from app.api.routes.system import auth_routes, health_routes
from app.api.routes.admin import empresa_routes, usuario_routes
from app.api.routes.catalogo import categoria_routes, producto_routes, proveedor_routes
from app.api.routes.ubicaciones import ubicacion_routes
from app.api.routes.inventario import alerta_routes, inventario_routes
from app.api.routes.compras import orden_compra_routes
from app.api.routes.reposiciones import reposicion_routes
from app.api.routes.ventas import cliente_routes, metodo_pago_routes, venta_routes
from app.api.routes.reportes import reporte_routes


api_router = APIRouter()

api_router.include_router(auth_routes.router)
api_router.include_router(empresa_routes.router)
api_router.include_router(health_routes.router)
api_router.include_router(ubicacion_routes.router)
api_router.include_router(usuario_routes.router)
api_router.include_router(categoria_routes.router)
api_router.include_router(cliente_routes.router)
api_router.include_router(metodo_pago_routes.router)
api_router.include_router(proveedor_routes.router)
api_router.include_router(producto_routes.router)
api_router.include_router(inventario_routes.router)
api_router.include_router(venta_routes.router)
api_router.include_router(orden_compra_routes.router)
api_router.include_router(reposicion_routes.router)
api_router.include_router(alerta_routes.router)
api_router.include_router(reporte_routes.router)
