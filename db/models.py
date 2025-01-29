import datetime

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import settings

engine = create_async_engine(settings.database_url, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = sa.Column(sa.Integer, primary_key=True)
    artikul = sa.Column(sa.String(255), unique=True, index=True)
    name = sa.Column(sa.String(255))
    price = sa.Column(sa.Numeric)
    rating = sa.Column(sa.Numeric)
    total_quantity = sa.Column(sa.Integer)
    last_updated = sa.Column(sa.DateTime(timezone=True), default=datetime.datetime.utcnow)

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = sa.Column(sa.Integer, primary_key=True)
    artikul = sa.Column(sa.String(255), unique=True, index=True)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session():
    async with async_session() as session:
        yield session