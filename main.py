# main.py - Microservicio de INSERCIÓN (versión corregida HttpUrl)
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, conint, confloat
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "caballerosdb")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "caballeros")

if not MONGO_URI:
    raise RuntimeError("La variable de entorno MONGO_URI no está configurada")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
caballeros_col = db[MONGO_COLLECTION]

app = FastAPI(title="MS Inserción Caballeros")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CaballeroIn(BaseModel):
    nombre: str
    constelacion: str
    edad: conint(ge=1, le=200)
    urlImagen: HttpUrl
    altura: confloat(ge=0.5, le=3.0)


@app.get("/")
def root():
    return {"mensaje": "Microservicio de inserción activo. Usa POST /caballeros"}


@app.post("/caballeros", status_code=201)
def insertar_caballero(caballero: CaballeroIn):
    try:
        # Validación de unicidad por nombre
        existente = caballeros_col.find_one({"nombre": caballero.nombre})
        if existente:
            raise HTTPException(
                status_code=409,
                detail="Ya existe un caballero con ese nombre",
            )

        doc = caballero.model_dump()
        doc["urlImagen"] = str(caballero.urlImagen)  # forzamos a str

        result = caballeros_col.insert_one(doc)

        return {
            "ok": True,
            "inserted_id": str(result.inserted_id),
            "mensaje": "Caballero insertado correctamente",
        }

    except HTTPException:
        raise
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en MongoDB: {e}"
        )
