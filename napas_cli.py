#!/usr/bin/env python3
"""
Interfaz de línea de comandos para el sistema de posicionamiento de napas.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Agregar el directorio src al path para importar los módulos
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.gestor import GestorPosicionamientoNapas


def crear_punto(args):
    """Crea un nuevo punto de medición."""
    gestor = GestorPosicionamientoNapas(args.archivo)
    
    try:
        punto = gestor.crear_punto_medicion(
            id_punto=args.id,
            nombre=args.nombre,
            latitud=args.latitud,
            longitud=args.longitud,
            descripcion=args.descripcion
        )
        gestor.guardar_datos()
        
        print(f"✓ Punto creado exitosamente:")
        print(f"  ID: {punto.id}")
        print(f"  Nombre: {punto.nombre}")
        print(f"  Coordenada: {punto.coordenada.latitud}, {punto.coordenada.longitud}")
        if punto.descripcion:
            print(f"  Descripción: {punto.descripcion}")
        
    except ValueError as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


def agregar_medicion(args):
    """Agrega una nueva medición a un punto."""
    gestor = GestorPosicionamientoNapas(args.archivo)
    
    try:
        fecha = None
        if args.fecha:
            fecha = datetime.strptime(args.fecha, "%Y-%m-%d %H:%M:%S")
        
        medicion = gestor.agregar_medicion(
            id_punto=args.punto,
            profundidad_napa=args.profundidad,
            fecha_medicion=fecha,
            observaciones=args.observaciones,
            elevacion_superficie=args.elevacion
        )
        gestor.guardar_datos()
        
        print(f"✓ Medición agregada exitosamente:")
        print(f"  ID: {medicion.id}")
        print(f"  Punto: {args.punto}")
        print(f"  Profundidad: {medicion.profundidad_napa} m")
        print(f"  Fecha: {medicion.fecha_medicion}")
        if medicion.observaciones:
            print(f"  Observaciones: {medicion.observaciones}")
        if medicion.nivel_absoluto_napa is not None:
            print(f"  Nivel absoluto: {medicion.nivel_absoluto_napa} m.s.n.m.")
        
    except ValueError as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


def listar_puntos(args):
    """Lista todos los puntos de medición."""
    gestor = GestorPosicionamientoNapas(args.archivo)
    puntos = gestor.listar_puntos()
    
    if not puntos:
        print("No hay puntos de medición registrados.")
        return
    
    print(f"Puntos de medición ({len(puntos)}):")
    print("-" * 80)
    
    for punto in puntos:
        print(f"ID: {punto.id}")
        print(f"Nombre: {punto.nombre}")
        print(f"Coordenada: {punto.coordenada.latitud:.6f}, {punto.coordenada.longitud:.6f}")
        print(f"Mediciones: {len(punto.mediciones)}")
        
        ultima = punto.obtener_ultima_medicion()
        if ultima:
            print(f"Última medición: {ultima.fecha_medicion} ({ultima.profundidad_napa} m)")
        
        print(f"Estado: {'Activo' if punto.activo else 'Inactivo'}")
        print("-" * 80)


def buscar_cercanos(args):
    """Busca puntos cercanos a una coordenada."""
    gestor = GestorPosicionamientoNapas(args.archivo)
    puntos_cercanos = gestor.buscar_puntos_cercanos(
        latitud=args.latitud,
        longitud=args.longitud,
        radio_metros=args.radio
    )
    
    if not puntos_cercanos:
        print(f"No se encontraron puntos en un radio de {args.radio} metros.")
        return
    
    print(f"Puntos cercanos (radio: {args.radio} m):")
    print("-" * 60)
    
    for punto, distancia in puntos_cercanos:
        print(f"ID: {punto.id}")
        print(f"Nombre: {punto.nombre}")
        print(f"Distancia: {distancia:.1f} m")
        print(f"Coordenada: {punto.coordenada.latitud:.6f}, {punto.coordenada.longitud:.6f}")
        print("-" * 60)


def generar_reporte(args):
    """Genera un reporte de un punto específico."""
    gestor = GestorPosicionamientoNapas(args.archivo)
    
    try:
        reporte = gestor.generar_reporte_punto(args.punto)
        
        print(f"REPORTE DEL PUNTO: {reporte['punto']['id']}")
        print("=" * 50)
        print(f"Nombre: {reporte['punto']['nombre']}")
        print(f"Coordenada: {reporte['punto']['coordenada']['latitud']:.6f}, {reporte['punto']['coordenada']['longitud']:.6f}")
        if reporte['punto']['descripcion']:
            print(f"Descripción: {reporte['punto']['descripcion']}")
        print(f"Fecha instalación: {reporte['punto']['fecha_instalacion']}")
        print(f"Estado: {'Activo' if reporte['punto']['activo'] else 'Inactivo'}")
        
        print("\nESTADÍSTICAS:")
        print("-" * 30)
        stats = reporte['estadisticas']
        print(f"Total de mediciones: {stats['total_mediciones']}")
        
        if stats['total_mediciones'] > 0:
            print(f"Profundidad promedio: {stats['profundidad_promedio']:.2f} m")
            print(f"Profundidad mínima: {stats['profundidad_min']:.2f} m")
            print(f"Profundidad máxima: {stats['profundidad_max']:.2f} m")
            print(f"Última medición: {stats['ultima_medicion']}")
        
    except ValueError as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


def main():
    """Función principal del CLI."""
    parser = argparse.ArgumentParser(
        description="Sistema de Posicionamiento de Medición de Napas",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--archivo", "-f",
        default="datos_napas.json",
        help="Archivo de datos JSON (por defecto: datos_napas.json)"
    )
    
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponibles")
    
    # Comando: crear punto
    parser_crear = subparsers.add_parser("crear-punto", help="Crear un nuevo punto de medición")
    parser_crear.add_argument("id", help="ID único del punto")
    parser_crear.add_argument("nombre", help="Nombre del punto")
    parser_crear.add_argument("latitud", type=float, help="Latitud en grados decimales")
    parser_crear.add_argument("longitud", type=float, help="Longitud en grados decimales")
    parser_crear.add_argument("--descripcion", "-d", help="Descripción del punto")
    parser_crear.set_defaults(func=crear_punto)
    
    # Comando: agregar medición
    parser_medicion = subparsers.add_parser("agregar-medicion", help="Agregar una medición a un punto")
    parser_medicion.add_argument("punto", help="ID del punto de medición")
    parser_medicion.add_argument("profundidad", type=float, help="Profundidad de la napa en metros")
    parser_medicion.add_argument("--fecha", help="Fecha y hora (YYYY-MM-DD HH:MM:SS)")
    parser_medicion.add_argument("--observaciones", "-o", help="Observaciones de la medición")
    parser_medicion.add_argument("--elevacion", "-e", type=float, help="Elevación superficie sobre n.m.m.")
    parser_medicion.set_defaults(func=agregar_medicion)
    
    # Comando: listar puntos
    parser_listar = subparsers.add_parser("listar", help="Listar todos los puntos de medición")
    parser_listar.set_defaults(func=listar_puntos)
    
    # Comando: buscar cercanos
    parser_buscar = subparsers.add_parser("buscar", help="Buscar puntos cercanos a una coordenada")
    parser_buscar.add_argument("latitud", type=float, help="Latitud de referencia")
    parser_buscar.add_argument("longitud", type=float, help="Longitud de referencia")
    parser_buscar.add_argument("--radio", "-r", type=float, default=1000, help="Radio de búsqueda en metros")
    parser_buscar.set_defaults(func=buscar_cercanos)
    
    # Comando: generar reporte
    parser_reporte = subparsers.add_parser("reporte", help="Generar reporte de un punto")
    parser_reporte.add_argument("punto", help="ID del punto")
    parser_reporte.set_defaults(func=generar_reporte)
    
    args = parser.parse_args()
    
    if not args.comando:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()