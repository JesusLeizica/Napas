#!/usr/bin/env python3
"""
Tests básicos para el sistema de napas.
"""

import sys
import tempfile
import os
from datetime import datetime
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models import Coordenada, MedicionNapa, PuntoMedicion
from src.gestor import GestorPosicionamientoNapas


def test_coordenada():
    """Test de la clase Coordenada."""
    print("Probando clase Coordenada...")
    
    # Coordenada válida
    coord = Coordenada(-34.6037, -58.3816)
    assert coord.latitud == -34.6037
    assert coord.longitud == -58.3816
    
    # Test de distancia
    coord2 = Coordenada(-34.5890, -58.3974)
    distancia = coord.distancia_a(coord2)
    assert 2000 < distancia < 3000  # Aproximadamente 2.2 km
    
    # Coordenadas inválidas
    try:
        Coordenada(91, 0)  # Latitud inválida
        assert False, "Debería fallar con latitud inválida"
    except ValueError:
        pass
    
    try:
        Coordenada(0, 181)  # Longitud inválida
        assert False, "Debería fallar con longitud inválida"
    except ValueError:
        pass
    
    print("✓ Coordenada: OK")


def test_medicion_napa():
    """Test de la clase MedicionNapa."""
    print("Probando clase MedicionNapa...")
    
    coord = Coordenada(-34.6037, -58.3816)
    fecha = datetime.now()
    
    # Medición válida
    medicion = MedicionNapa(
        id="TEST_001",
        coordenada=coord,
        profundidad_napa=2.5,
        fecha_medicion=fecha,
        elevacion_superficie=25.0
    )
    
    assert medicion.profundidad_napa == 2.5
    assert medicion.nivel_absoluto_napa == 22.5
    
    # Profundidad negativa
    try:
        MedicionNapa(
            id="TEST_002",
            coordenada=coord,
            profundidad_napa=-1.0,
            fecha_medicion=fecha
        )
        assert False, "Debería fallar con profundidad negativa"
    except ValueError:
        pass
    
    print("✓ MedicionNapa: OK")


def test_punto_medicion():
    """Test de la clase PuntoMedicion."""
    print("Probando clase PuntoMedicion...")
    
    coord = Coordenada(-34.6037, -58.3816)
    punto = PuntoMedicion(
        id="PM_TEST",
        nombre="Punto de Prueba",
        coordenada=coord
    )
    
    assert len(punto.mediciones) == 0
    assert punto.obtener_ultima_medicion() is None
    
    # Agregar medición
    medicion = MedicionNapa(
        id="MED_001",
        coordenada=coord,
        profundidad_napa=2.5,
        fecha_medicion=datetime.now()
    )
    
    punto.agregar_medicion(medicion)
    assert len(punto.mediciones) == 1
    assert punto.obtener_ultima_medicion() == medicion
    
    # Medición muy lejos del punto
    coord_lejana = Coordenada(-35.0, -59.0)
    medicion_lejana = MedicionNapa(
        id="MED_002",
        coordenada=coord_lejana,
        profundidad_napa=3.0,
        fecha_medicion=datetime.now()
    )
    
    try:
        punto.agregar_medicion(medicion_lejana)
        assert False, "Debería fallar con medición muy lejana"
    except ValueError:
        pass
    
    print("✓ PuntoMedicion: OK")


def test_gestor():
    """Test del GestorPosicionamientoNapas."""
    print("Probando GestorPosicionamientoNapas...")
    
    # Usar archivo temporal
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        archivo_temp = f.name
    
    try:
        gestor = GestorPosicionamientoNapas(archivo_temp)
        
        # Crear punto
        punto = gestor.crear_punto_medicion(
            id_punto="TEST_P1",
            nombre="Punto Test",
            latitud=-34.6037,
            longitud=-58.3816
        )
        
        assert punto.id == "TEST_P1"
        assert len(gestor.puntos_medicion) == 1
        
        # Punto duplicado
        try:
            gestor.crear_punto_medicion(
                id_punto="TEST_P1",
                nombre="Otro Punto",
                latitud=-34.0,
                longitud=-58.0
            )
            assert False, "Debería fallar con ID duplicado"
        except ValueError:
            pass
        
        # Agregar medición
        medicion = gestor.agregar_medicion(
            id_punto="TEST_P1",
            profundidad_napa=2.5,
            elevacion_superficie=25.0
        )
        
        assert medicion.profundidad_napa == 2.5
        assert len(punto.mediciones) == 1
        
        # Medición a punto inexistente
        try:
            gestor.agregar_medicion(
                id_punto="NO_EXISTE",
                profundidad_napa=1.0
            )
            assert False, "Debería fallar con punto inexistente"
        except ValueError:
            pass
        
        # Buscar puntos cercanos
        cercanos = gestor.buscar_puntos_cercanos(-34.6037, -58.3816, 100)
        assert len(cercanos) == 1
        assert cercanos[0][1] == 0.0  # Distancia 0
        
        # Guardar y cargar datos
        gestor.guardar_datos()
        
        gestor2 = GestorPosicionamientoNapas(archivo_temp)
        assert len(gestor2.puntos_medicion) == 1
        punto_cargado = gestor2.obtener_punto("TEST_P1")
        assert punto_cargado is not None
        assert punto_cargado.nombre == "Punto Test"
        assert len(punto_cargado.mediciones) == 1
        
        # Generar reporte
        reporte = gestor.generar_reporte_punto("TEST_P1")
        assert reporte['punto']['nombre'] == "Punto Test"
        assert reporte['estadisticas']['total_mediciones'] == 1
        assert reporte['estadisticas']['profundidad_promedio'] == 2.5
        
        print("✓ GestorPosicionamientoNapas: OK")
    
    finally:
        # Limpiar archivo temporal
        if os.path.exists(archivo_temp):
            os.unlink(archivo_temp)


def ejecutar_tests():
    """Ejecuta todos los tests."""
    print("=== EJECUTANDO TESTS DEL SISTEMA DE NAPAS ===\n")
    
    try:
        test_coordenada()
        test_medicion_napa()
        test_punto_medicion()
        test_gestor()
        
        print("\n✓ TODOS LOS TESTS PASARON EXITOSAMENTE ✓")
        return True
    
    except Exception as e:
        print(f"\n✗ ERROR EN LOS TESTS: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    exito = ejecutar_tests()
    sys.exit(0 if exito else 1)