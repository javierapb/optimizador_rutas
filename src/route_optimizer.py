from typing import List, Dict
from datetime import datetime
import networkx as nx
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import osmnx as ox

class RouteOptimizer:
    def __init__(self, graph):
        self.graph = graph
        self.VELOCIDAD_PROMEDIO = 30  # km/h para estimaciones
        
    def crear_matriz_distancias(self, puntos: List[Dict]) -> List[List[int]]:
        """
        Crea una matriz de distancias optimizada entre puntos
        """
        num_puntos = len(puntos)
        matriz = [[0] * num_puntos for _ in range(num_puntos)]
        
        # Cache para almacenar rutas ya calculadas
        rutas_cache = {}
        
        for i in range(num_puntos):
            for j in range(i + 1, num_puntos):  # Optimización: solo calcular mitad superior
                try:
                    key = (puntos[i]["node_id"], puntos[j]["node_id"])
                    if key in rutas_cache:
                        distancia = rutas_cache[key]
                    else:
                        ruta = nx.astar_path(  # Cambio a A* para mejor rendimiento
                            self.graph,
                            puntos[i]["node_id"],
                            puntos[j]["node_id"],
                            weight="length"
                        )
                        distancia = int(sum(
                            self.graph[ruta[k]][ruta[k+1]][0]["length"]
                            for k in range(len(ruta)-1)
                        ))
                        rutas_cache[key] = distancia
                    
                    matriz[i][j] = distancia
                    matriz[j][i] = distancia  # Matriz simétrica
                except nx.NetworkXNoPath:
                    matriz[i][j] = matriz[j][i] = 999999
                        
        return matriz

    def optimizar_ruta(self, puntos: List[Dict]) -> Dict:
        """
        Optimiza la ruta con estrategias mejoradas
        """
        matriz_distancias = self.crear_matriz_distancias(puntos)
        manager = pywrapcp.RoutingIndexManager(len(puntos), 1, 0)
        routing = pywrapcp.RoutingModel(manager)

        def distancia_callback(desde_index, hasta_index):
            desde_node = manager.IndexToNode(desde_index)
            hasta_node = manager.IndexToNode(hasta_index)
            return matriz_distancias[desde_node][hasta_node]

        transit_callback_index = routing.RegisterTransitCallback(distancia_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Configuración optimizada de parámetros
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        
        # Estrategia de solución inicial más rápida
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.SAVINGS
        )
        
        # Límite de tiempo para la búsqueda (5 segundos)
        search_parameters.time_limit.seconds = 5
        
        # Optimización local agresiva
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GREEDY_DESCENT
        )

        # Resolver con timeout
        solution = routing.SolveWithParameters(search_parameters)
        
        if not solution:
            raise ValueError("No se encontró una solución válida en el tiempo límite")

        # Construir resultado optimizado
        ruta = []
        distancia_total = 0
        index = routing.Start(0)
        
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            ruta.append(node_index)
            prev_index = index
            index = solution.Value(routing.NextVar(index))
            distancia_total += matriz_distancias[manager.IndexToNode(prev_index)][manager.IndexToNode(index)]

        # Calcular tiempo estimado usando velocidad promedio
        tiempo_estimado = (distancia_total / 1000.0) / self.VELOCIDAD_PROMEDIO * 60  # minutos

        return {
            "orden": ruta,
            "distancia_total": distancia_total,
            "tiempo_estimado": tiempo_estimado,
            "ruta_coordenadas": self._obtener_coordenadas_ruta(ruta)
        }

    def _obtener_coordenadas_ruta(self, indices: List[int]) -> List[Dict[str, float]]:
        """
        Obtiene coordenadas de manera optimizada
        """
        # Cache del grafo no proyectado
        if not hasattr(self, '_graph_unprojected'):
            self._graph_unprojected = ox.project_graph(self.graph, to_crs='EPSG:4326')
        
        nodes = list(self.graph.nodes())
        return [{
            "latitude": float(self._graph_unprojected.nodes[nodes[idx]]['y']),
            "longitude": float(self._graph_unprojected.nodes[nodes[idx]]['x'])
        } for idx in indices] 