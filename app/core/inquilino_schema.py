import itertools
import random
from datetime import datetime
from pydantic import BaseModel, Field

# 🔥 Generador global de IDs incrementales desde 1000
_id_generator = itertools.count(1)

def generar_cedula():
    """Genera una cédula simulada de 8 a 10 dígitos"""
    return random.randint(10_000_000, 9_999_999_999)

class Inquilino(BaseModel):
    # Identificación
    id_inquilino: int = Field(default_factory=lambda: next(_id_generator))
    cedula: int = Field(default_factory=generar_cedula)

    # Datos personales
    nombre: str
    edad: int
    genero: str

    # Hábitos y estilo de vida
    fumador: str
    mascotas: str
    orden: str
    deporte: str
    bioritmo: str

    # Información adicional
    nivel_educativo: str | None = None
    musica_tipo: str | None = None
    plan_perfecto: str | None = None
    visitas: str | None = None
    personalidad: str | None = None
    instrumento: str | None = None

    # Sistema
    compatible: int = 0
    rol: str = "inquilino"
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ==============================
# 🔹 Generador de inquilinos demo
# ==============================
def generar_inquilino_demo():
    nombres = [
        "Andrés", "Camila", "Juan", "Valentina", "Mateo", "Laura", "Isabella", "Sofía",
        "Mariana", "Sebastián", "Carlos", "Paula", "Gabriela", "Martín", "Lucía", "Diana",
        "José", "Miguel", "Felipe", "Daniela", "Adriana", "Natalia", "Santiago", "Tomás"
    ]
    apellidos = [
        "García", "Martínez", "Rodríguez", "López", "Hernández", "Gómez", "Díaz",
        "Ramírez", "Torres", "Álvarez", "Castro", "Ortiz", "Jiménez", "Morales",
        "Ruiz", "Cruz", "Mendoza", "Guerrero", "Pérez", "Fernández"
    ]

    # 🔹 Nombre completo con probabilidad de doble nombre/apellido
    nombre = random.choice(nombres)
    if random.random() > 0.5:
        nombre += f" {random.choice(nombres)}"
    apellido = f"{random.choice(apellidos)} {random.choice(apellidos)}"
    nombre_completo = f"{nombre} {apellido}"

    # Construcción del objeto Inquilino
    return Inquilino(
        nombre=nombre_completo,
        edad=random.randint(15, 99),
        genero=random.choice(["masculino", "femenino", "otro"]),
        fumador=random.choice(["si", "no"]),
        mascotas=random.choice(["con mascotas", "sin mascotas"]),
        orden=random.choice(["ordenada", "desordenada"]),
        deporte=random.choice(["si", "no"]),
        bioritmo=random.choice(["madrugador", "nocturno"]),
        nivel_educativo=random.choice(["secundaria", "universitaria", "posgrado", None]),
        musica_tipo=random.choice(["rock", "pop", "salsa", "vallenato", "reggaeton", None]),
        plan_perfecto=random.choice(["cine", "leer", "salir con amigos", "hacer deporte", None]),
        visitas=random.choice(["si", "no"]),
        personalidad=random.choice(["introvertido", "extrovertido", "equilibrado", None]),
        instrumento=random.choice(["si", "no"]),
        compatible=random.choice([0, 1])  # demo simple
    )
