from pydantic import BaseModel, Field
from typing import List, Dict

class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitud entre -90 y 90")
    longitude: float = Field(..., ge=-180, le=180, description="Longitud entre -180 y 180")

class PuntoRuta(BaseModel):
    latitude: float
    longitude: float
    hora_recogida: str = None
    ventana_tiempo: Dict[str, str] = None

class SolicitudRuta(BaseModel):
    origin: Coordinates = Field(..., description="Punto de origen del vehículo")
    destination: Coordinates = Field(..., description="Punto de destino final")
    puntos: List[PuntoRuta]
    # Aquí puedes agregar más campos según necesites para tu API 