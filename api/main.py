import json
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, func, delete
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from config.settings import settings
# from db.models import Subscription, get_session, Product, engine
from schemas.schemas import DeviceData, ImeiRequest



app = FastAPI(docs_url="/api/v1/doc")
scheduler = AsyncIOScheduler()
#211695539 
API_KEY_CKECKER = 'e4oEaZY1Kom5OXzybETkMlwjOCy3i8GSCGTHzWrhd4dc563b'
# API_KEY_CKECKER = settings.checker_api

origins = [
    f'{settings.app_host}:{settings.app_port}',  # Замените на адрес вашего веб-приложения
    f'{settings.app_host}:{settings.app_port}', # Или добавьте домен вашего фронтенда
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Origin", "X-Requested-With", "Content-Type", "Accept", "Authorization"],
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '')))
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="templates/static"), name="static")

# @app.on_event("startup")
# async def on_startup():
#     from db.models import create_db_and_tables
#     await create_db_and_tables()
#     await restore_subscriptions()
#     scheduler.start()

# @app.on_event("shutdown")
# async def on_shutdown():
#     scheduler.shutdown()

async def get_info_from_checker(imei: str) -> dict:
    url = "https://api.imeicheck.net/v1/checks"
    payload = json.dumps({
        "deviceId": imei,
        "serviceId": 1
    })
    headers = {
        'Authorization': f'Bearer {API_KEY_CKECKER}',
        'Accept-Language': 'en',
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()
        if data.get("state") != 0:
           raise HTTPException(status_code=404, detail="Product not found on Wildberries")
        imei_data = data["data"]["properties"]
        return {
            "name": imei_data["deviceName"],
            "image": imei_data["image"],
            "imei": imei_data["imei"],
            "simLock": imei_data["simLock"],
            "repairCoverage": imei_data["repairCoverage"],
            "technicalSupport": imei_data["technicalSupport"],
            "modelDesc": imei_data["modelDesc"],
            "demoUnit": imei_data["demoUnit"],
            "refurbished": imei_data["refurbished"],
            "apple/region": imei_data["apple/region"],
            "fmiOn": imei_data["fmiOn"],
            "lostMode": imei_data["lostMode"],
            "usaBlockStatus": imei_data["usaBlockStatus"],
            "network": imei_data["network"],
        }



@app.post("/api/v1/imei", response_model=DeviceData)
async def get_product_info(
    imei_request: ImeiRequest,
    api_key: str = Depends(APIKeyHeader(name="Authorization", auto_error=False)),
    ):
    """
    Эндпоинт для получения информации об IMEI.

    Args:
        product_request: Запрос с ID товара.
        api_key: Токен для авторизации.

    Returns:
        Информация о IMEI.
    """
    from bot.bot import bot
    await bot.send_message(498283860, 'В start')

    print(api_key)

    if api_key != f"Bearer {API_KEY_CKECKER}":
        raise HTTPException(status_code=401, detail="Невалидный токен")
    try:
        imei_data = await get_info_from_checker(imei_request)

        return DeviceData(
            deviceName = imei_data['deviceName'],
            image = imei_data['image'],
            imei = imei_data['imei'],
            estPurchaseDate = imei_data['estPurchaseDate'],
            simLock = imei_data['simLock'],
            warrantyStatus = imei_data['warrantyStatus'],
            repairCoverage = imei_data['repairCoverage'],
            technicalSupport = imei_data['technicalSupport'],
            modelDesc = imei_data['modelDesc'],
            demoUnit = imei_data['demoUnit'],
            refurbished = imei_data['refurbished'],
            purchaseCountry = imei_data['purchaseCountry'],
            apple_region = imei_data['apple_region'],
            fmiOn = imei_data['fmiOn'],
            lostMode = imei_data['lostMode'],
            usaBlockStatus = imei_data['usaBlockStatus'],
            network = imei_data['network'],
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
       raise HTTPException(status_code=500, detail=str(e))



@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/imei_info.html", response_class=HTMLResponse)
async def read_product(request: Request):
    return templates.TemplateResponse("imei_info.html", {"request": request})

if __name__ == "__main__":
      import uvicorn
      uvicorn.run(app, host="0.0.0.0", port=8000, ssl_certfile="localhost+2.pem", ssl_keyfile="localhost+2-key.pem")