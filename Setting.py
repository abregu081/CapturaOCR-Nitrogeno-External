import os
import Setting
import sys

class Setting:
 def __init__(self):
    self.path = None
 
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
  