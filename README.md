# ÉTER Café — Sistema CRUD con FastAPI

Proyecto académico de administración de cafetería con cuatro tablas y operaciones **Create, Read, Update y Delete**.

## Tecnologías

- Python 3.10 o superior
- FastAPI
- Uvicorn
- SQLite mediante `sqlite3` (incluido en Python)
- Jinja2
- HTML, CSS y JavaScript

**Importante:** este proyecto NO utiliza SQLAlchemy. La base de datos se administra directamente con `sqlite3`, por lo que evitas la dependencia que te causaba problemas en Windows.

## 1. Abrir el proyecto

1. Descomprime la carpeta `ETER_Cafe_FastAPI`.
2. Abre Visual Studio Code.
3. Selecciona **Archivo > Abrir carpeta** y abre `ETER_Cafe_FastAPI`.
4. Abre una terminal desde **Terminal > Nuevo terminal**.

## 2. Verificar Python

En la terminal ejecuta:

```powershell
python --version
```

Se recomienda Python 3.10 o superior. Si Windows no reconoce `python`, prueba:

```powershell
py --version
```

## 3. Crear un entorno virtual

En Windows PowerShell:

```powershell
py -m venv .venv
```

Actívalo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación, no cambies la política global de Windows. Ejecuta esta alternativa en la misma terminal:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Y para iniciar el servidor usa:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Si la activación sí funcionó, instala normalmente:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. Ejecutar el sistema

Con el entorno virtual activado:

```powershell
python -m uvicorn main:app --reload
```

Abre en tu navegador:

- Aplicación: http://127.0.0.1:8000
- Documentación interactiva de endpoints: http://127.0.0.1:8000/docs
- Documentación alternativa: http://127.0.0.1:8000/redoc

Para detener el servidor presiona `CTRL + C` en la terminal.

## 5. Base de datos

Al iniciar por primera vez, FastAPI crea automáticamente el archivo:

`eter_cafe.db`

Este archivo contiene las cuatro tablas:

- `pedidos`
- `inventario`
- `productos`
- `trabajadores`

Los datos permanecen guardados aunque cierres el navegador o detengas el servidor. No borres `eter_cafe.db` si deseas conservar tus registros. Para respaldarlo, detén el servidor y copia ese archivo a otra carpeta.

## 6. Endpoints CRUD

Todos los endpoints responden con JSON.

| Recurso | CREATE | READ (todos) | READ (uno) | UPDATE | DELETE |
|---|---|---|---|---|---|
| Pedidos | POST /api/pedidos | GET /api/pedidos | GET /api/pedidos/{id} | PUT /api/pedidos/{id} | DELETE /api/pedidos/{id} |
| Inventario | POST /api/inventario | GET /api/inventario | GET /api/inventario/{id} | PUT /api/inventario/{id} | DELETE /api/inventario/{id} |
| Productos | POST /api/productos | GET /api/productos | GET /api/productos/{id} | PUT /api/productos/{id} | DELETE /api/productos/{id} |
| Trabajadores | POST /api/trabajadores | GET /api/trabajadores | GET /api/trabajadores/{id} | PUT /api/trabajadores/{id} | DELETE /api/trabajadores/{id} |

El dashboard también consulta `GET /api/dashboard`.

## 7. Probar los endpoints desde Swagger

1. Inicia el servidor.
2. Abre http://127.0.0.1:8000/docs.
3. Despliega, por ejemplo, `POST /api/productos`.
4. Pulsa **Try it out**.
5. Introduce un JSON de prueba:

```json
{
  "nombre": "Americano",
  "categoria": "Cafés",
  "descripcion": "Café preparado con agua caliente y shot de espresso.",
  "precio": 30,
  "disponible": true
}
```

6. Pulsa **Execute** y revisa la respuesta.
7. Prueba `GET /api/productos` para consultar el registro.
8. Usa el ID que devolvió la respuesta para probar `PUT` y `DELETE`.

Los datos anteriores son únicamente para comprobar el funcionamiento; puedes registrar los productos reales de tu cafetería desde la interfaz.

## 8. Estructura del proyecto

```text
ETER_Cafe_FastAPI/
│
├── main.py                 # Aplicación FastAPI y endpoints CRUD
├── requirements.txt        # Dependencias
├── README.md               # Instalación y ejecución
├── DOCUMENTACION_CRUD.md   # Diccionario de datos y operaciones
├── eter_cafe.db            # Se genera al iniciar
│
├── templates/
│   └── index.html          # Interfaz principal
│
└── static/
    ├── styles.css          # Diseño visual ÉTER
    └── app.js              # Consumo de endpoints con fetch()
```

## 9. ¿Cómo consume la interfaz los endpoints?

El archivo `static/app.js` usa `fetch()` para enviar solicitudes HTTP a FastAPI:

- `GET` para consultar registros.
- `POST` para crear registros.
- `PUT` para actualizar registros.
- `DELETE` para eliminar registros.

Por ejemplo, al guardar un pedido, JavaScript envía un `POST` a `/api/pedidos`. FastAPI valida los datos con Pydantic, calcula el total y los guarda en SQLite. Después devuelve el registro creado en formato JSON.

## 10. Alcance y consideraciones

Esta es una versión académica local. No incluye autenticación, despliegue en internet, sincronización entre dispositivos ni control automático de consumo de insumos por venta. Para usarla como sistema real de negocio habría que agregar esos componentes, permisos, respaldos automatizados y controles adicionales.

El servidor `--reload` es para desarrollo, no para producción. Para acceder desde otro dispositivo de la misma red se requiere configurar el servidor con `--host 0.0.0.0` y permitir el puerto en la red/firewall; no expongas el sistema directamente a internet sin seguridad.
