# -*- coding: utf-8 -*-
"""
Clasifica un único dígito (7 segmentos) entre 0..9 o ' ' (vacío), con corrección para 8
en imágenes oscuras donde los segmentos laterales (e,f) se ven débiles.
"""
 
import numpy as np
#from PIL import Image
import json
from datetime import datetime
import subprocess
import cv2
import Setting as ST
import os
import sys
import Homeassistan as HA
import logs as LG
 
# Intentar OpenCV; fallback si no estuviese
try:
    import cv2
    OPENCV = True
except Exception:
    OPENCV = False
 
# Máscaras estándar de 7 segmentos (a,b,c,d,e,f,g)
SEGMENTS_FOR_DIGIT = {
    0: [1,1,1,1,1,1,0],
    1: [0,1,1,0,0,0,0],
    2: [1,1,0,1,1,0,1],
    3: [1,1,1,1,0,0,1],
    4: [0,1,1,0,0,1,1],
    5: [1,0,1,1,0,1,1],
    6: [1,0,1,1,1,1,1],
    7: [1,1,1,0,0,0,0],
    8: [1,1,1,1,1,1,1],
    9: [1,1,1,1,0,1,1],
}
 
def preprocess(gray):
  g = cv2.GaussianBlur(gray, (3,3), 0)
  _, th = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
  return th
 
def find_main_bbox(binary):
    """BBox principal (mayor componente)."""
    H, W = binary.shape
    if OPENCV:
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
        best = None
        best_area = 0
        for i in range(1, num_labels):
            x, y, w, h, area = stats[i, 0], stats[i, 1], stats[i, 2], stats[i, 3], stats[i, 4]
            if area > best_area:
                best_area = area
                best = (int(x), int(y), int(w), int(h))
        return best if best is not None else (0, 0, W, H)
    else:
        cols = np.where(np.sum(binary > 0, axis=0) > 0)[0]
        rows = np.where(np.sum(binary > 0, axis=1) > 0)[0]
        if cols.size == 0 or rows.size == 0:
            return (0, 0, W, H)
        x0, x1 = int(cols[0]), int(cols[-1] + 1)
        y0, y1 = int(rows[0]), int(rows[-1] + 1)
        return (x0, y0, x1 - x0, y1 - y0)
 
def sample_segment_probs(binary, bbox, regs):
    """Probabilidades (0..1) de segmentos a..g encendidos dentro del bbox."""
    x, y, w, h = bbox
    # Padding para asegurar cobertura de los trazos
    pad = max(1, int(0.06 * max(w, h)))
    x0 = max(0, x - pad)
    y0 = max(0, y - pad)
    x1 = min(binary.shape[1], x + w + pad)
    y1 = min(binary.shape[0], y + h + pad)
    roi = binary[y0:y1, x0:x1]
    H, W = roi.shape
 
    # Grosor relativo; un pelo más sensible a verticales
    t_h = max(1, int(0.13 * H))
    t_w = max(1, int(0.15 * W))
 
    probs = []
    for rx, ry, rw, rh in regs:
        sub = roi[ry:ry+rh, rx:rx+rw]
        if sub.size == 0:
            probs.append(0.0)
        else:
            on_ratio = np.sum(sub > 0) / sub.size
            # Logística: más agresiva para discriminar ON en zonas oscuras
            k = 14.0
            probs.append(1.0 / (1.0 + np.exp(-k * (on_ratio - 0.5))))
    return probs
 
#def classify_single_digit(image_path, force_eight_fix=True):
def classify_single_digit(gray, regs, force_eight_fix=True):
    """
    Devuelve:
      {
        'text': '0..9 | ' ',
        'probs': {'0':%,..., '9':%, ' ':%},
        'best': ('clase', %),
        'bbox': {'x','y','w','h'},
        'segments': {'a':p,...,'g':p}  # probs 0..1 por segmento
      }
    """
    binary = preprocess(gray)
    #bbox = find_main_bbox(binary)
    bbox = (3,3,30,60)
    segp = sample_segment_probs(binary, bbox, regs)
