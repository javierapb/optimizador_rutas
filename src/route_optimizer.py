from typing import List, Dict
from datetime import datetime
import networkx as nx
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import osmnx as ox

class RouteOptimizer:
    def __init__(self, graph):
        self.graph = graph
        
    def crear_matriz_distancias(self, puntos: List[Dict]) -> List[List[int]]:
        """
        Crea una matriz de distancias entre todos los puntos
        """
        num_puntos = len(puntos)
        matriz = [[0] * num_puntos for _ in range(num_puntos)]
        
        for i in range(num_puntos):
            for j in range(num_puntos):
                if i != j:
                    try:
                        ruta = nx.shortest_path(
                            self.graph,
                            puntos[i]["node_id"],
                            puntos[j]["node_id"],
                            weight="length"
                        )
                        matriz[i][j] = int(
                            sum(
                                self.graph[ruta[k]][ruta[k+1]][0]["length"]
                                for k in range(len(ruta)-1)
                            )
                        )
                    except nx.NetworkXNoPath:
                        matriz[i][j] = 999999  # valor grande para rutas imposibles
                        
        return matriz 

    def optimizar_ruta(self, puntos: List[Dict]) -> Dict:
        """
        Optimiza la ruta considerando las restricciones temporales
        """
        # Crear matriz de distancias
        matriz_distancias = self.crear_matriz_distancias(puntos)
        
        # Crear el modelo de routing
        manager = pywrapcp.RoutingIndexManager(len(puntos), 1, 0)
        routing = pywrapcp.RoutingModel(manager)

        def distancia_callback(desde_index, hasta_index):
            desde_node = manager.IndexToNode(desde_index)
            hasta_node = manager.IndexToNode(hasta_index)
            return matriz_distancias[desde_node][hasta_node]

        transit_callback_index = routing.RegisterTransitCallback(distancia_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Configurar parámetros de búsqueda
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )

        # Resolver el problema
        solution = routing.SolveWithParameters(search_parameters)
        
        if not solution:
            raise ValueError("No se encontró una solución válida")

        # Construir resultado
        ruta = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            ruta.append(node_index)
            index = solution.Value(routing.NextVar(index))

        return {
            "orden": ruta,
            "distancia_total": solution.ObjectiveValue(),
            "tiempo_estimado": solution.ObjectiveValue() / 30.0,  # Estimación simple
            "ruta_coordenadas": self._obtener_coordenadas_ruta(ruta)
        }

    def _obtener_coordenadas_ruta(self, indices: List[int]) -> List[Dict[str, float]]:
        """
        Convierte los índices de nodos en coordenadas geográficas (lat/lon)
        """
        coordenadas = []
        # Obtener el grafo no proyectado para las coordenadas geográficas
        graph_unprojected = ox.project_graph(self.graph, to_crs='EPSG:4326')
        
        for idx in indices:
            node = list(self.graph.nodes())[idx]
            # Usar el grafo no proyectado para obtener lat/lon
            coordenadas.append({
                "latitud": float(graph_unprojected.nodes[node]['y']),  # Convertir a float para asegurar serialización JSON
                "longitud": float(graph_unprojected.nodes[node]['x'])
            })
        return coordenadas 