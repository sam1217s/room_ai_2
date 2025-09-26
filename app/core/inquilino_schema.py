# app/core/inquilino_schema.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import random
import uuid


class Inquilino(BaseModel):
    """
    🎯 Esquema de datos para un Inquilino
    Se valida antes de insertar en MongoDB
    """

    id_inquilino: int = Field(..., gt=0, description="ID único del inquilino")
    nombre: str = Field(..., min_length=2, max_length=50, description="Nombre completo")
    edad: int = Field(..., ge=18, le=70, description="Edad entre 18 y 70")
    genero: str = Field(..., pattern="^(masculino|femenino|otro)$", description="Género")

    fumador: str = Field(..., pattern="^(si|no)$", description="¿Es fumador?")
    mascotas: str = Field(..., pattern="^(con mascotas|sin mascotas)$", description="Mascotas")
    orden: str = Field(..., pattern="^(ordenada|desordenada)$", description="Nivel de orden")
    deporte: str = Field(..., pattern="^(si|no)$", description="¿Practica deporte?")
    bioritmo: str = Field(..., pattern="^(madrugador|nocturno)$", description="Ritmo de vida")

    nivel_educativo: Optional[str] = Field(None, description="Nivel educativo")
    musica_tipo: Optional[str] = Field(None, description="Preferencia musical")
    plan_perfecto: Optional[str] = Field(None, description="Plan perfecto de fin de semana")
    visitas: Optional[str] = Field(None, pattern="^(si|no)$", description="¿Recibe visitas?")
    personalidad: Optional[str] = Field(None, description="Tipo de personalidad")
    instrumento: Optional[str] = Field(None, pattern="^(si|no)$", description="¿Toca algún instrumento?")

    compatible: int = Field(..., ge=0, le=1, description="Etiqueta binaria de compatibilidad")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # ==========================
    # VALIDACIONES PERSONALIZADAS
    # ==========================
    @validator("nombre")
    def nombre_capitalize(cls, v):
        return v.strip().title()

    @validator("nivel_educativo")
    def validar_nivel(cls, v):
        if v and v.lower() not in ["secundaria", "universitaria", "posgrado"]:
            raise ValueError("Nivel educativo inválido")
        return v

    @validator("musica_tipo")
    def validar_musica(cls, v):
        if v and len(v) < 3:
            raise ValueError("El tipo de música debe tener al menos 3 caracteres")
        return v


# =====================================================
# 🔧 GENERADOR DE INQUILINOS DEMO
# =====================================================
def generar_inquilino_demo() -> dict:
    nombres = ["Juan", "Ana", "Pedro", "Luisa", "Carlos", "Marta", "Felipe", "Sofía", "Andrés", "Camila"]
    generos = ["masculino", "femenino", "otro"]
    si_no = ["si", "no"]

    # Datos base
    inquilino = {
        "id_inquilino": int(uuid.uuid4().int % 1000000),
        "nombre": random.choice(nombres),
        "edad": random.randint(18, 70),
        "genero": random.choice(generos),
        "fumador": random.choice(si_no),
        "mascotas": random.choice(["con mascotas", "sin mascotas"]),
        "orden": random.choice(["ordenada", "desordenada"]),
        "deporte": random.choice(si_no),
        "bioritmo": random.choice(["madrugador", "nocturno"]),
        "nivel_educativo": random.choice(["secundaria", "universitaria", "posgrado"]),
        "musica_tipo": random.choice(["rock", "pop", "salsa", "vallenato", "jazz"]),
        "plan_perfecto": random.choice(["cine", "viajar", "leer", "salir con amigos"]),
        "visitas": random.choice(si_no),
        "personalidad": random.choice(["extrovertido", "introvertido", "neutral"]),
        "instrumento": random.choice(si_no),
    }

    # 🎯 Regla de compatibilidad
    puntaje = 0
    if inquilino["fumador"] == "no":
        puntaje += 1
    if inquilino["orden"] == "ordenada":
        puntaje += 1
    if inquilino["mascotas"] == "sin mascotas":
        puntaje += 1
    if inquilino["deporte"] == "si":
        puntaje += 1
    if inquilino["bioritmo"] == "madrugador":
        puntaje += 1

    # Etiqueta: 1 compatible, 0 no compatible
    inquilino["compatible"] = 1 if puntaje >= 3 else 0

    return Inquilino(**inquilino).dict()
