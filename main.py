import requests
import json

# 1 - берёза | 2 - дуб | 3 - ольха | 4 - полынь | 5 - орешник | 6 - злаки | 7 - маревые | 8 - амброзия |

BASE_URL = "https://new.pollen.club/ajax/get_pollen_data"
CENTER_MOSCOW = (55.7544, 37.6228)
TOLERANCE = 0.3

def get_pollen_info(alerg_type: int):
    filters = []
    all_data_points = []
    total_val = 0
    max_val = 0
    
    c_lat, c_lon = CENTER_MOSCOW

    try:
        query_params = {
            "url": "https://test.pollen.club/maps/ddr_query.php",
            "method": "indexStat",
            "params[type]": alerg_type, 
            "params[fromd]": "2026-03-25",
            "params[fromt]": "0"
        }

        response = requests.get(BASE_URL, params=query_params)
        data_json = response.json()

        if data_json.get("success"):
            inner_data = json.loads(data_json["data"])

            for r in inner_data:
                date = r["date"]
                lat, lon = float(r['latitude']), float(r['longitude'])
                value = int(r['value'])

                all_data_points.append((lat, lon))

                if abs(lat - c_lat) <= TOLERANCE and abs(lon - c_lon) <= TOLERANCE:
                    filters.append(r)
                    total_val += value
                    if value > max_val: max_val = value
                    '''
                    print(
                        date[:10],
                        f"({lat}, {lon})",
                        f"уровень={value}",
                    )
                    '''
            print(f"Подошло {len(filters)}/{len(all_data_points)} | среднее значение: {total_val/len(filters):.3f}, max: {max_val}")
            return filters
        
    except Exception as e: print(e)
    
for x in range(1, 9):
    get_pollen_info(x)
