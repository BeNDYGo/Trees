from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/homeView")
async def get_home_data(lat: float = None, lon: float = None):
    # Здесь в будущем ты сделаешь запрос к pollen.club или Яндекс Погоде
    # на основе полученных lat и lon.
    
    # А пока имитируем определение города:
    detected_city = "Москва" if lat and lon else "Город не определен"

    sample = {
      "city": detected_city, # <-- Отдаем город отсюда!
      "activity": 8,
      "allergens":[
        { "name": "Береза", "value": 9 },
        { "name": "Орешник", "value": 3 },
        { "name": "Ольха", "value": 5 }
      ],
      "weatherImage": "cloud.moon.fill"
    }
    return sample

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8750)