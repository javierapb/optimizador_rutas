from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from pydantic import BaseModel, Field
from datetime import datetime

from .osm_loader import OSMLoader
from .route_optimizer import RouteOptimizer
from .config import settings
from .schemas import Coordinates

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
    latitude: float
    longitude: float
    hora_recogida: str = None
    ventana_tiempo: Dict[str, str] = None

class SolicitudRuta(BaseModel):
    origin: Coordinates = Field(..., description="Punto de origen del vehículo")
    destination: Coordinates = Field(..., description="Punto de destino final")
    puntos: List[PuntoRuta]

class Coordenada(BaseModel):
    latitude: float = Field(..., description="Latitud en grados decimales")
    longitude: float = Field(..., description="Longitud en grados decimales")

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
        
        # Obtener coordenadas de origen y destino
        origin = (solicitud.origin.latitude, solicitud.origin.longitude)
        destination = (solicitud.destination.latitude, solicitud.destination.longitude)
        
        # Obtener coordenadas de puntos intermedios
        points = [(p.latitude, p.longitude) for p in solicitud.puntos]
        
        # Cargar el área que cubra todos los puntos
        if not osm_loader.cargar_area(origin, destination, points):
            raise HTTPException(status_code=500, detail="Error al cargar datos de OSM")

        # Convertir puntos a nodos, incluyendo origen y destino
        puntos_nodos = []
        
        # Añadir punto de origen
        origin_node = osm_loader.obtener_nodo_cercano(
            solicitud.origin.latitude, 
            solicitud.origin.longitude
        )
        puntos_nodos.append({
            "node_id": origin_node,
            "hora_recogida": None,
            "ventana_tiempo": None
        })

        # Añadir puntos intermedios
        for punto in solicitud.puntos:
            node_id = osm_loader.obtener_nodo_cercano(punto.latitude, punto.longitude)
            puntos_nodos.append({
                "node_id": node_id,
                "hora_recogida": punto.hora_recogida,
                "ventana_tiempo": punto.ventana_tiempo
            })

        # Añadir punto de destino
        destination_node = osm_loader.obtener_nodo_cercano(
            solicitud.destination.latitude, 
            solicitud.destination.longitude
        )
        puntos_nodos.append({
            "node_id": destination_node,
            "hora_recogida": None,
            "ventana_tiempo": None
        })

        # Optimizar ruta
        optimizer = RouteOptimizer(osm_loader.graph)
        resultado = optimizer.optimizar_ruta(puntos_nodos)
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 