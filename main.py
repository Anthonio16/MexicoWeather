# main.py - Registro climatologico de Ciudad de Mexico
# Proyecto ICCD332 Arquitectura de Computadores - Grupo 3
#
# Fuentes consultadas:
# - API OpenWeatherMap Current Weather: https://openweathermap.org/current
# - Escritura de CSV con DictWriter: https://docs.python.org/3/library/csv.html#csv.DictWriter
# - Libreria requests: https://requests.readthedocs.io/en/latest/user/quickstart/
# - Aplanar diccionarios anidados: https://stackoverflow.com/questions/6027558/flatten-nested-dictionaries-compressing-keys

import requests
import os
import csv
from datetime import datetime

# Coordenadas de Ciudad de Mexico (CDMX)
# Fuente: https://www.latlong.net/place/mexico-city-df-mexico-1988.html
MEXICO_LAT = 19.4326
MEXICO_LON = -99.1332

# La API key se lee de una variable de entorno para no exponerla en GitHub.
# Fuente: https://docs.python.org/3/library/os.html#os.environ
API_KEY = os.environ.get("OWM_API_KEY", "1487d66062fc8358ef8f6e8752b25400")

FILE_NAME = "clima-mexico-hoy.csv"

# Columnas fijas que cubren TODO el esquema del API de Current Weather,
# incluyendo rain y snow que solo aparecen cuando hay el fenomeno.
# Esto garantiza que el CSV siempre tenga las mismas columnas.
# Esquema documentado en: https://openweathermap.org/current#fields_json
FIELDNAMES = [
    "fecha_consulta",
    "coord_lon", "coord_lat",
    "weather_0_id", "weather_0_main", "weather_0_description", "weather_0_icon",
    "base",
    "main_temp", "main_feels_like", "main_temp_min", "main_temp_max",
    "main_pressure", "main_humidity", "main_sea_level", "main_grnd_level",
    "visibility",
    "wind_speed", "wind_deg", "wind_gust",
    "rain_1h", "rain_3h",
    "snow_1h", "snow_3h",
    "clouds_all",
    "dt",
    "sys_type", "sys_id", "sys_country", "sys_sunrise", "sys_sunset",
    "timezone", "id", "name", "cod",
]


def get_weather(lat, lon, api_key):
    """Consulta el API de OpenWeatherMap y devuelve el JSON como dict.
    Docs: https://openweathermap.org/current"""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
    response = requests.get(url, params=params, timeout=30)
    return response.json()


def flatten(data, parent_key=""):
    """Aplana un diccionario anidado usando '_' como separador.
    Las listas (como 'weather') se aplanan con el indice del elemento.
    Ej: {"main": {"temp": 20}} -> {"main_temp": 20}
    Basado en: https://stackoverflow.com/questions/6027558"""
    items = {}
    for key, value in data.items():
        new_key = f"{parent_key}_{key}" if parent_key else key
        if isinstance(value, dict):
            items.update(flatten(value, new_key))
        elif isinstance(value, list):
            for i, elem in enumerate(value):
                if isinstance(elem, dict):
                    items.update(flatten(elem, f"{new_key}_{i}"))
                else:
                    items[f"{new_key}_{i}"] = elem
        else:
            items[new_key] = value
    return items


def process(json_response):
    """Convierte la respuesta del API en una fila con las columnas fijas.
    Convierte los timestamps unix a fecha legible.
    Docs datetime: https://docs.python.org/3/library/datetime.html"""
    flat = flatten(json_response)

    # Conversion de timestamps unix a formato legible
    for ts_field in ("dt", "sys_sunrise", "sys_sunset"):
        if ts_field in flat and isinstance(flat[ts_field], (int, float)):
            flat[ts_field] = datetime.fromtimestamp(flat[ts_field]).strftime("%Y-%m-%d %H:%M:%S")

    # Fila final: toda columna del esquema, vacia si el API no la envio
    row = {col: flat.get(col, "") for col in FIELDNAMES}
    row["fecha_consulta"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return row


def write2csv(data_dict, csv_filename):
    """Agrega una fila al CSV; escribe el encabezado solo si el archivo no existe.
    Docs: https://docs.python.org/3/library/csv.html#csv.DictWriter"""
    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data_dict)


def main():
    print("===== Mexico-Clima | Grupo 3 ICCD332 =====")
    try:
        mexico_weather = get_weather(MEXICO_LAT, MEXICO_LON, API_KEY)
    except requests.exceptions.RequestException as e:
        # Si falla la red, se registra en output.log via crontab y se sale
        print(f"[ERROR] Fallo de conexion con el API: {e}")
        return

    # El API devuelve cod=200 (entero) en exito y cod="401"/"404" (string) en error
    # Fuente: https://openweathermap.org/faq#error401
    if str(mexico_weather.get("cod")) == "200":
        data = process(mexico_weather)
        write2csv(data, FILE_NAME)
        print(f"[OK] Dato guardado: {data['fecha_consulta']} | "
              f"{data['name']} | temp={data['main_temp']}C | "
              f"{data['weather_0_description']}")
    else:
        print(f"[ERROR] Respuesta del API: {mexico_weather}")


if __name__ == "__main__":
    main()
