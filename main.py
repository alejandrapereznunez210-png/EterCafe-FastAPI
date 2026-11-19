
from contextlib import asynccontextmanager
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field



BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "eter_cafe.db"



def get_connection():
    """Abre una conexión con la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:

        conn.executescript("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descripcion TEXT DEFAULT '',
            precio REAL NOT NULL CHECK(precio >= 0),
            disponible INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            cantidad REAL NOT NULL DEFAULT 0 CHECK(cantidad >= 0),
            unidad TEXT NOT NULL,
            stock_minimo REAL NOT NULL DEFAULT 0 CHECK(stock_minimo >= 0)
        );

        CREATE TABLE IF NOT EXISTS trabajadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            puesto TEXT NOT NULL,
            telefono TEXT DEFAULT '',
            correo TEXT DEFAULT '',
            estado TEXT NOT NULL DEFAULT 'Activo'
        );

        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL CHECK(cantidad > 0),
            precio_unitario REAL NOT NULL CHECK(precio_unitario >= 0),
            total REAL NOT NULL CHECK(total >= 0),
            fecha TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            estado TEXT NOT NULL DEFAULT 'Pendiente',
            observaciones TEXT DEFAULT ''
        );
        """)

     
        total_productos = conn.execute(
            "SELECT COUNT(*) FROM productos"
        ).fetchone()[0]

        if total_productos == 0:

            menu_inicial = [
                (
                    "Americano",
                    "Cafés",
                    "Café preparado con agua caliente, shot de espresso, canela y azúcar opcionales.",
                    30,
                    1
                ),
                (
                    "Moka",
                    "Cafés",
                    "Café con leche y suave chocolate, para los que aman lo dulce.",
                    35,
                    1
                ),
                (
                    "Capuchino de Vainilla",
                    "Capuchinos",
                    "Mezcla cremosa de capuchino en polvo con dulce vainilla.",
                    30,
                    1
                ),
                (
                    "Capuchino Pumpkin Spice",
                    "Capuchinos",
                    "Capuchino con un toque cálido de especias aromáticas de calabaza.",
                    35,
                    1
                ),
                (
                    "Latte de Vainilla",
                    "Lattes",
                    "Shot de espresso, leche cremosa, vainilla y azúcar al gusto.",
                    35,
                    1
                ),
                (
                    "Matcha Tradicional",
                    "Matcha",
                    "Matcha premium con leche de tu elección, textura suave y pura.",
                    35,
                    1
                ),
                (
                    "Matcha Pumpkin Spice",
                    "Matcha",
                    "Matcha tradicional con especias cálidas de la temporada.",
                    38,
                    1
                ),
                (
                    "Té de Manzanilla",
                    "Tés",
                    "Infusión suave y aromática de flor de manzanilla silvestre.",
                    25,
                    1
                ),
                (
                    "Taro",
                    "Bebidas sin café",
                    "Bebida de taro suave y cremoso con tu leche favorita.",
                    30,
                    1
                ),
                (
                    "Pumpkin Spice",
                    "Bebidas sin café",
                    "Nuestra mezcla de especias cálidas y reconfortantes, sin café.",
                    30,
                    1
                ),
                (
                    "Malteada de Fresa",
                    "Malteadas",
                    "Bebida cremosa con auténtico sabor a fresa.",
                    35,
                    1
                ),
                (
                    "Malteada de Vainilla",
                    "Malteadas",
                    "Clásica malteada con el suave aroma de la vainilla.",
                    35,
                    1
                ),
                (
                    "Malteada de Chocolate",
                    "Malteadas",
                    "Malteada con un rico e intenso sabor a chocolate.",
                    35,
                    1
                )
            ]

            conn.executemany(
                """
                INSERT INTO productos
                (nombre, categoria, descripcion, precio, disponible)
                VALUES (?, ?, ?, ?, ?)
                """,
                menu_inicial
            )

        conn.commit()




@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield




app = FastAPI(
    title="ÉTER Café API",
    description=(
        "API académica para administrar pedidos, inventario, "
        "menú y trabajadores de ÉTER Café."
    ),
    version="1.0.0",
    lifespan=lifespan
)




