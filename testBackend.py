from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники
    allow_methods=["*"],  # Разрешить POST, GET, etc.
    allow_headers=["*"],  # Разрешить JSON заголовки
)

sample = {
  "activity": 8,
  "allergens": [
    { "name": "Береза", "value": 9 },
    { "name": "Орешник", "value": 3 },
    { "name": "Ольха", "value": 5 }
  ],
  "weatherImage": "cloud.moon.fill"
}

@app.get("/")
async def ping():
    return sample

uvicorn.run(app, host="0.0.0.0", port=8750)

# python3 testBackend.py