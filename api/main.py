import json
import os
import sys
import time
import logging
import aiohttp
import requests

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

# Настройка логирования
logging.basicConfig(level=logging.INFO)

app = FastAPI(docs_url="/api/v1/doc")
scheduler = AsyncIOScheduler()
#211695539 
# API_KEY_CKECKER = '57V2of0gNh8PybWXMSjM6LzrQziw3d4pJNpygJb060f18f8a'
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
    logging.info(f'imei: {imei}')
    url = "https://api.imeicheck.net/v1/checks"
    payload = json.dumps({
        "deviceId": imei,
        "serviceId": 12
    })
    headers = {
        'Authorization': f'Bearer {API_KEY_CKECKER}',
        'Content-Type': 'application/json'
    }
    async with httpx.AsyncClient() as client:
        logging.info(f'in clint')
        response = await client.post(url, headers=headers, data=payload)
        logging.info(f'response: {response}')
        response.raise_for_status()
        data = response.json()
        print(data.get('properties'))
        if data.get('status') != 'successful':
           raise HTTPException(status_code=404, detail="Product not found on Wildberries")
        imei_data = data['properties']
        return {
            "name": imei_data.get("deviceName"),
            "image": imei_data.get("image"),
            "imei": imei_data.get("imei"),
            "simLock": imei_data.get("simLock"),
            "repairCoverage": imei_data.get("repairCoverage"),
            "technicalSupport": imei_data.get("technicalSupport"),
            "modelDesc": imei_data.get("modelDesc"),
            "demoUnit": imei_data.get("demoUnit"),
            "refurbished": imei_data.get("refurbished"),
            "apple/region": imei_data.get("apple/region"),
            "fmiOn": imei_data.get("fmiOn"),
            "lostMode": imei_data.get("lostMode"),
            "usaBlockStatus": imei_data.get("usaBlockStatus"),
            "network": imei_data.get("network"),
        }
async def get_balance():
    url = 'https://api.imeicheck.net/v1/account'
    
    headers = {
    'Authorization': 'Bearer ' + API_KEY_CKECKER,
    'Content-Type': 'application/json'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            balance = float(data['balance'])

            return balance
        
@app.get("/api/v1/balance")
async def balance(
    api_key: str = Depends(APIKeyHeader(name="Authorization", auto_error=False)),
    ):
    if api_key != f"Bearer {API_KEY_CKECKER}":
        raise HTTPException(status_code=401, detail="Невалидный токен")
    try:
        balance = await get_balance()
        return balance
    except HTTPException as e:
        raise e
    except Exception as e:
       raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/imei")
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
    await bot.send_message(498283860, 'in get_product_info')

    print(api_key)

    if api_key != f"Bearer {API_KEY_CKECKER}":
        raise HTTPException(status_code=401, detail="Невалидный токен")
    try:
        imei_data = await get_info_from_checker(imei_request.imei)
        return imei_data
        # return DeviceData(
        #     deviceName = imei_data['deviceName'],
        #     image = imei_data['image'],
        #     imei = imei_data['imei'],
        #     estPurchaseDate = imei_data['estPurchaseDate'],
        #     simLock = imei_data['simLock'],
        #     warrantyStatus = imei_data['warrantyStatus'],
        #     repairCoverage = imei_data['repairCoverage'],
        #     technicalSupport = imei_data['technicalSupport'],
        #     modelDesc = imei_data['modelDesc'],
        #     demoUnit = imei_data['demoUnit'],
        #     refurbished = imei_data['refurbished'],
        #     purchaseCountry = imei_data['purchaseCountry'],
        #     apple_region = imei_data['apple_region'],
        #     fmiOn = imei_data['fmiOn'],
        #     lostMode = imei_data['lostMode'],
        #     usaBlockStatus = imei_data['usaBlockStatus'],
        #     network = imei_data['network'],
        # )
        
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
      uvicorn.run(app, host="127.0.0.1", port=8080, ssl_certfile="localhost+2.pem", ssl_keyfile="localhost+2-key.pem")