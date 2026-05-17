"""
Бекап даних 1 семестру з MongoDB у JSON-файли.
Створює папку backups/2025-2026_semester1/ та зберігає туди:
- monitoring_data_semester1.json (тільки записи з semester=1)
- monitoring_data_all.json (УСІ записи моніторингу, на всякий випадок)
- users.json (всі користувачі)
- school_data.json (структура школи)
- backup_info.txt (метадані бекапу)
"""

import os
import json
from datetime import datetime
from bson import ObjectId
import db_mongo


# ──────────────────────────────────────────────────────────────
# Допоміжна функція: серіалізація MongoDB-об'єктів у JSON
# ──────────────────────────────────────────────────────────────
class MongoJSONEncoder(json.JSONEncoder):
    """Конвертує ObjectId та datetime у рядки для JSON."""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def save_json(data, filepath):
    """Зберегти список словників у JSON-файл."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, cls=MongoJSONEncoder)
    size_kb = os.path.getsize(filepath) / 1024
    print(f"  ✓ {os.path.basename(filepath)}  ({size_kb:.1f} KB, записів: {len(data) if isinstance(data, list) else 1})")


# ──────────────────────────────────────────────────────────────
# Основний скрипт
# ──────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("📦 БЕКАП ДАНИХ 1 СЕМЕСТРУ 2025-2026")
    print("=" * 70)

    # 1. Створити папку
    backup_dir = os.path.join('backups', '2025-2026_semester1')
    os.makedirs(backup_dir, exist_ok=True)
    print(f"\n📁 Папка: {backup_dir}\n")

    # 2. Дамп моніторингу — ТІЛЬКИ 1 семестр
    print("📊 Експорт записів моніторингу (semester=1)...")
    semester1_data = list(db_mongo.monitoring_collection.find({'semester': 1}))
    save_json(semester1_data, os.path.join(backup_dir, 'monitoring_data_semester1.json'))

    # 3. Дамп моніторингу — УСІ записи (як страховка)
    print("\n📊 Експорт усіх записів моніторингу (страховий бекап)...")
    all_monitoring = list(db_mongo.monitoring_collection.find({}))
    save_json(all_monitoring, os.path.join(backup_dir, 'monitoring_data_all.json'))

    # 4. Дамп користувачів
    print("\n👥 Експорт користувачів...")
    users = list(db_mongo.users_collection.find({}))
    save_json(users, os.path.join(backup_dir, 'users.json'))

    # 5. Дамп структури школи (класи, вчителі, навантаження)
    print("\n🏫 Експорт структури школи...")
    school_data = list(db_mongo.school_data_collection.find({}))
    save_json(school_data, os.path.join(backup_dir, 'school_data.json'))

    # 6. Метадані бекапу
    print("\n📝 Створення файлу метаданих...")
    info = {
        'backup_date': datetime.now().isoformat(),
        'academic_year': '2025-2026',
        'semester': 1,
        'counts': {
            'monitoring_semester1': len(semester1_data),
            'monitoring_all': len(all_monitoring),
            'users': len(users),
            'school_data': len(school_data),
        }
    }
    info_path = os.path.join(backup_dir, 'backup_info.json')
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print(f"  ✓ backup_info.json")

    # Підсумок
    print("\n" + "=" * 70)
    print("✅ БЕКАП ЗАВЕРШЕНО!")
    print("=" * 70)
    print(f"📁 Розташування: {os.path.abspath(backup_dir)}")
    print(f"📊 Записів моніторингу (1 семестр): {len(semester1_data)}")
    print(f"📊 Записів моніторингу (всього):    {len(all_monitoring)}")
    print(f"👥 Користувачів:                     {len(users)}")
    print(f"🏫 Записів школи:                    {len(school_data)}")
    print("=" * 70)


if __name__ == '__main__':
    main()