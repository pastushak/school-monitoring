import db_mongo

EMAIL = "nadraga_svyatoslav@kolgym.if.ua"
NEW = "Напора Святослав Іванович"

result = db_mongo.users_collection.update_one(
    {"email": EMAIL},
    {"$set": {"name": NEW}}
)
print(f"Оновлено users: {result.modified_count}")