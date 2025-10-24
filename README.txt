================================================================================
PROCESADOR DE IMÁGENES - PROYECTO DE PROCESAMIENTO DIGITAL
================================================================================

DESCRIPCIÓN
-----------
Sistema de procesamiento de imágenes que implementa 15 transformaciones 
fundamentales del procesamiento digital de imágenes, incluyendo operaciones 
puntuales, geométricas, análisis estadístico y conversiones de espacios de 
color.

================================================================================
REQUISITOS
================================================================================

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

================================================================================
INSTALACIÓN
================================================================================

1. Clonar o descargar el repositorio:
   
   git clone <C:\Users\cris4\OneDrive\Documents\Clases\CompuGrafica\proyecto2\ProyectoProcesadorImagenes>
   cd ProyectoProcesadorImagenes

2. Instalar dependencias:
   
   pip install -r requirements.txt

================================================================================
DEPENDENCIAS
================================================================================

numpy>=1.21.0
Pillow>=9.0.0
matplotlib>=3.5.0
opencv-python>=4.5.0

================================================================================
EJECUCIÓN
================================================================================

python main.py

================================================================================
ESTRUCTURA DEL PROYECTO
================================================================================

procesador_imagenes/
│
├── main.py                  # Interfaz gráfica (GUI)
├── libreria_imagenes.py     # Librería de transformaciones
├── README.md                # Documentación
└── requirements.txt         # Dependencias

================================================================================
FUNCIONALIDADES
================================================================================

1. TRANSFORMACIONES DE INTENSIDAD
   --------------------------------

   a) Brillo Global
      Ajuste de intensidad mediante suma escalar.
      Fórmula: I'(x,y) = I(x,y) + β
      Rango: β ∈ [-100, 100]

   b) Brillo por Canal
      Ajuste independiente de cada canal RGB.

   c) Contraste Logarítmico
      Expansión de valores oscuros mediante transformación logarítmica.
      Fórmula: s = c · log(1 + r)

   d) Contraste Exponencial (Gamma Correction)
      Fórmula: s = 255 · (r/255)^γ
      - γ < 1: Aclara la imagen
      - γ > 1: Oscurece la imagen


2. TRANSFORMACIONES GEOMÉTRICAS
   -----------------------------

   a) Recorte (Cropping)
      Extracción de región de interés mediante coordenadas rectangulares.

   b) Zoom
      Ampliación 2x con interpolación lineal.

   c) Rotación
      Rotación arbitraria con relleno de bordes constante.


3. ANÁLISIS ESTADÍSTICO
   ---------------------

   a) Histograma RGB
      Cálculo y visualización de la distribución de intensidades por canal.


4. FUSIÓN DE IMÁGENES
   -------------------

   a) Alpha Blending
      Fórmula: I_result = α · I1 + (1-α) · I2
      Rango: α ∈ [0, 1]

   b) Fusión con Ecualización
      Ecualización de histograma previa a la fusión para mejorar contraste.


5. EXTRACCIÓN DE COMPONENTES
   --------------------------

   a) Canales RGB
      Separación de componentes Rojo, Verde y Azul.

   b) Conversión CMYK
      Transformación al espacio de color sustractivo:
      K = 1 - max(R, G, B)
      C = (1 - R - K) / (1 - K)
      M = (1 - G - K) / (1 - K)
      Y = (1 - B - K) / (1 - K)


6. CONVERSIONES DE COLOR
   ----------------------

   a) Negativo
      Inversión de intensidades.
      Fórmula: I'(x,y) = 255 - I(x,y)

   b) Escala de Grises
      Conversión mediante promedio ponderado perceptual:
      Gray = 0.299·R + 0.587·G + 0.114·B

   c) Binarización (Thresholding)
      Segmentación mediante umbral global:
      I'(x,y) = {255 si I(x,y) > T, 0 en otro caso}

================================================================================
USO BÁSICO
================================================================================

DESDE LA INTERFAZ GRÁFICA
--------------------------

1. Cargar imagen: Archivo → Abrir imagen (Ctrl+O)
2. Aplicar transformación: Usar controles del panel lateral
3. Guardar resultado: Archivo → Guardar (Ctrl+S)


DESDE CÓDIGO PYTHON
--------------------

from libreria_imagenes import ProcesadorImagenes
import numpy as np
from PIL import Image

# Cargar imagen
img = np.array(Image.open('input.jpg'))

# Aplicar transformación
img_procesada = ProcesadorImagenes.ajustar_brillo_global(img, 50)

# Guardar
Image.fromarray(img_procesada).save('output.jpg')

================================================================================
API DE LA LIBRERÍA
================================================================================

Clase: ProcesadorImagenes
Todos los métodos son estáticos.

TRANSFORMACIONES DE INTENSIDAD
-------------------------------
- ajustar_brillo_global(imagen, factor) → ndarray
- ajustar_brillo_canal(imagen, canal, factor) → ndarray
- contraste_logaritmico(imagen, c) → ndarray
- contraste_exponencial(imagen, gamma) → ndarray

