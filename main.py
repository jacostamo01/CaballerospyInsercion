# main.py - Microservicio de INSERCIÓN
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, conint, confloat
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "caballerosdb")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "caballeros")

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


@app.post("/caballerosI", status_code=201)
def insertar_caballero(caballero: CaballeroIn):
    """
    POST /caballeros
    Body JSON:
    {
      "nombre": "...",
      "constelacion": "...",
      "edad": 20,
      "urlImagen": "https://...",
      "altura": 1.80
    }
    """
    # Evitar duplicados por nombre (puedes quitar esto si no quieres restricción)
    existente = caballeros_col.find_one({"nombre": caballero.nombre})
    if existente:
        raise HTTPException(status_code=409, detail="Ya existe un caballero con ese nombre")

    result = caballeros_col.insert_one(caballero.dict())
    return {
        "ok": True,
        "inserted_id": str(result.inserted_id),
        "mensaje": "Caballero insertado correctamente",
    }
