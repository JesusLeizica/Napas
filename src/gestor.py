"""
Gestor del sistema de posicionamiento de mediciones de napa.
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from .models import Coordenada, MedicionNapa, PuntoMedicion


class GestorPosicionamientoNapas:
    """Gestor principal para el sistema de posicionamiento de mediciones de napa."""
    
    def __init__(self, archivo_datos: Optional[str] = None):
        """
        Inicializa el gestor.
        
        Args:
            archivo_datos: Ruta al archivo de datos JSON para persistencia
        """
        self.puntos_medicion: Dict[str, PuntoMedicion] = {}
        self.archivo_datos = archivo_datos or "datos_napas.json"
        self.cargar_datos()
    
    def crear_punto_medicion(self, id_punto: str, nombre: str, 
                            latitud: float, longitud: float,
                            descripcion: Optional[str] = None) -> PuntoMedicion:
        """
        Crea un nuevo punto de medición.
        
        Args:
            id_punto: Identificador único del punto
            nombre: Nombre descriptivo del punto
            latitud: Latitud en grados decimales
            longitud: Longitud en grados decimales
            descripcion: Descripción opcional del punto
            
        Returns:
            El punto de medición creado
            
        Raises:
            ValueError: Si el ID ya existe o las coordenadas son inválidas
        """
        if id_punto in self.puntos_medicion:
            raise ValueError(f"Ya existe un punto con ID '{id_punto}'")
        
        coordenada = Coordenada(latitud, longitud)
        punto = PuntoMedicion(
            id=id_punto,
            nombre=nombre,
            coordenada=coordenada,
            descripcion=descripcion,
            fecha_instalacion=datetime.now()
        )
        
        self.puntos_medicion[id_punto] = punto
        return punto
    
    def agregar_medicion(self, id_punto: str, profundidad_napa: float,
                        fecha_medicion: Optional[datetime] = None,
                        observaciones: Optional[str] = None,
                        elevacion_superficie: Optional[float] = None) -> MedicionNapa:
        """
        Agrega una nueva medición a un punto existente.
        
        Args:
            id_punto: ID del punto de medición
            profundidad_napa: Profundidad de la napa en metros
            fecha_medicion: Fecha de la medición (por defecto: ahora)
            observaciones: Observaciones opcionales
            elevacion_superficie: Elevación sobre el nivel del mar
            
        Returns:
            La medición creada
            
        Raises:
            ValueError: Si el punto no existe
        """
        if id_punto not in self.puntos_medicion:
            raise ValueError(f"No existe un punto con ID '{id_punto}'")
        
        punto = self.puntos_medicion[id_punto]
        
        if fecha_medicion is None:
            fecha_medicion = datetime.now()
        
        # Generar ID único para la medición
        id_medicion = f"{id_punto}_{fecha_medicion.strftime('%Y%m%d_%H%M%S')}"
        
        medicion = MedicionNapa(
            id=id_medicion,
            coordenada=punto.coordenada,
            profundidad_napa=profundidad_napa,
            fecha_medicion=fecha_medicion,
            observaciones=observaciones,
            elevacion_superficie=elevacion_superficie
        )
        
        punto.agregar_medicion(medicion)
        return medicion
    
    def obtener_punto(self, id_punto: str) -> Optional[PuntoMedicion]:
        """Obtiene un punto de medición por su ID."""
        return self.puntos_medicion.get(id_punto)
    
    def listar_puntos(self, solo_activos: bool = True) -> List[PuntoMedicion]:
        """
        Lista todos los puntos de medición.
        
        Args:
            solo_activos: Si True, solo devuelve puntos activos
            
        Returns:
            Lista de puntos de medición
        """
        puntos = list(self.puntos_medicion.values())
        if solo_activos:
            puntos = [p for p in puntos if p.activo]
        return puntos
    
    def buscar_puntos_cercanos(self, latitud: float, longitud: float, 
                              radio_metros: float = 1000) -> List[tuple]:
        """
        Busca puntos de medición cerca de una coordenada.
        
        Args:
            latitud: Latitud de referencia
            longitud: Longitud de referencia
            radio_metros: Radio de búsqueda en metros
            
        Returns:
            Lista de tuplas (punto, distancia_metros)
        """
        coordenada_ref = Coordenada(latitud, longitud)
        puntos_cercanos = []
        
        for punto in self.puntos_medicion.values():
            if not punto.activo:
                continue
            
            distancia = coordenada_ref.distancia_a(punto.coordenada)
            if distancia <= radio_metros:
                puntos_cercanos.append((punto, distancia))
        
        # Ordenar por distancia
        puntos_cercanos.sort(key=lambda x: x[1])
        return puntos_cercanos
    
    def generar_reporte_punto(self, id_punto: str) -> Dict:
        """
        Genera un reporte completo de un punto de medición.
        
        Args:
            id_punto: ID del punto
            
        Returns:
            Diccionario con información del punto y estadísticas
            
        Raises:
            ValueError: Si el punto no existe
        """
        if id_punto not in self.puntos_medicion:
            raise ValueError(f"No existe un punto con ID '{id_punto}'")
        
        punto = self.puntos_medicion[id_punto]
        mediciones = punto.mediciones
        
        reporte = {
            "punto": {
                "id": punto.id,
                "nombre": punto.nombre,
                "coordenada": {
                    "latitud": punto.coordenada.latitud,
                    "longitud": punto.coordenada.longitud
                },
                "descripcion": punto.descripcion,
                "fecha_instalacion": punto.fecha_instalacion.isoformat() if punto.fecha_instalacion else None,
                "activo": punto.activo
            },
            "estadisticas": {
                "total_mediciones": len(mediciones),
                "profundidad_promedio": None,
                "profundidad_min": None,
                "profundidad_max": None,
                "ultima_medicion": None
            }
        }
        
        if mediciones:
            profundidades = [m.profundidad_napa for m in mediciones]
            reporte["estadisticas"].update({
                "profundidad_promedio": sum(profundidades) / len(profundidades),
                "profundidad_min": min(profundidades),
                "profundidad_max": max(profundidades),
                "ultima_medicion": punto.obtener_ultima_medicion().fecha_medicion.isoformat()
            })
        
        return reporte
    
    def guardar_datos(self) -> None:
        """Guarda los datos en el archivo JSON."""
        datos = {}
        
        for id_punto, punto in self.puntos_medicion.items():
            mediciones_data = []
            for medicion in punto.mediciones:
                medicion_data = {
                    "id": medicion.id,
                    "profundidad_napa": medicion.profundidad_napa,
                    "fecha_medicion": medicion.fecha_medicion.isoformat(),
                    "observaciones": medicion.observaciones,
                    "elevacion_superficie": medicion.elevacion_superficie
                }
                mediciones_data.append(medicion_data)
            
            punto_data = {
                "id": punto.id,
                "nombre": punto.nombre,
                "latitud": punto.coordenada.latitud,
                "longitud": punto.coordenada.longitud,
                "descripcion": punto.descripcion,
                "fecha_instalacion": punto.fecha_instalacion.isoformat() if punto.fecha_instalacion else None,
                "activo": punto.activo,
                "mediciones": mediciones_data
            }
            datos[id_punto] = punto_data
        
        with open(self.archivo_datos, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
    
    def cargar_datos(self) -> None:
        """Carga los datos desde el archivo JSON si existe."""
        if not Path(self.archivo_datos).exists():
            return
        
        try:
            with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            for id_punto, punto_data in datos.items():
                coordenada = Coordenada(punto_data["latitud"], punto_data["longitud"])
                
                punto = PuntoMedicion(
                    id=punto_data["id"],
                    nombre=punto_data["nombre"],
                    coordenada=coordenada,
                    descripcion=punto_data.get("descripcion"),
                    fecha_instalacion=datetime.fromisoformat(punto_data["fecha_instalacion"]) if punto_data.get("fecha_instalacion") else None,
                    activo=punto_data.get("activo", True)
                )
                
                # Cargar mediciones
                for medicion_data in punto_data.get("mediciones", []):
                    medicion = MedicionNapa(
                        id=medicion_data["id"],
                        coordenada=coordenada,
                        profundidad_napa=medicion_data["profundidad_napa"],
                        fecha_medicion=datetime.fromisoformat(medicion_data["fecha_medicion"]),
                        observaciones=medicion_data.get("observaciones"),
                        elevacion_superficie=medicion_data.get("elevacion_superficie")
                    )
                    punto.mediciones.append(medicion)
                
                self.puntos_medicion[id_punto] = punto
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error cargando datos: {e}")
            self.puntos_medicion = {}