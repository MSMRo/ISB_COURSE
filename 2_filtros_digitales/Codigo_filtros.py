import numpy as np
import csv
import matplotlib.pyplot as plt
from scipy.signal import lfilter
from scipy.fft import fft, fftfreq

# Función para leer la quinta columna de un archivo
def leer_columna_cinco(ruta_archivo):
    datos_columna_5 = []

    with open(ruta_archivo, 'r') as archivo:
        # Saltar el encabezado hasta 'EndOfHeader'
        for linea in archivo:
            if 'EndOfHeader' in linea:
                break

        # Leer las columnas y extraer la quinta columna
        for linea in archivo:
            columnas = linea.strip().split()
            if len(columnas) >= 6:  # Asegurarse de que haya al menos 6 columnas
                try:
                    datos_columna_5.append(float(columnas[5]))  # Columna 5 (índice 5)
                except ValueError:
                    continue  # Ignorar líneas mal formateadas
    
    return np.array(datos_columna_5)

# Función para leer el archivo CSV con coeficientes
def leer_csv(filepath):
    b, a = [], []
    with open(filepath, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Asegurar que haya al menos dos columnas
            if len(row) >= 2:
                b.append(float(row[0]))  # Columna izquierda
                a.append(float(row[1]))  # Columna derecha
            else:
                b.append(float(row[0]))  # Si solo hay una columna, la asigna a b
                a.append(1.0)            # Si falta la columna derecha, asigna 1.0 a a
    
    return np.array(a), np.array(b)

# Función para convertir ADC a milivoltios
def ADCtomV(ADC, n=10, VCC=3.3):
    volts = (((ADC/(2**n)) - (1/2)) * VCC) / 1009
    volts=volts*1000
    return volts 

# Función para calcular la FFT
def calcular_fft(senal, fs):
    N = len(senal)
    fft_senal = fft(senal)
    f = fftfreq(N, 1/fs)
    amplitud_fft = (2.0 / N * np.abs(fft_senal[:N//2]))  # FFT amplitud
    amplitud_fft_db = 20 * np.log10(amplitud_fft + 1e-10)  # Convertir a dB, suma un valor pequeño para evitar log(0)
    return f[:N//2], amplitud_fft_db

# Función para ploteo conjunto de señal original, señal filtrada y sus FFTs
def plotear_senal_y_fft_conjunto(data, fs, b, a, title="Señal"):
    # Crear vector de tiempo
    tiempo = np.arange(0, len(data)) / fs

    # Filtrar la señal
    senal_filtrada = lfilter(b, a, data)

    # Calcular las FFTs
    f_original, amplitud_fft_original = calcular_fft(data, fs)
    f_filtrada, amplitud_fft_filtrada = calcular_fft(senal_filtrada, fs)

    # Crear la figura con 2 filas y 2 columnas
    plt.figure(figsize=(12, 8))

    # Señal original en el dominio del tiempo
    plt.subplot(2, 2, 1)
    plt.plot(tiempo, data, color='b',linewidth=0.6)
    plt.title(f"{title} Original (Tiempo)")
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Amplitud (mV)')
    
    plt.grid(True)

    # FFT de la señal original
    plt.subplot(2, 2, 3)
    plt.plot(f_original, amplitud_fft_original, color='b',linewidth=0.6)
    plt.title(f"{title} Original (Frecuencia)")
    plt.xlabel('Frecuencia (Hz)')
    plt.ylabel('Amplitud')
    
    plt.grid(True)

    # Señal filtrada en el dominio del tiempo
    plt.subplot(2, 2, 2)
    plt.plot(tiempo, senal_filtrada, color='r',linewidth=0.6)
    plt.title(f"{title} Filtrada (Tiempo)")
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Amplitud (mV)')
    plt.xlim(0,4)
    plt.grid(True)

    # FFT de la señal filtrada
    plt.subplot(2, 2, 4)
    plt.plot(f_filtrada, amplitud_fft_filtrada, color='r',linewidth=0.6)
    plt.title(f"{title} Filtrada (Frecuencia)")
    plt.xlabel('Frecuencia (Hz)')
    plt.ylabel('Amplitud')
    plt.grid(True)
    

    # Ajustar el espacio entre subplots
    plt.tight_layout()
    plt.show()

# Parámetros de ejemplo
ruta_archivo = "C:/Users/DELL/Downloads/EMG1/LAB7/SenalesECG/ejercicio_ECG.txt"
ruta_csv = "C:/Users/DELL/Downloads/EMG1/LAB7/Filtro3Hann_ECG.csv"
fs = 1000  # Frecuencia de muestreo

# Leer la señal y convertirla a milivoltios
data = leer_columna_cinco(ruta_archivo)
datamv = ADCtomV(data, 10, 3.3)

# Leer los coeficientes del filtro
a, b = leer_csv(ruta_csv)

# Aplicar la función para plotear la señal original y filtrada, junto con sus FFTs en un solo gráfico
plotear_senal_y_fft_conjunto(datamv, fs, b, a, title="Señal EMG")



