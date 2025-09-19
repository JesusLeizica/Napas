"""
Modelos de datos para el sistema de medición de napas.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import math


@dataclass
class Coordenada:
    """Representa una coordenada geográfica."""
    latitud: float
    longitud: float
    
    def __post_init__(self):
        """Valida las coordenadas."""
        if not (-90 <= self.latitud <= 90):
            raise ValueError("La latitud debe estar entre -90 y 90 grados")
        if not (-180 <= self.longitud <= 180):
            raise ValueError("La longitud debe estar entre -180 y 180 grados")
    
    def distancia_a(self, otra_coordenada: 'Coordenada') -> float:
        """
        Calcula la distancia en metros entre dos coordenadas usando la fórmula de Haversine.
        """
        R = 6371000  # Radio de la Tierra en metros
        
        lat1_rad = math.radians(self.latitud)
        lat2_rad = math.radians(otra_coordenada.latitud)
        delta_lat = math.radians(otra_coordenada.latitud - self.latitud)
        delta_lon = math.radians(otra_coordenada.longitud - self.longitud)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c


@dataclass
class MedicionNapa:
    """Representa una medición de nivel freático."""
    id: str
    coordenada: Coordenada
    profundidad_napa: float  # Profundidad en metros
    fecha_medicion: datetime
    observaciones: Optional[str] = None
    elevacion_superficie: Optional[float] = None  # Elevación sobre el nivel del mar
    
    def __post_init__(self):
        """Valida los datos de la medición."""
        if self.profundidad_napa < 0:
            raise ValueError("La profundidad de la napa no puede ser negativa")
        if self.elevacion_superficie is not None and self.elevacion_superficie < -500:
            raise ValueError("La elevación parece incorrecta")
    
    @property
    def nivel_absoluto_napa(self) -> Optional[float]:
        """Calcula el nivel absoluto de la napa sobre el nivel del mar."""
        if self.elevacion_superficie is not None:
            return self.elevacion_superficie - self.profundidad_napa
        return None


@dataclass
class PuntoMedicion:
    """Representa un punto de medición establecido."""
    id: str
    nombre: str
    coordenada: Coordenada
    descripcion: Optional[str] = None
    fecha_instalacion: Optional[datetime] = None
    activo: bool = True
    mediciones: List[MedicionNapa] = None
    
    def __post_init__(self):
        """Inicializa la lista de mediciones si no se proporciona."""
        if self.mediciones is None:
            self.mediciones = []
    
    def agregar_medicion(self, medicion: MedicionNapa) -> None:
        """Agrega una nueva medición al punto."""
        if medicion.coordenada.distancia_a(self.coordenada) > 10:  # 10 metros de tolerancia
            raise ValueError("La medición está muy lejos del punto de medición establecido")
        self.mediciones.append(medicion)
    
    def obtener_ultima_medicion(self) -> Optional[MedicionNapa]:
        """Obtiene la medición más reciente."""
        if not self.mediciones:
            return None
        return max(self.mediciones, key=lambda m: m.fecha_medicion)
    
    def obtener_mediciones_periodo(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[MedicionNapa]:
        """Obtiene mediciones en un período específico."""
        return [m for m in self.mediciones 
                if fecha_inicio <= m.fecha_medicion <= fecha_fin]