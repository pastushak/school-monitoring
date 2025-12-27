#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Додати semester до старих записів в MongoDB
"""

from db_mongo import db

def fix_old_records():
    """Додати semester: 1 до записів без semester"""
    print("=" * 60)
    print("ВИПРАВЛЕННЯ СТАРИХ ЗАПИСІВ")
    print("=" * 60)
    
    # Знайти записи без semester
    query = {"semester": {"$exists": False}}
    old_records = list(db['monitoring_data'].find(query))
    
    print(f"Знайдено записів без semester: {len(old_records)}")
    
    if len(old_records) == 0:
        print("✓ Всі записи вже мають semester")
        return
    
    # Показати які записи
    for record in old_records:
        print(f"  - {record['year']} | {record['class']} | {record['subject']} | {record['teacher']}")
    
    # Оновити всі записи
    result = db['monitoring_data'].update_many(
        query,
        {"$set": {"semester": 1}}  # Додати I семестр за замовчуванням
    )
    
    print(f"\n✓ Оновлено {result.modified_count} записів")
    print("=" * 60)
    print("ВИПРАВЛЕННЯ ЗАВЕРШЕНО!")
    print("=" * 60)

if __name__ == '__main__':
    fix_old_records()