#!/usr/bin/env python3
"""
Script para generar datos de ejemplo del sistema de napas.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.gestor import GestorPosicionamientoNapas


def generar_datos_ejemplo():
    """Genera datos de ejemplo para demostrar el sistema."""
    gestor = GestorPosicionamientoNapas("datos_ejemplo.json")
    
    # Crear algunos puntos de medición en diferentes ubicaciones
    puntos_ejemplo = [
        {
            "id_punto": "PM001",
            "nombre": "Punto Medición Centro",
            "latitud": -34.6037,
            "longitud": -58.3816,
            "descripcion": "Punto ubicado en el centro de Buenos Aires"
        },
        {
            "id_punto": "PM002", 
            "nombre": "Punto Medición Norte",
            "latitud": -34.5890,
            "longitud": -58.3974,
            "descripcion": "Punto ubicado en la zona norte"
        },
        {
            "id_punto": "PM003",
            "nombre": "Punto Medición Sur",
            "latitud": -34.6297,
            "longitud": -58.3685,
            "descripcion": "Punto ubicado en la zona sur"
        }
    ]
    
    # Crear los puntos
    for punto_data in puntos_ejemplo:
        punto = gestor.crear_punto_medicion(**punto_data)
        print(f"✓ Creado punto: {punto.nombre}")
    
    # Agregar mediciones históricas (últimos 30 días)
    fecha_base = datetime.now() - timedelta(days=30)
    
    for i, punto_id in enumerate(["PM001", "PM002", "PM003"]):
        # Simular mediciones cada 3 días
        for dia in range(0, 30, 3):
            fecha_medicion = fecha_base + timedelta(days=dia)
            
            # Simular variaciones en la profundidad de la napa
            profundidad_base = 2.5 + i * 0.5  # Diferentes niveles base
            variacion = 0.3 * (dia / 30)  # Variación temporal
            profundidad = profundidad_base + variacion
            
            elevacion = 25.0 + i * 5.0  # Diferentes elevaciones
            
            observaciones = None
            if dia % 9 == 0:  # Cada 3 mediciones, agregar observación
                observaciones = f"Medición de control día {dia}"
            
            medicion = gestor.agregar_medicion(
                id_punto=punto_id,
                profundidad_napa=profundidad,
                fecha_medicion=fecha_medicion,
                observaciones=observaciones,
                elevacion_superficie=elevacion
            )
            print(f"  + Medición {punto_id}: {profundidad:.2f}m el {fecha_medicion.date()}")
    
    # Guardar todos los datos
    gestor.guardar_datos()
    print(f"\n✓ Datos guardados en: datos_ejemplo.json")
    
    # Mostrar estadísticas
    print("\nRESUMEN DE DATOS GENERADOS:")
    print("=" * 40)
    
    for punto in gestor.listar_puntos():
        reporte = gestor.generar_reporte_punto(punto.id)
        stats = reporte['estadisticas']
        print(f"\n{punto.nombre} ({punto.id}):")
        print(f"  - Mediciones: {stats['total_mediciones']}")
        print(f"  - Profundidad promedio: {stats['profundidad_promedio']:.2f} m")
        print(f"  - Rango: {stats['profundidad_min']:.2f} - {stats['profundidad_max']:.2f} m")


if __name__ == "__main__":
    print("Generando datos de ejemplo para el sistema de napas...")
    generar_datos_ejemplo()