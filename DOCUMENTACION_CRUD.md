# Documentación de base de datos y CRUD — ÉTER Café

## 1. Descripción general

ÉTER Café es un sistema web para administrar las operaciones básicas de una cafetería. Está desarrollado con Python y FastAPI. SQLite almacena la información y JavaScript consume los endpoints mediante solicitudes HTTP.

La base de datos contiene cuatro tablas: `pedidos`, `inventario`, `productos` y `trabajadores`. Cada tabla implementa las operaciones CRUD: crear, leer, actualizar y eliminar.

## 2. Diccionario de datos

### Tabla: pedidos

| Campo | Tipo de dato | Descripción |
|---|---|---|
| id | INTEGER, PK | Identificador único autoincremental del pedido |
| cliente | TEXT | Nombre del cliente |
| producto | TEXT | Producto solicitado |
| cantidad | INTEGER | Número de unidades solicitadas |
| precio_unitario | REAL | Precio de una unidad |
| total | REAL | Importe calculado (cantidad × precio unitario) |
| fecha | TEXT | Fecha y hora de registro |
| estado | TEXT | Estado del pedido |
| observaciones | TEXT | Notas adicionales |

**CRUD de pedidos:**
- Create: `POST /api/pedidos` registra cliente, producto, cantidad, precio, estado y observaciones. El sistema calcula el total.
- Read: `GET /api/pedidos` muestra todos los pedidos; `GET /api/pedidos/{id}` consulta uno.
- Update: `PUT /api/pedidos/{id}` modifica los datos del pedido y recalcula el total.
- Delete: `DELETE /api/pedidos/{id}` elimina el pedido indicado.

### Tabla: inventario

| Campo | Tipo de dato | Descripción |
|---|---|---|
| id | INTEGER, PK | Identificador único autoincremental |
| nombre | TEXT | Nombre del insumo |
| categoria | TEXT | Clasificación del insumo |
| cantidad | REAL | Cantidad disponible |
| unidad | TEXT | Unidad de medida: gramos, mililitros, piezas, etc. |
| stock_minimo | REAL | Cantidad mínima deseada antes de considerar stock bajo |

**CRUD de inventario:**
- Create: `POST /api/inventario` registra un insumo.
- Read: `GET /api/inventario` consulta todos los insumos; `GET /api/inventario/{id}` consulta uno.
- Update: `PUT /api/inventario/{id}` modifica la información o existencia.
- Delete: `DELETE /api/inventario/{id}` elimina el insumo.

### Tabla: productos

| Campo | Tipo de dato | Descripción |
|---|---|---|
| id | INTEGER, PK | Identificador único autoincremental |
| nombre | TEXT | Nombre de la bebida o producto |
| categoria | TEXT | Categoría del menú |
| descripcion | TEXT | Descripción del producto |
| precio | REAL | Precio de venta en pesos mexicanos |
| disponible | INTEGER | 1 si está disponible y 0 si no está disponible |

**CRUD de productos:**
- Create: `POST /api/productos` agrega una bebida al menú.
- Read: `GET /api/productos` consulta el menú; `GET /api/productos/{id}` consulta un producto.
- Update: `PUT /api/productos/{id}` modifica nombre, categoría, descripción, precio o disponibilidad.
- Delete: `DELETE /api/productos/{id}` elimina el producto.

### Tabla: trabajadores

| Campo | Tipo de dato | Descripción |
|---|---|---|
| id | INTEGER, PK | Identificador único autoincremental |
| nombre | TEXT | Nombre completo |
| puesto | TEXT | Función o puesto dentro de la cafetería |
| telefono | TEXT | Número telefónico |
| correo | TEXT | Correo electrónico |
| estado | TEXT | Situación laboral: Activo o Inactivo |

**CRUD de trabajadores:**
- Create: `POST /api/trabajadores` registra un trabajador.
- Read: `GET /api/trabajadores` consulta todos; `GET /api/trabajadores/{id}` consulta uno.
- Update: `PUT /api/trabajadores/{id}` modifica sus datos.
- Delete: `DELETE /api/trabajadores/{id}` elimina el registro.

## 3. Métodos HTTP utilizados

| Método | Operación | Función |
|---|---|---|
| POST | Create | Envía información nueva para guardarla |
| GET | Read | Obtiene uno o varios registros |
| PUT | Update | Actualiza los datos de un registro |
| DELETE | Delete | Elimina un registro |

## 4. Consumo de endpoints

La interfaz utiliza JavaScript y `fetch()` para comunicarse con FastAPI. Los datos se envían y reciben en formato JSON. FastAPI recibe la petición, valida el contenido con modelos Pydantic, ejecuta la consulta correspondiente en SQLite y devuelve una respuesta.

## 5. Validaciones

- Los nombres y campos principales son obligatorios.
- Los precios no pueden ser negativos.
- Las cantidades de inventario no pueden ser negativas.
- La cantidad de un pedido debe ser mayor que cero.
- Si el ID solicitado no existe, FastAPI responde con el código HTTP 404.
- Si los datos enviados no cumplen las validaciones, FastAPI responde con el código HTTP 422.

## 6. Conclusión

El proyecto demuestra la implementación de una API REST con FastAPI, el uso de métodos HTTP y la persistencia de información en una base de datos SQLite. Las cuatro tablas cuentan con las operaciones CRUD completas y pueden administrarse desde la interfaz web o probarse individualmente mediante la documentación automática de FastAPI en `/docs`.