TRANSFORMACIONES GEOMÉTRICAS
-----------------------------
- recortar_imagen(imagen, x1, y1, x2, y2) → ndarray
- aplicar_zoom(imagen, factor, centro_x, centro_y) → ndarray
- rotar_imagen(imagen, angulo) → ndarray

ANÁLISIS
--------
- calcular_histograma(imagen) → tuple[ndarray, ndarray, ndarray]
- visualizar_histograma(imagen) → Figure

FUSIÓN
------
- fusionar_imagenes(img1, img2, alpha) → ndarray
- fusionar_ecualizadas(img1, img2, alpha) → ndarray
- ecualizar_histograma(imagen) → ndarray

EXTRACCIÓN DE CAPAS
-------------------
- extraer_rgb(imagen) → tuple[ndarray, ndarray, ndarray]
- extraer_cmyk(imagen) → tuple[ndarray, ndarray, ndarray, ndarray]

CONVERSIONES
------------
- foto_negativa(imagen) → ndarray
- convertir_grises(imagen) → ndarray
- binarizar(imagen, umbral) → ndarray

UTILIDADES
----------
- cargar_imagen(ruta) → ndarray
- guardar_imagen(imagen, ruta) → None

================================================================================
ARQUITECTURA
================================================================================

main.py
-------
Implementa la interfaz gráfica usando Tkinter:
- Clase AplicacionProcesamiento: Controlador principal
- Gestión de eventos de usuario
- Visualización en tiempo real
- Manejo de estado de la aplicación

libreria_imagenes.py
--------------------
Implementa las transformaciones usando:
- NumPy: Operaciones matriciales
- OpenCV: Transformaciones geométricas y conversiones de color
- Pillow: I/O de imágenes
- Matplotlib: Visualización de histogramas

================================================================================
FORMATOS SOPORTADOS
================================================================================

ENTRADA/SALIDA:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)

================================================================================
LIMITACIONES CONOCIDAS
================================================================================

- Las imágenes muy grandes (>4000x4000) pueden causar lentitud en la 
  visualización
- La rotación usa relleno blanco en los bordes
- El zoom está fijado a factor 2x en la interfaz

================================================================================
SOLUCIÓN DE PROBLEMAS
================================================================================

ERROR: "cannot import name 'ProcesadorImagenes'"
------------------------------------------------
Verifica que los archivos estén en la misma carpeta:

   ls -l
   # Debe mostrar: main.py y libreria_imagenes.py


ERROR: "No module named 'tkinter'"
-----------------------------------
Linux (Ubuntu/Debian):
   sudo apt-get install python3-tk

Linux (Fedora):
   sudo dnf install python3-tkinter


ERROR: ModuleNotFoundError
---------------------------
Reinstalar dependencias:
   pip install --upgrade -r requirements.txt

================================================================================
EJEMPLOS DE USO
================================================================================

EJEMPLO 1: Ajustar brillo de una imagen
----------------------------------------
from libreria_imagenes import ProcesadorImagenes, cargar_imagen, guardar_imagen

img = cargar_imagen('foto.jpg')
img_brillante = ProcesadorImagenes.ajustar_brillo_global(img, 50)
guardar_imagen(img_brillante, 'foto_brillante.jpg')


EJEMPLO 2: Aplicar contraste logarítmico
-----------------------------------------
img = cargar_imagen('foto_oscura.jpg')
img_mejorada = ProcesadorImagenes.contraste_logaritmico(img, c=1.5)
guardar_imagen(img_mejorada, 'foto_mejorada.jpg')


EJEMPLO 3: Fusionar dos imágenes
---------------------------------
img1 = cargar_imagen('imagen1.jpg')
img2 = cargar_imagen('imagen2.jpg')
img_fusion = ProcesadorImagenes.fusionar_imagenes(img1, img2, alpha=0.5)
guardar_imagen(img_fusion, 'fusion.jpg')


EJEMPLO 4: Extraer canal rojo
------------------------------
img = cargar_imagen('foto.jpg')
canal_r, canal_g, canal_b = ProcesadorImagenes.extraer_rgb(img)
guardar_imagen(canal_r, 'canal_rojo.jpg')


EJEMPLO 5: Binarizar imagen
----------------------------
img = cargar_imagen('documento.jpg')
img_binaria = ProcesadorImagenes.binarizar(img, umbral=127)
guardar_imagen(img_binaria, 'documento_binario.jpg')


================================================================================
AUTOR
================================================================================

Cristhian Galvis Ossa
Universidad Tecnologica de Pereira
Computacion Grafica

================================================================================
REFERENCIAS
================================================================================

- Gonzalez, R. C., & Woods, R. E. (2018). Digital Image Processing (4th ed.). 
  Pearson.
- OpenCV Documentation: https://docs.opencv.org/
- NumPy Documentation: https://numpy.org/doc/
- Pillow Documentation: https://pillow.readthedocs.io/

================================================================================
LICENCIA
================================================================================

Proyecto académico - Uso educativo

================================================================================

Versión: 1.0
Fecha: 10/24/2025

================================================================================
FIN DEL DOCUMENTO
================================================================================