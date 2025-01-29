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
from db.models import Subscription, get_session, Product, engine
from schemas.schemas import ProductRequest, ProductResponse, MessageResponse



app = FastAPI(docs_url="/api/v1/doc")
scheduler = AsyncIOScheduler()
#211695539 

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

async def get_product_from_wb(artikul: str) -> dict:
    url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={artikul}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("state") != 0:
           raise HTTPException(status_code=404, detail="Product not found on Wildberries")
        product_data = data["data"]["products"][0]
        return {
            "name": product_data["name"],
            "artikul": str(product_data["id"]),
            "price": product_data["salePriceU"] / 100,
            "rating": product_data["rating"],
            "total_quantity": sum([stock["qty"] for stock in product_data["sizes"][0]["stocks"]]),
        }

async def get_product_from_db(session: AsyncSession, artikul: str) -> Product:
    query = select(Product).where(Product.artikul == artikul)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def create_product(session: AsyncSession, product_data: dict) -> Product:
   query = insert(Product).values(product_data).returning(Product)
   result = await session.execute(query)
   await session.commit()
   return result.scalar_one()


async def update_product(session: AsyncSession, artikul:str, product_data: dict) -> Product:
    query = select(Product).where(Product.artikul == artikul)
    result = await session.execute(query)
    product = result.scalar_one()
    if product:
        for key, value in product_data.items():
            setattr(product, key, value)
        product.last_updated = func.now()
        await session.commit()
    return product

async def add_subscription(session: AsyncSession, artikul: str):
    query = select(Subscription).where(Subscription.artikul == artikul)
    result = await session.execute(query)
    if not result.scalar_one_or_none():
        query = insert(Subscription).values(artikul=artikul)
        await session.execute(query)
        await session.commit()
        print(f'Added subscription to {artikul}')
    else:
        print(f"Subscription to {artikul} already exists")


async def restore_subscriptions():
    async for session in get_session():
        query = select(Subscription)
        result = await session.execute(query)
        for subscription in result.scalars():
            scheduler.add_job(
                scheduled_product_update,
                trigger=CronTrigger(minute="*/3"),
                args=[subscription.artikul, session],
                id=subscription.artikul,
                replace_existing=True,
            )

async def remove_subscription(session: AsyncSession, artikul: str):
    query = delete(Subscription).where(Subscription.artikul == artikul)
    await session.execute(query)
    await session.commit()
    job = scheduler.get_job(artikul)
    if not job:
        print(f"Subscription to {artikul} does not exist")
        return
    scheduler.remove_job(job_id=artikul)
    print(f'Removed subscription to {artikul}')

async def scheduled_product_update(artikul: str, session: AsyncSession):
    try:
        product_data = await get_product_from_wb(artikul)
        existing_product = await get_product_from_db(session, product_data["artikul"])
        if existing_product:
            await update_product(session, product_data["artikul"], product_data)
        else:
           await create_product(session, product_data)
        print(f'Updated product')
    except Exception as e:
         print(f"Error updating product {artikul}: {e}")

@app.get('/api/v1/wb', response_model=ProductResponse)
async def get_product_wb(
    product_request: ProductRequest,
    api_key: str = Depends(APIKeyHeader(name="Authorization", auto_error=False)),
    session: AsyncSession = Depends(get_session)
    ):
    """
    Эндпоинт для получения информации о товаре из wb.

    Args:
        product_request: Запрос с ID товара.
        api_key: Токен для авторизации.
        session: Сессия для работы с базой данных.

    Returns:
        Информация о товаре.
    """
    if api_key != "Bearer test_api_key":
        raise HTTPException(status_code=401, detail="Невалидный токен")
    try:
        product_data = await get_product_from_wb(product_request.artikul)
        return ProductResponse(
               name=product_data.get('name'),
               artikul=product_data.get('artikul'),
               price=float(product_data.get('price')),
               rating=float(product_data.get('rating')),
               total_quantity=product_data.get('total_quantity')
            )
    except HTTPException as e:
        raise e
    except Exception as e:
       raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/products", response_model=ProductResponse)
async def get_product_info(
    product_request: ProductRequest,
    api_key: str = Depends(APIKeyHeader(name="Authorization", auto_error=False)),
    session: AsyncSession = Depends(get_session)
    ):
    """
    Эндпоинт для получения информации о товаре и записи в базу.

    Args:
        product_request: Запрос с ID товара.
        api_key: Токен для авторизации.
        session: Сессия для работы с базой данных.

    Returns:
        Информация о товаре.
    """
<<<<<<< HEAD
    from bot import bot
    await bot.send_message(498283860, 'В start')
=======
    print(api_key)
>>>>>>> d2a4e04ea3abbbdc1bc07eb6ac9af6e9e6d8260a
    if api_key != "Bearer test_api_key":
        raise HTTPException(status_code=401, detail="Невалидный токен")
    try:
        product_data = await get_product_from_wb(product_request.artikul)
        existing_product = await get_product_from_db(session, product_data["artikul"])
        if existing_product:
            updated_product = await update_product(session, product_data["artikul"], product_data)
            return ProductResponse(
               name=updated_product.name,
               artikul=updated_product.artikul,
               price=float(updated_product.price),
               rating=float(updated_product.rating),
               total_quantity=updated_product.total_quantity
            )
        else:
            created_product = await create_product(session, product_data)
            return ProductResponse(
               name=created_product.name,
               artikul=created_product.artikul,
               price=float(created_product.price),
               rating=float(created_product.rating),
               total_quantity=created_product.total_quantity
            )
    except HTTPException as e:
        raise e
    except Exception as e:
       raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/subscribe/{artikul}", response_model=MessageResponse)
async def subscribe_product(artikul: str, api_key: str = Depends(APIKeyHeader(name="Authorization", auto_error=False)), session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для подписки на обновления данных о товаре.

    Args:
        artikul: Артикул товара.
        api_key: Токен для авторизации.
        session: Сессия для работы с базой данных.

    Returns:
        Сообщение о результате подписки.
    """
    if api_key != "Bearer test_api_key":
        raise HTTPException(status_code=401, detail="Невалидный токен")
    await add_subscription(session, artikul)
    scheduler.add_job(
        scheduled_product_update,
        trigger=CronTrigger(minute="*/30"),
        args=[artikul, session],
        id=artikul,
        replace_existing=True,
    )
    return {"message": f"Subscription for product {artikul} started."}

@app.get("/api/v1/unsubscribe/{artikul}", response_model=MessageResponse)
async def unsubscribe_product(artikul: str, api_key: str = Depends(APIKeyHeader(name="Authorization", auto_error=False)), session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для отписки от обновлений данных о товаре.

    Args:
        artikul: Артикул товара.
        api_key: Токен для авторизации.
        session: Сессия для работы с базой данных.

    Returns:
        Сообщение о результате отписки.
    """
    if api_key != "Bearer test_api_key":
        raise HTTPException(status_code=401, detail="Невалидный токен")
    await remove_subscription(session, artikul)
    return {"message": f"Subscription for product {artikul} stopped."}


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/product.html", response_class=HTMLResponse)
async def read_product(request: Request):
    return templates.TemplateResponse("product.html", {"request": request})

if __name__ == "__main__":
      import uvicorn
      uvicorn.run(app, host="0.0.0.0", port=8000, ssl_certfile="localhost+2.pem", ssl_keyfile="localhost+2-key.pem")