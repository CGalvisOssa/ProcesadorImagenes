"""
main.py
Interfaz gráfica para el procesador de imágenes
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
from libreria_imagenes import ProcesadorImagenes
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cv2


class AplicacionProcesamiento:
    """
    Clase principal de la aplicación
    Maneja toda la interfaz y las interacciones
    """
    
    def __init__(self, root):
        """
        Constructor: se ejecuta cuando creamos la aplicación
        
        Parámetros:
        -----------
        root : tk.Tk
            Ventana principal de Tkinter
        """
        self.root = root
        self.root.title("Procesador de Imágenes - Proyecto Final")
        self.root.geometry("1400x900")
        
        # Variables para almacenar imágenes
        self.imagen_original = None      # PIL Image original
        self.imagen_procesada = None     # PIL Image actual
        self.imagen_segunda = None       # Para fusión
        self.imagen_display = None       # Para mostrar en pantalla
        
        # Variables de control (conectadas a widgets)
        self.var_brillo_global = tk.IntVar(value=0)
        self.var_brillo_r = tk.IntVar(value=0)
        self.var_brillo_g = tk.IntVar(value=0)
        self.var_brillo_b = tk.IntVar(value=0)
        self.var_gamma = tk.DoubleVar(value=1.0)
        self.var_c_log = tk.DoubleVar(value=1.0)
        self.var_umbral = tk.IntVar(value=127)
        self.var_alpha_fusion = tk.DoubleVar(value=0.5)
        self.var_angulo_rotacion = tk.IntVar(value=0)
        
        # Crear la interfaz
        self.crear_menu()
        self.crear_interfaz()
        
        print("✅ Aplicación iniciada correctamente")
    
    def crear_menu(self):
        """
        Crea la barra de menú superior
        """
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Abrir imagen principal", 
                                command=self.abrir_imagen,
                                accelerator="Ctrl+O")
        menu_archivo.add_command(label="Abrir segunda imagen (fusión)", 
                                command=self.abrir_segunda_imagen)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Guardar imagen", 
                                command=self.guardar_imagen,
                                accelerator="Ctrl+S")
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.quit)
        
        # Menú Edición
        menu_edicion = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="✏️ Edición", menu=menu_edicion)
        menu_edicion.add_command(label="Restaurar original", 
                                command=self.restaurar_original)
        menu_edicion.add_command(label="Resetear controles", 
                                command=self.resetear_controles)
        
        # Menú Ayuda
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="Acerca de", command=self.mostrar_acerca_de)
        
        # Atajos de teclado
        self.root.bind('<Control-o>', lambda e: self.abrir_imagen())
        self.root.bind('<Control-s>', lambda e: self.guardar_imagen())
    
    def crear_interfaz(self):
        """
        Crea toda la estructura de la interfaz
        """
        # Frame principal (contiene todo)
        frame_principal = tk.Frame(self.root)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Dividir en dos: controles (izquierda) y visualización (derecha)
        self.crear_panel_controles(frame_principal)
        self.crear_panel_visualizacion(frame_principal)
        
        # Barra de estado en la parte inferior
        self
        # Barra de estado en la parte inferior
        self.crear_barra_estado()
    
    def crear_panel_controles(self, parent):
        """
        Crea el panel izquierdo con todos los controles
        """
        # Frame principal de controles con scrollbar
        frame_controles_wrapper = tk.Frame(parent, width=350, bg='#f0f0f0')
        frame_controles_wrapper.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        frame_controles_wrapper.pack_propagate(False)  # Mantener ancho fijo
        
        # Canvas con scrollbar para los controles
        canvas_controles = tk.Canvas(frame_controles_wrapper, bg='#f0f0f0', 
                                     highlightthickness=0)
        scrollbar = tk.Scrollbar(frame_controles_wrapper, orient="vertical", 
                                command=canvas_controles.yview)
        
        frame_controles = tk.Frame(canvas_controles, bg='#f0f0f0')
        
        frame_controles.bind(
            "<Configure>",
            lambda e: canvas_controles.configure(scrollregion=canvas_controles.bbox("all"))
        )
        
        canvas_controles.create_window((0, 0), window=frame_controles, anchor="nw")
        canvas_controles.configure(yscrollcommand=scrollbar.set)
        
        canvas_controles.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind para scroll con mouse wheel
        def _on_mousewheel(event):
            canvas_controles.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas_controles.bind_all("<MouseWheel>", _on_mousewheel)
        
        # ===== SECCIÓN 1: BRILLO =====
        self.crear_seccion_brillo(frame_controles)
        
        # ===== SECCIÓN 2: CONTRASTE =====
        self.crear_seccion_contraste(frame_controles)
        
        # ===== SECCIÓN 3: TRANSFORMACIONES GEOMÉTRICAS =====
        self.crear_seccion_geometricas(frame_controles)
        
        # ===== SECCIÓN 4: ANÁLISIS =====
        self.crear_seccion_analisis(frame_controles)
        
        # ===== SECCIÓN 5: FUSIÓN =====
        self.crear_seccion_fusion(frame_controles)
        
        # ===== SECCIÓN 6: EXTRACCIÓN DE CAPAS =====
        self.crear_seccion_capas(frame_controles)
        
        # ===== SECCIÓN 7: CONVERSIONES =====
        self.crear_seccion_conversiones(frame_controles)
    
    def crear_seccion_brillo(self, parent):
        """Crea controles de brillo"""
        frame = tk.LabelFrame(parent, text="🔆 BRILLO", font=('Arial', 10, 'bold'),
                             bg='#f0f0f0', padx=10, pady=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Brillo Global
        tk.Label(frame, text="Brillo Global:", bg='#f0f0f0').pack(anchor='w')
        scale_brillo = tk.Scale(frame, from_=-100, to=100, orient=tk.HORIZONTAL,
                               variable=self.var_brillo_global,
                               command=lambda v: self.aplicar_transformacion())
        scale_brillo.pack(fill=tk.X)
        
        # Separador
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # Brillo por canal R
        tk.Label(frame, text="Canal Rojo:", bg='#f0f0f0', fg='red').pack(anchor='w')
        scale_r = tk.Scale(frame, from_=-100, to=100, orient=tk.HORIZONTAL,
                          variable=self.var_brillo_r, fg='red',
                          command=lambda v: self.aplicar_transformacion())
        scale_r.pack(fill=tk.X)
        
        # Brillo por canal G
        tk.Label(frame, text="Canal Verde:", bg='#f0f0f0', fg='green').pack(anchor='w')
        scale_g = tk.Scale(frame, from_=-100, to=100, orient=tk.HORIZONTAL,
                          variable=self.var_brillo_g, fg='green',
                          command=lambda v: self.aplicar_transformacion())
        scale_g.pack(fill=tk.X)
        
        # Brillo por canal B
        tk.Label(frame, text="Canal Azul:", bg='#f0f0f0', fg='blue').pack(anchor='w')
        scale_b = tk.Scale(frame, from_=-100, to=100, orient=tk.HORIZONTAL,
                          variable=self.var_brillo_b, fg='blue',
                          command=lambda v: self.aplicar_transformacion())
        scale_b.pack(fill=tk.X)
    
    def crear_seccion_contraste(self, parent):
        """Crea controles de contraste"""
        frame = tk.LabelFrame(parent, text="🎨 CONTRASTE", font=('Arial', 10, 'bold'),
                             bg='#f0f0f0', padx=10, pady=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Contraste Logarítmico
        tk.Label(frame, text="Logarítmico (c):", bg='#f0f0f0').pack(anchor='w')
        scale_log = tk.Scale(frame, from_=0.1, to=3.0, resolution=0.1,
                            orient=tk.HORIZONTAL, variable=self.var_c_log)
        scale_log.pack(fill=tk.X)
        tk.Button(frame, text="Aplicar Contraste Log",
                 command=self.aplicar_contraste_log,
                 bg='#4CAF50', fg='white').pack(fill=tk.X, pady=2)
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # Contraste Exponencial (Gamma)
        tk.Label(frame, text="Exponencial (gamma):", bg='#f0f0f0').pack(anchor='w')
        scale_gamma = tk.Scale(frame, from_=0.1, to=3.0, resolution=0.1,
                              orient=tk.HORIZONTAL, variable=self.var_gamma)
        scale_gamma.pack(fill=tk.X)
        tk.Button(frame, text="Aplicar Contraste Exp",
                 command=self.aplicar_contraste_exp,
                 bg='#4CAF50', fg='white').pack(fill=tk.X, pady=2)
    
    def crear_seccion_geometricas(self, parent):
        """Crea controles de transformaciones geométricas"""
        frame = tk.LabelFrame(parent, text="📐 TRANSFORMACIONES GEOMÉTRICAS", 
                             font=('Arial', 10, 'bold'),
                             bg='#f0f0f0', padx=10, pady=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Recorte
        tk.Button(frame, text="✂️ Recortar Imagen",
                 command=self.recortar_imagen_dialogo,
                 bg='#2196F3', fg='white').pack(fill=tk.X, pady=2)
        
        # Zoom
        tk.Button(frame, text="🔍 Aplicar Zoom 2x",
                 command=self.aplicar_zoom,
                 bg='#2196F3', fg='white').pack(fill=tk.X, pady=2)
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # Rotación
        tk.Label(frame, text="Ángulo de rotación:", bg='#f0f0f0').pack(anchor='w')
        scale_rotacion = tk.Scale(frame, from_=-180, to=180, orient=tk.HORIZONTAL,
                                 variable=self.var_angulo_rotacion)
        scale_rotacion.pack(fill=tk.X)
        tk.Button(frame, text="🔄 Rotar Imagen",
                 command=self.rotar_imagen,
                 bg='#2196F3', fg='white').pack(fill=tk.X, pady=2)
    
    def crear_seccion_analisis(self, parent):
        """Crea controles de análisis"""
        frame = tk.LabelFrame(parent, text="📊 ANÁLISIS", font=('Arial', 10, 'bold'),
                             bg='#f0f0f0', padx=10, pady=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(frame, text="📈 Ver Histograma",
                 command=self.mostrar_histograma,
                 bg='#9C27B0', fg='white').pack(fill=tk.X, pady=2)
    
    def crear_seccion_fusion(self, parent):
        """Crea controles de fusión"""
        frame = tk.LabelFrame(parent, text="🔀 FUSIÓN DE IMÁGENES", 
                             font=('Arial', 10, 'bold'),
                             bg='#f0f0f0', padx=10, pady=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(frame, text="Alpha (peso primera imagen):", 
                bg='#f0f0f0').pack(anchor='w')
        scale_alpha = tk.Scale(frame, from_=0.0, to=1.0, resolution=0.1,
                              orient=tk.HORIZONTAL, variable=self.var_alpha_fusion)
        scale_alpha.pack(fill=tk.X)
        
        tk.Button(frame, text="🖼️ Fusionar Imágenes Normales",
                 command=self.fusionar_normal,
                 bg='#FF9800', fg='white').pack(fill=tk.X, pady=2)
        
        tk.Button(frame, text="⚡ Fusionar Imágenes Ecualizadas",
                 command=self.fusionar_ecualizadas,
                 bg='#FF9800', fg='white').pack(fill=tk.X, pady=2)
    
    def crear_seccion_capas(self, parent):
        """Crea controles de extracción de capas"""
        frame = tk.LabelFrame(parent, text="🎭 EXTRACCIÓN DE CAPAS", 
                             font=('Arial', 10, 'bold'),
                             bg='#f0f0f0', padx=10, pady=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        # RGB
        tk.Label(frame, text="RGB:", bg='#f0f0f0', font=('Arial', 9, 'bold')).pack(anchor='w')
        frame_rgb = tk.Frame(frame, bg='#f0f0f0')
        frame_rgb.pack(fill=tk.X)
        
        tk.Button(frame_rgb, text="R", command=lambda: self.extraer_canal_rgb('R'),
                 bg='red', fg='white', width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(frame_rgb, text="G", command=lambda: self.extraer_canal_rgb('G'),
                 bg='green', fg='white', width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(frame_rgb, text="B", command=lambda: self.extraer_canal_rgb('B'),
                 bg='blue', fg='white', width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # CMYK
        tk.Label(frame, text="CMYK:", bg='#f0f0f0', font=('Arial', 9, 'bold')).pack(anchor='w')
        frame_cmyk = tk.Frame(frame, bg='#f0f0f0')
        frame_cmyk.pack(fill=tk.X)
        
        tk.Button(frame_cmyk, text="C", command=lambda: self.extraer_canal_cmyk('C'),
                 bg='cyan', width=6).pack(side=tk.LEFT, padx=2)
        tk.Button(frame_cmyk, text="M", command=lambda: self.extraer_canal_cmyk('M'),
                 bg='magenta', fg='white', width=6).pack(side=tk.LEFT, padx=2)
        tk.Button(frame_cmyk, text="Y", command=lambda: self.extraer_canal_cmyk('Y'),
                 bg='yellow', width=6).pack(side=tk.LEFT, padx=2)
        tk.Button(frame_cmyk, text="K", command=lambda: self.extraer_canal_cmyk('K'),
                 bg='black', fg='white', width=6).pack(side=tk.LEFT, padx=2)
    
    def crear_seccion_conversiones(self, parent):
        """Crea controles de conversiones de color"""
        frame = tk.LabelFrame(parent, text="🎨 CONVERSIONES", font=('Arial', 10, 'bold'),
                             bg='#f0f0f0', padx=10, pady=10)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(frame, text="⚫⚪ Negativo",
                 command=self.aplicar_negativo,
                 bg='#607D8B', fg='white').pack(fill=tk.X, pady=2)
        
        tk.Button(frame, text="🌓 Escala de Grises",
                 command=self.convertir_grises,
                 bg='#607D8B', fg='white').pack(fill=tk.X, pady=2)
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        tk.Label(frame, text="Binarización - Umbral:", bg='#f0f0f0').pack(anchor='w')
        scale_umbral = tk.Scale(frame, from_=0, to=255, orient=tk.HORIZONTAL,
                               variable=self.var_umbral)
        scale_umbral.pack(fill=tk.X)
        tk.Button(frame, text="🔲 Binarizar",
                 command=self.binarizar_imagen,
                 bg='#607D8B', fg='white').pack(fill=tk.X, pady=2)
    
    def crear_panel_visualizacion(self, parent):
        """Crea el panel derecho para mostrar la imagen"""
        frame_viz = tk.Frame(parent, bg='white')
        frame_viz.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Título
        tk.Label(frame_viz, text="IMAGEN PROCESADA", 
                font=('Arial', 14, 'bold'),
                bg='white').pack(pady=5)
        
        # Canvas para mostrar imagen
        self.canvas = tk.Canvas(frame_viz, bg='#e0e0e0', highlightthickness=1,
                               highlightbackground='gray')
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Texto inicial
        self.canvas.create_text(500, 300, 
                               text="Abre una imagen usando Archivo → Abrir imagen",
                               font=('Arial', 12), fill='gray',
                               tags='placeholder')
    
    def crear_barra_estado(self):
        """Crea la barra de estado en la parte inferior"""
        self.barra_estado = tk.Label(self.root, text="Listo", 
                                     bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                     bg='#f0f0f0')
        self.barra_estado.pack(side=tk.BOTTOM, fill=tk.X)
    
    def actualizar_estado(self, mensaje):
        """Actualiza el texto de la barra de estado"""
        self.barra_estado.config(text=mensaje)
        self.root.update_idletasks()
    
    # ============================================
    # MÉTODOS DE CARGA Y GUARDADO
    # ============================================
    
    def abrir_imagen(self):
        """Abre una imagen desde el disco"""
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if ruta:
            try:
                # Cargar imagen
                self.imagen_original = Image.open(ruta).convert('RGB')
                self.imagen_procesada = self.imagen_original.copy()
                
                # Resetear controles
                self.resetear_controles()
                
                # Mostrar
                self.mostrar_imagen()
                
                # Actualizar estado
                ancho, alto = self.imagen_original.size
                self.actualizar_estado(f"Imagen cargada: {ruta} | {ancho}x{alto} píxeles")
                
                print(f"✅ Imagen cargada: {ruta}")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la imagen:\n{str(e)}")
                print(f"❌ Error al cargar imagen: {e}")
    
    def abrir_segunda_imagen(self):
        """Abre una segunda imagen para fusión"""
        if self.imagen_original is None:
            messagebox.showwarning("Advertencia", 
                                 "Primero abre la imagen principal")
            return
        
        ruta = filedialog.askopenfilename(
            title="Seleccionar segunda imagen para fusión",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        
        if ruta:
            try:
                self.imagen_segunda = Image.open(ruta).convert('RGB')
                messagebox.showinfo("Éxito", "Segunda imagen cargada correctamente")
                self.actualizar_estado(f"Segunda imagen: {ruta}")
                print(f"✅ Segunda imagen cargada: {ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la imagen:\n{str(e)}")
    
    def guardar_imagen(self):
        """Guarda la imagen procesada"""
        if self.imagen_procesada is None:
            messagebox.showwarning("Advertencia", "No hay imagen para guardar")
            return
        
        ruta = filedialog.asksaveasfilename(
            title="Guardar imagen",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("BMP", "*.bmp"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if ruta:
            try:
                self.imagen_procesada.save(ruta)
                messagebox.showinfo("Éxito", f"Imagen guardada en:\n{ruta}")
                self.actualizar_estado(f"Imagen guardada: {ruta}")
                print(f"✅ Imagen guardada: {ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{str(e)}")
    
    def mostrar_imagen(self):
        """Muestra la imagen procesada en el canvas"""
        if self.imagen_procesada is None:
            return
        
        # Eliminar placeholder si existe
        self.canvas.delete('placeholder')
        
        # Obtener tamaño del canvas
        self.canvas.update()
        canvas_ancho = self.canvas.winfo_width()
        canvas_alto = self.canvas.winfo_height()
        
        # Redimensionar imagen para que quepa en el canvas
        img_display = self.imagen_procesada.copy()
        img_display.thumbnail((canvas_ancho - 20, canvas_alto - 20), Image.Resampling.LANCZOS)
        
        # Convertir a PhotoImage
        self.photo = ImageTk.PhotoImage(img_display)
        
        # Limpiar canvas y mostrar
        self.canvas.delete("all")
        x_centro = canvas_ancho // 2
        y_centro = canvas_alto // 2
        self.canvas.create_image(x_centro, y_centro, image=self.photo, anchor=tk.CENTER)
    
    # ============================================
    # MÉTODOS DE TRANSFORMACIÓN
    # ============================================
    
    def aplicar_transformacion(self):
        """Aplica transformaciones acumulativas de brillo"""
        if self.imagen_original is None:
            return
        
        try:
            # Empezar desde la original
            img_array = np.array(self.imagen_original)
            
            # Aplicar brillo global si no es 0
            brillo_global = self.var_brillo_global.get()
            if brillo_global != 0:
                img_array = ProcesadorImagenes.ajustar_brillo_global(img_array, brillo_global)
            
            # Aplicar brillo por canal R
            brillo_r = self.var_brillo_r.get()
            if brillo_r != 0:
                img_array = ProcesadorImagenes.ajustar_brillo_canal(img_array, 'R', brillo_r)
            
            # Aplicar brillo por canal G
            brillo_g = self.var_brillo_g.get()
            if brillo_g != 0:
                img_array = ProcesadorImagenes.ajustar_brillo_canal(img_array, 'G', brillo_g)
            
            # Aplicar brillo por canal B
            brillo_b = self.var_brillo_b.get()
            if brillo_b != 0:
                img_array = ProcesadorImagenes.ajustar_brillo_canal(img_array, 'B', brillo_b)
            
            # Actualizar imagen procesada
            self.imagen_procesada = Image.fromarray(img_array)
            self.mostrar_imagen()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar transformación:\n{str(e)}")
            print(f"❌ Error: {e}")
    
    def aplicar_contraste_log(self):
        """Aplica contraste logarítmico"""
        if self.imagen_original is None:
            messagebox.showwarning("Advertencia", "Primero abre una imagen")
            return
        
        try:
            c = self.var_c_log.get()
            img_array = np.array(self.imagen_procesada)
            img_procesada = ProcesadorImagenes.contraste_logaritmico(img_array, c)
            self.imagen_procesada = Image.fromarray(img_procesada)
            self.mostrar_imagen()
            self.actualizar_estado(f"Contraste logarítmico aplicado (c={c})")
        except Exception as e:
            messagebox.showerror("Error", f"Error:\n{str(e)}")
    
    def aplicar_contraste_exp(self):
        """Aplica contraste exponencial"""
        if self.imagen_original is None:
            messagebox.showwarning("Advertencia", "Primero abre una imagen")
            return
        
        try:
            gamma = self.var_gamma.get()
            img_array = np.array(self.imagen_procesada)
            img_procesada = ProcesadorImagenes.contraste_exponencial(img_array, gamma)
            self.imagen_procesada = Image.fromarray(img_procesada)
            self.mostrar_imagen()
            self.actualizar_estado(f"Contraste exponencial aplicado (gamma={gamma})")
        except Exception as e:
            messagebox.showerror("Error", f"Error:\n{str(e)}")
    
    def recortar_imagen_dialogo(self):
        """Muestra diálogo para recortar imagen"""
        if self.imagen_original is None:
            messagebox.showwarning("Advertencia", "Primero abre una imagen")
            return
        
        # Crear ventana de diálogo
        dialogo = tk.Toplevel(self.root)
        dialogo.title("Recortar Imagen")
        dialogo.geometry("300x200")
        
        ancho, alto = self.imagen_procesada.size
        
        tk.Label(dialogo, text=f"Tamaño actual: {ancho}x{alto}").pack(pady=5)
        tk.Label(dialogo, text="Ingresa las coordenadas:").pack()
        
        frame_coords = tk.Frame(dialogo)
        frame_coords.pack(pady=10)
        
        tk.Label(frame_coords, text="X1:").grid(row=0, column=0)
        entry_x1 = tk.Entry(frame_coords, width=10)
        entry_x1.grid(row=0, column=1)
        entry_x1.insert(0, "0")
        
        tk.Label(frame_coords, text="Y1:").grid(row=1, column=0)
        entry_y1 = tk.Entry(frame_coords, width=10)
        entry_y1.grid(row=1, column=1)
        entry_y1.insert(0, "0")
        
        tk.Label(frame_coords, text="X2:").grid(row=0, column=2, padx=(10,0))
        entry_x2 = tk.Entry(frame_coords, width=10)
        entry_x2.grid(row=0, column=3)
        entry_x2.insert(0, str(ancho))
        
        tk.Label(frame_coords, text="Y2:").grid(row=1, column=2, padx=(10,0))
        entry_y2 = tk.Entry(frame_coords, width=10)
        entry_y2.grid(row=1, column=3)
        entry_y2.insert(0, str(alto))
        
        def ejecutar_recorte():
            try:
                x1 = int(entry_x1.get())
                y1 = int(entry_y1.get())
                x2 = int(entry_x2.get())
                y2 = int(entry_y2.get())
                
                img_array = np.array(self.imagen_procesada)
                img_recortada = ProcesadorImagenes.recortar_imagen(img_array, x1, y1, x2, y2)
                self.imagen_procesada = Image.fromarray(img_recortada)
                self.mostrar_imagen()
                self.actualizar_estado(f"Imagen recortada: ({x1},{y1}) a ({x2},{y2})")
                dialogo.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Coordenadas inválidas:\n{str(e)}")
        
        tk.Button(dialogo, text="Recortar", command=ejecutar_recorte,
                 bg='#4CAF50', fg='white').pack(pady=10)
    
    def aplicar_zoom(self):
        """Aplica zoom 2x"""
        if self.imagen_original is None:
            messagebox.showwarning("Advertencia", "Primero abre una imagen")
            return
        
        try:
            img_array = np.array(self.imagen_procesada)
            img_zoom = ProcesadorImagenes.aplicar_zoom(img_array, 2.0)
            self.imagen_procesada = Image.fromarray(img_zoom)
            self.mostrar_imagen()
            self.actualizar_estado("Zoom 2x aplicado")
        except Exception as e:
            messagebox.showerror("Error", f"Error:\n{str(e)}")
    
    def rotar_imagen(self):
        """Rota la imagen"""
        if self.imagen_original is None:
            messagebox.showwarning("Advertencia", "Primero abre una imagen")
            return
        
        try:
            angulo = self.var_angulo_rotacion.get()
            img_array = np.array(self.imagen_procesada)
            img_rotada = ProcesadorImagenes.rotar_imagen(img_array, angulo)
            self.imagen_procesada = Image.fromarray(img_rotada)
            self.mostrar_imagen()
            self.actualizar_estado(f"Imagen rotada {angulo}°")
        except Exception as e:
            messagebox.showerror("Error", f"Error:\n{str(e)}")
    
    def mostrar_histograma(self):
        """Muestra el histograma en una ventana nueva"""
        if self.imagen_procesada is None:
            messagebox.showwarning("Advertencia", "Primero abre una imagen")
            return
        
        try:
            # Crear ventana nueva
            ventana_hist = tk.Toplevel(self.root)
            ventana_hist.title("Histograma RGB")
            ventana_hist.geometry("800x400")
            
            # Generar histograma
            img_array = np.array(self.imagen_procesada)
            fig = ProcesadorImagenes.visualizar_histograma(img_array)
            
            # Mostrar en la ventana
            canvas_hist = FigureCanvasTkAgg(fig, master=ventana_hist)
            canvas_hist.draw()
            canvas_hist.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self.actualizar_estado("Histograma mostrado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar histograma:\n{str(e)}")
    
    def fusionar_normal(self):
        """Fusiona dos imágenes normales"""
        if self.imagen_original is None or self.imagen_segunda is None:
            messagebox.showwarning("Advertencia", 
                                 "Necesitas abrir dos imágenes para fusionar")
            return
        
        try:
            alpha = self.var_alpha_fusion.get()
            img1_array = np.array(self.imagen_procesada)
            img2_array = np.array(self.imagen_segunda)
            
            img_fusion = ProcesadorImagenes.fusionar_imagenes(img1_array, img2_array, alpha)

            self.imagen_procesada = Image.fromarray(img_fusion)
            self.mostrar_imagen()
            self.actualizar_estado(f"Fusión normal aplicada (alpha={alpha})")
        except Exception as e:
            messagebox.showerror("Error", f"Error al fusionar:\n{str(e)}")
    
    def fusionar_ecualizadas(self):
        """Fusiona dos imágenes ecualizadas"""
        if self.imagen_original is None or self.imagen_segunda is None:
            messagebox.showwarning("Advertencia", 
                                 "Necesitas abrir dos imágenes para fusionar")
            return
        
        try:
            alpha = self.var_alpha_fusion.get()
            img1_array = np.array(self.imagen_procesada)
            img2_array = np.array(self.imagen_segunda)
            
            img_fusion = ProcesadorImagenes.fusionar_ecualizadas(img1_array, img2_array, alpha)
            self.imagen_procesada = Image.fromarray(img_fusion)
            self.mostrar_imagen()
            self.actualizar_estado(f"Fusión ecualizada aplicada (alpha={alpha})")
        except Exception as e:
            messagebox.showerror("Error", f"Error al fusionar:\n{str(e)}")
    
    def extraer_canal_rgb(self, canal):
        """Extrae un canal RGB específico"""
        if self.imagen_original is None:
            messagebox.showwarning("Advertencia", "Primero abre una imagen")
            return
        
        try:
            img_array = np.array(self.imagen_procesada)
            img_r, img_g, img_b = ProcesadorImagenes.extraer_rgb(img_array)
            
            if canal == 'R':
                self.imagen_procesada = Image.fromarray(img_r)
            elif canal == 'G':
                self.imagen_procesada = Image.fromarray(img_g)
            elif canal == 'B':
                self.imagen_procesada = Image.fromarray(img_b)
            
            self.mostrar_imagen()
            self.actualizar_estado(f"Canal {canal} extraído")
        except Exception as e:
            messagebox.showerror("Error", f"Error:\n{str(e)}")
    
    def extraer_canal_cmyk(self, canal):
        """Extrae un canal CMYK específico"""
        if self.imagen_original is None:
            messagebox.showwarning("Advertencia", "Primero abre una imagen")
            return
        
        try:
            img_array = np.array(self.imagen_procesada)
            C, M, Y, K = ProcesadorImagenes.extraer_cmyk(img_array)
            
            # Convertir a imagen visualizable (3 canales)
            if canal == 'C':
                img_display = cv2.cvtColor(C, cv2.COLOR_GRAY2RGB)
            elif canal == 'M':
                img_display = cv2.cvtColor(M, cv2.COLOR_GRAY2RGB)
            elif canal == 'Y':
                img_display = cv2.cvtColor(Y, cv2.COLOR_GRAY2RGB)
            elif canal == 'K':
                img_display = cv2.cvtColor(K, cv2.COLOR_GRAY2RGB)
            
            self.imagen_procesada = Image.fromarray(img_display)
            self.mostrar_imagen()
            self.actualizar_estado(f"Canal CMYK {canal} extraído")
        except Exception as e:
            messagebox.showerror("Error", f"Error:\n{str(e)}")
    
    def aplicar_negativo(self):
        """Aplica foto negativa"""
        if self.imagen_original is None:
            messagebox.showwarning("Advertencia", "Primero abre una imagen")
            return
        
        try:
            img_array = np.array(self.imagen_procesada)
            img_negativa = ProcesadorImagenes.foto_negativa(img_array)
            self.imagen_procesada = Image.fromarray(img_negativa)
            self.mostrar_imagen()
            self.actualizar_estado("Negativo aplicado")
        except Exception as e:
            messagebox.showerror("Error", f"Error:\n{str(e)}")
    
    def convertir_grises(self):
        """Convierte a escala de grises"""
        if self.imagen_original is None:
            messagebox.showwarning("Advertencia", "Primero abre una imagen")
            return
        
        try:
            img_array = np.array(self.imagen_procesada)
            img_gris = ProcesadorImagenes.convertir_grises(img_array)
            self.imagen_procesada = Image.fromarray(img_gris)
            self.mostrar_imagen()
            self.actualizar_estado("Convertido a escala de grises")
        except Exception as e:
            messagebox.showerror("Error", f"Error:\n{str(e)}")
    
    def binarizar_imagen(self):
        """Binariza la imagen"""
        if self.imagen_original is None:
            messagebox.showwarning("Advertencia", "Primero abre una imagen")
            return
        
        try:
            umbral = self.var_umbral.get()
            img_array = np.array(self.imagen_procesada)
            img_binaria = ProcesadorImagenes.binarizar(img_array, umbral)
            self.imagen_procesada = Image.fromarray(img_binaria)
            self.mostrar_imagen()
            self.actualizar_estado(f"Binarización aplicada (umbral={umbral})")
        except Exception as e:
            messagebox.showerror("Error", f"Error:\n{str(e)}")
    
    # ============================================
    # MÉTODOS DE UTILIDAD
    # ============================================
    
    def restaurar_original(self):
        """Restaura la imagen original"""
        if self.imagen_original is None:
            messagebox.showwarning("Advertencia", "No hay imagen original")
            return
        
        self.imagen_procesada = self.imagen_original.copy()
        self.resetear_controles()
        self.mostrar_imagen()
        self.actualizar_estado("Imagen original restaurada")
    
    def resetear_controles(self):
        """Resetea todos los controles a sus valores por defecto"""
        self.var_brillo_global.set(0)
        self.var_brillo_r.set(0)
        self.var_brillo_g.set(0)
        self.var_brillo_b.set(0)
        self.var_gamma.set(1.0)
        self.var_c_log.set(1.0)
        self.var_umbral.set(127)
        self.var_alpha_fusion.set(0.5)
        self.var_angulo_rotacion.set(0)
    
    def mostrar_acerca_de(self):
        """Muestra información sobre la aplicación"""
        mensaje = """
        PROCESADOR DE IMÁGENES
        Versión 1.0
        
        Proyecto Final de Procesamiento de Imágenes
        
        Funcionalidades:
        ✓ 15 transformaciones de imagen
        ✓ Ajuste de brillo y contraste
        ✓ Transformaciones geométricas
        ✓ Análisis de histogramas
        ✓ Fusión de imágenes
        ✓ Extracción de capas RGB/CMYK
        ✓ Conversiones de color
        
        Desarrollado con:
        • Python 3
        • Tkinter
        • NumPy
        • OpenCV
        • Pillow
        • Matplotlib
        """
        messagebox.showinfo("Acerca de", mensaje)


# ============================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================

def main():
    """
    Función principal que inicia la aplicación
    """
    print("=" * 50)
    print("PROCESADOR DE IMÁGENES - Iniciando...")
    print("=" * 50)
    
    # Crear ventana principal
    root = tk.Tk()
    
    # Crear aplicación
    app = AplicacionProcesamiento(root)
    
    # Iniciar loop de eventos
    print("✅ Interfaz creada correctamente")
    print("💡 Usa Archivo → Abrir imagen para comenzar")
    root.mainloop()


if __name__ == "__main__":
    main()