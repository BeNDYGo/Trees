from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import requests
import json
import math
import uvicorn
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

# ==========================================
# 1. ГЛОБАЛЬНОЕ ХРАНИЛИЩЕ (КЭШ)
# ==========================================
# Здесь мы будем хранить скачанные данные. 
# Ключ - индекс аллергена (0-7), Значение - список кортежей (lat, lon, value)
POLLEN_CACHE = {i:[] for i in range(8)}
LAST_UPDATED = "Никогда"

dataTrees =["Берёза", "Дуб", "Ольха", "Полынь", "Орешник", "Злаки", "Маревые", "Амброзия"]
BASE_URL = "https://new.pollen.club/ajax/get_pollen_data"

# ==========================================
# 2. МАТЕМАТИКА (Дистанция)
# ==========================================
def get_distance_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ==========================================
# 3. ФОНОВЫЙ ЗАГРУЗЧИК ДАННЫХ
# ==========================================
def fetch_all_data_sync():
    """Синхронно скачивает всю базу и обновляет кэш"""
    global POLLEN_CACHE, LAST_UPDATED
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Начинаю скачивание базы данных Pollen Club...")
    date_from = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    
    new_cache = {}
    
    for i in range(8):
        queryParams = {
            "url": "https://test.pollen.club/maps/ddr_query.php",
            "method": "indexStat",
            "params[type]": i + 1,
            "params[fromd]": date_from,
            "params[fromt]": "0"
        }
        
        try:
            response = requests.get(BASE_URL, params=queryParams, timeout=10)
            data_json = response.json()
            
            parsed_points =[]
            if data_json.get("success"):
                inner_data = json.loads(data_json["data"])
                # Сразу переводим строки в числа, чтобы не тратить на это время при запросе от юзера!
                for r in inner_data:
                    parsed_points.append((float(r['latitude']), float(r['longitude']), int(r['value'])))
            
            new_cache[i] = parsed_points
            print(f" -> {dataTrees[i]} загружено: {len(parsed_points)} точек")
            
        except Exception as e:
            print(f" -> Ошибка загрузки {dataTrees[i]}: {e}")
            # Если произошла ошибка, оставляем старые данные из кэша
            new_cache[i] = POLLEN_CACHE.get(i,[])

    # Подменяем старый кэш новым
    POLLEN_CACHE.clear()
    POLLEN_CACHE.update(new_cache)
    LAST_UPDATED = datetime.now().strftime('%H:%M:%S')
    print(f"База успешно обновлена в {LAST_UPDATED}")

async def update_daemon():
    """Бесконечный цикл, который просыпается раз в час"""
    while True:
        # Засыпаем на 3600 секунд (1 час)
        await asyncio.sleep(3600)
        # Запускаем тяжелое скачивание в отдельном потоке, чтобы сервер не зависал
        await asyncio.to_thread(fetch_all_data_sync)


# ==========================================
# 4. ЖИЗНЕННЫЙ ЦИКЛ СЕРВЕРА
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код, который выполняется при старте сервера
    print("Запуск сервера...")
    # Сначала скачиваем базу один раз СРАЗУ, чтобы первым юзерам не отдавало нули
    fetch_all_data_sync()
    # Запускаем фоновый таймер на будущее
    task = asyncio.create_task(update_daemon())
    yield
    # Код, который выполняется при выключении сервера
    task.cancel()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 5. АПИ ДЛЯ МОБИЛЬНОГО ПРИЛОЖЕНИЯ
# ==========================================
@app.get("/homeView")
async def get_home_data(lat: float = 55.75, lon: float = 37.61):
    allergens_result =[]
    total_activity = 0
    
    # Пробегаемся по нашему КЭШУ (это происходит в оперативной памяти за доли миллисекунды)
    for i in range(8):
        points = POLLEN_CACHE.get(i,[])
        
        total_val = 0
        valid_count = 0
        
        # Ищем точки в радиусе 50 км от пользователя
        for p_lat, p_lon, p_value in points:
            if get_distance_km(p_lat, p_lon, lat, lon) <= 50.0:
                total_val += p_value
                valid_count += 1
                
        # Переводим 3-балльную систему в 10-балльную
        if valid_count > 0:
            avg_3_scale = total_val / valid_count
            val_10_scale = int(round((avg_3_scale / 3.0) * 10))
            
            allergens_result.append({
                "name": dataTrees[i],
                "value": val_10_scale
            })
            total_activity += val_10_scale

    # Твоя формула: среднее + "штраф" за аномалию
    final_activity = 0
    if len(allergens_result) > 0:
        base_avg = total_activity / len(allergens_result)
        max_allergen = max(allergens_result, key=lambda x: x["value"])["value"]
        
        if max_allergen >= 6:
            final_activity = int(round(base_avg)) + 2
        else:
            final_activity = int(round(base_avg))
            
        if final_activity > 10: final_activity = 10

    allergens_result.sort(key=lambda x: x["value"], reverse=True)

    # Отдаем ответ пользователю
    return {
        "activity": final_activity,
        "allergens": allergens_result,
        "weatherImage": "sun.max.fill" if final_activity < 5 else "wind",
        "server_info": f"Данные актуальны на {LAST_UPDATED}" # Можешь убрать это поле, оно для дебага
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8750)