#    cv2.imshow("Escala_grises", binary)
#    cv2.waitKey(0)
    classes = [str(d) for d in range(10)] + [' ']
    probs = {c: 0.0 for c in classes}
    eps = 1e-6
 
    # Scores por dígito (producto de ON/OFF)
    for d in range(10):
        mask = SEGMENTS_FOR_DIGIT[d]
        logsum = 0.0
        for p, m in zip(segp, mask):
            logsum += np.log(max(p, eps)) if m == 1 else np.log(max(1.0 - p, eps))
        probs[str(d)] = float(np.exp(logsum))
 
    # Vacío: todos OFF
    p_off = 1.0
    for p in segp:
        p_off *= max(1.0 - p, eps)
    probs[' '] = float(p_off)
 
    # --- Corrección para 8 en escenas oscuras ---
    # Si el top sale 3 o 2, pero TODOS los segmentos tienen activación moderada,
    # aplicamos un prior hacia 8 y renormalizamos.
    if force_eight_fix:
        best_cls = max(probs.items(), key=lambda kv: kv[1])[0]
        # condición de "todos moderadamente ON"
        all_moderate_on = sum(1 for p in segp if p > 0.40) >= 6 and min(segp) > 0.30
        if best_cls in ('3', '2') and all_moderate_on:
            # prior hacia 8 (multiplicador)
            probs['8'] *= 5.0
            # leve penalización a 3/2
            probs['3'] *= 0.7
            probs['2'] *= 0.7
 
    # Normalización a %
    total = float(sum(probs.values()))
    if total <= 1e-12:
        probs[' '] = 1.0
        total = 1.0
    for k in list(probs.keys()):
        probs[k] = 100.0 * probs[k] / total
 
    best_cls, best_pct = max(probs.items(), key=lambda kv: kv[1])
    return {
        'text': best_cls,
        'probs': probs,
        'best': (best_cls, best_pct),
        'bbox': {'x': int(bbox[0]), 'y': int(bbox[1]), 'w': int(bbox[2]), 'h': int(bbox[3])},
        'segments': dict(zip(list('abcdefg'), [float(p) for p in segp]))
    }
ahora = str(datetime.now().strftime("%Y%m%d_%H%M%S"))
dias_antiguedad_para_borrar = 4

# Verificar si se debe guardar imágenes binarizadas
guardar_binarias = len(sys.argv) > 1 and sys.argv[1].lower() == 'bin'
if guardar_binarias:
    print("Modo BIN activado: Se guardarán las imágenes binarizadas")

ha = HA.HomeAssistantAPI()
usuario, contraseña = ST.Setting.obtener_credenciales()
url = ST.Setting.obtener_url_de_archivo_ini()
comando=f'curl -u {usuario}:{contraseña} --digest "{url}" -o imagen_camara' + '.jpg --silent --show-error --max-time 10'
print(comando)
resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)

# Verificar si el comando curl falló
if resultado.returncode != 0:
    print(f"Error al ejecutar curl. Código de error: {resultado.returncode}")
    print(f"Error: {resultado.stderr}")
    
    # Crear archivo de error indicando falta de conexión
    archivo_error = "sin_conexion.txt"
    ahora_error = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(archivo_error, "w") as f:
        f.write(f"{ahora_error} - Error de conexión\n")
        f.write(f"No se pudo descargar la imagen de la cámara\n")
        f.write(f"Código de error: {resultado.returncode}\n")
        f.write(f"Detalle: {resultado.stderr}\n")
    
    print(f"Archivo '{archivo_error}' creado. Saliendo sin procesar imágenes antiguas.")
    exit(1)

pathfile = ST.Setting.obtener_path_de_archivo_ini()
path_log = ST.Setting.obtener_path_log_de_archivo_ini()
logs = LG.GuardarLog(path_log)
regiones_segmentos = ST.Setting.obtener_regiones_segmentos()
coordenadas_digitos = ST.Setting.obtener_coordenadas_digitos()
imgfile = "imagen_camara"
codigo = []
imgTotally = cv2.imread(pathfile +imgfile + ".jpg", cv2.IMREAD_GRAYSCALE)
carpeta_imagenes_recortes = logs.carpeta_recortes


print(pathfile + imgfile + ".jpg")
# Verificar que la imagen se cargó correctamente
if imgTotally is None:
    print("Error: No se pudo cargar la imagen. Verifica la ruta del archivo.")
    exit(1)
# Mostrar dimensiones de la imagen
print(f"Dimensiones de la imagen: {imgTotally.shape}")
guardar_imagen_completa = logs.guardar_imagen_principal(imgTotally, imgfile + ".jpg")
roi = imgTotally[100:270,1000:1200]
if roi.size > 0:
    print(f"Dimensiones del ROI: {roi.shape}")
    #cv2.imshow("Escala_grises", roi)
    #cv2.waitKey(0)
