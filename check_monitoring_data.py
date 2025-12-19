import db_mongo
from datetime import datetime

# Підключитися до MongoDB
db_mongo.init_mongodb()

print("=" * 80)
print("📊 ПЕРЕВІРКА ДАНИХ В БАЗІ MONGODB")
print("=" * 80)

# 1. Підрахунок записів
monitoring_count = db_mongo.db['monitoring_data'].count_documents({})
users_count = db_mongo.db['users'].count_documents({})
school_data_count = db_mongo.db['school_data'].count_documents({})

print(f"\n📈 Загальна статистика:")
print(f"   Користувачів: {users_count}")
print(f"   Записів школи: {school_data_count}")
print(f"   Записів моніторингу: {monitoring_count}")

# 2. Записи по роках
print(f"\n📅 Розподіл по навчальних роках:")
years = db_mongo.db['monitoring_data'].distinct('year')
for year in sorted(years):
    count = db_mongo.db['monitoring_data'].count_documents({'year': year})
    print(f"   {year}: {count} записів")

# 3. Записи по класах
print(f"\n🎓 Розподіл по класах:")
classes = db_mongo.db['monitoring_data'].distinct('class')
for class_name in sorted(classes):
    count = db_mongo.db['monitoring_data'].count_documents({'class': class_name})
    print(f"   {class_name}: {count} записів")

# 4. Записи по вчителях
print(f"\n👨‍🏫 Розподіл по вчителях:")
teachers = db_mongo.db['monitoring_data'].distinct('teacher')
for teacher in sorted(teachers):
    count = db_mongo.db['monitoring_data'].count_documents({'teacher': teacher})
    print(f"   {teacher}: {count} записів")

# 5. Останні 10 записів
print(f"\n📝 Останні 10 внесених записів:")
recent_records = db_mongo.db['monitoring_data'].find().sort('_id', -1).limit(10)

for idx, record in enumerate(recent_records, 1):
    print(f"\n   {idx}. {record.get('year')} - {record.get('class')} - {record.get('subject')}")
    print(f"      Вчитель: {record.get('teacher')}")
    print(f"      Учнів: {record.get('student_count')}")
    stats = record.get('statistics', {})
    print(f"      СБ: {stats.get('avgScore', 'N/A')}, СН: {stats.get('learningLevel', 'N/A')}")

print("\n" + "=" * 80)