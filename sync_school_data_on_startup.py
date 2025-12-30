# Автоматична синхронізація school_data при старті
def sync_school_data_on_startup():
    """Синхронізувати school_data.json з MongoDB при старті"""
    import json
    from db_mongo import db  # ✅ ВАЖЛИВО!
    
    print("=" * 60)
    print("СИНХРОНІЗАЦІЯ school_data.json → MongoDB")
    print("=" * 60)
    
    try:
        with open('data/school_data.json', 'r', encoding='utf-8') as f:
            school_data = json.load(f)
        
        # Видалити стару колекцію
        result = db['school_data'].delete_many({})
        print(f"✓ Видалено старих записів: {result.deleted_count}")
        
        # Вставити нові дані
        db['school_data'].insert_one(school_data)
        print(f"✓ Додано класів: {len(school_data['classes'])}")
        print(f"✓ Додано вчителів: {len(school_data['teachers'])}")
        
        print("=" * 60)
        print("✓ СИНХРОНІЗАЦІЯ ЗАВЕРШЕНА!")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ ПОМИЛКА синхронізації: {e}")