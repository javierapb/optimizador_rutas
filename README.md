# Optimizador de Rutas con OpenStreetMap

Sistema de optimización de rutas que utiliza OpenStreetMap (OSM) y Google OR-Tools para calcular rutas óptimas con múltiples paradas y restricciones temporales.

## Proceso de Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git

### Pasos de Instalación

1. **Clonar el Repositorio**
```bash
git clone https://github.com/javierapb/optimizador_rutas.git
cd optimizador-rutas-osm
```
2. **Crear y activar entorno virtual**

```bash

#Crear entorno virtual
python -m venv venv

#Activar entorno virtual
#En Mac/Linux:
source venv/bin/activate
#En Windows:
venv\Scripts\activate
```
3. **Instalar Dependencias**
```bash

pip install -r requirements.txt
```

4. **Iniciar el Servidor**
```bash
uvicorn src.main:app --reload
```
El servidor estará disponible en http://localhost:8000

## Ejemplo de Uso (CURL)

```
curl --location 'http://localhost:8000/optimizar-ruta' \
--header 'Content-Type: application/json' \
--data '{
    "origin": {
        "latitude": -33.440364,
        "longitude": -70.650927
    },
    "destination": {
        "latitude": -33.422890,
        "longitude": -70.607166
    },
    "puntos": [
        {
            "latitude": -33.437277,
            "longitude": -70.634504,
            "hora_recogida": "2024-03-20T09:15:00",
            "ventana_tiempo": {
                "hora_inicio": "2024-03-20T09:00:00",
                "hora_termino": "2024-03-20T09:30:00"
            }
        },
        {
            "latitude": -33.432562,
            "longitude": -70.623518,
            "hora_recogida": "2024-03-20T09:30:00",
            "ventana_tiempo": {
                "hora_inicio": "2024-03-20T09:15:00",
                "hora_termino": "2024-03-20T09:45:00"
            }
        }
    ]
}'
```
Proyecto
El ejemplo muestra una ruta en Santiago de Chile desde Metro Universidad de Chile hasta Costanera Center, pasando por Parque Forestal y Plaza Italia.



El ejemplo muestra una ruta en Santiago de Chile desde Metro Universidad de Chile hasta Costanera Center, pasando por Parque Forestal y Plaza Italia.

## Algoritmo de Optimización

### Algoritmo Principal
El sistema utiliza una combinación de dos algoritmos principales:

1. **Vehicle Routing Problem (VRP)**
   - Implementado con Google OR-Tools
   - Optimiza la secuencia de visitas
   - Considera restricciones temporales
   - Minimiza la distancia total

2. **A* Pathfinding**
   - Reemplaza al algoritmo Dijkstra original
   - Mejor rendimiento en redes de calles
   - Optimizado para distancias urbanas

### Optimizaciones Implementadas

1. **Optimización de Matriz de Distancias**
   - Cache de rutas calculadas
   - Aprovechamiento de simetría en la matriz
   - Solo calcula la mitad superior de la matriz
   - Reduce significativamente los cálculos

2. **Mejoras en OR-Tools**
   - Estrategia SAVINGS para solución inicial rápida
   - GREEDY_DESCENT para optimización local
   - Límite de tiempo de 5 segundos
   - Mayor velocidad de respuesta

3. **Optimizaciones Generales**
   - Cache del grafo no proyectado
   - Estimación precisa de tiempos
   - Uso eficiente de memoria
   - Reducción de cálculos redundantes

### Resultados de la Optimización
- Respuestas más rápidas
- Mejor calidad de rutas
- Mayor estabilidad
- Soporte para más puntos intermedios

## Estructura del Proyecto

src/
├── main.py # Punto de entrada de la API
├── route_optimizer.py # Algoritmo de optimización
├── schemas.py # Esquemas de datos
└── requirements.txt # Dependencias
