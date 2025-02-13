from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configuración de la API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Optimizador de Rutas OSM"
    
    # Configuración del optimizador
    MAX_VEHICLES: int = 1
    MAX_TIME_WINDOW: int = 3600  # 1 hora en segundos
    
    class Config:
        case_sensitive = True

settings = Settings() 