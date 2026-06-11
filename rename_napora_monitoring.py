# rename_napora_monitoring.py
import db_mongo

OLD = "Надрага Святослав Іванович"
NEW = "Напора Святослав Іванович"   # ← звірте, що ТОЧНО так, як у users і school_data

result = db_mongo.monitoring_collection.update_many(
    {"teacher": OLD},
    {"$set": {"teacher": NEW}}
)
print(f"Оновлено записів: {result.modified_count}")