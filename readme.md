# Curso de Introducción a Señales Biomédicas

Repositorio de materiales prácticos para estudiar el procesamiento de señales biomédicas con Python. El contenido está organizado en módulos numerados y combina notebooks de Jupyter, scripts y datos de ejemplo.

## Contenido del curso

1. [Señales y sistemas](1_señales_sistemas/readme.md): señales senoidales, escalón y rampa; análisis de sistemas en los dominios \(s\) y \(z\).
2. [Filtros digitales](2_filtros_digitales/readme.md): análisis en frecuencia y diseño y aplicación de filtros FIR e IIR.
3. [Filtros adaptativos](3_filtros_adaptativos/readme.md): algoritmos LMS, filtro de Wiener y estimación mediante Kalman.
4. [Filtros wavelet](4_filtros_wavelets/readme.md): transformada wavelet discreta (DWT) y análisis de señales.
5. [Extracción de características](5_extracción_caracteristicas/readme.md): preparación de señales EMG y ECG, ventanas deslizantes y características.
6. [Reconocimiento de patrones](6_reconocimiento_patrones/readme.md): generación y segmentación de señales ECG, modelos LSTM y exportación para dispositivos.
7. [Edge Impulse](7_edge_impulse/readme.md): conversión de adquisiciones OpenSignals a archivos compatibles con flujos de Edge Impulse.

Cada módulo enlaza a su carpeta, donde se encuentran los notebooks, scripts y datos correspondientes.

## Requisitos y entorno

El proyecto requiere Python 3.12 o posterior y utiliza [uv](https://docs.astral.sh/uv/) para gestionar el entorno y las dependencias declaradas en `pyproject.toml`.

Desde la raíz del repositorio, sincroniza el entorno:

```sh
uv sync
```

Abre los archivos `.ipynb` con Jupyter en VS Code o con un entorno Jupyter que use el entorno del proyecto. Los notebooks pueden depender de los archivos de datos que están en sus respectivas carpetas; conserva la estructura del repositorio al ejecutarlos.

## Estructura

- `1_señales_sistemas/` a `6_reconocimiento_patrones/`: materiales de fundamentos, procesamiento y análisis de señales.
- `7_edge_impulse/`: ejemplos de preparación de datos biomédicos para Edge Impulse.
- `src/opensignalsreader/`: paquete local utilizado para leer archivos de OpenSignals y convertir señales BITalino. Consulta su [documentación](src/opensignalsreader/README.md).
