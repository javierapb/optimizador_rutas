import osmnx as ox
import networkx as nx
from typing import Tuple

class OSMLoader:
    def __init__(self):
        self.graph = None
        
    def cargar_area(self, bbox: Tuple[float, float, float, float]):
        """
        Carga los datos de OSM para un área específica definida por su bounding box
        """
        try:
            # Método alternativo usando place name
            self.graph = ox.graph_from_place(
                'Madrid, Spain',
                network_type='drive',
                simplify=True
            )
            # O usar un área más pequeña con coordenadas centrales y distancia
            # center_lat = (bbox[0] + bbox[1]) / 2
            # center_lon = (bbox[2] + bbox[3]) / 2
            # self.graph = ox.graph_from_point(
            #     (center_lat, center_lon),
            #     dist=1000,  # metros
            #     network_type='drive',
            #     simplify=True
            # )
            
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