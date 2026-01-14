# services/mongodb_indexes.py
"""Ініціалізація індексів MongoDB"""
import logging

logger = logging.getLogger(__name__)


def remove_duplicates(monitoring_collection):
    """Видалити дублікати перед створенням унікального індексу"""
    pipeline = [
        {
            '$group': {
                '_id': {
                    'year': '$year',
                    'class': '$class',
                    'teacher': '$teacher',
                    'subject': '$subject',
                    'semester': '$semester'
                },
                'ids': {'$push': '$_id'},
                'count': {'$sum': 1}
            }
        },
        {
            '$match': {
                'count': {'$gt': 1}
            }
        }
    ]
    
    duplicates = list(monitoring_collection.aggregate(pipeline))
    
    if duplicates:
        print(f"⚠️  Знайдено {len(duplicates)} груп дублікатів")
        removed_count = 0
        
        for dup in duplicates:
            # Залишити тільки перший запис, видалити інші
            ids_to_remove = dup['ids'][1:]  # всі крім першого
            result = monitoring_collection.delete_many({'_id': {'$in': ids_to_remove}})
            removed_count += result.deleted_count
        
        print(f"✓ Видалено {removed_count} дублікатів")
    else:
        print("✓ Дублікатів не знайдено")


def initialize_indexes(monitoring_collection):
    """Створює індекси один раз при старті"""
    try:
        # Спочатку видалити дублікати
        remove_duplicates(monitoring_collection)
        
        existing = monitoring_collection.index_information()
        
        # Унікальний індекс для моніторингу
        if 'monitoring_unique_idx' not in existing:
            monitoring_collection.create_index([
                ("year", 1),
                ("class", 1),
                ("teacher", 1),
                ("subject", 1),
                ("semester", 1)
            ], unique=True, background=True, name="monitoring_unique_idx")
            print("✓ Створено monitoring_unique_idx")
        else:
            print("✓ monitoring_unique_idx вже існує")
        
        # Індекс для сортування по даті
        if 'updated_at_idx' not in existing:
            monitoring_collection.create_index(
                [("updated_at", -1)],
                background=True,
                name="updated_at_idx"
            )
            print("✓ Створено updated_at_idx")
        else:
            print("✓ updated_at_idx вже існує")
        
        # Індекс для пошуку по вчителю
        if 'teacher_idx' not in existing:
            monitoring_collection.create_index(
                [("teacher", 1)],
                background=True,
                name="teacher_idx"
            )
            print("✓ Створено teacher_idx")
        else:
            print("✓ teacher_idx вже існує")
        
        print("✅ MongoDB індекси готові!")
        
    except Exception as e:
        logger.error(f"✗ Помилка створення індексів: {e}")
        print(f"⚠️ Помилка створення індексів: {e}")