app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)




class ProductoIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    categoria: str = Field(min_length=1, max_length=60)
    descripcion: str = ""
    precio: float = Field(ge=0)
    disponible: bool = True


class InventarioIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    categoria: str = Field(min_length=1, max_length=60)
    cantidad: float = Field(ge=0)
    unidad: str = Field(min_length=1, max_length=30)
    stock_minimo: float = Field(ge=0)


class TrabajadorIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    puesto: str = Field(min_length=1, max_length=60)
    telefono: str = ""
    correo: str = ""
    estado: str = "Activo"


class PedidoIn(BaseModel):
    cliente: str = Field(min_length=1, max_length=100)
    producto: str = Field(min_length=1, max_length=100)
    cantidad: int = Field(gt=0)
    precio_unitario: float = Field(ge=0)
    estado: str = "Pendiente"
    observaciones: str = ""



def rows(query, params=()):
    with get_connection() as conn:
        resultado = conn.execute(query, params).fetchall()
        return [dict(r) for r in resultado]


def one(query, params=()):
    with get_connection() as conn:
        resultado = conn.execute(query, params).fetchone()
        return dict(resultado) if resultado else None


def create_record(table, data):
    columns = list(data.keys())
    placeholders = ", ".join("?" for _ in columns)

    sql = (
        f"INSERT INTO {table} "
        f"({', '.join(columns)}) "
        f"VALUES ({placeholders})"
    )

    with get_connection() as conn:
        cur = conn.execute(sql, tuple(data.values()))
        conn.commit()
        new_id = cur.lastrowid

    return new_id


def update_record(table, item_id, data):
    assignments = ", ".join(
        f"{key} = ?" for key in data
    )

    with get_connection() as conn:
        cur = conn.execute(
            f"UPDATE {table} SET {assignments} WHERE id = ?",
            (*data.values(), item_id)
        )

        conn.commit()
        return cur.rowcount


def delete_record(table, item_id):
    with get_connection() as conn:
        cur = conn.execute(
            f"DELETE FROM {table} WHERE id = ?",
            (item_id,)
        )

        conn.commit()
        return cur.rowcount




@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )



@app.get("/api/dashboard")
def dashboard():
    return {
        "pedidos": one(
            "SELECT COUNT(*) AS total FROM pedidos"
        )["total"],

        "productos": one(
            "SELECT COUNT(*) AS total FROM productos"
        )["total"],

        "insumos": one(
            "SELECT COUNT(*) AS total FROM inventario"
        )["total"],

        "trabajadores": one(
            "SELECT COUNT(*) AS total FROM trabajadores"
        )["total"],

        "ventas": one(
            "SELECT COALESCE(SUM(total), 0) AS total FROM pedidos"
        )["total"]
    }




@app.post("/api/productos", status_code=201)
def crear_producto(item: ProductoIn):
    data = item.model_dump()
    data["disponible"] = int(data["disponible"])

    item_id = create_record("productos", data)

    return one(
        "SELECT * FROM productos WHERE id = ?",
        (item_id,)
    )


@app.get("/api/productos")
def listar_productos():
    return rows(
        "SELECT * FROM productos ORDER BY id DESC"
    )


