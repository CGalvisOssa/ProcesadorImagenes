"""
libreria_imagenes.py
Librería para psamiento de imágenes
Contiene todas las transformaciones necesarias para el proyecto
"""

import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt

class ProcesadorImagenes:
    """
    Clase que contiene todas las transformaciones de imagen
    Todos los métodos son estáticos (no necesitan crear un objeto)
    """
    
    # ============================================
    # TRANSFORMACIONES DE BRILLO
    # ============================================
    
    @staticmethod
    def ajustar_brillo_global(imagen, factor):
        """
        Ajusta el brillo de toda la imagen sumando un valor a todos los píxeles
        
        Parámetros:
        -----------
        imagen : numpy.ndarray
            Imagen de entrada en formato numpy array (H, W, 3)
        factor : int
            Cantidad a sumar a cada píxel (-100 a 100)
            Positivo = más brillo, Negativo = menos brillo
        
        Retorna:
        --------
        numpy.ndarray : Imagen con brillo ajustado
        
        Ejemplo:
        --------
        >>> img = np.array(Image.open('foto.jpg'))
        >>> img_brillante = ProcesadorImagenes.ajustar_brillo_global(img, 50)
        """
        # Convertir a float para evitar overflow
        # (si sumas 50 a 220, da 270, que no cabe en 0-255)
        img_float = imagen.astype(np.float32)
        
        # Sumar el factor a todos los píxeles
        img_ajustada = img_float + factor
        
        # Asegurar que los valores estén entre 0 y 255
        # np.clip: si es menor que 0 → 0, si es mayor que 255 → 255
        img_ajustada = np.clip(img_ajustada, 0, 255)
        
        # Convertir de vuelta a uint8 (enteros de 0-255)
        return img_ajustada.astype(np.uint8)
    
    @staticmethod
    def ajustar_brillo_canal(imagen, canal, factor):
        """
        Ajusta el brillo de UN SOLO canal de color (R, G o B)
        
        Parámetros:
        -----------
        imagen : numpy.ndarray
            Imagen RGB
        canal : str
            'R', 'G' o 'B' (Rojo, Verde o Azul)
        factor : int
            Cantidad a sumar (-100 a 100)
        
        Retorna:
        --------
        numpy.ndarray : Imagen con el canal ajustado
        """
        # Hacer una copia para no modificar la original
        img_copia = imagen.copy().astype(np.float32)
        
        # Seleccionar el canal correcto
        # En RGB: canal 0 = Rojo, canal 1 = Verde, canal 2 = Azul
        if canal == 'R':
            indice_canal = 0
        elif canal == 'G':
            indice_canal = 1
        elif canal == 'B':
            indice_canal = 2
        else:
            raise ValueError("Canal debe ser 'R', 'G' o 'B'")
        
        # Ajustar solo ese canal
        img_copia[:, :, indice_canal] += factor
        
        # Clip y convertir
        img_copia = np.clip(img_copia, 0, 255)
        return img_copia.astype(np.uint8)
    
    # ============================================
    # TRANSFORMACIONES DE CONTRASTE
    # ============================================
    
    @staticmethod
    def contraste_logaritmico(imagen, c=1):
        """
        Aplica transformación logarítmica para mejorar zonas oscuras
        Fórmula: s = c * log(1 + r)
        
        ¿Cuándo usar? Cuando tienes una imagen muy oscura y quieres
        ver mejor los detalles en las sombras
        
        Parámetros:
        -----------
        imagen : numpy.ndarray
            Imagen de entrada
        c : float
            Constante de escala (por defecto 1)
        
        Retorna:
        --------
        numpy.ndarray : Imagen transformada
        """
        # Convertir a float
        img_float = imagen.astype(np.float32)
        
        # Aplicar logaritmo: log(1 + valor)
        # El +1 es importante para evitar log(0)
        img_log = c * np.log1p(img_float)
        
        # Normalizar al rango 0-255
        # Encontrar el valor máximo y escalar todo proporcionalmente
        img_log = (img_log / img_log.max()) * 255
        
        return img_log.astype(np.uint8)
    
    @staticmethod
    def contraste_exponencial(imagen, gamma=1.0):
        """
        Aplica transformación exponencial (Gamma correction)
        Fórmula: s = 255 * (r/255)^gamma
        
        ¿Cuándo usar?
        - gamma < 1: Aclara la imagen (expande zonas oscuras)
        - gamma > 1: Oscurece la imagen (expande zonas claras)
        - gamma = 1: No hace nada
        
        Parámetros:
        -----------
        imagen : numpy.ndarray
            Imagen de entrada
        gamma : float
            Valor de gamma (típicamente 0.5 a 2.5)
        
        Retorna:
        --------
        numpy.ndarray : Imagen transformada
        """
        # Normalizar a rango 0-1
        img_normalizada = imagen.astype(np.float32) / 255.0
        
        # Aplicar potencia gamma
        img_gamma = np.power(img_normalizada, gamma)
        
        # Volver a escala 0-255
        img_gamma = img_gamma * 255
        
        return img_gamma.astype(np.uint8)
    
    # ============================================
    # TRANSFORMACIONES GEOMÉTRICAS
    # ============================================
    
    @staticmethod
    def recortar_imagen(imagen, x1, y1, x2, y2):
        """
        Recorta una región rectangular de la imagen
        
        Parámetros:
        -----------
        imagen : numpy.ndarray
            Imagen completa
        x1, y1 : int
            Coordenadas de la esquina superior izquierda
        x2, y2 : int
            Coordenadas de la esquina inferior derecha
        
        Retorna:
        --------
        numpy.ndarray : Imagen recortada
        """
        # En numpy, las imágenes se indexan como [fila, columna]
        # pero en coordenadas pensamos en (x, y)
        # Por eso: filas = y, columnas = x
        return imagen[y1:y2, x1:x2]
    
    @staticmethod
    def aplicar_zoom(imagen, factor, centro_x=None, centro_y=None):
        """
        Amplía la imagen (zoom in) sobre un punto central
        
        Parámetros:
        -----------
        imagen : numpy.ndarray
            Imagen original
        factor : float
            Factor de zoom (2.0 = doble tamaño, 0.5 = mitad)
        centro_x, centro_y : int, opcional
            Punto central del zoom (si no se da, usa el centro de la imagen)
        
        Retorna:
        --------
        numpy.ndarray : Imagen con zoom aplicado
        """
        altura, ancho = imagen.shape[:2]
        
        # Si no se especifica centro, usar el centro de la imagen
        if centro_x is None:
            centro_x = ancho // 2
        if centro_y is None:
            centro_y = altura // 2
        
        # Calcular nuevo tamaño
        nuevo_ancho = int(ancho * factor)
        nuevo_alto = int(altura * factor)
        
        # Redimensionar usando OpenCV
        img_zoom = cv2.resize(imagen, (nuevo_ancho, nuevo_alto), 
                              interpolation=cv2.INTER_LINEAR)
        
        # Si factor > 1, recortar al tamaño original centrado
        if factor > 1:
            inicio_x = (nuevo_ancho - ancho) // 2
            inicio_y = (nuevo_alto - altura) // 2
            img_zoom = img_zoom[inicio_y:inicio_y+altura, inicio_x:inicio_x+ancho]
        
        return img_zoom
    
    @staticmethod
    def rotar_imagen(imagen, angulo):
        """
        Rota la imagen un ángulo dado en sentido antihorario
        
        Parámetros:
        -----------
        imagen : numpy.ndarray
            Imagen a rotar
        angulo : float
            Ángulo de rotación en grados (positivo = antihorario)
        
        Retorna:
        --------
        numpy.ndarray : Imagen rotada
        """
        altura, ancho = imagen.shape[:2]
        centro = (ancho // 2, altura // 2)
        
        # Obtener matriz de rotación
        matriz_rotacion = cv2.getRotationMatrix2D(centro, angulo, 1.0)
        
        # Aplicar rotación
        img_rotada = cv2.warpAffine(imagen, matriz_rotacion, (ancho, altura),
                                     borderMode=cv2.BORDER_CONSTANT,
                                     borderValue=(255, 255, 255))
        
        return img_rotada
    
    # ============================================
    # HISTOGRAMA
    # ============================================
    
    @staticmethod
    def calcular_histograma(imagen):
        """
        Calcula el histograma de cada canal RGB
        
        Un histograma muestra cuántos píxeles hay de cada intensidad (0-255)
        
        Parámetros:
        -----------
        imagen : numpy.ndarray
            Imagen RGB
        
        Retorna:
        --------
        tuple : (hist_r, hist_g, hist_b)
            Tres arrays con los histogramas de cada canal
        """
        # Separar canales
        canal_r = imagen[:, :, 0]
        canal_g = imagen[:, :, 1]
        canal_b = imagen[:, :, 2]
        
        # Calcular histograma de cada canal
        # bins=256 porque tenemos valores de 0 a 255
        hist_r, _ = np.histogram(canal_r.flatten(), bins=256, range=(0, 256))
        hist_g, _ = np.histogram(canal_g.flatten(), bins=256, range=(0, 256))
        hist_b, _ = np.histogram(canal_b.flatten(), bins=256, range=(0, 256))
        
        return hist_r, hist_g, hist_b
    
    @staticmethod
    def visualizar_histograma(imagen):
        """
        Crea una visualización del histograma
        
        Parámetros:
        -----------
        imagen : numpy.ndarray
            Imagen RGB
        
        Retorna:
        --------
        matplotlib.figure.Figure : Figura con el histograma
        """
        hist_r, hist_g, hist_b = ProcesadorImagenes.calcular_histograma(imagen)
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 4))
        
        # Graficar cada canal
        ax.plot(hist_r, color='red', alpha=0.7, label='Rojo')
        ax.plot(hist_g, color='green', alpha=0.7, label='Verde')
        ax.plot(hist_b, color='blue', alpha=0.7, label='Azul')
        
        ax.set_xlabel('Intensidad de píxel')
        ax.set_ylabel('Frecuencia')
        ax.set_title('Histograma RGB')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig
    
    # ============================================
    # FUSIÓN DE IMÁGENES
    # ============================================
    
    @staticmethod
    def fusionar_imagenes(img1, img2, alpha=0.5):
        """
        Fusiona dos imágenes con un peso alpha
        Resultado = img1 * alpha + img2 * (1 - alpha)
        
        Parámetros:
        -----------
        img1, img2 : numpy.ndarray
            Imágenes a fusionar (deben tener el mismo tamaño)
        alpha : float
            Peso de la primera imagen (0.0 a 1.0)
            0.5 = 50% de cada una
        
        Retorna:
        --------
        numpy.ndarray : Imagen fusionada
        """
        # Verificar que tengan el mismo tamaño
        if img1.shape != img2.shape:
            # Redimensionar img2 al tamaño de img1
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        
        # Fusionar
        img_fusionada = cv2.addWeighted(img1, alpha, img2, 1-alpha, 0)
        
        return img_fusionada
    
    @staticmethod
    def ecualizar_histograma(imagen):
        """
        Ecualiza el histograma para mejorar el contraste
        
        La ecualización distribuye uniformemente las intensidades
        
        Parámetros:
        -----------
        imagen : numpy.ndarray
            Imagen RGB
        
        Retorna:
        --------
        numpy.ndarray : Imagen ecualizada
        """
        # Convertir a espacio de color YUV
        # (Y = luminosidad, UV = color)
        img_yuv = cv2.cvtColor(imagen, cv2.COLOR_RGB2YUV)
        
        # Ecualizar solo el canal Y (luminosidad)
        img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
        
        # Convertir de vuelta a RGB
        img_ecualizada = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2RGB)
        
        return img_ecualizada
    
    @staticmethod
    def fusionar_ecualizadas(img1, img2, alpha=0.5):
        """
        Ecualiza ambas imágenes antes de fusionarlas
        
        Parámetros:
        -----------
        img1, img2 : numpy.ndarray
            Imágenes a fusionar
        alpha : float
            Peso de fusión
        
        Retorna:
        --------
        numpy.ndarray : Imagen fusionada y ecualizada
        """
        # Ecualizar ambas
        img1_eq = ProcesadorImagenes.ecualizar_histograma(img1)
        img2_eq = ProcesadorImagenes.ecualizar_histograma(img2)
        
        # Fusionar
        return ProcesadorImagenes.fusionar_imagenes(img1_eq, img2_eq, alpha)
    
    # ============================================
    # EXTRACCIÓN DE CAPAS
    # ============================================
    
    @staticmethod
    def extraer_rgb(imagen):
        """
        Extrae los tres canales RGB como imágenes separadas
        
        Parámetros:
        -----------
        imagen : numpy.ndarray
            Imagen RGB
        
        Retorna:
        --------
        tuple : (img_r, img_g, img_b)
            Tres imágenes en escala de grises, una por cada canal
        """
        # Separar canales
        canal_r = imagen[:, :, 0]
        canal_g = imagen[:, :, 1]
        canal_b = imagen[:, :, 2]
        
        # Crear imágenes de 3 canales para visualizar
        # (así se ven como imágenes grises)
        img_r = np.zeros_like(imagen)
        img_r[:, :, 0] = canal_r  # Solo canal rojo activo
        
        img_g = np.zeros_like(imagen)
        img_g[:, :, 1] = canal_g  # Solo canal verde activo
        
        img_b = np.zeros_like(imagen)
        img_b[:, :, 2] = canal_b  # Solo canal azul activo
        
        return img_r, img_g, img_b
    
    @staticmethod
    def extraer_cmyk(imagen):
        """
        Convierte RGB a CMYK y extrae los cuatro canales
        
        CMYK = Cyan, Magenta, Yellow, Key (negro)
        Se usa en impresión
        
        Parámetros:
        -----------
        imagen : numpy.ndarray
            Imagen RGB
        
        Retorna:
        --------
        tuple : (canal_c, canal_m, canal_y, canal_k)
            Cuatro arrays con los canales CMYK (valores 0-255)
        """
        # Normalizar RGB a 0-1
        img_float = imagen.astype(np.float32) / 255.0
        
        # Extraer canales RGB
        R = img_float[:, :, 0]
        G = img_float[:, :, 1]
        B = img_float[:, :, 2]
        
        # Calcular K (negro)
        K = 1 - np.maximum(np.maximum(R, G), B)
        
        # Evitar división por cero
        K_inv = 1 - K
        K_inv[K_inv == 0] = 1
        
        # Calcular CMY
        C = (1 - R - K) / K_inv
        M = (1 - G - K) / K_inv
        Y = (1 - B - K) / K_inv
        
        # Convertir a rango 0-255
        C = (C * 255).astype(np.uint8)
        M = (M * 255).astype(np.uint8)
        Y = (Y * 255).astype(np.uint8)
        K = (K * 255).astype(np.uint8)
        
        return C, M, Y, K
    
    # ============================================
    # CONVERSIONES DE COLOR
    # ============================================
    
    @staticmethod
    def foto_negativa(imagen):
        """
        Invierte los colores de la imagen (como un negativo fotográfico)
        Fórmula: s = 255 - r
        
        Parámetros:
        -----------
        imagen : numpy.ndarray
            Imagen original
        
        Retorna:
        --------
        numpy.ndarray : Imagen negativa
        """
        return 255 - imagen
    
    @staticmethod
    def convertir_grises(imagen):
        """
        Convierte imagen RGB a escala de grises
        
        Usa la fórmula estándar:
        Gris = 0.299*R + 0.587*G + 0.114*B
        (el ojo humano es más sensible al verde)
        
        Parámetros:
        -----------
        imagen : numpy.ndarray
            Imagen RGB
        
        Retorna:
        --------
        numpy.ndarray : Imagen en escala de grises (3 canales iguales)
        """
        # Usar la conversión estándar de OpenCV
        img_gris = cv2.cvtColor(imagen, cv2.COLOR_RGB2GRAY)
        
        # Convertir a 3 canales para mantener compatibilidad
        img_gris_3ch = cv2.cvtColor(img_gris, cv2.COLOR_GRAY2RGB)
        
        return img_gris_3ch
    
    @staticmethod
    def binarizar(imagen, umbral=127):
        """
        Convierte la imagen a solo dos colores: blanco y negro
        Píxeles por debajo del umbral → negro (0)
        Píxeles por encima del umbral → blanco (255)
        
        Parámetros:
        -----------
        imagen : numpy.ndarray
            Imagen de entrada (preferiblemente en grises)
        umbral : int
            Valor de umbral (0-255), por defecto 127 (mitad)
        
        Retorna:
        --------
        numpy.ndarray : Imagen binarizada
        """
        # Convertir a escala de grises primero
        if len(imagen.shape) == 3:
            img_gris = cv2.cvtColor(imagen, cv2.COLOR_RGB2GRAY)
        else:
            img_gris = imagen
        
        # Aplicar umbral
        _, img_binaria = cv2.threshold(img_gris, umbral, 255, cv2.THRESH_BINARY)
        
        # Convertir a 3 canales
        img_binaria_3ch = cv2.cvtColor(img_binaria, cv2.COLOR_GRAY2RGB)
        
        return img_binaria_3ch


# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

def cargar_imagen(ruta):
    """
    Carga una imagen desde un archivo
    
    Parámetros:
    -----------
    ruta : str
        Ruta al archivo de imagen
    
    Retorna:
    --------
    numpy.ndarray : Imagen en formato RGB
    """
    img = Image.open(ruta)
    # Convertir a RGB (por si es RGBA o otro formato)
    img_rgb = img.convert('RGB')
    # Convertir a numpy array
    return np.array(img_rgb)


def guardar_imagen(imagen, ruta):
    """
    Guarda una imagen en un archivo
    
    Parámetros:
    -----------
    imagen : numpy.ndarray
        Imagen a guardar
    ruta : str
        Ruta donde guardar (debe incluir extensión: .jpg, .png, etc.)
    """
    img_pil = Image.fromarray(imagen)
    img_pil.save(ruta)
    print(f"Imagen guardada en: {ruta}")