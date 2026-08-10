import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "telegram_store_bot")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

users_collection = db["users"]
accounts_collection = db["accounts"]
orders_collection = db["orders"]

async def get_user(user_id: int):
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        user = {
            "user_id": user_id,
            "balance": 0,
            "created_at": datetime.utcnow()
        }
        await users_collection.insert_one(user)
    return user

async def update_balance(user_id: int, amount: int):
    await users_collection.update_one(
        {"user_id": user_id},
        {"$inc": {"balance": amount}},
        upsert=True
    )

async def add_account(country: str, phone: str, session_string: str, price: int):
    account = {
        "country": country,
        "phone": phone,
        "session_string": session_string,
        "price": price,
        "is_sold": False,
        "added_at": datetime.utcnow()
    }
    await accounts_collection.insert_one(account)

async def get_available_accounts(country: str):
    cursor = accounts_collection.find({"country": country, "is_sold": False})
    return await cursor.to_list(length=None)

async def get_account_by_id(account_id: str):
    from bson.ObjectId import ObjectId
    try:
        return await accounts_collection.find_one({"_id": ObjectId(account_id), "is_sold": False})
    except:
        return None

async def mark_account_as_sold(account_id: str, user_id: int, order_id: str):
    from bson.ObjectId import ObjectId
    await accounts_collection.update_one(
        {"_id": ObjectId(account_id)},
        {"$set": {"is_sold": True, "sold_to": user_id, "order_id": order_id, "sold_at": datetime.utcnow()}}
    )

async def create_order(order_data: dict):
    await orders_collection.insert_one(order_data)

async def get_order(order_id: str):
    return await orders_collection.find_one({"order_id": order_id})