@app.get("/api/productos/{item_id}")
def obtener_producto(item_id: int):
    item = one(
        "SELECT * FROM productos WHERE id = ?",
        (item_id,)
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    return item


@app.put("/api/productos/{item_id}")
def actualizar_producto(item_id: int, item: ProductoIn):
    data = item.model_dump()
    data["disponible"] = int(data["disponible"])

    if not update_record("productos", item_id, data):
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    return one(
        "SELECT * FROM productos WHERE id = ?",
        (item_id,)
    )


@app.delete("/api/productos/{item_id}")
def eliminar_producto(item_id: int):
    if not delete_record("productos", item_id):
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    return {
        "mensaje": "Producto eliminado correctamente"
    }




@app.post("/api/inventario", status_code=201)
def crear_insumo(item: InventarioIn):
    item_id = create_record(
        "inventario",
        item.model_dump()
    )

    return one(
        "SELECT * FROM inventario WHERE id = ?",
        (item_id,)
    )


@app.get("/api/inventario")
def listar_inventario():
    return rows(
        "SELECT * FROM inventario ORDER BY id DESC"
    )


@app.get("/api/inventario/{item_id}")
def obtener_insumo(item_id: int):
    item = one(
        "SELECT * FROM inventario WHERE id = ?",
        (item_id,)
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Insumo no encontrado"
        )

    return item


@app.put("/api/inventario/{item_id}")
def actualizar_insumo(item_id: int, item: InventarioIn):
    if not update_record(
        "inventario",
        item_id,
        item.model_dump()
    ):
        raise HTTPException(
            status_code=404,
            detail="Insumo no encontrado"
        )

    return one(
        "SELECT * FROM inventario WHERE id = ?",
        (item_id,)
    )


@app.delete("/api/inventario/{item_id}")
def eliminar_insumo(item_id: int):
    if not delete_record("inventario", item_id):
        raise HTTPException(
            status_code=404,
            detail="Insumo no encontrado"
        )

    return {
        "mensaje": "Insumo eliminado correctamente"
    }




@app.post("/api/trabajadores", status_code=201)
def crear_trabajador(item: TrabajadorIn):
    item_id = create_record(
        "trabajadores",
        item.model_dump()
    )

    return one(
        "SELECT * FROM trabajadores WHERE id = ?",
        (item_id,)
    )


@app.get("/api/trabajadores")
def listar_trabajadores():
    return rows(
        "SELECT * FROM trabajadores ORDER BY id DESC"
    )


@app.get("/api/trabajadores/{item_id}")
def obtener_trabajador(item_id: int):
    item = one(
        "SELECT * FROM trabajadores WHERE id = ?",
        (item_id,)
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Trabajador no encontrado"
        )

    return item


@app.put("/api/trabajadores/{item_id}")
def actualizar_trabajador(item_id: int, item: TrabajadorIn):
    if not update_record(
        "trabajadores",
        item_id,
        item.model_dump()
    ):
        raise HTTPException(
            status_code=404,
            detail="Trabajador no encontrado"
        )

    return one(
        "SELECT * FROM trabajadores WHERE id = ?",
        (item_id,)
    )


@app.delete("/api/trabajadores/{item_id}")
def eliminar_trabajador(item_id: int):
    if not delete_record("trabajadores", item_id):
        raise HTTPException(
            status_code=404,
            detail="Trabajador no encontrado"
        )

    return {
        "mensaje": "Trabajador eliminado correctamente"
    }




@app.post("/api/pedidos", status_code=201)
def crear_pedido(item: PedidoIn):
    data = item.model_dump()

    data["total"] = round(
        data["cantidad"] * data["precio_unitario"],
        2
    )

    item_id = create_record("pedidos", data)

    return one(
        "SELECT * FROM pedidos WHERE id = ?",
        (item_id,)
    )


@app.get("/api/pedidos")
def listar_pedidos():
    return rows(
        "SELECT * FROM pedidos ORDER BY id DESC"
    )


@app.get("/api/pedidos/{item_id}")
def obtener_pedido(item_id: int):
    item = one(
        "SELECT * FROM pedidos WHERE id = ?",
        (item_id,)
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    return item


@app.put("/api/pedidos/{item_id}")
def actualizar_pedido(item_id: int, item: PedidoIn):
    data = item.model_dump()

    data["total"] = round(
        data["cantidad"] * data["precio_unitario"],
        2
    )

    if not update_record("pedidos", item_id, data):
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    return one(
        "SELECT * FROM pedidos WHERE id = ?",
        (item_id,)
    )


@app.delete("/api/pedidos/{item_id}")
def eliminar_pedido(item_id: int):
    if not delete_record("pedidos", item_id):
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado"
        )

    return {
        "mensaje": "Pedido eliminado correctamente"
    }
