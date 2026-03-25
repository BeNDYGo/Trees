import requests
import json

url = "https://new.pollen.club/ajax/get_pollen_data"

params = {
    "url": "https://test.pollen.club/maps/ddr_query.php",
    "method": "indexStat",
    "params[type]": "5",
    "params[fromd]": "2026-03-25",
    "params[fromt]": "0"
}

response = requests.get(url, params=params)

outer_response = response.json()
print(outer_response)

my = "55.7160, 37.6606"
my_lat, my_lon = map(float, my.split(", "))
tolerance = 0.1

if outer_response.get("success"):
    inner_data = json.loads(outer_response["data"])

    for r in inner_data:
        date = r["date"]
        lat, lon = float(r['latitude']), float(r['longitude'])
        value = r['value']

        print(
            date[:10],
            f"({lat, lon})",
            f"уровень={value}",
        )
