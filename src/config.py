from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configuración de la API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Optimizador de Rutas OSM"
    
    # Configuración de OSM
    DEFAULT_CITY: str = "Madrid"
    BBOX_DEFAULT: tuple = (40.4367, 40.4167, -3.6833, -3.7033)  # Madrid centro

    #destination
    COORDINATES_DESTINATION: tuple = (40.421247, -3.684443)
    # Configuración del optimizador
    MAX_VEHICLES: int = 1
    MAX_TIME_WINDOW: int = 3600  # 1 hora en segundos
    
    class Config:
        case_sensitive = True

settings = Settings() 