else:
    print("Advertencia: El ROI está vacío. Verifica las coordenadas del slice.")
 
for indice, sizenum in enumerate(coordenadas_digitos):
  crop = imgTotally[sizenum[1]:sizenum[1]+sizenum[3],sizenum[0]:sizenum[0]+sizenum[2]]
  img = cv2.resize(crop, (30, 60), interpolation=cv2.INTER_AREA)
  cv2.imwrite(os.path.join(carpeta_imagenes_recortes, f'imagen_recortada_{indice+1}_.jpg'), img)
  
  # Guardar imagen binarizada si está en modo BIN
  if guardar_binarias:
    img_binaria = preprocess(img)
    cv2.imwrite(os.path.join(carpeta_imagenes_recortes, f'imagen_Bin_{indice+1}_.jpg'), img_binaria)
  
  result = classify_single_digit(img, regiones_segmentos)
  guardar_resultado_log_file = logs.escribir_log(f"Imagen recortada {indice+1}: {json.dumps(result, ensure_ascii=False)}\n")
  print(imgfile, json.dumps(result, ensure_ascii=False, indent=2))
  codigo.append(result['text'])


print("--------------------------------------------------------")
print("Disponible: ",codigo[0]+codigo[1]+"." + codigo[2] + " %")
print("Presion: ",codigo[3]+codigo[4]+"." + codigo[5] + " bar")
print("--------------------------------------------------------")
print("Enviando datos a Home Assistant...")
if not ha.url or not ha.token:
    print("Configuracion de Home Assistant no encontrada en Setting.ini")
else:
    porcentaje_n2 = float(codigo[0]+codigo[1]+"." + codigo[2])
    presion_bar = float(codigo[3]+codigo[4]+"." + codigo[5])
    enviar_porcentaje = ha.enviar_datos_n2(porcentaje_n2)
    enviar_presion = ha.enviar_datos_presion(presion_bar)
    if enviar_porcentaje and enviar_presion:
        print("Datos enviados correctamente a Home Assistant.")
    else:
        print("Error al enviar datos a Home Assistant.")

# Leer registros existentes y filtrar los últimos 2 días
registros_validos = []
archivo_calculado = "Calculado.txt"
dias_a_mantener = 2

if os.path.exists(archivo_calculado):
    try:
        with open(archivo_calculado, "r") as archivo:
            for linea in archivo:
                # Extraer la fecha del registro (formato: YYYYMMDD_HHMMSS)
                if linea.strip() and " - " in linea:
                    try:
                        fecha_str = linea.split(" - ")[0].strip()
                        fecha_registro = datetime.strptime(fecha_str, "%Y%m%d_%H%M%S")
                        diferencia = (datetime.now() - fecha_registro).days
                        if diferencia < dias_a_mantener:
                            registros_validos.append(linea)
                    except ValueError:
                        # Si no se puede parsear la fecha, mantener el registro
                        registros_validos.append(linea)
    except Exception as e:
        print(f"Error leyendo Calculado.txt: {e}")

# Agregar el nuevo registro
nuevo_registro = ahora + " - " "Disponible: " + codigo[0]+codigo[1]+"." + codigo[2] + " % - " + "Presion: " + codigo[3]+codigo[4]+"." + codigo[5] + " bar\n"
registros_validos.append(nuevo_registro)

# Reescribir el archivo solo con los registros válidos
with open(archivo_calculado, "w") as archivo:
    archivo.writelines(registros_validos)

print(f"Registro guardado en {archivo_calculado} (últimos {dias_a_mantener} días)")

# Limpiar archivos antiguos
archivos_eliminados = 0
for archivos in os.listdir(carpeta_imagenes_recortes):
    ruta_completa = os.path.join(carpeta_imagenes_recortes, archivos)
    if os.path.isfile(ruta_completa):
        fecha_modificacion = os.path.getmtime(ruta_completa)
        fecha_modificacion_dt = datetime.fromtimestamp(fecha_modificacion)
        diferencia_dias = (datetime.now() - fecha_modificacion_dt).days
        if diferencia_dias >= dias_antiguedad_para_borrar:
            os.remove(ruta_completa)
            archivos_eliminados += 1
            print(f"  - Eliminado: {archivos} (antigüedad: {diferencia_dias} días)")

if archivos_eliminados > 0:
    print(f"Se eliminaron {archivos_eliminados} archivos con más de {dias_antiguedad_para_borrar} días.")
else:
    print(f"No hay archivos con más de {dias_antiguedad_para_borrar} días para eliminar.")