# Sistema MYPE POS - Proyecto SW505

## Descripción general

Este proyecto es una solución de punto de venta y gestión de inventarios diseñada para pequeñas y medianas empresas (MYPE) del sector comercial. Combina una API backend en Python con FastAPI y una interfaz frontend en React + Vite, además de una base de datos MySQL. El objetivo es facilitar el control de productos, ventas, proveedores, reposiciones, órdenes de compra y alertas de stock.

## ¿A quién va dirigido?

- Dueños de tiendas y sucursales con operaciones de inventario y ventas.
- Supervisores de almacén y sucursales que necesitan visibilidad de stock y solicitudes de reposición.
- Vendedores que utilizan el sistema para registrar ventas y clientes.
- Equipos académicos que buscan un proyecto completo de ingeniería de software con arquitectura backend/frontend/Docker.

## Qué busca solucionar

El proyecto aborda los retos comunes de las MYPE:

- Falta de control centralizado del inventario y ubicaciones.
- Dificultad para gestionar proveedores y órdenes de compra.
- Necesidad de alertas automáticas por bajo stock o productos agotados.
- Registro de ventas y clientes con diferentes métodos de pago.
- Gestión de usuarios con roles específicos (administrador, supervisor, vendedor).

## Componentes principales

- `backend/`: API REST construida con FastAPI, SQLAlchemy y MySQL.
- `frontend/`: interfaz web creada con React, Vite y Tailwind.
- `database/`: scripts SQL para generar esquema y cargar datos base de muestra.
- `docker-compose.yml`: orquesta una base de datos MySQL, el backend y el frontend en contenedores.

## Características destacadas

- Gestión de productos, categorías, proveedores y ubicaciones.
- Control de inventario por sucursal y almacén central.
- Generación de alertas por stock mínimo o agotado.
- Creación y seguimiento de órdenes de compra y solicitudes de reposición.
- Autenticación y roles de usuario.
- Frontend con rutas para diferentes perfiles de usuario.

## Ejecución local con Docker

Desde la carpeta raíz del proyecto (`entregables/entregable4`):

```bash
docker compose up --build
```

Luego:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Configuración del backend

El servicio backend lee variables de entorno desde `./entregables/entregable4/.env.docker` cuando se ejecuta con Docker. Las variables principales son:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `APP_DEBUG`

## Ejecución sin Docker

1. Ir a `entregables/entregable4/backend`
2. Crear y activar un entorno virtual
3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Crear un archivo `.env` con las variables necesarias.
5. Ejecutar el servidor:

```bash
python run.py
```

## Estructura del repositorio

- `entregables/entregable1/` - Primer entregable del curso.
- `entregables/entregable2/` - Segundo entregable.
- `entregables/entregable3/` - Tercer entregable.
- `entregables/entregable4/` - Entregable final con la aplicación completa.

## Tecnologías usadas

- Python 3.13
- FastAPI
- SQLAlchemy
- MySQL / PyMySQL
- React
- Vite
- Tailwind CSS
- Docker
- Docker Compose

## Observaciones

El proyecto está pensado para ser una aplicación de demostración funcional para MYPE, con un backend modular y un frontend escalable. El uso de Docker facilita su despliegue y prueba sin necesidad de instalar todas las dependencias manualmente.

---

Si subes este repositorio a GitHub, este README sirve como una guía clara del propósito del proyecto, su alcance y cómo ejecutarlo localmente.