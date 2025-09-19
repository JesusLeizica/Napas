# Napas - Sistema de Posicionamiento de Medición de Napa

Sistema integral para la gestión y posicionamiento de mediciones de niveles freáticos (napas de agua subterránea).

## Características

- **Gestión de Puntos de Medición**: Crear y administrar puntos de medición georreferenciados
- **Registro de Mediciones**: Almacenar mediciones históricas con metadatos completos
- **Cálculos Geoespaciales**: Calcular distancias entre puntos usando la fórmula de Haversine
- **Búsqueda Espacial**: Encontrar puntos de medición cercanos a coordenadas específicas
- **Persistencia de Datos**: Almacenamiento en formato JSON para portabilidad
- **Interfaz CLI**: Línea de comandos completa para todas las operaciones
- **Validación de Datos**: Validación automática de coordenadas y mediciones

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/JesusLeizica/Napas.git
cd Napas

# El sistema no requiere dependencias externas, usa solo la biblioteca estándar de Python
```

## Uso Básico

### Interfaz de Línea de Comandos

```bash
# Crear un punto de medición
python napas_cli.py crear-punto PM001 "Punto Centro" -34.6037 -58.3816 --descripcion "Centro de Buenos Aires"

# Agregar una medición
python napas_cli.py agregar-medicion PM001 2.5 --observaciones "Medición inicial" --elevacion 25.0

# Listar todos los puntos
python napas_cli.py listar

# Buscar puntos cercanos
python napas_cli.py buscar -34.6037 -58.3816 --radio 500

# Generar reporte de un punto
python napas_cli.py reporte PM001
```

### Uso Programático

```python
from src.gestor import GestorPosicionamientoNapas

# Crear gestor
gestor = GestorPosicionamientoNapas("mi_proyecto.json")

# Crear punto de medición
punto = gestor.crear_punto_medicion(
    id_punto="PM001",
    nombre="Punto Principal",
    latitud=-34.6037,
    longitud=-58.3816,
    descripcion="Descripción del punto"
)

# Agregar medición
medicion = gestor.agregar_medicion(
    id_punto="PM001",
    profundidad_napa=2.5,
    elevacion_superficie=25.0,
    observaciones="Primera medición"
)

# Guardar datos
gestor.guardar_datos()
```

## Estructura del Proyecto

```
Napas/
├── src/
│   ├── __init__.py          # Inicialización del paquete
│   ├── models.py            # Modelos de datos (Coordenada, MedicionNapa, PuntoMedicion)
│   └── gestor.py            # Gestor principal del sistema
├── napas_cli.py             # Interfaz de línea de comandos
├── generar_ejemplo.py       # Script para generar datos de ejemplo
└── README.md                # Documentación
```

## Modelos de Datos

### Coordenada
Representa una posición geográfica con validación automática:
- `latitud`: float (-90 a 90 grados)
- `longitud`: float (-180 a 180 grados)
- Método `distancia_a()` para cálculo de distancias

### MedicionNapa
Almacena una medición individual:
- `id`: Identificador único
- `coordenada`: Posición GPS
- `profundidad_napa`: Profundidad en metros
- `fecha_medicion`: Timestamp de la medición
- `observaciones`: Notas opcionales
- `elevacion_superficie`: Altura sobre nivel del mar

### PuntoMedicion
Representa un sitio de medición establecido:
- `id`: Identificador único
- `nombre`: Nombre descriptivo
- `coordenada`: Posición fija
- `descripcion`: Descripción del sitio
- `fecha_instalacion`: Cuándo se estableció
- `activo`: Estado del punto
- `mediciones`: Historial de mediciones

## Ejemplos de Uso

### Generar Datos de Ejemplo

```bash
python generar_ejemplo.py
```

Este script crea un archivo `datos_ejemplo.json` con:
- 3 puntos de medición en Buenos Aires
- 30 días de mediciones históricas
- Diferentes niveles de napa simulados

### Casos de Uso Comunes

1. **Monitoreo de Pozo**:
   ```bash
   python napas_cli.py crear-punto POZO_01 "Pozo Principal" -34.123 -58.456
   python napas_cli.py agregar-medicion POZO_01 3.2 --elevacion 28.5
   ```

2. **Red de Monitoreo**:
   ```bash
   # Crear múltiples puntos en área de estudio
   python napas_cli.py crear-punto P1 "Norte" -34.123 -58.456
   python napas_cli.py crear-punto P2 "Centro" -34.124 -58.457  
   python napas_cli.py crear-punto P3 "Sur" -34.125 -58.458
   
   # Buscar puntos cercanos a coordenada específica
   python napas_cli.py buscar -34.124 -58.457 --radio 1000
   ```

3. **Análisis Temporal**:
   ```bash
   # Agregar mediciones en diferentes fechas
   python napas_cli.py agregar-medicion P1 2.8 --fecha "2024-01-15 10:00:00"
   python napas_cli.py agregar-medicion P1 3.1 --fecha "2024-02-15 10:00:00"
   python napas_cli.py reporte P1
   ```

## Validaciones y Controles

- **Coordenadas**: Validación automática de rangos válidos
- **Proximidad**: Las mediciones deben estar cerca del punto asignado (±10m)
- **Profundidad**: No permite valores negativos
- **Elevación**: Controles de rangos razonables
- **IDs únicos**: Previene duplicación de identificadores

## Formato de Datos

Los datos se almacenan en formato JSON estructurado:

```json
{
  "PM001": {
    "id": "PM001",
    "nombre": "Punto Principal",
    "latitud": -34.6037,
    "longitud": -58.3816,
    "descripcion": "Centro de Buenos Aires",
    "fecha_instalacion": "2024-01-15T10:00:00",
    "activo": true,
    "mediciones": [
      {
        "id": "PM001_20240115_100000",
        "profundidad_napa": 2.5,
        "fecha_medicion": "2024-01-15T10:00:00",
        "observaciones": "Medición inicial",
        "elevacion_superficie": 25.0
      }
    ]
  }
}
```

## Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles.