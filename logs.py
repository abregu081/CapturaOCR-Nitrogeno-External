import os
from datetime import datetime

class GuardarLog:
    def __init__(self, ruta_logs):
        self.nombre_archivo = "Valores_Caputurados.txt"
        self.ruta_logs = ruta_logs
        if not os.path.exists(ruta_logs):
            os.makedirs(ruta_logs)
        self.carpeta_fecha = os.path.join(ruta_logs, datetime.now().strftime("%Y-%m-%d"))
        if not os.path.exists(self.carpeta_fecha):
            os.makedirs(self.carpeta_fecha)
        self.carpeta_hora = os.path.join(self.carpeta_fecha, datetime.now().strftime("%H-%M-%S"))
        if not os.path.exists(self.carpeta_hora):
            os.makedirs(self.carpeta_hora)
        self.carpeta_recortes = os.path.join(self.carpeta_hora, "Recortes")
        if not os.path.exists(self.carpeta_recortes):
            os.makedirs(self.carpeta_recortes)
        self.carpeta_imagen = os.path.join(self.carpeta_hora, "Imagene")
        if not os.path.exists(self.carpeta_imagen):
            os.makedirs(self.carpeta_imagen)
            
    def escribir_log(self, mensaje):
        ruta_completa = os.path.join(self.carpeta_hora, self.nombre_archivo)
        with open(ruta_completa, "a") as archivo_log:
            archivo_log.write(f"{mensaje}")
    
    def guardar_imagen_principal(self, imagen, nombre_archivo):
        """
        Guarda imagen usando cv2 (numpy array)
        imagen: numpy array de OpenCV
        nombre_archivo: nombre del archivo (ej: 'captura.jpg')
        """
        import cv2
        ruta_imagen = os.path.join(self.carpeta_imagen, nombre_archivo)
        cv2.imwrite(ruta_imagen, imagen)
        return ruta_imagen
    
    def guardar_recortes(self, imagenes_recortes):
        """
        Guarda múltiples recortes usando cv2
        imagenes_recortes: lista de numpy arrays de OpenCV
        """
        import cv2
        for indice, imagen in enumerate(imagenes_recortes):
            nombre_archivo = f"recorte_{indice + 1}.jpg"
            ruta_recorte = os.path.join(self.carpeta_recortes, nombre_archivo)
            cv2.imwrite(ruta_recorte, imagen)

