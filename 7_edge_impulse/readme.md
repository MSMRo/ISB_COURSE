# Módulo 7: Preparación de datos para Edge Impulse

Este módulo reúne ejemplos para convertir registros biomédicos de OpenSignals a formatos que puedan cargarse en flujos de trabajo de Edge Impulse.

## Un archivo

En [`7_1_one_file/`](7_1_one_file/) se encuentra un ejemplo con `SampleECG.txt`. El notebook `main_text2json.ipynb` demuestra la exportación de una señal ECG a JSON o CSV. También incluye pruebas para verificar la estructura y los valores de los archivos exportados.

## Varios archivos etiquetados

En [`7_2_multiple__files/`](7_2_multiple__files/) el notebook `main_convert2ei.ipynb` busca archivos `.txt` bajo `records_bitalino/label_*/raw`, convierte el canal ECG a mV y guarda CSV en la carpeta `formateado` de cada etiqueta. El prefijo del archivo conserva la etiqueta para facilitar su identificación al cargar los datos.

La carpeta `records_bitalino/` contiene ejemplos organizados por etiqueta. `otros.py` muestra una forma de crear copias de respaldo y modificar ligeramente muestras de archivos crudos; no representa nuevas adquisiciones ni corrige etiquetas.

## Uso

Abre los notebooks con el entorno del proyecto (consulta los requisitos en el [README principal](../readme.md)) y revisa las rutas de entrada y salida antes de ejecutar las celdas. Conserva la organización por etiqueta y no sobrescribas datos originales que quieras mantener.
