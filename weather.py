import requests
import pandas as pd

# ===== НАСТРОЙКИ =====
CITY = "Novosibirsk"
LAT = None
LON = None
START_DATE = "2026-03-01"
END_DATE = "2026-05-31"
OUTPUT_FILE = "weather_data_new.csv"

# Параметры API Open-Meteo
BASE_URL = "https://archive-api.open-meteo.com/v1/archive"
PARAMS = {
    "latitude": LAT,
    "longitude": LON,
    "start_date": START_DATE,
    "end_date": END_DATE,
    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "precipitation_sum",
        "rain_sum",
        "snowfall_sum",
        "wind_speed_10m_max",
        "wind_gusts_10m_max",
        "wind_direction_10m_dominant"
    ],
    "timezone": "auto"
}

def get_coordinates(city_name):
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    resp = requests.get(geo_url, params={"name": city_name, "count": 1})
    if resp.status_code == 200:
        data = resp.json()
        if data.get("results"):
            lat = data["results"][0]["latitude"]
            lon = data["results"][0]["longitude"]
            return lat, lon
    return None, None


def fetch_weather_data(lat, lon, start_date, end_date):
    params = PARAMS.copy()
    params["latitude"] = lat
    params["longitude"] = lon
    params["start_date"] = start_date
    params["end_date"] = end_date

    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        print(f"Ошибка API: {response.status_code}")
        print(response.text)
        return None

    return response.json()


def process_data(raw_data):
    if not raw_data or "daily" not in raw_data:
        return None

    daily = raw_data["daily"]
    df = pd.DataFrame(daily)

    column_mapping = {
        "time": "Дата",
        "temperature_2m_max": "Макс. температура (°C)",
        "temperature_2m_min": "Мин. температура (°C)",
        "temperature_2m_mean": "Средняя температура (°C)",
        "precipitation_sum": "Осадки (мм)",
        "rain_sum": "Дождь (мм)",
        "snowfall_sum": "Снег (см)",
        "wind_speed_10m_max": "Макс. скорость ветра (км/ч)",
        "wind_gusts_10m_max": "Макс. порывы ветра (км/ч)",
        "wind_direction_10m_dominant": "Направление ветра (°)"
    }
    df = df.rename(columns=column_mapping)

    df["Город"] = CITY

    df["Дата"] = pd.to_datetime(df["Дата"])

    return df


def main():
    global LAT, LON

    # Если координаты не заданы, тогда пробуем получить по названию города
    if LAT is None or LON is None:
        lat, lon = get_coordinates(CITY)
        if lat is None:
            print(f"Город '{CITY}' не найден")
            return
        LAT, LON = lat, lon

    print(f"Сбор данных для {CITY} ({LAT}, {LON})")
    print(f"Период: с {START_DATE} по {END_DATE}")

    raw_data = fetch_weather_data(LAT, LON, START_DATE, END_DATE)
    if raw_data is None:
        return

    df = process_data(raw_data)
    if df is None or df.empty:
        print("Данные не получены")
        return

    # Сохраняем в CSV
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"Данные сохранены в {OUTPUT_FILE}")
    print(f"Всего записей: {len(df)}")
    print()
    print(df.head(3))
    print(df.tail(3))


if __name__ == "__main__":
    main()