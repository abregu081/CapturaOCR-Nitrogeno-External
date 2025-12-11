"""
Módulo de integración con Home Assistant
Permite enviar datos de sensores (N2% y Presión) a Home Assistant via API REST
"""

import requests
import json
from datetime import datetime
import Setting as ST


class HomeAssistantAPI:
    """Clase para comunicarse con Home Assistant via API REST"""
    
    def __init__(self, url=None, token=None):
        """
        Inicializa la conexión con Home Assistant
        
        Args:
            url: URL de Home Assistant (ej: http://192.168.1.100:8123)
            token: Token de acceso de larga duración
        """
        if url and token:
            self.url = url.rstrip('/')
            self.token = token
        else:
            self.url, self.token = self._cargar_config()
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def _cargar_config(self):
        """Carga la configuración de Home Assistant desde Setting.ini"""
        try:
            archivo_txt = ST.Setting.Capturar_datos_txt("Setting.ini")
            dict_valores = ST.Setting.Crear_tupla_Setting(archivo_txt)
            url = dict_valores.get("ha_url", "").strip()
            token = dict_valores.get("ha_token", "").strip()
            return url, token
        except Exception as e:
            print(f"Error cargando config de Home Assistant: {e}")
            return "", ""
    
    def verificar_conexion(self):
        """Verifica si la conexión con Home Assistant está funcionando"""
        try:
            response = requests.get(
                f"{self.url}/api/",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                print("Conexion con Home Assistant exitosa")
                return True
            else:
                print(f"Error de conexion: HTTP {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"No se puede conectar a {self.url}")
            return False
        except Exception as e:
            print(f"Error verificando conexion: {e}")
            return False
    
    def actualizar_sensor(self, entity_id, estado, atributos=None):
        """Actualiza o crea un sensor en Home Assistant"""
        try:
            payload = {
                "state": estado,
                "attributes": atributos or {}
            }
            
            response = requests.post(
                f"{self.url}/api/states/{entity_id}",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"Sensor '{entity_id}' actualizado: {estado}")
                return True
            else:
                print(f"Error actualizando sensor: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error enviando datos: {e}")
            return False
    
    def enviar_datos_n2(self, valor_n2):
        """Envía el valor de N2% a Home Assistant"""
        atributos = {
            "unit_of_measurement": "%",
            "friendly_name": "Nitrogeno (N2)",
            "icon": "mdi:molecule",
            "ultima_lectura": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return self.actualizar_sensor("sensor.n2_porcentaje", valor_n2, atributos)
    
    def enviar_datos_presion(self, valor_presion):
        """Envía el valor de presión a Home Assistant"""
        atributos = {
            "unit_of_measurement": "bar",
            "friendly_name": "Presion",
            "icon": "mdi:gauge",
            "ultima_lectura": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return self.actualizar_sensor("sensor.presion_bar", valor_presion, atributos)
    
    def enviar_todos_los_datos(self, valor_n2, valor_presion, conf_n2=None, conf_presion=None):
        """Envía todos los datos de una sola vez"""
        exito_n2 = self.enviar_datos_n2(valor_n2)
        exito_presion = self.enviar_datos_presion(valor_presion)
        return exito_n2, exito_presion


def enviar_a_homeassistant(valor_n2, valor_presion):
    """
    Función rápida para enviar datos a Home Assistant
    
    Returns:
        bool: True si ambos datos se enviaron correctamente
    """
    try:
        ha = HomeAssistantAPI()
        if not ha.url or not ha.token:
            print("Configuracion de Home Assistant no encontrada en Setting.ini")
            return False
        
        exito_n2, exito_presion = ha.enviar_todos_los_datos(
            valor_n2, valor_presion
        )
        return exito_n2 and exito_presion
    except Exception as e:
        print(f"Error enviando a Home Assistant: {e}")
        return False


if __name__ == "__main__":
    print("=== Test de conexion con Home Assistant ===\n")
    
    ha = HomeAssistantAPI()
    
    if not ha.url or not ha.token:
        print("ERROR: Configura ha_url y ha_token en Setting.ini")
    else:
        print(f"URL: {ha.url}")
        if ha.verificar_conexion():
            print("\n=== Enviando datos de prueba ===")
            ha.enviar_datos_n2(95.5)
            ha.enviar_datos_presion(2.3)
