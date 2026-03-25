import requests
import json
import folium

# Настройки запроса
url = "https://new.pollen.club/ajax/get_pollen_data"
params = {
    "url": "https://test.pollen.club/maps/ddr_query.php",
    "method": "indexStat",
    "params[type]": "5",
    "params[fromd]": "2026-03-25",
    "params[fromt]": "0"
}

# Твои координаты для центра карты
my_coords = [55.7160, 37.6606]

# Функция для выбора цвета в зависимости от уровня пыльцы
def get_color(value):
    val = int(value)
    if val <= 1: return 'green'   # Низкий
    if val == 2: return 'yellow'  # Средний
    if val == 3: return 'orange'  # Высокий
    if val >= 4: return 'red'     # Очень высокий
    return 'gray'

response = requests.get(url, params=params)
outer_response = response.json()

if outer_response.get("success"):
    inner_data = json.loads(outer_response["data"])

    # Создаем карту, центрированную на тебе
    m = folium.Map(location=my_coords, zoom_start=8, tiles='OpenStreetMap')

    # Добавляем маркер твоего местоположения
    folium.Marker(
        my_coords, 
        popup="Я здесь", 
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)

    # Добавляем точки пыльцы
    for r in inner_data:
        lat, lon = float(r['latitude']), float(r['longitude'])
        value = r['value']
        
        # Рисуем круги (CircleMarker) — они нагляднее для интенсивности
        folium.CircleMarker(
            location=[lat, lon],
            radius=10, # Размер круга
            popup=f"Уровень: {value}<br>Дата: {r['date']}",
            color=get_color(value),
            fill=True,
            fill_color=get_color(value),
            fill_opacity=0.6
        ).add_to(m)

    # Сохраняем в файл
    filename = "pollen_map.html"
    m.save(filename)
    print(f"Карта создана и сохранена в файл {filename}. Просто открой его в браузере.")
else:
    print("Ошибка получения данных")