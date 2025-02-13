import osmnx as ox
import networkx as nx
from typing import Tuple

class OSMLoader:
    def __init__(self):
        self.graph = None
        
    def cargar_area(self, origin: Tuple[float, float], destination: Tuple[float, float], points: list[Tuple[float, float]] = None):
        """
        Carga los datos de OSM para un área que cubra todos los puntos necesarios
        """
        try:
            # Recolectar todos los puntos
            all_points = [origin, destination]
            if points:
                all_points.extend(points)
            
            # Calcular el centro y la distancia necesaria
            north = max(p[0] for p in all_points)
            south = min(p[0] for p in all_points)
            east = max(p[1] for p in all_points)
            west = min(p[1] for p in all_points)
            
            # Añadir un margen del 10%
            lat_margin = (north - south) * 0.1
            lon_margin = (east - west) * 0.1
            
            # Crear bbox con margen
            bbox = (
                south - lat_margin,
                north + lat_margin,
                west - lon_margin,
                east + lon_margin
            )
            
            # Cargar el grafo para el área calculada
            self.graph = ox.graph_from_bbox(
                bbox[1], bbox[0], bbox[3], bbox[2],
                network_type='drive',
                simplify=True
            )
            
            self.graph = ox.project_graph(self.graph)
            return True
        except Exception as e:
            print(f"Error al cargar datos OSM: {str(e)}")
            return False
    
    def obtener_nodo_cercano(self, lat: float, lon: float) -> int:
        """
        Obtiene el nodo más cercano a las coordenadas dadas
        """
        if self.graph is None:
            raise ValueError("El grafo no ha sido cargado")
            
        return ox.nearest_nodes(self.graph, lon, lat) 