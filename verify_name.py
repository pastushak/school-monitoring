# verify_name.py
import db_mongo
u = db_mongo.users_collection.find_one({"name": {"$regex": "Напора"}})
print("users:", repr(u.get("name")) if u else "НЕ ЗНАЙДЕНО")

sd = db_mongo.get_school_data()
napora_keys = [k for k in sd.get("teachers", {}) if "Напора" in k]
print("school_data:", [repr(k) for k in napora_keys])