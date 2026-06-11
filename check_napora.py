# check_napora.py
import db_mongo
count = db_mongo.monitoring_collection.count_documents({"teacher": "Надрага Святослав Іванович"})
print(f"Записів під старим ПІБ: {count}")