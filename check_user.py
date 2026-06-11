# check_user.py
import db_mongo
# шукаємо за фрагментом email або старим прізвищем
u_old = db_mongo.users_collection.find_one({"name": {"$regex": "Надрага"}})
print("Надрага у users:", repr(u_old.get("name")) if u_old else "нема")

u_new = db_mongo.users_collection.find_one({"name": {"$regex": "Напора"}})
print("Напора у users:", repr(u_new.get("name")) if u_new else "нема")

# знайдемо за email (email не мав мінятись)
u_email = db_mongo.users_collection.find_one({"email": {"$regex": "nadraga|napora"}})
print("За email:", repr(u_email) if u_email else "нема")