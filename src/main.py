from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from pydantic import BaseModel, Field
from datetime import datetime

from .osm_loader import OSMLoader
from .route_optimizer import RouteOptimizer
from .config import settings

app = FastAPI(
    title="Optimizador de Rutas OSM",
    description="API para optimización de rutas con restricciones temporales usando OpenStreetMap"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PuntoRuta(BaseModel):
    latitud: float
    longitud: float
    hora_recogida: str = None
    ventana_tiempo: Dict[str, str] = None

class SolicitudRuta(BaseModel):
    puntos: List[PuntoRuta]

class Coordenada(BaseModel):
    latitud: float = Field(..., description="Latitud en grados decimales")
    longitud: float = Field(..., description="Longitud en grados decimales")

class RutaOptimizada(BaseModel):
    orden: List[int]
    distancia_total: float = Field(..., description="Distancia total en metros")
    tiempo_estimado: float = Field(..., description="Tiempo estimado en minutos")
    ruta_coordenadas: List[Coordenada]

@app.post("/optimizar-ruta", response_model=RutaOptimizada)
async def optimizar_ruta(solicitud: SolicitudRuta):
    """
    Optimiza la ruta entre múltiples puntos considerando restricciones temporales
    """
    try:
        # Inicializar el cargador de OSM
        osm_loader = OSMLoader()
        if not osm_loader.cargar_area(settings.BBOX_DEFAULT):
            raise HTTPException(status_code=500, detail="Error al cargar datos de OSM")

        # Convertir puntos a nodos
        puntos_nodos = []
        for punto in solicitud.puntos:
            node_id = osm_loader.obtener_nodo_cercano(punto.latitud, punto.longitud)
            puntos_nodos.append({
                "node_id": node_id,
                "hora_recogida": punto.hora_recogida,
                "ventana_tiempo": punto.ventana_tiempo
            })

        # Optimizar ruta
        optimizer = RouteOptimizer(osm_loader.graph)
        resultado = optimizer.optimizar_ruta(puntos_nodos)
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 