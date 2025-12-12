import os
import Setting
import sys

class Setting:
 def __init__(self):
    self.path = None
    self.path_logs = None
 
 @staticmethod
 def Capturar_datos_txt(Archivo):
   try:
      script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
      ruta_archivo = os.path.join(script_dir, Archivo)
      print(ruta_archivo)
      with open(ruta_archivo, 'r') as archivo:
          archivo_txt = archivo.readlines()
          archivo_txt = [linea.strip() for linea in archivo_txt]
      return archivo_txt
   except Exception as error1:
            print(str(error1))

 @staticmethod
 def obtener_path_log_de_archivo_ini():
    try:
       archivo_txt= Setting.Capturar_datos_txt("Setting.ini")
       dict_valores = Setting.Crear_tupla_Setting(archivo_txt)
       return dict_valores["path_logs"]
    except Exception as ErrorPath:
       print(str(ErrorPath))
      
 @staticmethod
 def obtener_url_de_archivo_ini():
    try:
       archivo_txt= Setting.Capturar_datos_txt("Setting.ini")
       dict_valores = Setting.Crear_tupla_Setting(archivo_txt)
       return dict_valores["url"]
    except Exception as ErrorPath:
       print(str(ErrorPath))

 @staticmethod
 def obtener_path_de_archivo_ini():
    try:
       archivo_txt= Setting.Capturar_datos_txt("Setting.ini")
       dict_valores = Setting.Crear_tupla_Setting(archivo_txt)
       return dict_valores["path"]
    except Exception as ErrorPath:
       print(str(ErrorPath))
       return ""

 @staticmethod
 def obtener_credenciales():
    """Obtiene usuario y contraseña del archivo Setting.ini"""
    try:
       archivo_txt = Setting.Capturar_datos_txt("Setting.ini")
       dict_valores = Setting.Crear_tupla_Setting(archivo_txt)
       usuario = dict_valores.get("usuario", "")
       password = dict_valores.get("password", "")
       return usuario, password
    except Exception as error:
       print(f"Error obteniendo credenciales: {error}")
       return "", ""

 @staticmethod
 def obtener_regiones_segmentos():
    """Obtiene las regiones de los 7 segmentos del archivo Setting.ini"""
    try:
       archivo_txt = Setting.Capturar_datos_txt("Setting.ini")
       dict_valores = Setting.Crear_tupla_Setting(archivo_txt)
       
       segmentos = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
       regs = []
       
       for seg in segmentos:
          key = f"segment_{seg}"
          if key in dict_valores:
             valores = dict_valores[key].split(',')
             if len(valores) == 4:
                x, y, w, h = map(int, valores)
                regs.append((x, y, w, h))
          else:
             # Valores por defecto si no están en el archivo
             defaults = {
                'a': (12, 5, 8, 7),
                'b': (23, 18, 5, 8),
                'c': (21, 42, 5, 8),
                'd': (11, 53, 8, 7),
                'e': (3, 41, 5, 8),
                'f': (3, 17, 5, 8),
                'g': (12, 28, 10, 8)
             }
             regs.append(defaults[seg])
       
       return regs
    except Exception as error:
       print(f"Error obteniendo regiones de segmentos: {error}")
       # Valores por defecto en caso de error
       return [
          (12, 5, 8, 7),    # a
          (23, 18, 5, 8),   # b
          (21, 42, 5, 8),   # c
          (11, 53, 8, 7),   # d
          (3, 41, 5, 8),    # e
          (3, 17, 5, 8),    # f
          (12, 28, 10, 8)   # g
       ]

 @staticmethod
 def obtener_coordenadas_digitos():
    """Obtiene las coordenadas de los dígitos OCR del archivo Setting.ini"""
    try:
       archivo_txt = Setting.Capturar_datos_txt("Setting.ini")
       dict_valores = Setting.Crear_tupla_Setting(archivo_txt)
       
       coordenadas = []
       # Buscar hasta 10 dígitos (digit_1 a digit_10)
       for i in range(1, 11):
          key = f"digit_{i}"
          if key in dict_valores:
             valores = dict_valores[key].split(',')
             if len(valores) == 4:
                x, y, w, h = map(int, valores)
                coordenadas.append([x, y, w, h])
          else:
             # Si no hay más dígitos configurados, terminar
             break
       
       # Si no se encontró ninguno, usar valores por defecto
       if len(coordenadas) == 0:
          coordenadas = [
             [1057, 115, 30, 60],
             [1094, 114, 30, 60],
             [1134, 113, 30, 60],
             [1024, 187, 30, 60],
             [1059, 183, 30, 60],
             [1100, 204, 22, 38]
          ]
       
       return coordenadas
    except Exception as error:
       print(f"Error obteniendo coordenadas de dígitos: {error}")
       # Valores por defecto en caso de error
       return [
          [1057, 115, 30, 60],
          [1094, 114, 30, 60],
          [1134, 113, 30, 60],
          [1024, 187, 30, 60],
          [1059, 183, 30, 60],
          [1100, 204, 22, 38]
       ]
 
 #Metodo para crear una tupla de datos obtenida del archivo Setting.ini
 @staticmethod
 def Crear_tupla_Setting(valores_txt):
      try:
         dict_valores = {}
         for valor_txt in valores_txt:
               # Ignora líneas vacías y comentarios
               if not valor_txt or valor_txt.startswith(";") or valor_txt.startswith("//"):
                  continue
               if "=" in valor_txt:
                  clave, valor = valor_txt.split("=", 1)
                  dict_valores[clave.strip()] = valor.strip()
         return dict_valores
      except Exception as error1:
         print(str(error1))
         return {}
  